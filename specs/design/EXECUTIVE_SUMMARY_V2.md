# Executive Summary: Dynamic Skill System - Revised (v2.0)

> **Date**: 2025-11-01
> **Version**: 2.0 (Smart Reuse)
> **Previous Version**: 1.0 (24h Auto-Delete)
> **Status**: Approved
> **Revision Reason**: User requirement: "solo quiero que se actualicen los skills cuando sea necesario"

---

## 🎯 What Changed?

### Core Principle Revision

**BEFORE (v1.0 - TTL Model)**:
- Generate ephemeral skill
- Use for 24 hours
- Auto-delete
- Next task regenerates (wasted effort)

**AFTER (v2.0 - Smart Reuse Model)**:
- Generate ephemeral skill with metadata
- Cache indefinitely
- Check staleness (context-based, not time-based)
- Reuse if dependencies unchanged
- Regenerate only on breaking changes
- Archive after 6 months (preserve history)
- Never delete

### Why This Change?

| Problem | Impact | Solution |
|---------|--------|----------|
| **Wasted Regeneration** | Skill for "Redis caching" deleted after 24h, regenerated for similar task 1 hour later | Smart reuse: if context hash unchanged, reuse immediately |
| **Unnecessary Growth** | Tens of ephemeral skills with identical content (different timestamps) | One skill reused multiple times, marked with generation_count |
| **Lost Institutional Knowledge** | Skills deleted → patterns lost → need external research again | Archive strategy: preserve 6+ months of history, never delete |
| **Time-Based Expiry** | Skill expires at 24h mark even if context unchanged | Context-based detection: only regenerate if tools/versions/gaps changed |

---

## 📊 System Architecture (v2.0)

### Overview Diagram

```
┌────────────────────────────────────────────────────────────┐
│                     WORKFLOW EXECUTION                      │
└──────────────────────┬─────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    Task Starts              "Do we need a skill?"
        │                             │
        │                        SRD Analysis
        │                             │
        │                      ┌──────┴──────┐
        │                      │             │
        │                   NO/LOW       HIGH/MEDIUM
        │                      │             │
        │              Static Context   SkillManager
        │                      │             │
        │              [Use base prompt] [Prepare Skill]
        │                      │             │
        │              ┌───────┴────────┬────┴──────┐
        │              │                │           │
        │          Search Cache    Cache Hit   Cache Miss
        │              │                │           │
        │              │        ┌────────┴────┐     │
        │              │        │   Check      │     │
        │              │     Staleness     Generate
        │              │        │              │
        │        ┌─────┴────┐   │        ┌─────┴─────┐
        │        │          │   │        │ Fresh  Stale
        │     Fresh     Stale   │        │ (new)  (regen)
        │        │          │   │        │   │       │
        │        │      Regen   │        └───┴───────┘
        │        │          │   │            │
        │        └──────┬───┘   │            │
        │               │       │            │
        │          ┌────┴───────┴────────────┘
        │          │
        └──────────┼──────────────────┐
                   │                  │
            Inject in Context    Format Skills
                   │                  │
                   └──────┬───────────┘
                          │
                 Render with POML
                          │
                     Execute Task
                          │
              ┌───────────┴────────────┐
              │                        │
         Task Results           Distill to Base
              │                   (keep learning)
              │                        │
           Return                  Archive Old
              │                   (if needed)
              │                        │
              └───────────┬────────────┘
                          │
                     Workflow Continues
```

### Two-Tier Skill System (Unchanged)

**Base Skills** (Persistent)
- Generic patterns and best practices
- Grow over time with learnings from tasks
- Updated via daily background job (check for new versions)
- Version history with update notes
- Never deleted, only accumulate

**Ephemeral Skills** (Task-Specific)
- Generated on-demand for specific tasks
- Includes context-aware code examples
- Known issues and workarounds
- Now: **Reused if context unchanged** (NEW)
- Now: **Archived after 6 months** (NEW)
- Now: **Never deleted** (NEW)

---

## 🔄 Smart Reuse Algorithm (Core Innovation)

### Context Hash: Fingerprint of Dependencies

Each ephemeral skill gets tagged with a **context hash** capturing:

```
context_hash = SHA256({
  "domain": "database",
  "tools": ["redis", "fastapi", "python"],
  "tool_versions": {
    "redis": "7.2.4",
    "redis-py": "5.0.1",
    "fastapi": "0.104.1"
  },
  "knowledge_gaps": ["redis pub/sub", "cache invalidation"]
})
```

### Staleness Check Process

```
Task: "Implement Redis caching for user profiles"
  ↓
1. Compute current context hash
   - Tools: redis, fastapi, python
   - Versions: redis 7.2.4, redis-py 5.0.1, fastapi 0.104.1
   - Gaps: redis pub/sub, caching
   - Hash: a1b2c3d4e5f6...
  ↓
2. Search cache for matching ephemeral skills
   - Found: "Redis Caching" skill (created 30 days ago)
   - Stored hash: a1b2c3d4e5f6... (SAME!)
  ↓
3. Check: Has context changed?
   - Hash match: YES
   - Breaking changes detected: NO
   - Last verified: 2 days ago (< 30 day threshold)
  ↓
4. Decision: REUSE SKILL
   - Load cached skill
   - Update last_used timestamp
   - Increment generation_count → 3
   - Inject into prompt (3rd time this skill used)
```

### When Regeneration Happens

Skill is marked **stale** and regenerated if:

1. **Context Hash Mismatch**
   - Example: redis upgraded from 7.2 → 8.0
   - Detection: New hash ≠ stored hash
   - Action: Regenerate

2. **Breaking Changes Detected**
   - Example: redis-py 4.x → 5.x API changes
   - Detection: GitHub issue search for breaking changes
   - Action: Regenerate

3. **Stale Verification** (every 30 days)
   - Example: Last verified 45 days ago
   - Detection: Check tool version updates
   - Action: Verify → if changes, regenerate

---

## 📈 Impact Metrics

### Expected Improvements (After 30-60 days)

| Metric | v1.0 (TTL) | v2.0 (Smart Reuse) | Improvement |
|--------|------------|-------------------|-------------|
| **Skill Reuse Rate** | ~5% (rare) | >70% | **14x increase** |
| **Avg Generation/Day** | 50+ new skills | 5-10 new skills | **80% reduction** |
| **Storage Efficiency** | 1 skill × 100 variants | 1 skill × N reuses | **95% storage saving** |
| **Context Freshness** | 24h fixed | Depends on context | **100% accurate** |
| **Skill Retention** | 0% (all deleted) | 100% (archived) | **Preserve history** |
| **Latency** | Gen: 2-3s | Reuse: <100ms | **30x faster** |

### Dashboard Success Criteria

After 60 days:

```
✅ Skill Reuse Rate         > 70%     (ratio of reuse to new generation)
✅ Avg Staleness Check      < 1s      (performance of context detection)
✅ Archive Rate             < 20%     (not over-archiving)
✅ Restoration Rate         < 5%      (low need to recover archived skills)
✅ Generation Reduction     > 80%     (vs v1.0 baseline)
```

---

## 🔐 Archival Strategy (6-Month Rule)

### Inactive Skill Detection

```
Ephemeral Skill Lifecycle:

Day 0:   created_at = 2025-05-01
Day 10:  last_used = 2025-05-10 (reused once)
Day 180: last_used still 2025-05-10 (inactive 180+ days)
         Background job detects: (today - last_used).days > 180
         Status: active → archived
         File: .copilot/skills/ephemeral/skill.md
            → .copilot/skills/archived/skill_id/skill.md
         Metadata: archived_at = 2025-11-01
```

### Why 6 Months?

- **Too short (24h)**: Waste regeneration effort (v1.0 problem)
- **Too long (12+ months)**: Skills accumulate indefinitely
- **Just right (6 months)**: Preserve learning, manage storage
- **Key**: Skills NEVER deleted, always in archive if not active

### Recovery (If Needed)

If analyst needs to review or reuse archived skill:

```python
# API call
cde_restoreArchivedSkill(skill_id="redis-cache-a1b2c3d4")

# Result: Skill moved back to active, ready for reuse
# Metadata: archived_at cleared, status = active
# Use: Same as any other ephemeral skill
```

---

## 🎯 Implementation Roadmap (8 weeks)

### Phase 1: Smart Reuse Logic (Weeks 1-2)

**Deliverable**: Core staleness detection working

- [ ] Implement `compute_context_hash()` function
- [ ] Implement `is_skill_stale()` method with comparison logic
- [ ] Implement `prepare_ephemeral_skill()` (smart reuse orchestrator)
- [ ] Write unit tests for all 3 functions
- [ ] Validation: Can reuse skill if context unchanged

**Success Criterion**: Reuse rate > 50% in manual test

### Phase 2: Metadata Updates (Weeks 2-3)

**Deliverable**: Full lifecycle tracking in metadata

- [ ] Update `EphemeralSkill` model (remove `expires`, add `context_hash`)
- [ ] Add `SkillMetadata` fields: `last_used`, `generation_count`, `status`, `update_checks`
- [ ] Persist metadata to JSON on disk
- [ ] Load metadata on startup
- [ ] Tests: Full lifecycle from creation to reuse to archival

**Success Criterion**: Metadata correctly tracked across multiple reuses

### Phase 3: Background Jobs (Weeks 3-4)

**Deliverable**: Automated archival and base skill updates

- [ ] Implement `SkillArchivalManager` class
- [ ] Implement daily archival job (find inactive skills)
- [ ] Implement skill restoration API (`cde_restoreArchivedSkill`)
- [ ] Implement base skill daily update check
- [ ] Scheduler integration (APScheduler)
- [ ] Tests: Archival happens on schedule, restoration works

**Success Criterion**: Jobs run daily, archive skills correctly

### Phase 4: Monitoring & Integration (Weeks 4-5+)

**Deliverable**: Observability and production readiness

- [ ] Add Prometheus metrics (reuse rate, staleness checks, archive count)
- [ ] Integration tests with `cde_startFeature`
- [ ] Performance benchmarks (reuse latency < 100ms)
- [ ] Error handling and recovery
- [ ] Documentation and operational runbooks

**Success Criterion**: All metrics in dashboard, reuse rate > 70%

---

## 🔄 Component Dependencies

### Architecture

```
┌────────────────────┐
│  cde_startFeature  │  (MCP Tool Entry Point)
└────────┬───────────┘
         │
    ┌────▼─────────────┐
    │SkillRequirement  │ (Detect if skill needed)
    │  Detector        │
    └────┬─────────────┘
         │
    ┌────▼──────────────┐
    │ SkillManager      │ (Orchestrator with smart reuse)
    │ prepare_ephemeral │
    │ _skill()          │
    └────┬──────────────┘
         │
    ┌────┴─────────────────────────┐
    │                              │
┌───▼──────────────┐     ┌────────▼──────────┐
│ SkillStorage     │     │ SkillGenerator    │
│ (Cache/Index)    │     │ (LLM-powered)     │
└──────────────────┘     └───────────────────┘
         │
    ┌────▼──────────────┐
    │ SkillArchival     │ (Background job)
    │ Manager           │
    └──────────────────┘
```

### Data Flow (Smart Reuse Example)

```
Task: "Implement Redis caching"
  ↓
SkillRequirementDetector.analyze_task()
  → Returns: SkillRequirement(
      needs_skill=True,
      domain="database",
      knowledge_gaps=["redis","caching"],
      confidence=0.92
    )
  ↓
SkillManager.prepare_ephemeral_skill()
  1. Search cache for matching skills
  2. For each candidate:
     a. Check staleness (context_hash comparison)
     b. If fresh: return with updated metadata ✅
     c. If stale: regenerate via SkillGenerator
  3. Return EphemeralSkill (reused or new)
  ↓
Skill injected into prompt context
  ↓
Task executes with enhanced context
  ↓
Results distilled to base skill
  ↓
Metadata updated (last_used, generation_count)
  ↓
[Daily Background Job]
SkillArchivalManager.archive_inactive_skills()
  → Find skills inactive > 180 days
  → Move to archive storage
  → Update status, metadata
```

---

## ⚠️ Risk Mitigation

### Risk 1: Context Hash Collisions

**Problem**: Different tasks get same hash, wrong skill reused

**Probability**: Very low (SHA256 is cryptographically unique)

**Mitigation**:
- Include knowledge_gaps in hash
- Include domain in hash
- Verify hash manually in logs

**Test**: Hash uniqueness test in test suite

### Risk 2: Archival Too Aggressive

**Problem**: Accidentally archive actively-used skill

**Probability**: Low (6-month threshold is generous)

**Mitigation**:
- Track all skill accesses in metrics
- Send email alert if skill archived
- Easy restore API available

**Test**: Manual restore test

### Risk 3: Breaking Changes Not Detected

**Problem**: Tool version updated with breaking changes, skill still reused

**Probability**: Low (GitHub search covers most changes)

**Mitigation**:
- Manual review of version updates
- Subscribe to tool release channels
- Re-verify every 30 days minimum
- User can force regeneration

**Test**: Test breaking change detection with real GitHub data

### Risk 4: Performance Regression

**Problem**: Context hash computation too slow

**Probability**: Very low (SHA256 < 1ms)

**Mitigation**:
- Cache computed hashes
- Benchmark on startup
- Alert if compute > 100ms

**Test**: Performance test with 1000 skills

---

## 🔍 Comparison: v1.0 vs v2.0

### Feature Comparison

| Feature | v1.0 | v2.0 | Notes |
|---------|------|------|-------|
| **Smart Reuse** | ❌ | ✅ | New: context hash-based |
| **Context Hash** | ❌ | ✅ | Fingerprint of dependencies |
| **TTL Expiry** | ✅ (24h) | ❌ | Replaced with staleness checks |
| **Archival** | ❌ | ✅ | 6-month inactive → archive |
| **Skill Deletion** | ✅ (24h) | ❌ | Never delete, always archive |
| **Reuse Rate** | ~5% | >70% | 14x improvement |
| **Storage** | Growing | Stable | Archive old skills |
| **Latency (Reuse)** | N/A | <100ms | Cache lookup only |
| **Latency (Gen)** | 2-3s | 2-3s | Unchanged |

### Migration Path (v1.0 → v2.0)

1. **Day 0**: Deploy v2.0 code
2. **Day 0-1**: Migrate existing ephemeral skills
   - Add context_hash to old skills (compute from metadata)
   - Set status = "active"
   - Set last_used = modified_time
3. **Day 1+**: System runs with smart reuse
4. **Day 180+**: First batch of old skills eligible for archival
5. **Day 365+**: Full year of archive history built up

---

## 📚 Documentation Updates

### For Developers

1. **specs/design/EPHEMERAL_SMART_REUSE.md** - Complete smart reuse strategy
2. **specs/design/SMART_REUSE_INTEGRATION.md** - Integration with SkillManager
3. **src/cde_orchestrator/skills/models.py** - Updated Pydantic models

### For Operations

1. Archival job monitoring dashboard
2. Restoration procedure runbook
3. Metrics alerting rules

### For Users

1. "Skills are cached, not deleted" messaging
2. How to interpret skill reuse metrics
3. How to request manual skill restoration

---

## ✅ Approval Checklist

- [x] Design approved by stakeholders
- [x] Gemini CLI research validated approach (2025-11-01)
- [x] Core metrics defined
- [x] Risk mitigation planned
- [x] Test strategy complete
- [x] Migration path defined
- [ ] Code review complete (pending Phase 1)
- [ ] Performance baseline established (pending)
- [ ] Production deployment (pending Phase 4)

---

## 📞 Contact & Questions

**Question**: Why not delete after archival?

**Answer**: Preserve institutional knowledge. Patterns learned from old tasks inform future skills. Archived skills can be restored if context becomes relevant again.

**Question**: Why 6 months?

**Answer**: Balance between preservation and management. 6 months is approximately 180+ ephemeral skills if generating 1/day. Annual archival would grow unbounded.

**Question**: What if context hash collides?

**Answer**: Extremely unlikely with SHA256. Plus, we verify by human inspection in logs. And we can manually force regeneration.

---

**Status**: ✅ Ready for Phase 1 Implementation
**Date Approved**: 2025-11-01
**Version**: 2.0 (Smart Reuse)
