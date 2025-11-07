---
title: Ephemeral Skill Smart Reuse Strategy
description: '``` ┌─────────────────────────────────────────────────────────────┐'
type: guide
status: draft
created: '2025-11-02'
updated: '2025-11-02'
author: Auto-Generated
tags:
- api
- database
- ephemeral_smart_reuse
- performance
- python
- workflow
llm_summary: 'User guide for Ephemeral Skill Smart Reuse Strategy.

  > **Document Type**: Implementation Guide (Replaces 24h Auto-Delete) > **Version**: 2.0 > **Date**: 2025-11-01 > **Status**: Approved by Gemini CLI Research | Field | Purpose | When Updated | |-------|---------|--------------|

  Reference when working with guide documentation.'
---

# Ephemeral Skill Smart Reuse Strategy

> **Document Type**: Implementation Guide (Replaces 24h Auto-Delete)
> **Version**: 2.0
> **Date**: 2025-11-01
> **Status**: Approved by Gemini CLI Research

---

## 🎯 Core Principle: Smart Reuse vs. Dumb Regeneration

**OLD APPROACH:**
- ❌ Generate ephemeral skill
- ❌ Use for 24 hours
- ❌ Delete automatically
- ❌ Next task regenerates from scratch (wasted effort)

**NEW APPROACH:**
- ✅ Generate ephemeral skill with metadata
- ✅ Cache it indefinitely
- ✅ Check for staleness before reuse
- ✅ Regenerate ONLY if dependencies changed
- ✅ Archive after 6 months without use
- ✅ Preserve full history

---

## 📊 Ephemeral Skill Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                   EPHEMERAL SKILL WORKFLOW                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                    Task Starts
                         │
         ┌───────────────┴───────────────┐
         │                               │
      NEW TASK                      SIMILAR TASK
         │                               │
    ┌────▼────┐                  ┌──────▼──────┐
    │ Search  │                  │ Search      │
    │Existing │                  │Existing     │
    │ Skills  │                  │Skills       │
    └────┬────┘                  └──────┬──────┘
         │                              │
       NO MATCH                    SKILL FOUND
         │                              │
    ┌────▼────────────┐           ┌─────▼──────────┐
    │Generate New     │           │Compare Context │
    │Ephemeral Skill  │           │Hash + Versions │
    │- Web Research   │           │(deps changed?) │
    │- Code Examples  │           └─────┬──────────┘
    │- Known Issues   │                 │
    └────┬────────────┘         ┌───────┴────────┐
         │                      │                │
         └──────────┬───────────┘         ┌──────▼─────┐
                    │                     │            │
         ┌──────────▼──────────┐    STALE (changed)  FRESH
         │  Register Skill     │    │                 │
         │  in Cache           │    │          ┌──────▼─────┐
         │  - Set created_at   │    │          │Reuse Skill  │
         │  - Set context_hash │    │          │Update       │
         │  - Init last_used   │    │          │last_used    │
         └──────────┬──────────┘    │          │last_verified│
                    │               │          └──────┬──────┘
                    │               │                 │
                    │          ┌────▼────────┐        │
                    │          │Regenerate   │        │
                    │          │Skill        │        │
                    │          │- Mark old   │        │
                    │          │  as stale   │        │
                    │          │- Create new │        │
                    │          │  with new   │        │
                    │          │  context_   │        │
                    │          │  hash       │        │
                    │          └────┬────────┘        │
                    │               │                 │
                    └───────────────┴─────────────────┘
                                    │
                           ┌────────▼────────┐
                           │ Use Skill in    │
                           │ Workflow        │
                           │ (same for both) │
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │Task Complete    │
                           │- Distill to Base│
                           │- Update Metrics │
                           └─────────────────┘
```

---

## 🔍 Staleness Detection Algorithm

### Context Hash (Fingerprint)

Each ephemeral skill is tagged with a **context hash** that captures:

```python
context_hash = hash({
    "domain": "database",
    "tools": ["redis", "fastapi", "python"],
    "tool_versions": {
        "redis": "7.2.4",
        "redis-py": "5.0.1",
        "fastapi": "0.104.1"
    },
    "source_hash": sha256(skill_source_code),
    "knowledge_gaps": ["redis pub/sub", "cache invalidation"]
})
```

### Staleness Detection Process

When a workflow wants to reuse an ephemeral skill:

```python
async def is_skill_stale(
    existing_skill: EphemeralSkill,
    current_task: str,
    current_domain: str,
    current_tools: List[str]
) -> bool:
    """
    Determine if skill needs regeneration due to changes.
    """

    # 1. Generate current context hash
    current_hash = compute_context_hash(
        domain=current_domain,
        tools=current_tools,
        versions=await fetch_current_versions(current_tools)
    )

    # 2. Compare with stored hash
    if current_hash != existing_skill.metadata.context_hash:
        logger.info(f"Skill is stale: hash mismatch")
        return True

    # 3. Check for breaking changes
    breaking_changes = await detect_breaking_changes(
        old_versions=existing_skill.metadata.update_checks["tool_versions"],
        new_versions=await fetch_current_versions(current_tools)
    )

    if breaking_changes:
        logger.info(f"Skill is stale: breaking changes detected: {breaking_changes}")
        return True

    # 4. Check source code changes
    if source_code_hash_changed(existing_skill):
        logger.info(f"Skill is stale: source code changed")
        return True

    # 5. Skill is still fresh
    logger.info(f"Skill is fresh, reusing (last used: {existing_skill.metadata.last_used})")
    return False
```

### Breaking Change Detection

```python
async def detect_breaking_changes(
    old_versions: Dict[str, str],
    new_versions: Dict[str, str]
) -> List[str]:
    """
    Compare versions and detect breaking changes.

    Examples:
    - redis 7.2.3 → 8.0.0: MIGRATE command breaking change
    - redis-py 4.x → 5.x: async API changes
    - fastapi 0.100 → 1.0: router signature changes
    """
    breaking = []

    for tool, old_version in old_versions.items():
        new_version = new_versions.get(tool)

        if not new_version:
            continue

        # Parse versions
        old_major = parse_version(old_version)[0]
        new_major = parse_version(new_version)[0]

        # Major version bump = likely breaking
        if old_major != new_major:
            # Check GitHub releases for breaking changes
            issues = await github_searcher.find_breaking_changes(
                tool=tool,
                from_version=old_version,
                to_version=new_version
            )

            if issues:
                breaking.append(f"{tool}: {old_version} → {new_version}")

    return breaking
```

---

## 📝 Ephemeral Skill Metadata Schema

### Complete Structure

```json
{
  "skill_id": "redis-cache-a1b2c3d4",
  "name": "Redis Caching for FastAPI",
  "type": "ephemeral",
  "domain": "database",

  "lifecycle": {
    "created_at": "2025-11-01T14:30:00Z",
    "last_used": "2025-11-01T18:45:00Z",
    "last_verified": "2025-11-01T18:45:00Z",
    "archived_at": null,
    "generation_count": 1  // How many times regenerated
  },

  "context": {
    "context_hash": "a1b2c3d4e5f6g7h8i9j0",
    "domain": "database",
    "knowledge_gaps": ["redis pub/sub", "cache invalidation", "fastapi middleware"],
    "tools": ["redis", "redis-py", "fastapi", "python"],
    "parent_task": "Implement Redis caching for product catalog API"
  },

  "dependencies": {
    "tool_versions": {
      "redis": "7.2.4",
      "redis-py": "5.0.1",
      "fastapi": "0.104.1",
      "python": "3.11.0"
    },
    "library_versions": {
      "asyncio": "builtin",
      "prometheus_client": "0.18.0"
    },
    "source_code_hash": "sha256_of_skill_file"
  },

  "update_checks": {
    "last_version_check": "2025-11-01T18:45:00Z",
    "breaking_changes_found": false,
    "new_versions_available": {
      "redis-py": "5.0.2"  // Patch, not breaking
    }
  },

  "status": "active",  // active, stale, archived
  "file_path": ".copilot/skills/ephemeral/redis-cache-a1b2c3d4.md",
  "size_bytes": 8192,
  "token_count": 2048
}
```

### Key Fields Explained

| Field | Purpose | When Updated |
|-------|---------|--------------|
| `created_at` | Original creation timestamp | Once (immutable) |
| `last_used` | Last time skill was loaded | Every reuse |
| `last_verified` | Last staleness check | Every workflow start |
| `context_hash` | Fingerprint of dependencies | On generation |
| `generation_count` | How many times regenerated | On regeneration |
| `breaking_changes_found` | Did we detect breaking changes? | On verification |
| `status` | active / stale / archived | Based on rules |

---

## 🔄 Smart Reuse Workflow

### Step 1: Pre-Execution Check

```python
async def prepare_ephemeral_skill(
    task: str,
    domain: str,
    knowledge_gaps: List[str]
) -> EphemeralSkill:
    """
    Prepare skill for task execution with smart reuse logic.
    """

    # 1. Search for existing skills matching domain + gaps
    candidates = skill_cache.find_by_domain_and_gaps(domain, knowledge_gaps)

    if not candidates:
        logger.info("No existing skills found, generating new ephemeral skill")
        return await skill_generator.generate(task, domain, knowledge_gaps)

    # 2. For each candidate, check if it's stale
    for candidate in candidates:
        is_stale = await is_skill_stale(
            existing_skill=candidate,
            current_task=task,
            current_domain=domain,
            current_tools=knowledge_gaps
        )

        if not is_stale:
            # 3. Reuse this skill
            logger.info(f"Reusing skill {candidate.skill_id}")

            # Update metadata
            candidate.metadata.last_used = datetime.now()
            candidate.metadata.last_verified = datetime.now()
            candidate.metadata.generation_count += 1

            # Save metadata update
            skill_cache.update_metadata(candidate)

            # Log reuse
            metrics.skill_reuse_count.inc()
            metrics.skill_reuse_by_domain[domain].inc()

            return candidate

        else:
            logger.info(f"Skill {candidate.skill_id} is stale, regenerating")

            # Mark old as stale
            candidate.metadata.status = "stale"
            candidate.metadata.last_verified = datetime.now()
            skill_cache.update_metadata(candidate)

            # Generate new version
            new_skill = await skill_generator.generate(task, domain, knowledge_gaps)

            # Link to previous version
            new_skill.metadata.previous_version_id = candidate.skill_id

            return new_skill

    # No fresh candidates found, generate new
    logger.info("All existing skills are stale, generating new ephemeral skill")
    return await skill_generator.generate(task, domain, knowledge_gaps)
```

### Step 2: Usage

```python
# In cde_startFeature or any workflow

# 1. Detect skill requirements
skill_req = skill_detector.analyze_task(user_prompt)

# 2. Prepare skill (with smart reuse)
ephemeral_skill = await prepare_ephemeral_skill(
    task=user_prompt,
    domain=skill_req.domain,
    knowledge_gaps=skill_req.knowledge_gaps
)

# 3. Format for context (same as before, whether reused or new)
skills_context = skill_manager.format_skills_for_prompt([ephemeral_skill])

# 4. Inject into prompt
context = {
    "USER_PROMPT": user_prompt,
    "SKILLS_CONTEXT": skills_context
}

final_prompt = prompt_manager.load_and_prepare(poml_path, context)

# 5. Execute workflow (unchanged)
result = await workflow_executor.execute(final_prompt)

# 6. Post-task distillation (unchanged)
await skill_manager.distill_to_base_skill(ephemeral_skill, result)
```

---

## 📦 Archival Strategy (6-Month Inactive Rule)

### Background Job: Daily Archival Check

```python
class SkillArchivalManager:
    """Manages archival of inactive ephemeral skills."""

    ARCHIVE_THRESHOLD = 180  # days (6 months)

    async def archive_inactive_skills(self):
        """
        Daily job: Check for skills inactive for 6+ months.
        """
        now = datetime.now()
        all_ephemeral = skill_cache.list_all(type="ephemeral", status="active")

        to_archive = []

        for skill in all_ephemeral:
            days_since_use = (now - skill.metadata.last_used).days

            if days_since_use > self.ARCHIVE_THRESHOLD:
                to_archive.append(skill)

        logger.info(f"Found {len(to_archive)} skills to archive")

        for skill in to_archive:
            await self.archive_skill(skill)

    async def archive_skill(self, skill: EphemeralSkill):
        """
        Move skill to archive storage.
        """
        # Option 1: Move to .copilot/skills/archived/
        archive_path = Path(".copilot/skills/archived") / skill.skill_id / f"{skill.name}.md"
        archive_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(skill.file_path), str(archive_path))

        # Option 2: Upload to S3 (if configured)
        if self.s3_client:
            await self.s3_client.upload_file(
                file_path=archive_path,
                bucket="skill-archive",
                key=f"ephemeral/{skill.skill_id}/{skill.name}.md"
            )

        # Update metadata
        skill.metadata.archived_at = datetime.now()
        skill.metadata.status = "archived"
        skill.file_path = archive_path

        # Remove from active cache
        skill_cache.remove_from_active(skill.skill_id)

        # Add to archive index
        skill_cache.add_to_archive_index(skill)

        logger.info(f"Archived skill {skill.skill_id}")
        metrics.skills_archived.inc()
```

### Recovery: Access Archived Skills

```python
async def restore_archived_skill(skill_id: str) -> Optional[EphemeralSkill]:
    """
    Restore archived skill if needed (for audit/analysis).
    """
    archived = skill_cache.find_in_archive(skill_id)

    if not archived:
        return None

    # Restore to active
    skill_path = Path(".copilot/skills/ephemeral") / f"{skill_id}.md"
    shutil.copy(str(archived.file_path), str(skill_path))

    # Update metadata
    archived.file_path = skill_path
    archived.metadata.status = "active"
    archived.metadata.last_used = datetime.now()
    archived.metadata.archived_at = None

    # Reindex
    skill_cache.add_to_active(archived)
    skill_cache.remove_from_archive(skill_id)

    logger.info(f"Restored skill {skill_id}")

    return archived
```

---

## 📊 New Metrics for Smart Reuse

### Prometheus Metrics

```python
class SkillReuseMetrics:
    """Track smart reuse effectiveness."""

    # Reuse rate
    skill_reuse_count = Counter(
        'dsms_skill_reuse_total',
        'Total ephemeral skills reused',
        ['domain']
    )

    skill_generation_count = Counter(
        'dsms_skill_generation_total',
        'Total new ephemeral skills generated',
        ['domain']
    )

    # Staleness
    skill_stale_detected = Counter(
        'dsms_skill_stale_detected_total',
        'Times skill detected as stale',
        ['reason']  # hash_mismatch, breaking_changes, code_change
    )

    # Efficiency
    skill_reuse_rate = Gauge(
        'dsms_skill_reuse_rate',
        'Percentage of reused vs generated skills'
    )

    # Cache
    active_ephemeral_skills = Gauge(
        'dsms_ephemeral_skills_active',
        'Number of active ephemeral skills'
    )

    archived_ephemeral_skills = Gauge(
        'dsms_ephemeral_skills_archived',
        'Number of archived ephemeral skills'
    )

    # Staleness detection
    staleness_check_duration = Histogram(
        'dsms_staleness_check_duration_seconds',
        'Time to check if skill is stale'
    )

def update_reuse_metrics():
    """Calculate and update reuse rate."""
    total_reuse = skill_reuse_count._value.value
    total_generation = skill_generation_count._value.value
    total = total_reuse + total_generation

    if total > 0:
        reuse_rate = (total_reuse / total) * 100
        skill_reuse_rate.set(reuse_rate)
        logger.info(f"Skill reuse rate: {reuse_rate:.1f}%")
```

### Dashboard Queries

```promql
# Reuse rate (should be high once populated)
rate(dsms_skill_reuse_total[1d]) /
(rate(dsms_skill_reuse_total[1d]) + rate(dsms_skill_generation_total[1d]))

# Staleness reasons (help identify what changes most)
sum by (reason) (rate(dsms_skill_stale_detected_total[1d]))

# Active vs archived balance
dsms_ephemeral_skills_active / (dsms_ephemeral_skills_active + dsms_ephemeral_skills_archived)

# Average staleness check time (should be < 1s)
histogram_quantile(0.95, dsms_staleness_check_duration_seconds)
```

---

## 🧪 Implementation Checklist

### Phase 2 Modifications (from original Phase 2)

- [ ] **TASK-05b**: Modify `SkillGenerator` to NOT set expiration (remove 24h timer)
- [ ] **TASK-07b**: Replace cleanup job with `SkillArchivalManager` (6-month archival)
- [ ] **TASK-08b**: Add `prepare_ephemeral_skill()` function with staleness detection
- [ ] **TASK-08c**: Implement `is_skill_stale()` with context hash comparison
- [ ] **TASK-08d**: Add breaking change detection via GitHub issue search

### Phase 3 Modifications

- [ ] **TASK-12b**: Extend metadata schema with reuse fields (last_used, generation_count, etc.)
- [ ] **TASK-12c**: Add version linking (previous_version_id)
- [ ] **TASK-12d**: Implement archive index tracking

### Phase 4 Modifications

- [ ] **TASK-14b**: Add `cde_listArchivedSkills()` tool
- [ ] **TASK-14c**: Add `cde_restoreArchivedSkill(skill_id)` tool
- [ ] **TASK-16b**: Add reuse metrics to monitoring dashboard

---

## 🎯 Success Metrics (Updated)

| Metric | Target | Purpose |
|--------|--------|---------|
| **Skill Reuse Rate** | > 70% (after 30 days) | Shows effectiveness of smart reuse |
| **Staleness Accuracy** | > 95% | Correct detection of changes |
| **Average Check Time** | < 1s | Performance of staleness detection |
| **Archive Rate** | < 20% of generated | Not archiving too aggressively |
| **Restoration Rate** | < 5% | Low need to restore archived skills |

---

## 🔮 Future Enhancements

### Skill Versioning

Allow multiple versions of same skill to coexist:

```
redis-caching/
├── v1.0.0/
│   └── redis-caching-v1.0.0.md (redis 7.0, redis-py 4.x)
├── v2.0.0/
│   └── redis-caching-v2.0.0.md (redis 7.2, redis-py 5.x)
└── active -> v2.0.0 (symlink)
```

### Skill Diffing

Show what changed between versions:

```
redis-caching: v1.0.0 → v2.0.0

Breaking Changes:
- MIGRATE command requires AUTH parameter
- redis-py connection API changed

New Features:
- SINTERCARD command for efficient set operations
- Built-in health checks in redis-py 5.0

Code Changes:
- 3 new patterns added
- 2 patterns deprecated
- 15 lines updated

Diff: https://github.com/...
```

---

**Status**: ✅ Approved by Gemini CLI (2025-11-01)
**Next**: Update implementation code to reflect smart reuse strategy
