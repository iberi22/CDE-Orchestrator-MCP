---
author: Auto-Generated
created: '2025-11-02'
description: '```python from datetime import datetime, timedelta'
llm_summary: "User guide for Smart Reuse Integration in SkillManager.\n  > **File**:\
  \ Implementation of `prepare_ephemeral_skill()` logic > **Status**: Ready for Phase\
  \ 2 > **Impact**: Replaces 24h cleanup with smart context-based reuse **Status**:\
  \ Ready for Phase 2 Implementation\n  Reference when working with guide documentation."
status: draft
tags:
- api
- database
- python
- smart_reuse_integration
- workflow
title: Smart Reuse Integration in SkillManager
type: design
updated: '2025-11-02'
---

# Smart Reuse Integration in SkillManager

> **File**: Implementation of `prepare_ephemeral_skill()` logic
> **Status**: Ready for Phase 2
> **Impact**: Replaces 24h cleanup with smart context-based reuse

---

## 📋 Manager Class Update

### Original Manager Pattern (24h Cleanup)

```python
class SkillManager:
    async def get_or_create_ephemeral_skill(
        self,
        task: str,
        domain: str
    ) -> EphemeralSkill:
        """Old approach: Always generate or check expiry."""

        existing = self.cache.find_by_domain(domain)
        if existing and not existing.is_expired():
            return existing

        # Either expired or not found - regenerate
        return await self.generator.generate(task, domain)
```

### NEW Manager Pattern (Smart Reuse)

```python
class SkillManager:
    """Manager with smart reuse logic (no TTL)."""

    def __init__(
        self,
        cache: SkillStorage,
        generator: SkillGenerator,
        detector: SkillRequirementDetector,
        archiver: SkillArchivalManager
    ):
        self.cache = cache
        self.generator = generator
        self.detector = detector
        self.archiver = archiver
        self.logger = logging.getLogger(__name__)

    async def prepare_ephemeral_skill(
        self,
        task: str,
        domain: str,
        knowledge_gaps: List[str]
    ) -> EphemeralSkill:
        """
        Prepare skill with smart reuse (core new functionality).

        Algorithm:
        1. Search for existing skills matching domain + gaps
        2. For each candidate:
           a. Check staleness (context hash + versions)
           b. If fresh: return with updated metadata
           c. If stale: regenerate and link to previous
        3. If no candidates: generate new
        """

        self.logger.info(
            f"Preparing skill for domain={domain}, gaps={knowledge_gaps}"
        )

        # Step 1: Find candidates
        candidates = self.cache.find_by_domain_and_gaps(
            domain=domain,
            knowledge_gaps=knowledge_gaps,
            status="active"  # Only active skills, not archived
        )

        self.logger.debug(f"Found {len(candidates)} candidate skills")

        if not candidates:
            self.logger.info("No existing skills found, generating new")
            return await self.generator.generate(task, domain, knowledge_gaps)

        # Step 2: Check staleness for each candidate
        for candidate in sorted(
            candidates,
            key=lambda s: s.metadata.last_used,
            reverse=True  # Most recently used first
        ):
            is_stale = await self._check_staleness(
                skill=candidate,
                current_domain=domain,
                current_gaps=knowledge_gaps
            )

            if not is_stale:
                self.logger.info(
                    f"Reusing skill {candidate.metadata.name} "
                    f"(fresh, last used: {candidate.metadata.last_used})"
                )

                # Update metadata
                candidate.metadata.last_used = datetime.now()
                candidate.metadata.last_verified = datetime.now()
                candidate.metadata.generation_count += 1

                # Persist metadata update
                await self.cache.update_metadata(candidate)

                # Metrics
                self._record_skill_reuse(domain)

                return candidate

            else:
                self.logger.info(
                    f"Skill {candidate.metadata.name} is stale, regenerating"
                )

                # Mark as stale
                candidate.metadata.status = "stale"
                candidate.metadata.last_verified = datetime.now()
                await self.cache.update_metadata(candidate)

                # Generate new version
                new_skill = await self.generator.generate(
                    task=task,
                    domain=domain,
                    knowledge_gaps=knowledge_gaps
                )

                # Link to previous
                new_skill.metadata.previous_version_id = candidate.metadata.skill_id
                new_skill.metadata.generation_count = candidate.metadata.generation_count + 1

                # Metrics
                self._record_skill_regeneration(domain)

                return new_skill

        # Step 3: No fresh candidates found
        self.logger.info("All candidates are stale, generating new skill")
        new_skill = await self.generator.generate(task, domain, knowledge_gaps)
        self._record_skill_generation(domain)
        return new_skill

    async def _check_staleness(
        self,
        skill: EphemeralSkill,
        current_domain: str,
        current_gaps: List[str]
    ) -> bool:
        """
        Determine if skill needs regeneration.

        Returns True if any of:
        - Context hash changed
        - Dependencies have breaking changes
        - Source code changed
        - Not verified for > 30 days
        """

        # Method 1: Context hash comparison
        current_hash = self._compute_context_hash(
            domain=current_domain,
            gaps=current_gaps,
            tools=skill.metadata.tools
        )

        if current_hash != skill.metadata.context_hash:
            self.logger.debug(
                f"Context hash mismatch: {current_hash} vs {skill.metadata.context_hash}"
            )
            return True

        # Method 2: Breaking changes detected
        if skill.metadata.update_checks.get("breaking_changes_found"):
            self.logger.debug(
                f"Breaking changes found in {skill.metadata.name}"
            )
            return True

        # Method 3: Stale verification (check every 30 days)
        last_verify = skill.metadata.last_verified
        days_since = (datetime.now() - last_verify).days
        if days_since > 30:
            self.logger.debug(
                f"Skill not verified for {days_since} days, checking updates"
            )

            # Check for updates in dependencies
            breaking = await self._detect_breaking_changes(skill)
            if breaking:
                skill.metadata.update_checks["breaking_changes_found"] = True
                await self.cache.update_metadata(skill)
                return True

        return False

    def _compute_context_hash(
        self,
        domain: str,
        gaps: List[str],
        tools: List[str]
    ) -> str:
        """
        Generate fingerprint of skill context.

        Hash includes:
        - Domain (what area of expertise)
        - Tools (redis, fastapi, etc.)
        - Tool versions (7.2.4, 0.104.1, etc.)
        - Knowledge gaps (specific missing knowledge)
        """
        import hashlib
        import json

        context_dict = {
            "domain": domain,
            "tools": sorted(tools),
            "gaps": sorted(gaps),
            "tool_versions": {
                tool: self._get_tool_version(tool)
                for tool in tools
            }
        }

        context_json = json.dumps(context_dict, sort_keys=True)
        return hashlib.sha256(context_json.encode()).hexdigest()

    def _get_tool_version(self, tool: str) -> str:
        """Fetch current version of tool (redis, python, etc.)."""
        # Mock implementation
        versions = {
            "redis": "7.2.4",
            "python": "3.11.0",
            "fastapi": "0.104.1",
            "redis-py": "5.0.1"
        }
        return versions.get(tool, "unknown")

    async def _detect_breaking_changes(
        self,
        skill: EphemeralSkill
    ) -> List[str]:
        """
        Check if tool versions have breaking changes.

        Returns list of tools with breaking changes detected.
        """
        breaking = []

        for tool, old_version in skill.metadata.update_checks.get(
            "tool_versions", {}
        ).items():
            new_version = self._get_tool_version(tool)

            if await self._has_breaking_changes(tool, old_version, new_version):
                breaking.append(f"{tool}: {old_version} → {new_version}")

        return breaking

    async def _has_breaking_changes(
        self,
        tool: str,
        old_version: str,
        new_version: str
    ) -> bool:
        """
        Query GitHub for breaking changes between versions.

        Mock: Check major version bump
        Real: Use GitHub API to find release notes
        """
        old_major = old_version.split(".")[0]
        new_major = new_version.split(".")[0]

        # Major version change = likely breaking
        if old_major != new_major:
            # In production: query GitHub releases
            return True

        return False

    def _record_skill_reuse(self, domain: str):
        """Update metrics for skill reuse."""
        if not hasattr(self, '_metrics'):
            self._metrics = {
                'reuse': 0,
                'generation': 0,
                'regeneration': 0,
                'by_domain': {}
            }

        self._metrics['reuse'] += 1
        if domain not in self._metrics['by_domain']:
            self._metrics['by_domain'][domain] = {'reuse': 0, 'gen': 0}
        self._metrics['by_domain'][domain]['reuse'] += 1

        self.logger.info(
            f"Metrics: {self._metrics['reuse']} reuses, "
            f"{self._metrics['generation']} generations"
        )

    def _record_skill_generation(self, domain: str):
        """Update metrics for new skill generation."""
        if not hasattr(self, '_metrics'):
            self._metrics = {'reuse': 0, 'generation': 0, 'by_domain': {}}

        self._metrics['generation'] += 1
        if domain not in self._metrics['by_domain']:
            self._metrics['by_domain'][domain] = {'reuse': 0, 'gen': 0}
        self._metrics['by_domain'][domain]['gen'] += 1

    def _record_skill_regeneration(self, domain: str):
        """Update metrics for skill regeneration (stale detected)."""
        if not hasattr(self, '_metrics'):
            self._metrics = {
                'reuse': 0,
                'generation': 0,
                'regeneration': 0,
                'by_domain': {}
            }

        self._metrics['regeneration'] += 1
        if domain not in self._metrics['by_domain']:
            self._metrics['by_domain'][domain] = {
                'reuse': 0,
                'gen': 0,
                'regen': 0
            }
        self._metrics['by_domain'][domain]['regen'] += 1
```

---

## 🏗️ Archival Manager (Background Job)

```python
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import logging


class SkillArchivalManager:
    """
    Manages archival of inactive ephemeral skills.

    Runs daily (or on-demand) to archive skills inactive > 6 months.
    Skills are NEVER deleted, only archived.
    """

    ARCHIVE_THRESHOLD_DAYS = 180  # 6 months
    ARCHIVE_BASE_PATH = Path(".copilot/skills/archived")

    def __init__(self, cache: SkillStorage):
        self.cache = cache
        self.logger = logging.getLogger(__name__)

    async def archive_inactive_skills(self):
        """
        Daily background job: Archive inactive ephemeral skills.

        Archival criteria:
        - Type = ephemeral
        - Status = active
        - last_used > 180 days ago
        """
        now = datetime.now()
        all_ephemeral = await self.cache.list_all(
            type="ephemeral",
            status="active"
        )

        to_archive = [
            skill for skill in all_ephemeral
            if (now - skill.metadata.last_used).days > self.ARCHIVE_THRESHOLD_DAYS
        ]

        self.logger.info(
            f"Found {len(to_archive)} skills to archive "
            f"(inactive > {self.ARCHIVE_THRESHOLD_DAYS} days)"
        )

        for skill in to_archive:
            await self.archive_skill(skill)

    async def archive_skill(self, skill: EphemeralSkill):
        """
        Move skill to archive storage.

        Steps:
        1. Create archive directory
        2. Move skill file
        3. Update metadata
        4. Remove from active index
        5. Add to archive index
        """
        try:
            # Step 1-2: Create and move
            archive_path = (
                self.ARCHIVE_BASE_PATH /
                skill.metadata.skill_id /
                f"{skill.metadata.name}.md"
            )
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(skill.file_path), str(archive_path))

            # Step 3: Update metadata
            skill.metadata.archived_at = datetime.now()
            skill.metadata.status = "archived"
            skill.file_path = archive_path

            # Step 4-5: Update indices
            await self.cache.remove_from_active(skill.metadata.skill_id)
            await self.cache.add_to_archive_index(skill)

            self.logger.info(
                f"Archived skill {skill.metadata.skill_id} "
                f"to {archive_path}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to archive skill {skill.metadata.skill_id}: {e}"
            )
            raise

    async def restore_archived_skill(
        self,
        skill_id: str
    ) -> Optional[EphemeralSkill]:
        """
        Restore archived skill if needed (audit/reanalysis).

        Use case:
        - Analyst needs to review old skill generation
        - Skill context becomes relevant again (new project in same domain)
        """
        archived = await self.cache.find_in_archive(skill_id)

        if not archived:
            self.logger.warning(f"Skill {skill_id} not found in archive")
            return None

        # Restore to active
        active_path = Path(".copilot/skills/ephemeral") / f"{skill_id}.md"
        shutil.copy(str(archived.file_path), str(active_path))

        # Update metadata
        archived.metadata.file_path = active_path
        archived.metadata.status = "active"
        archived.metadata.last_used = datetime.now()
        archived.metadata.archived_at = None

        # Update indices
        await self.cache.add_to_active(archived)
        await self.cache.remove_from_archive(skill_id)

        self.logger.info(f"Restored skill {skill_id} to active")

        return archived
```

---

## 🎯 Integration with cde_startFeature

### Original Pattern (Static Context)

```python
async def cde_startFeature(project_name: str, user_prompt: str) -> str:
    """Start feature (without skill enhancement)."""

    # Load workflow
    workflow = workflow_engine.load_workflow()

    # Get define phase prompt
    define_phase = workflow.get_phase("define")
    prompt = prompt_manager.render_poml(
        template=define_phase.prompt_template,
        context={"user_prompt": user_prompt}
    )

    # Execute
    return {"phase": "define", "prompt": prompt}
```

### NEW Pattern (With Smart Reuse)

```python
async def cde_startFeature(project_name: str, user_prompt: str) -> str:
    """
    Start feature WITH skill enhancement (smart reuse).

    New workflow:
    1. Detect if skill needed (complexity, domain)
    2. Prepare skill (reuse if fresh, regenerate if stale)
    3. Inject skill context into prompt
    4. Execute as normal
    """

    # Step 1: Detect skill requirement
    skill_req = skill_detector.analyze_task(user_prompt)

    if not skill_req.needs_skill:
        # No skill needed - use original pattern
        self.logger.info("No skill needed for this task")
        workflow = workflow_engine.load_workflow()
        define_phase = workflow.get_phase("define")
        prompt = prompt_manager.render_poml(
            template=define_phase.prompt_template,
            context={"user_prompt": user_prompt}
        )
        return {"phase": "define", "prompt": prompt}

    # Step 2: Prepare skill (smart reuse!)
    self.logger.info(
        f"Task requires skill: domain={skill_req.domain}, "
        f"gaps={skill_req.knowledge_gaps}"
    )

    ephemeral_skill = await skill_manager.prepare_ephemeral_skill(
        task=user_prompt,
        domain=skill_req.domain,
        knowledge_gaps=skill_req.knowledge_gaps
    )

    # Step 3: Format skill context
    skills_context = skill_manager.format_skills_for_prompt([ephemeral_skill])

    # Step 4: Load workflow and render with skill
    workflow = workflow_engine.load_workflow()
    define_phase = workflow.get_phase("define")

    # Context includes both user prompt AND skill context
    full_context = {
        "user_prompt": user_prompt,
        "skills_context": skills_context,
        "task_domain": skill_req.domain,
        "complexity": skill_req.complexity.value
    }

    prompt = prompt_manager.render_poml(
        template=define_phase.prompt_template,
        context=full_context
    )

    # Step 5: Execute with enhanced prompt
    result = {
        "phase": "define",
        "prompt": prompt,
        "skill_id": ephemeral_skill.metadata.skill_id,
        "skill_reused": ephemeral_skill.metadata.generation_count > 1
    }

    return result
```

---

## 📊 Startup & Configuration

### DI Container Setup

```python
class SkillSystemContainer:
    """Dependency injection for skill system."""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self._init_paths()

    def _init_paths(self):
        """Create skill directories if needed."""
        Path(".copilot/skills/base").mkdir(parents=True, exist_ok=True)
        Path(".copilot/skills/ephemeral").mkdir(parents=True, exist_ok=True)
        Path(".copilot/skills/archived").mkdir(parents=True, exist_ok=True)

    def get_skill_manager(self) -> SkillManager:
        """Build SkillManager with all dependencies."""
        cache = SkillStorage(base_path=self.project_path)
        detector = SkillRequirementDetector()
        generator = SkillGenerator(cache=cache)
        archiver = SkillArchivalManager(cache=cache)

        return SkillManager(
            cache=cache,
            generator=generator,
            detector=detector,
            archiver=archiver
        )

    def get_archival_job(self) -> SkillArchivalManager:
        """Build standalone archival job."""
        cache = SkillStorage(base_path=self.project_path)
        return SkillArchivalManager(cache=cache)
```

### Background Job Scheduling

```python
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SkillSystem:
    """Manages skill system lifecycle and background jobs."""

    def __init__(self, project_path: str):
        self.container = SkillSystemContainer(project_path)
        self.scheduler = AsyncIOScheduler()
        self.running = False

    async def start(self):
        """Start background jobs."""
        self.logger.info("Starting skill system background jobs")

        # Job 1: Archive inactive skills (daily at 2 AM)
        self.scheduler.add_job(
            self._archive_job,
            'cron',
            hour=2,
            minute=0,
            id='skill_archival_daily'
        )

        # Job 2: Update base skills (weekly Monday at 3 AM)
        self.scheduler.add_job(
            self._update_base_skills_job,
            'cron',
            day_of_week=0,
            hour=3,
            minute=0,
            id='base_skill_update_weekly'
        )

        self.scheduler.start()
        self.running = True

    async def _archive_job(self):
        """Background archival job."""
        try:
            archiver = self.container.get_archival_job()
            await archiver.archive_inactive_skills()
        except Exception as e:
            self.logger.error(f"Archival job failed: {e}")

    async def _update_base_skills_job(self):
        """Background base skill update job."""
        try:
            manager = self.container.get_skill_manager()
            # Update logic (see SkillUpdater in main design doc)
            self.logger.info("Base skill update job completed")
        except Exception as e:
            self.logger.error(f"Update job failed: {e}")
```

---

## ✅ Validation Tests

### Test: Smart Reuse Works

```python
@pytest.mark.asyncio
async def test_prepare_ephemeral_skill_reuses_fresh_skill():
    """
    Scenario: Existing skill is fresh (context unchanged)
    Expected: Skill reused, metadata updated
    """
    manager = SkillManager(...)

    # Create skill 1
    skill1 = await manager.prepare_ephemeral_skill(
        task="Implement Redis caching",
        domain="database",
        knowledge_gaps=["redis", "caching"]
    )
    assert skill1.metadata.generation_count == 0

    # Prepare skill 2 (same domain/gaps)
    skill2 = await manager.prepare_ephemeral_skill(
        task="Add Redis to FastAPI",  # Different task, same needs
        domain="database",
        knowledge_gaps=["redis", "caching"]
    )

    # Should reuse skill1
    assert skill2.metadata.skill_id == skill1.metadata.skill_id
    assert skill2.metadata.generation_count == 1
    assert skill2.metadata.last_used > skill1.metadata.last_used
```

### Test: Stale Detection Works

```python
@pytest.mark.asyncio
async def test_stale_detection_regenerates_on_version_change():
    """
    Scenario: Tool version changed (redis 7.2 → 8.0)
    Expected: Skill marked stale, regenerated
    """
    manager = SkillManager(...)

    # Create skill with redis 7.2
    skill1 = await manager.prepare_ephemeral_skill(
        task="Cache products",
        domain="database",
        knowledge_gaps=["redis"]
    )

    # Simulate version change
    skill1.metadata.update_checks["tool_versions"]["redis"] = "8.0.0"
    skill1.metadata.update_checks["breaking_changes_found"] = True

    # Try to reuse
    skill2 = await manager.prepare_ephemeral_skill(
        task="Cache users",  # Same needs, same domain
        domain="database",
        knowledge_gaps=["redis"]
    )

    # Should regenerate (different skill_id)
    assert skill2.metadata.skill_id != skill1.metadata.skill_id
    assert skill2.metadata.previous_version_id == skill1.metadata.skill_id
```

### Test: Archival Works

```python
@pytest.mark.asyncio
async def test_archival_manager_archives_old_skills():
    """
    Scenario: Skill unused for 200 days
    Expected: Moved to archive, status updated
    """
    archiver = SkillArchivalManager(cache)

    # Create old skill
    skill = EphemeralSkill(...)
    skill.metadata.last_used = (
        datetime.now() - timedelta(days=200)
    )
    skill.metadata.status = "active"

    # Archive
    await archiver.archive_skill(skill)

    # Verify
    assert skill.metadata.status == "archived"
    assert skill.metadata.archived_at is not None
    assert not skill.file_path.exists()  # Moved
    assert Path(".copilot/skills/archived") / skill.metadata.skill_id in skill.file_path.parents
```

---

**Status**: Ready for Phase 2 Implementation
**Next**: Create feature branch and implement SkillManager with smart reuse
