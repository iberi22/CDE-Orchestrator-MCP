---
title: "Dynamic Skill System - Core Architecture"
description: "Core models and architecture for the Dynamic Skill Management System (DSMS)"
type: "design"
status: "active"
created: "2025-11-20"
updated: "2025-11-20"
author: "CDE Team"
llm_summary: |
  Core architecture of Dynamic Skill Management System (DSMS).
  Covers models, requirement detection, skill sourcing from external repos.
  Reference for: skill lifecycle, storage, type system, ephemeral smart-reuse.
---

# Dynamic Skill System - Core Architecture

> **Part 1 of 3**: Core Models & Architecture
> **Type**: Technical Design
> **Status**: Active
> **Reference**: Part 2: `dynamic-skill-system-implementation-guide.md`

---

## 🎯 Overview

The Dynamic Skill Management System (DSMS) is the AI knowledge layer for CDE Orchestrator. It automatically acquires, maintains, and reuses domain-specific knowledge to accelerate development tasks.

**Key Principles**:
- **Ephemeral Smart Reuse** (NO TTL): Skills persist indefinitely, reused if context unchanged
- **External Sourcing**: Downloads skills from awesome-claude-skills, anthropics/skills
- **Web Research**: Keeps skills current with latest patterns, breaking changes
- **LLM-Generated**: Creates task-specific skills via Gemini/Claude
- **Base Accumulation**: Persistent skills grow with learnings, never forgotten

---

## 📋 Core Models (`models.py`)

### SkillType Enum

```python
class SkillType(str, Enum):
    """Skill lifecycle types."""
    BASE = "base"           # Persistent, accumulative
    EPHEMERAL = "ephemeral" # Task-specific, smart-reuse (NO TTL)
```

**BASE Skills**:
- Generic, reusable knowledge
- Grow with updates over time
- Never deleted
- Examples: "redis-caching", "oauth2-implementation", "kubernetes-patterns"

**EPHEMERAL Skills**:
- Task-specific knowledge
- Smart reuse: persists if context unchanged
- Archives after 6 months no use (never deleted)
- Examples: "user-auth-redis-integration", "async-migration-fastapi"

---

### ComplexityLevel Enum

```python
class ComplexityLevel(str, Enum):
    """Task complexity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

Used by `SkillRequirementDetector` to determine if skill is needed.

---

### SkillRequirement (Output)

Result from analyzing whether task needs specialized skills:

```python
class SkillRequirement(BaseModel):
    needs_skill: bool                    # Should we source/generate skill?
    complexity: ComplexityLevel          # Task difficulty
    domain: str                          # e.g., "database", "web"
    knowledge_gaps: List[str]            # What skills to source
    suggested_sources: List[str]         # External repos to check
    confidence: float                    # 0.0-1.0
```

**Example**:
```json
{
  "needs_skill": true,
  "complexity": "high",
  "domain": "database",
  "knowledge_gaps": ["redis pub/sub", "connection pooling"],
  "suggested_sources": ["awesome-claude-skills", "redis-py docs"],
  "confidence": 0.92
}
```

---

### SkillMetadata

Extracted from skill YAML frontmatter. Tracks lifecycle and dependencies:

```python
class SkillMetadata(BaseModel):
    name: str
    skill_type: SkillType
    domain: str
    tools: List[str]
    version: str = "1.0.0"

    # Lifecycle tracking (context-based, not time-based)
    created_at: datetime
    last_used: datetime
    last_verified: datetime
    archived_at: Optional[datetime] = None
    generation_count: int = 0  # Regeneration counter

    # Context fingerprinting (smart reuse)
    context_hash: str  # Fingerprint of dependencies
    previous_version_id: Optional[str] = None

    # Dependency tracking
    update_checks: Dict[str, Any]  # Version info, breaking changes
    status: str = "active"  # active, stale, archived
    expires: Optional[datetime] = None  # For ephemeral skills
    task_id: Optional[str] = None  # Link to task
```

---

### BaseSkill

Persistent skill that grows with learnings:

```python
class BaseSkill(BaseModel):
    metadata: SkillMetadata
    content: str  # Full markdown content
    update_history: List[UpdateNote] = []
    file_path: Path
    token_count: int = 0

    def append_update_note(self, note: UpdateNote):
        """Add update without modifying core content."""
        # Appends to update history section
```

**Example Structure**:

```markdown
---
title: "Redis Caching Patterns"
skill_type: base
domain: database
tools: ["redis", "python"]
created_at: 2025-11-01T10:00:00Z
last_used: 2025-11-20T15:30:00Z
---

# Redis Caching Patterns

## Overview
[Original content...]

## 📅 Update History

### 2025-11-15 (v1.2.1)
- Redis 7.2.4 released: SINTERCARD command added
- Breaking change: MIGRATE now requires explicit AUTH
- Reference: https://redis.io/docs/releases/7.2.4/

### 2025-11-10 (v1.2.0)
- Added connection pooling patterns
- [...]
```

---

### EphemeralSkill

Task-specific skill with **smart reuse** (NO TTL):

```python
class EphemeralSkill(BaseModel):
    metadata: SkillMetadata
    content: str
    task_context: str  # Original user request
    parent_base_skill: Optional[str] = None  # Link to base
    file_path: Path
    token_count: int = 0

    async def is_stale(self, current_context_hash: str) -> bool:
        """Check if skill needs regeneration."""
        # Returns True if:
        # 1. Context hash changed (dependencies updated)
        # 2. Breaking changes detected
        # 3. 30+ days since last verification
```

**Smart Reuse Logic**:

```
IF context_hash MATCHES current context
   AND no breaking changes detected
   AND last_verified < 30 days ago
THEN
   Reuse skill (skip generation)
ELSE
   Regenerate skill (new context)
```

---

### ResearchResult & ResearchResults

Web research findings:

```python
class ResearchResult(BaseModel):
    query: str
    source: str  # "official_docs", "github", "stackoverflow"
    title: str
    url: str
    snippet: str
    date: Optional[datetime] = None
    relevance_score: float  # 0.0-1.0

class ResearchResults(BaseModel):
    docs: List[ResearchResult] = []
    issues: List[ResearchResult] = []
    discussions: List[ResearchResult] = []
    qa: List[ResearchResult] = []

    def top_k(self, k: int = 5) -> List[ResearchResult]:
        """Get top K most relevant results."""
```

---

## 🔍 Skill Requirement Detector (`detector.py`)

Analyzes tasks to determine if specialized skills needed.

### SkillRequirementDetector

```python
class SkillRequirementDetector:
    """
    Uses heuristics based on:
    - Task complexity (keywords, patterns)
    - Domain detection (technology mentions)
    - Knowledge gap identification
    """

    COMPLEXITY_PATTERNS = {
        ComplexityLevel.HIGH: [
            r"implement .+ (cache|caching|queue|database)",
            r"optimize .+ (performance|speed)",
            r"migrate .+ to .+",
            r"distribute|real-?time|pub/sub",
        ],
        ComplexityLevel.MEDIUM: [
            r"refactor .+",
            r"add .+ feature",
            r"fix .+ (bug|issue)",
        ],
        ComplexityLevel.LOW: [
            r"rename|format|update.+comment",
        ],
    }

    DOMAIN_PATTERNS = {
        "database": [r"\b(sql|redis|mongo|postgres)\b", ...],
        "web": [r"\b(react|fastapi|django|api)\b", ...],
        "infrastructure": [r"\b(docker|kubernetes|terraform)\b", ...],
        "ml": [r"\b(pytorch|tensorflow|model)\b", ...],
        "security": [r"\b(auth|oauth|encryption)\b", ...],
    }
```

### Usage

```python
detector = SkillRequirementDetector()
requirement = detector.analyze_task(
    "Add Redis pub/sub for real-time notifications"
)

# Returns:
# SkillRequirement(
#     needs_skill=True,
#     complexity=ComplexityLevel.HIGH,
#     domain="database",
#     knowledge_gaps=["redis pub/sub", "async patterns"],
#     confidence=0.92
# )
```

---

## 📚 Skill Sourcer (`sourcer.py`)

Downloads skills from external repositories.

### SkillSourcer

```python
class SkillSourcer:
    """
    Primary sources:
    - awesome-claude-skills
    - anthropics/skills
    - obra/superpowers
    """

    async def search_templates(self, domain: str) -> List[SkillTemplate]:
        """Search all sources for domain-relevant templates."""

    async def _scrape_source(self, source: dict, domain: str):
        """Scrape single repository."""

    def _extract_skill_links(self, readme: str, domain: str) -> List[str]:
        """Extract GitHub links from README."""
```

### SkillTemplate

```python
class SkillTemplate(BaseModel):
    name: str
    domain: str
    source_url: str
    code_examples: List[str]
    patterns: List[Dict[str, str]]
    known_issues: List[Dict[str, str]]
    tools: List[str]
```

### Usage

```python
sourcer = SkillSourcer()

# Search for database skills
templates = await sourcer.search_templates("database")

for template in templates[:3]:
    print(f"{template.name}: {len(template.code_examples)} examples")
```

---

## 📂 File Storage Structure

```
.copilot/skills/
├── base/                          # Persistent, generic
│   ├── redis-caching.md
│   ├── oauth2-implementation.md
│   └── kubernetes-patterns.md
│
└── ephemeral/                     # Task-specific, smart-reuse
    ├── database-user-auth-redis-integration-a1b2c3.md
    ├── async-migration-fastapi-postgres-d4e5f6.md
    └── [auto-archived after 6 months no use]
```

---

## 🔄 Skill Lifecycle

```
1. DETECT NEED
   ↓
2. SOURCE EXTERNAL
   ├─ Search awesome-claude-skills
   ├─ Download templates
   └─ Extract patterns
   ↓
3. GENERATE EPHEMERAL
   ├─ Web research on knowledge gaps
   ├─ Compile known issues
   └─ LLM generation (Gemini)
   ↓
4. REUSE (SMART)
   ├─ IF context hash matches
   │  AND no breaking changes
   │  THEN reuse existing skill
   │  ↓
   └─ ELSE regenerate
   ↓
5. ACCUMULATE TO BASE
   ├─ Successful patterns → base skill
   ├─ Append update notes
   └─ Grow knowledge base
```

---

## 🎓 Key Concepts

### Context Hash

Fingerprint of skill dependencies. If unchanged, skill can be reused:

```python
context = {
    "tool_versions": {"redis": "7.2.4", "python": "3.14"},
    "library_versions": {"redis-py": "5.0.1"},
    "source_code_hash": "abc123def456",
}

context_hash = hashlib.sha256(
    json.dumps(context, sort_keys=True).encode()
).hexdigest()
```

If `context_hash` matches previous skill's `context_hash`, reuse it.

### Breaking Changes Detection

Automatically flags skills needing regeneration:

```python
breaking_changes = {
    "redis": {
        "7.2.0": ["MIGRATE now requires AUTH"],
        "7.0.0": ["RESP3 protocol changes"],
    },
    "python": {
        "3.14": ["Removal of deprecated asyncio APIs"],
    },
}
```

### Smart Reuse (NO TTL)

Traditional approach: Delete skills after 24h/7 days/30 days (TTL)

**Our Approach**:
- Skills persist indefinitely
- Reuse if: `context_hash matches` AND `no breaking changes`
- Archive only after: 6 months without use
- Never delete (storage is cheap, re-learning is expensive)

---

## 📊 Metrics & Monitoring

Track skill lifecycle:

```python
METRICS = {
    "skills_total": 42,
    "skills_base": 18,
    "skills_ephemeral": 24,
    "skills_archived": 3,
    "reuse_rate": 0.72,  # 72% skills reused without regeneration
    "generation_time_mean": 12.5,  # seconds
    "web_research_calls": 156,
    "external_sources_queries": 89,
}
```

---

## 🔗 See Also

- **Part 2**: `dynamic-skill-system-implementation-guide.md` - Generator, Researcher, LLM integration
- **Part 3**: `dynamic-skill-system-examples.md` - Usage examples, case studies
- **Reference**: `specs/design/architecture/README.md` - Full system architecture
