# Dynamic Skill Management System - Executive Summary

> **Status**: ✅ Design Complete - Ready for Review & Approval
> **Creation Date**: 2025-11-01
> **Estimated Implementation**: 8 weeks (4 sprints × 2 weeks)

---

## 🎯 What Was Created

Based on your request to create a robust skill management system inspired by [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills), we've designed a **self-evolving knowledge layer** that makes CDE Orchestrator continuously learn and improve.

### Documents Created

1. **`specs/design/dynamic-skill-system.md`** (44 pages)
   - Complete architecture and design philosophy
   - Dual-skill system (Base + Ephemeral)
   - Workflow diagrams and component breakdown
   - Success criteria and monitoring strategy

2. **`specs/design/dynamic-skill-system-implementation.md`** (1,380+ lines)
   - Production-ready Python code for all components
   - Complete implementation guide with tests
   - Integration hooks for existing CDE workflow
   - Deployment and monitoring setup

3. **`.github/copilot-instructions.md`** (updated)
   - Added DSMS as core pillar documentation
   - Quick reference for AI agents

---

## 💡 Core Innovation: Skill Loop

**Every task execution becomes a learning opportunity:**

```
User Task → Complexity Analysis → Skill Requirement Detection
     ↓
  ┌──────────────────────────────────────┐
  │     Does Skill Exist & Current?     │
  └──────────┬───────────────────────────┘
             │
       ┌─────┴─────┐
       NO          YES
       ↓            ↓
  Generate New   Load Existing
  Ephemeral      Base + Ephemeral
       ↓            ↓
  ┌────────────────────┐
  │  Execute Task      │
  │  with Enhanced     │
  │  Context           │
  └────────┬───────────┘
           ↓
  ┌────────────────────┐
  │ Distill Learnings  │
  │ to Base Skill      │
  └────────────────────┘
```

---

## 🏗️ Two-Tier Skill Architecture

### Base Skills (Persistent)

**Location**: `.copilot/skills/base/`

**Purpose**: Accumulative institutional knowledge

**Characteristics**:
- Generic, reusable patterns
- Updated monthly via web research
- Version history tracked
- Never deleted, only grows
- References to official docs

**Example**: `redis-caching.md`
```markdown
---
skill_type: base
domain: database
tools: [redis, python, asyncio]
version: 2.1.0
last_updated: 2025-11-01
---

# Redis Caching for Python Applications

## Core Patterns
- Cache-Aside Pattern
- Write-Through Pattern
- Connection Pooling

## Known Issues
- Memory leak in Redis < 7.2.3
- Connection pool exhaustion patterns

## 📅 Update History
### 2025-11-01 (v2.1.0)
- Redis 7.2.4 released
- New: SINTERCARD command
- Reference: https://redis.io/docs/...
```

### Ephemeral Skills (Task-Specific)

**Location**: `.copilot/skills/ephemeral/`

**Purpose**: Context-aware implementation guides

**Characteristics**:
- Generated on-demand for complex tasks
- Includes task-specific code examples
- Aware of known issues and workarounds
- Auto-deleted after 24 hours
- Learnings distilled to base skill

**Example**: Generated for "Implement Redis caching for FastAPI"
```markdown
---
skill_type: ephemeral
task_id: TASK-Redis-FastAPI-001
created: 2025-11-01T14:30:00Z
expires: 2025-11-02T14:30:00Z
---

# Redis Caching for FastAPI (Task-Specific)

## Task Context
Implement Redis caching for product catalog API
with automatic invalidation

## FastAPI-Specific Implementation
- Middleware approach
- Route decorators
- Cache invalidation on PUT/DELETE
- Prometheus metrics integration

## Known Issues (FastAPI-specific)
- Request objects not serializable
- Lifespan events for connection pool
```

---

## 🔍 Key Components

### 1. Skill Requirement Detector (SRD)

**Purpose**: Analyze tasks to determine if specialized knowledge is needed

**Heuristics**:
- **Complexity Detection**: Regex patterns for HIGH/MEDIUM/LOW
  - `"implement .+ cache"` → HIGH
  - `"refactor .+"` → MEDIUM
  - `"rename .+"` → LOW

- **Domain Detection**: Technology mentions
  - `redis|postgres|mongodb` → "database"
  - `react|fastapi|api` → "web"
  - `docker|kubernetes` → "infrastructure"

- **Knowledge Gap Identification**: Extract tools + key phrases
  - Task: "Implement Redis pub/sub for notifications"
  - Gaps: `["redis", "pub/sub", "real-time"]`

**Output**: `SkillRequirement` with confidence score

### 2. Skill Sourcer

**Purpose**: Scrape external skill repositories for templates

**Sources**:
1. `awesome-claude-skills` (1.5k ⭐) - Curated community skills
2. `anthropics/skills` - Official Anthropic skills
3. `obra/superpowers` - Battle-tested patterns

**Process**:
1. Fetch README from GitHub
2. Extract skill links matching domain keywords
3. Download SKILL.md files (raw content)
4. Parse metadata, code examples, patterns
5. Return `SkillTemplate` objects

### 3. Skill Generator

**Purpose**: Create ephemeral skills via AI + web research

**Steps**:
1. Source external templates (from Skill Sourcer)
2. Research each knowledge gap:
   - Official documentation (latest versions)
   - GitHub issues (known bugs, workarounds)
   - StackOverflow (community solutions)
3. Find known issues related to tools
4. Generate skill via LLM (Gemini CLI)
5. Save to `.copilot/skills/ephemeral/`

**LLM Prompt Structure**:
```
Generate Claude skill for: {task}
Domain: {domain}

External Templates:
{templates from awesome-claude-skills}

Research Findings:
{latest docs, issues, best practices}

Known Issues:
{GitHub issues with workarounds}

Create markdown with:
- YAML frontmatter
- Task context
- Implementation patterns
- Known issues & fixes
- References
```

### 4. Skill Updater

**Purpose**: Keep base skills current via background job

**Schedule**: Daily background task

**Process**:
1. Check all base skills for age > 30 days
2. For each tool in skill:
   - Fetch latest version from package registry
   - Scrape changelog for breaking changes
   - Search GitHub for new issues
3. Generate update note with references
4. Append to skill (preserve core content)
5. Bump version number

**Update Note Format**:
```markdown
## 📅 Update History

### 2025-11-01 (v2.1.0)
- **Redis 7.2.4 Released**
  - New: SINTERCARD command for set ops
  - Breaking: MIGRATE requires AUTH param
  - Docs: https://redis.io/docs/releases/7.2.4/

- **redis-py 5.0.1**
  - Added: Built-in health checks
  - Fixed: Memory leak in pool cleanup
  - Docs: https://redis-py.readthedocs.io/...
```

### 5. Web Researcher

**Purpose**: Multi-source research with recency bias

**Sources**:
- **Official Docs**: redis.io, fastapi.tiangolo.com, etc.
- **GitHub**: Issues, discussions, pull requests
- **StackOverflow**: Q&A with high votes

**Research Query Example**:
```python
research = await researcher.research(
    query="redis pub/sub best practices latest 2025",
    sources=["official_docs", "github", "stackoverflow"]
)

# Returns top 3 results per source:
results.docs = [
    {title: "...", url: "...", snippet: "...", date: "2025-10-15"},
    ...
]
results.issues = [...]
results.qa = [...]

# Filter by recency
results.filter_by_date(since="2024-01-01")
```

### 6. Skill Distiller

**Purpose**: Extract learnings from ephemeral → base skills

**Post-Task Process**:
1. Parse ephemeral skill content
2. Extract generic code patterns (not task-specific)
3. Find corresponding base skill by domain
4. Check if patterns already exist
5. Append new patterns to "Community Patterns" section
6. Cite source: `Distilled from task {task_id}`

---

## 🔌 Integration with CDE Workflow

### Modified `cde_startFeature`

```python
@app.tool()
async def cde_startFeature(user_prompt: str) -> str:
    # 1. Detect skill requirements (NEW!)
    skill_req = skill_detector.analyze_task(user_prompt)

    # 2. Load or generate skills (NEW!)
    skills_context = ""
    if skill_req.needs_skill:
        skills = await skill_manager.get_or_create_skills(
            domain=skill_req.domain,
            knowledge_gaps=skill_req.knowledge_gaps,
            task=user_prompt
        )
        skills_context = skill_manager.format_skills_for_prompt(skills)

    # 3. Prepare context with skills
    context = {
        "USER_PROMPT": user_prompt,
        "FEATURE_ID": feature_id,
        "SKILLS_CONTEXT": skills_context  # <-- Enhanced!
    }

    # 4. Load POML prompt with skill context
    final_prompt = prompt_manager.load_and_prepare(poml_path, context)

    # ... rest of implementation
```

### New MCP Tools

```python
# List all skills
cde_listSkills(skill_type="base")  # or "ephemeral"
→ Returns JSON with name, domain, tools, version, last_updated

# Get skill content
cde_getSkill(skill_name="redis-caching")
→ Returns full markdown content

# Force skill update check
cde_refreshSkills()
→ Runs background updater immediately
→ Returns {"updated": 3, "skipped": 5, "errors": 0}
```

---

## 📊 Success Metrics

### Quantitative Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Skill Generation Success Rate | > 90% | Generations without errors / Total |
| Average Generation Time | < 30s | P95 of `skill_generation_duration` |
| Skill Hit Rate | > 60% | Tasks using skills / Total tasks |
| Update Freshness | < 30 days | Average age of base skills |
| Research Accuracy | > 85% | Manual review of 20 skills |

### Qualitative Checks

- [ ] Skills contain copy-paste-ready code
- [ ] Update notes include valid references (no 404s)
- [ ] No redundant info between base/ephemeral
- [ ] Skills self-contained (minimal cross-refs)
- [ ] Known issues have workarounds

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal**: Core detection and sourcing capabilities

**Tasks**:
- TASK-01: Implement `SkillRequirementDetector` with heuristics
- TASK-02: Create `SkillManager` orchestrator
- TASK-03: Build `SkillSourcer` to scrape awesome-claude-skills
- TASK-04: Implement `WebResearcher` with Gemini CLI

**Deliverables**:
- `src/cde_orchestrator/skills/detector.py`
- `src/cde_orchestrator/skills/sourcer.py`
- `src/cde_orchestrator/skills/researcher.py`
- Unit tests for detection accuracy (90%+)

### Phase 2: Skill Generation (Week 3-4)

**Goal**: On-demand skill creation

**Tasks**:
- TASK-05: Implement `SkillGenerator` with LLM
- TASK-06: Create seed base skills (top 5 domains)
- TASK-07: Build ephemeral cleanup job (24h expiry)
- TASK-08: Add distillation logic

**Deliverables**:
- `src/cde_orchestrator/skills/generator.py`
- `.copilot/skills/base/` with 5 seed skills
- Background cleanup job
- Integration tests for generation

### Phase 3: Skill Updates (Week 5-6)

**Goal**: Keep skills current automatically

**Tasks**:
- TASK-09: Implement `SkillUpdater` background job
- TASK-10: Add version detection (package registries)
- TASK-11: Create update note formatter
- TASK-12: Add version history tracking

**Deliverables**:
- `src/cde_orchestrator/skills/updater.py`
- Daily background job in `server.py`
- Update note templates
- Skills with proper version history

### Phase 4: Integration (Week 7-8)

**Goal**: Seamless workflow integration

**Tasks**:
- TASK-13: Hook SRD into `cde_startFeature`
- TASK-14: Add MCP tools (`cde_listSkills`, etc.)
- TASK-15: Create skill UI (file structure)
- TASK-16: Add monitoring (Prometheus metrics)

**Deliverables**:
- Modified `cde_startFeature` with skill loading
- 3 new MCP tools
- Monitoring dashboard queries
- End-to-end integration tests

---

## ⚠️ Risks & Mitigations

### Risk 1: LLM Hallucinations

**Issue**: Generated skills may contain outdated/incorrect info

**Mitigation**:
- Always include source URLs
- Validate links (check for 404s)
- LLM reviews own output
- Human review for critical domains (security)

### Risk 2: External API Rate Limits

**Issue**: GitHub/StackOverflow/Gemini rate limits

**Mitigation**:
- Exponential backoff with retries
- Cache research results (7 days, SQLite)
- Prioritize official docs
- Rotate API keys

### Risk 3: Skill Bloat

**Issue**: Base skills grow too large (token limit)

**Mitigation**:
- Max skill size: 5000 tokens (tracked)
- Archive old update notes (90+ days)
- Split into sub-skills if needed
- Compress redundant sections

### Risk 4: Context Window Overflow

**Issue**: Base + ephemeral exceeds LLM limit

**Mitigation**:
- Load skills lazily (only when needed)
- Skill ranking (most relevant first)
- Use skill summaries (100-token version)
- Truncate ephemeral if base is critical

---

## 📋 Review Checklist

Before approving implementation, verify:

### Design Review
- [ ] Architecture aligns with hexagonal principles
- [ ] Two-tier system (base/ephemeral) is clear
- [ ] Skill loop workflow is well-defined
- [ ] External sources are reputable

### Technical Review
- [ ] All components have clear interfaces
- [ ] Code examples are production-ready
- [ ] Error handling is comprehensive
- [ ] Testing strategy is adequate

### Operational Review
- [ ] Monitoring metrics are actionable
- [ ] Background jobs won't overload system
- [ ] Skill cleanup prevents disk bloat
- [ ] API rate limits are respected

### Business Review
- [ ] Success metrics align with goals
- [ ] 8-week timeline is acceptable
- [ ] Resources (Gemini API, GitHub tokens) available
- [ ] ROI: Improved task completion vs. implementation cost

---

## 🎬 Next Steps

### Immediate Actions

1. **Review Design Documents**
   - Read `specs/design/dynamic-skill-system.md` (architecture)
   - Read `specs/design/dynamic-skill-system-implementation.md` (code)

2. **Approve Roadmap**
   - Confirm 8-week timeline
   - Allocate resources (API keys, review time)
   - Identify pilot domains (start with 3 instead of 5?)

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/dynamic-skill-system
   ```

4. **Install Dependencies**
   ```bash
   pip install aiohttp beautifulsoup4 tiktoken lxml aiofiles
   ```

5. **Begin Phase 1**
   - Start with TASK-01: `SkillRequirementDetector`
   - Use TDD: write tests first
   - Target: 90%+ detection accuracy

### Questions to Consider

- **Which domains should we prioritize?** (database, web, infrastructure, ml, security)
- **What's the acceptable skill generation time?** (< 30s? < 60s?)
- **Should we seed base skills manually or generate them?**
- **Do we have access to required APIs?** (GitHub token, Gemini API key)
- **Who will review generated skills for accuracy?** (human-in-the-loop)

---

## 💬 Summary

We've created a **self-improving AI assistant** that:

1. **Learns continuously**: Every task execution adds to institutional knowledge
2. **Stays current**: Web research keeps skills up-to-date automatically
3. **Adapts to context**: Task-specific ephemeral skills for complex work
4. **Never forgets**: Base skills accumulate learnings over time
5. **Sources externally**: Leverages awesome-claude-skills and official docs
6. **Scales infinitely**: No limit to knowledge domains

**Key Innovation**: The skill loop transforms CDE Orchestrator from a static workflow engine into an **evolving knowledge system** that gets smarter with every use.

---

**Status**: ✅ Design Complete
**Next Action**: Review & Approve Phase 1
**Owner**: [Your Name]
**Reviewers**: [Stakeholder Names]
**Target Start Date**: [After Approval]
