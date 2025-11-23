"""
Skill Storage Adapter - Filesystem persistence for skills.

Handles saving/loading base and ephemeral skills from `.copilot/skills/` directory.
Manages skill lifecycle: creation, updates, archival, and cleanup.
"""

import asyncio
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles

from cde_orchestrator.infrastructure.telemetry import trace_execution

from .models import (
    BaseSkill,
    EphemeralSkill,
    SkillIndexEntry,
    SkillMetadata,
    SkillStatus,
    SkillType,
)


class SkillStorageAdapter:
    """
    Manages skill persistence on the filesystem.

    Skills are stored in the following structure:
    .copilot/
    ├── skills/
    │   ├── base/              # Persistent skills
    │   │   ├── skill-id-1/
    │   │   │   ├── SKILL.md
    │   │   │   └── metadata.json
    │   │   └── skill-id-2/
    │   │       ├── SKILL.md
    │   │       └── metadata.json
    │   └── ephemeral/         # Task-specific, auto-cleaned
    │       ├── task-uuid-1/
    │       │   ├── SKILL.md
    │       │   └── metadata.json
    │       └── task-uuid-2/
    │           ├── SKILL.md
    │           └── metadata.json
    │   └── index.json             # Fast lookup index
    """

    def __init__(self, cde_root: Optional[Path] = None):
        """
        Initialize storage adapter.

        Args:
            cde_root: Path to CDE project root. If None, searches for .cde/ directory.
        """
        if cde_root is None:
            # Try to find .cde/ in current directory or parent
            cde_root = self._find_cde_root()

        self.cde_root = Path(cde_root)
        self.skills_dir = self.cde_root / ".copilot" / "skills"
        self.base_skills_dir = self.skills_dir / "base"
        self.ephemeral_skills_dir = self.skills_dir / "ephemeral"
        self.index_file = self.skills_dir / "index.json"

        # Create directories if they don't exist
        self.base_skills_dir.mkdir(parents=True, exist_ok=True)
        self.ephemeral_skills_dir.mkdir(parents=True, exist_ok=True)

        self.index: Dict[str, SkillIndexEntry] = {}
        # Index loading is now async, must be called explicitly or lazily
        # For backward compatibility, we initialize empty and expect load_index to be called

    @staticmethod
    def _find_cde_root() -> Path:
        """Find .cde directory in current or parent directories."""
        current = Path.cwd()
        for _ in range(5):  # Search up to 5 levels
            if (current / ".cde").exists():
                return current
            current = current.parent
        # Default to current directory
        return Path.cwd()

    async def initialize(self) -> None:
        """Async initialization to load index."""
        await self._load_index()

    async def _load_index(self) -> None:
        """Load the skill index from disk."""
        if self.index_file.exists():
            try:
                async with aiofiles.open(self.index_file, "r", encoding="utf-8") as f:
                    content = await f.read()
                    data = json.loads(content)
                    self.index = {k: SkillIndexEntry(**v) for k, v in data.items()}
            except Exception:
                # If index is corrupted, start fresh
                self.index = {}
        else:
            self.index = {}

    async def _save_index(self) -> None:
        """Save the skill index to disk."""
        async with aiofiles.open(self.index_file, "w", encoding="utf-8") as f:
            data = {k: v.dict() for k, v in self.index.items()}
            await f.write(json.dumps(data, indent=2, default=str))

    async def save_base_skill(self, skill: BaseSkill) -> Path:
        """
        Save a base skill to persistent storage.

        Args:
            skill: BaseSkill to save

        Returns:
            Path to the saved skill directory
        """
        skill_dir = self.base_skills_dir / skill.id
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Save SKILL.md content
        skill_file = skill_dir / "SKILL.md"
        async with aiofiles.open(skill_file, "w", encoding="utf-8") as f:
            await f.write(skill.content)

        # Save metadata as JSON
        metadata_file = skill_dir / "metadata.json"
        async with aiofiles.open(metadata_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(skill.dict(), indent=2, default=str))

        # Update index
        self.index[skill.id] = SkillIndexEntry(
            skill_id=skill.id,
            skill_type=SkillType.BASE,
            domain=skill.domain,
            complexity=skill.complexity,
            tags=skill.tags,
            file_path=skill_file,
            last_indexed=datetime.now(timezone.utc),
            size_bytes=skill_file.stat().st_size,
            status=skill.status,
        )
        await self._save_index()

        return skill_dir

    async def save_ephemeral_skill(self, skill: EphemeralSkill) -> Path:
        """
        Save an ephemeral skill to temporary storage.

        Args:
            skill: EphemeralSkill to save

        Returns:
            Path to the saved skill directory
        """
        skill_dir = self.ephemeral_skills_dir / skill.id
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Save SKILL.md content
        skill_file = skill_dir / "SKILL.md"
        async with aiofiles.open(skill_file, "w", encoding="utf-8") as f:
            await f.write(skill.content)

        # Save metadata as JSON
        metadata_file = skill_dir / "metadata.json"
        async with aiofiles.open(metadata_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(skill.dict(), indent=2, default=str))

        # Update index
        self.index[skill.id] = SkillIndexEntry(
            skill_id=skill.id,
            skill_type=SkillType.EPHEMERAL,
            domain=skill.domain,
            complexity=skill.complexity,
            tags=skill.tags,
            file_path=skill_file,
            last_indexed=datetime.now(timezone.utc),
            size_bytes=skill_file.stat().st_size,
            status=SkillStatus.ACTIVE,
        )
        await self._save_index()

        return skill_dir

    async def load_base_skill(self, skill_id: str) -> Optional[BaseSkill]:
        """
        Load a base skill from disk.

        Args:
            skill_id: Skill ID to load

        Returns:
            BaseSkill object or None if not found
        """
        metadata_file = self.base_skills_dir / skill_id / "metadata.json"
        if not metadata_file.exists():
            return None

        async with aiofiles.open(metadata_file, "r", encoding="utf-8") as f:
            content = await f.read()
            data = json.loads(content)
            return BaseSkill(**data)

    async def load_ephemeral_skill(self, skill_id: str) -> Optional[EphemeralSkill]:
        """
        Load an ephemeral skill from disk.

        Args:
            skill_id: Skill ID to load

        Returns:
            EphemeralSkill object or None if not found
        """
        metadata_file = self.ephemeral_skills_dir / skill_id / "metadata.json"
        if not metadata_file.exists():
            return None

        async with aiofiles.open(metadata_file, "r", encoding="utf-8") as f:
            content = await f.read()
            data = json.loads(content)
            return EphemeralSkill(**data)

    async def delete_base_skill(self, skill_id: str) -> bool:
        """
        Delete a base skill.

        Args:
            skill_id: Skill ID to delete

        Returns:
            True if deleted, False if not found
        """
        skill_dir = self.base_skills_dir / skill_id
        if not skill_dir.exists():
            return False

        # Remove directory recursively in executor to avoid blocking
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, shutil.rmtree, skill_dir)

        # Remove from index
        self.index.pop(skill_id, None)
        await self._save_index()

        return True

    async def delete_ephemeral_skill(self, skill_id: str) -> bool:
        """
        Delete an ephemeral skill.

        Args:
            skill_id: Skill ID to delete

        Returns:
            True if deleted, False if not found
        """
        skill_dir = self.ephemeral_skills_dir / skill_id
        if not skill_dir.exists():
            return False

        # Remove directory recursively in executor
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, shutil.rmtree, skill_dir)

        # Remove from index
        self.index.pop(skill_id, None)
        await self._save_index()

        return True

    @trace_execution
    async def list_base_skills(self) -> List[SkillMetadata]:
        """
        List all base skills.

        Returns:
            List of skill metadata
        """
        if not self.base_skills_dir.exists():
            return []

        # Collect tasks for parallel execution
        tasks = []
        for skill_dir in self.base_skills_dir.iterdir():
            if skill_dir.is_dir():
                tasks.append(self.load_base_skill(skill_dir.name))

        if not tasks:
            return []

        # Execute in parallel
        loaded_skills = await asyncio.gather(*tasks)

        # Filter and convert to metadata
        skills = []
        for skill in loaded_skills:
            if skill:
                skills.append(
                    SkillMetadata(
                        id=skill.id,
                        title=skill.title,
                        domain=skill.domain,
                        complexity=skill.complexity,
                        tags=skill.tags,
                        status=skill.status,
                        updated_at=skill.updated_at,
                        size_tokens=skill.size_tokens,
                        confidence_score=skill.confidence_score,
                    )
                )
        return skills

    @trace_execution
    async def list_ephemeral_skills(self) -> List[SkillMetadata]:
        """
        List all ephemeral skills.

        Returns:
            List of skill metadata
        """
        if not self.ephemeral_skills_dir.exists():
            return []

        # Collect tasks for parallel execution
        tasks = []
        for skill_dir in self.ephemeral_skills_dir.iterdir():
            if skill_dir.is_dir():
                tasks.append(self.load_ephemeral_skill(skill_dir.name))

        if not tasks:
            return []

        # Execute in parallel
        loaded_skills = await asyncio.gather(*tasks)

        # Filter and convert to metadata
        skills = []
        for skill in loaded_skills:
            if skill:
                skills.append(
                    SkillMetadata(
                        id=skill.id,
                        title=skill.title,
                        domain=skill.domain,
                        complexity=skill.complexity,
                        tags=skill.tags,
                        status=(
                            SkillStatus.ACTIVE
                            if not skill.is_expired
                            else SkillStatus.ARCHIVED
                        ),
                        updated_at=skill.created_at,
                        size_tokens=skill.size_tokens,
                        confidence_score=skill.confidence_score,
                    )
                )
        return skills

    async def cleanup_expired_ephemeral_skills(self) -> int:
        """
        Delete expired ephemeral skills.

        Returns:
            Number of skills deleted
        """
        if not self.ephemeral_skills_dir.exists():
            return 0

        # Load all skills in parallel
        tasks = []
        for skill_dir in self.ephemeral_skills_dir.iterdir():
            if skill_dir.is_dir():
                tasks.append(self.load_ephemeral_skill(skill_dir.name))

        if not tasks:
            return 0

        loaded_skills = await asyncio.gather(*tasks)

        # Filter expired skills
        expired_skills = [s for s in loaded_skills if s and s.is_expired]

        if not expired_skills:
            return 0

        # Delete in parallel
        delete_tasks = [self.delete_ephemeral_skill(s.id) for s in expired_skills]
        results = await asyncio.gather(*delete_tasks)

        return sum(1 for r in results if r)

    async def search_skills(
        self, query: str, skill_type: Optional[SkillType] = None
    ) -> List[SkillMetadata]:
        """
        Search for skills by title/description/tags.

        Args:
            query: Search query (lowercase)
            skill_type: Filter by type (base/ephemeral) or None for all

        Returns:
            List of matching skill metadata
        """
        query_lower = query.lower()
        results = []

        # Search base skills
        if skill_type is None or skill_type == SkillType.BASE:
            base_skills = await self.list_base_skills()
            for skill in base_skills:
                if (
                    query_lower in skill.title.lower()
                    or query_lower in skill.id.lower()
                    or any(query_lower in tag.lower() for tag in skill.tags)
                ):
                    results.append(skill)

        # Search ephemeral skills
        if skill_type is None or skill_type == SkillType.EPHEMERAL:
            ephemeral_skills = await self.list_ephemeral_skills()
            for skill in ephemeral_skills:
                if (
                    query_lower in skill.title.lower()
                    or query_lower in skill.id.lower()
                    or any(query_lower in tag.lower() for tag in skill.tags)
                ):
                    results.append(skill)

        return results

    async def get_storage_stats(self) -> Dict[str, int | str]:
        """
        Get storage statistics.

        Returns:
            Dictionary with stats
        """
        base_skills = await self.list_base_skills()
        ephemeral_skills = await self.list_ephemeral_skills()

        total_base_tokens = sum(s.size_tokens for s in base_skills)
        total_ephemeral_tokens = sum(s.size_tokens for s in ephemeral_skills)

        return {
            "total_base_skills": len(base_skills),
            "total_ephemeral_skills": len(ephemeral_skills),
            "total_base_tokens": total_base_tokens,
            "total_ephemeral_tokens": total_ephemeral_tokens,
            "storage_dir": str(self.skills_dir),
        }
