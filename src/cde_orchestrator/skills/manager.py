"""
Skill Manager - Orchestrates the skill lifecycle.

Coordinates:
1. Skill detection and requirement analysis
2. Ephemeral skill preparation (combining base + new research)
3. Skill caching and reuse
4. Cleanup of expired skills
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .detector import SkillRequirementDetector
from .models import BaseSkill, EphemeralSkill, SkillDomain, SkillRequirement
from .storage import SkillStorageAdapter


class SkillManager:
    """
    Central orchestrator for skill lifecycle management.

    Responsibilities:
    - Analyze task requirements (via SkillRequirementDetector)
    - Load existing skills (base + ephemeral)
    - Prepare context-rich ephemeral skills for tasks
    - Manage cleanup of expired/archived skills
    """

    def __init__(self, cde_root: Optional[Path] = None):
        """
        Initialize SkillManager.

        Args:
            cde_root: Path to CDE project root
        """
        self.storage = SkillStorageAdapter(cde_root)
        self.detector = SkillRequirementDetector()
        self._ephemeral_cache: Dict[str, EphemeralSkill] = {}

    async def initialize(self) -> None:
        """Async initialization."""
        await self.storage.initialize()

    def analyze_task(self, task_description: str) -> SkillRequirement:
        """
        Analyze a task to determine skill requirements.

        Args:
            task_description: Natural language task description

        Returns:
            SkillRequirement with analysis results
        """
        return self.detector.analyze_task(task_description)

    async def get_base_skill(self, skill_id: str) -> Optional[BaseSkill]:
        """
        Retrieve a base skill by ID.

        Args:
            skill_id: Skill ID to retrieve

        Returns:
            BaseSkill or None if not found
        """
        return await self.storage.load_base_skill(skill_id)

    async def get_ephemeral_skill(self, skill_id: str) -> Optional[EphemeralSkill]:
        """
        Retrieve an ephemeral skill by ID.

        Args:
            skill_id: Skill ID to retrieve

        Returns:
            EphemeralSkill or None if not found
        """
        # Check cache first
        if skill_id in self._ephemeral_cache:
            skill = self._ephemeral_cache[skill_id]
            if not skill.is_expired:
                return skill
            else:
                del self._ephemeral_cache[skill_id]

        # Load from storage
        loaded_skill = await self.storage.load_ephemeral_skill(skill_id)
        if loaded_skill and not loaded_skill.is_expired:
            self._ephemeral_cache[skill_id] = loaded_skill
            return loaded_skill

        return None

    async def prepare_skills_for_task(
        self, task_description: str, task_id: str
    ) -> List[BaseSkill | EphemeralSkill]:
        """
        Prepare all relevant skills for a task execution.

        This is the main entry point for agents. It:
        1. Analyzes the task
        2. Finds matching base skills
        3. Returns ready-to-use skills

        Args:
            task_description: Task description
            task_id: Unique task identifier

        Returns:
            List of applicable skills (base and/or ephemeral)
        """
        # Analyze task
        requirement = self.analyze_task(task_description)

        if not requirement.needs_skill:
            return []

        skills: List[BaseSkill | EphemeralSkill] = []

        # Find matching base skills
        base_skills = await self._find_matching_base_skills(
            requirement.domain, requirement.knowledge_gaps
        )
        skills.extend(base_skills)

        # Try to find existing ephemeral skills that match
        matching_ephemeral = await self._find_matching_ephemeral_skills(
            task_id, requirement.knowledge_gaps
        )
        skills.extend(matching_ephemeral)

        # If not enough coverage, recommend skill generation
        covered_gaps = self._get_covered_gaps(skills, requirement.knowledge_gaps)
        uncovered_gaps = [
            g for g in requirement.knowledge_gaps if g not in covered_gaps
        ]

        if uncovered_gaps:
            # TODO: Would trigger SkillGenerator here to create ephemeral skills
            # For now, just return what we have
            pass

        return skills

    async def _find_matching_base_skills(
        self, domain: SkillDomain, knowledge_gaps: List[str]
    ) -> List[BaseSkill]:
        """
        Find base skills that match the domain and knowledge gaps.

        Args:
            domain: Task domain
            knowledge_gaps: Knowledge gaps to fill

        Returns:
            List of matching base skills
        """
        matching_skills: List[BaseSkill] = []

        # Get all base skills
        all_skills = await self.storage.list_base_skills()

        for skill_metadata in all_skills:
            skill = await self.get_base_skill(skill_metadata.id)
            if not skill:
                continue

            # Match by domain
            if skill.domain == domain:
                matching_skills.append(skill)
                continue

            # Match by knowledge gap tags
            for gap in knowledge_gaps:
                if gap in skill.tags or gap in skill.id:
                    matching_skills.append(skill)
                    break

        return matching_skills

    async def _find_matching_ephemeral_skills(
        self, task_id: str, knowledge_gaps: List[str]
    ) -> List[EphemeralSkill]:
        """
        Find ephemeral skills that match the task and knowledge gaps.

        Args:
            task_id: Task identifier
            knowledge_gaps: Knowledge gaps to fill

        Returns:
            List of matching ephemeral skills
        """
        matching_skills: List[EphemeralSkill] = []

        # Get all ephemeral skills
        all_skills = await self.storage.list_ephemeral_skills()

        for skill_metadata in all_skills:
            skill = await self.get_ephemeral_skill(skill_metadata.id)
            if not skill or skill.is_expired:
                continue

            # Check if skill is tagged with Any of our gaps
            for gap in knowledge_gaps:
                if gap in skill.tags or gap in skill.id:
                    matching_skills.append(skill)
                    break

        return matching_skills

    def _get_covered_gaps(
        self, skills: List[BaseSkill | EphemeralSkill], knowledge_gaps: List[str]
    ) -> List[str]:
        """
        Determine which knowledge gaps are covered by the given skills.

        Args:
            skills: List of skills to check
            knowledge_gaps: Knowledge gaps to match against

        Returns:
            List of covered gap IDs
        """
        covered = set()

        for skill in skills:
            for gap in knowledge_gaps:
                if gap in skill.tags or gap in skill.id:
                    covered.add(gap)

        return list(covered)

    async def cleanup_expired_skills(self) -> Dict[str, Any]:
        """
        Clean up expired ephemeral skills.

        Returns:
            Dictionary with cleanup statistics
        """
        deleted_count = await self.storage.cleanup_expired_ephemeral_skills()
        self._ephemeral_cache.clear()

        return {
            "ephemeral_deleted": deleted_count,
            "cleanup_time": datetime.now(timezone.utc).isoformat(),
        }

    async def get_storage_stats(self) -> Dict:
        """
        Get statistics about stored skills.

        Returns:
            Dictionary with storage stats
        """
        return await self.storage.get_storage_stats()

    async def search_skills(self, query: str) -> List:
        """
        Search for skills by query.

        Args:
            query: Search query

        Returns:
            List of matching skill metadata
        """
        return await self.storage.search_skills(query)

    async def list_all_skills(self) -> Dict[str, List]:
        """
        List all available skills.

        Returns:
            Dictionary with base and ephemeral skills
        """
        return {
            "base": await self.storage.list_base_skills(),
            "ephemeral": await self.storage.list_ephemeral_skills(),
        }

    async def save_base_skill(self, skill: BaseSkill) -> Path:
        """
        Save a base skill to storage.

        Args:
            skill: BaseSkill to save

        Returns:
            Path to saved skill directory
        """
        return await self.storage.save_base_skill(skill)

    async def save_ephemeral_skill(self, skill: EphemeralSkill) -> Path:
        """
        Save an ephemeral skill to storage.

        Args:
            skill: EphemeralSkill to save

        Returns:
            Path to saved skill directory
        """
        # Add to cache
        self._ephemeral_cache[skill.id] = skill
        return await self.storage.save_ephemeral_skill(skill)

    async def delete_base_skill(self, skill_id: str) -> bool:
        """
        Delete a base skill.

        Args:
            skill_id: Skill ID to delete

        Returns:
            True if deleted successfully
        """
        return await self.storage.delete_base_skill(skill_id)

    async def delete_ephemeral_skill(self, skill_id: str) -> bool:
        """
        Delete an ephemeral skill.

        Args:
            skill_id: Skill ID to delete

        Returns:
            True if deleted successfully
        """
        # Remove from cache if present
        self._ephemeral_cache.pop(skill_id, None)
        return await self.storage.delete_ephemeral_skill(skill_id)
