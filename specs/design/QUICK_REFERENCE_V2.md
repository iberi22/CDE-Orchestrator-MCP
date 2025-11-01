# Smart Reuse Strategy: Quick Reference

> **Version**: 2.0 (Revised)
> **Date**: 2025-11-01
> **Key Change**: NO auto-delete, context-based reuse instead

---

## 🔑 Core Concepts

### Context Hash: Fingerprint

```python
# Unique identifier for skill's dependencies
context_hash = SHA256({
    "domain": "database",
    "tools": ["redis", "fastapi", "python"],
    "tool_versions": {"redis": "7.2.4", "redis-py": "5.0.1", ...},
    "knowledge_gaps": ["redis pub/sub", "cache invalidation"]
})

# If context_hash unchanged → REUSE
# If context_hash changed → REGENERATE
```

### Staleness: Multi-Factor Detection

```python
is_stale = (
    context_hash_changed OR
    breaking_changes_detected OR
    last_verified > 30_days_ago
)
```

### Lifecycle: Persistent by Default

```
┌─────────────────────────────────────────────┐
│  EPHEMERAL SKILL LIFECYCLE (NO TTL)         │
├─────────────────────────────────────────────┤
│                                             │
│  Created         Used          Stale       │
│    │              │              │         │
│    ├──Reused──────┼──Check───────┤        │
│    │              │   Hash?      │         │
│    │              │   │          │         │
│    │              │   Match  Mismatch     │
│    │              │   │        │          │
│    │          Fresh  Regen     │          │
│    │          (use)   (new)    │          │
│    │              │      │     │          │
│    └──────────────┴──────┴──────┤         │
│                              │          │
│                         180 Days        │
│                         Inactive        │
│                              │          │
│                          ARCHIVE        │
│                          (preserve)     │
│                                         │
│                    (NEVER DELETE)       │
└─────────────────────────────────────────────┘
```

---

## 📌 Key Differences vs v1.0

| Aspect | v1.0 (TTL) | v2.0 (Smart) |
|--------|-----------|-------------|
| **Expiration** | 24h fixed | Context-based |
| **Reuse** | ~5% chance | >70% chance |
| **Storage** | Grows (deleted after 24h) | Stable (archived after 6mo) |
| **Latency (reuse)** | N/A | <100ms |
| **Deleted?** | Yes | No (archived) |
| **User PR phrase** | "Skills expire after 24h" | "Skills cached indefinitely" |

---

## 🔍 Decision Tree: When to Reuse vs Regenerate

```
Found existing skill?
  │
  NO → GENERATE new
  │
  YES
  │
  ├─→ Hash unchanged?
  │     │
  │     YES
  │     │
  │     └─→ Breaking changes?
  │           │
  │           NO → REUSE ✅
  │           │
  │           YES → Mark stale, REGENERATE
  │
  │
  └─→ Hash changed?
        │
        YES
        │
        └─→ Version mismatch detected
              │
              └─→ Mark stale, REGENERATE
```

---

## 📊 Metadata Schema (Key Fields)

```json
{
  "skill_id": "redis-cache-a1b2c3d4",
  "name": "Redis Caching for FastAPI",

  "lifecycle": {
    "created_at": "2025-11-01T14:30:00Z",
    "last_used": "2025-11-01T18:45:00Z",
    "last_verified": "2025-11-01T18:45:00Z",
    "archived_at": null,
    "generation_count": 3  ← Track reuses
  },

  "context": {
    "context_hash": "a1b2c3d4e5f6...",  ← Fingerprint
    "domain": "database",
    "knowledge_gaps": ["redis pub/sub", "cache invalidation"]
  },

  "dependencies": {
    "tool_versions": {
      "redis": "7.2.4",
      "redis-py": "5.0.1"
    }
  },

  "status": "active|stale|archived"  ← NEW
}
```

---

## 🎯 Implementation Phases

### Phase 1 (Weeks 1-2): Smart Reuse Logic

**Functions to implement**:
```python
compute_context_hash(domain, tools, versions, gaps) → str
is_skill_stale(skill, current_hash) → bool
prepare_ephemeral_skill(task, domain, gaps) → EphemeralSkill
```

**Success**: Reuse rate > 50% in manual testing

### Phase 2 (Weeks 2-3): Metadata Schema

**Models to update**:
```python
EphemeralSkill:
  - Remove: expires (datetime)
  + Add: context_hash, status, generation_count
  + Add: update_checks (nested dict)
```

**Success**: Metadata correctly tracked through full lifecycle

### Phase 3 (Weeks 3-4): Background Jobs

**Schedulers to implement**:
```python
SkillArchivalManager.archive_inactive_skills()  # Daily
SkillUpdater.check_base_skills()                # Weekly
```

**Success**: Archival runs on schedule, skills move correctly

### Phase 4 (Weeks 4-5+): Production Ready

**Polish**:
- Prometheus metrics
- Error handling
- Performance benchmarks
- Integration tests

**Success**: Reuse rate > 70%, all metrics green

---

## 💾 Migration from v1.0

```python
# For each existing ephemeral skill in v1.0:

old_skill = load_from_disk()

# Compute what context hash SHOULD have been
new_hash = compute_context_hash(
    domain=old_skill.domain,
    tools=old_skill.tools,
    versions=old_skill.metadata.get("tool_versions", {}),
    gaps=old_skill.metadata.get("knowledge_gaps", [])
)

# Add new fields
old_skill.metadata.context_hash = new_hash
old_skill.metadata.status = "active"
old_skill.metadata.generation_count = 0
old_skill.metadata.last_used = old_skill.metadata.created_at
old_skill.metadata.last_verified = datetime.now()

# Remove old fields
del old_skill.metadata.expires

save_to_disk(old_skill)
```

---

## 📈 Expected Metrics (After 60 days)

```
Metric                    Target      How to Measure
──────────────────────────────────────────────────────
Skill Reuse Rate          > 70%       reuses / (reuses + gens)
Staleness Check Time      < 1s        hash computation + lookup
Archive Rate              < 20%       archived / total_ephemeral
Restoration Rate          < 5%        restored / archived
Generation Reduction      > 80%       vs v1.0 baseline
Avg Skill Reuse Count     > 3.0       generation_count across active
```

---

## ⚡ Quick Commands (Future)

```bash
# List all ephemeral skills (active)
cde_listSkills type=ephemeral status=active

# List archived skills
cde_listSkills type=ephemeral status=archived

# Get skill details
cde_getSkill skill_id=redis-cache-a1b2c3d4

# Restore archived skill
cde_restoreArchivedSkill skill_id=redis-cache-a1b2c3d4

# Force regenerate
cde_refreshSkills domain=database force=true

# Check metrics
cde_getSkillMetrics time_range=7d
```

---

## 🧪 Test Patterns

### Test 1: Smart Reuse Works

```python
# Create skill 1
skill1 = prepare_ephemeral_skill(
    task="Implement Redis caching",
    domain="database",
    knowledge_gaps=["redis"]
)
# skill1.metadata.generation_count == 0

# Prepare skill 2 (same domain/gaps)
skill2 = prepare_ephemeral_skill(
    task="Add Redis to FastAPI",  # Different task!
    domain="database",
    knowledge_gaps=["redis"]
)

# Should reuse skill1
assert skill2.metadata.skill_id == skill1.metadata.skill_id
assert skill2.metadata.generation_count == 1
```

### Test 2: Staleness Detected

```python
# Create skill with redis 7.2
skill1 = prepare_ephemeral_skill(
    task="Cache products",
    domain="database",
    knowledge_gaps=["redis"]
)

# Simulate version change: redis 7.2 → 8.0
skill1.metadata.update_checks["breaking_changes_found"] = True

# Try to reuse (same domain/gaps)
skill2 = prepare_ephemeral_skill(
    task="Cache users",
    domain="database",
    knowledge_gaps=["redis"]
)

# Should regenerate (new ID)
assert skill2.metadata.skill_id != skill1.metadata.skill_id
assert skill2.metadata.previous_version_id == skill1.metadata.skill_id
```

### Test 3: Archival Works

```python
skill = create_old_skill(
    last_used=datetime.now() - timedelta(days=200)
)

await archiver.archive_inactive_skills()

# Verify moved
assert not skill.file_path.exists()
assert ".copilot/skills/archived" in str(skill.file_path)
assert skill.metadata.status == "archived"
```

---

## 🚀 Launching Phase 1

### Preparation

1. Create feature branch: `feature/dynamic-skill-system-v2`
2. Read: `specs/design/EPHEMERAL_SMART_REUSE.md`
3. Read: `specs/design/SMART_REUSE_INTEGRATION.md`
4. Setup: `src/cde_orchestrator/skills/` directory structure

### First PR (Smart Reuse Logic)

Files to implement:
```
src/cde_orchestrator/skills/
├── models.py               (DONE: updated in Phase 0)
├── reuse_engine.py         (NEW: smart reuse logic)
└── storage.py              (NEW: cache interface)

tests/skills/
├── test_reuse_engine.py    (NEW: test smart reuse)
└── test_storage.py         (NEW: test cache)
```

### Success Criteria (Phase 1)

- [x] Models updated with context_hash
- [ ] `compute_context_hash()` working
- [ ] `is_skill_stale()` working
- [ ] `prepare_ephemeral_skill()` working
- [ ] Reuse > 50% in manual test
- [ ] All unit tests passing
- [ ] No performance regression

---

## 📖 Reading Order

1. **First**: This file (Quick Reference)
2. **Second**: `EPHEMERAL_SMART_REUSE.md` (Complete strategy)
3. **Third**: `SMART_REUSE_INTEGRATION.md` (Code patterns)
4. **Fourth**: `dynamic-skill-system-implementation.md` (Full models)

---

**Status**: Ready for Phase 1
**Next Action**: Create feature branch and begin implementation
