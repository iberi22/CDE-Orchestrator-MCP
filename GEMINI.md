---
title: GitHub Copilot Instructions for CDE Orchestrator MCP
description: 'Comprehensive AI agent guidelines. See AGENTS.md for quick reference.'
---

# GitHub Copilot Instructions for CDE Orchestrator MCP

> **Target**: GitHub Copilot, AI Coding Agents
> **Updated**: 2025-11-24
> **Quick Ref**: `AGENTS.md` | **Architecture**: `specs/design/architecture/README.md`

---

## 🚨 CRITICAL GOVERNANCE (Enforced by Pre-Commit)

### 5 Core Rules

1. **NO .md in root** except: README, CHANGELOG, CONTRIBUTING, AGENTS, GEMINI
2. **Correct location**: `specs/[feature]/` for features, `agent-docs/execution/` for reports
3. **YAML frontmatter**: All .md files need title, description, type, status, dates, author
4. **Clear names**: `execution-topic-2025-11-24.md`, not `REPORT.md`
5. **Token efficiency**: Max 1500 lines, use lists/tables, link don't duplicate

📖 **Full Rules**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`

**Common Violations to Avoid**:
```
❌ PHASE3C_SUMMARY.md (root) → agent-docs/execution/execution-phase3c-summary-2025-11-24.md
❌ Missing frontmatter → Add YAML block with required fields
❌ SCREAMING_CASE.md → lowercase-with-hyphens-2025-11-24.md
```


---

## 🎯 Project Overview

**What**: MCP server for Context-Driven Engineering + AI-powered development
**How**: Hexagonal architecture, stateless multi-project, MCP-first workflow
**New**: Spec-Kit adoption (2025-11-24) - unified feature documentation

📖 **Architecture**: `specs/design/architecture/README.md`
📖 **Roadmap**: `specs/tasks/improvement-roadmap.md` (63 tasks)

---

## 📂 Directory Structure (Spec-Kit Standard)

```
specs/
├── [feature-name]/        # NEW: Feature-specific (Spec-Kit)
│   ├── spec.md           # PRD (user stories, requirements)
│   ├── plan.md           # Technical design
│   └── tasks.md          # Executable checklist
├── design/               # Cross-cutting architecture
├── governance/           # Process rules
├── tasks/                # Project roadmaps
└── templates/            # Reusable templates

agent-docs/               # Audit logs only (no feature docs)
├── execution/            # Execution reports
├── sessions/             # Session summaries
├── feedback/             # System feedback
└── research/             # Web research (90-day archive)

src/cde_orchestrator/
├── domain/               # Business logic (NO external deps)
├── application/          # Use cases (orchestration)
├── adapters/             # Infrastructure (filesystem, CLI, MCP)
└── infrastructure/       # DI container, config
```

**Migration Status** (2025-11-24):
- ✅ HIGH: ai-assistant-config, onboarding-system → `specs/[feature]/`
- ⏸️ MEDIUM: python-314, server-refactoring, amazon-q (pending)
- 📦 LOW: 4 archived proposals

📖 **Details**: `specs/features/README.md`

---

## 🏗️ Architecture (Hexagonal)

**Pattern**: Ports & Adapters (Clean Architecture)

```
External → MCP Server → Application (UseCases) → Domain (Entities)
                            ↓
                        Adapters (Filesystem, CLI, APIs)
```

**Critical Rule**: Dependencies point INWARD
✅ Adapters → Application → Domain
❌ Domain NEVER imports Adapters

**Key Concepts**:
- **Domain** (`entities.py`): Business rules, NO infrastructure
- **Ports** (`ports.py`): Interfaces (IProjectRepository, ICodeExecutor)
- **Use Cases** (`application/use_cases/`): Orchestration logic
- **Adapters** (`adapters/`): Implementations (filesystem, Copilot CLI, MCP)

📖 **Full Diagram**: `specs/design/architecture/README.md`

---

## 🔧 Spec-Kit Workflow (NEW)

### Automated (Recommended)

```python
# 1. Analyze & recommend workflow
cde_selectWorkflow("Add Redis caching to auth")
# → Returns: workflow_type, complexity, recipe_id, required_skills

# 2. Start feature (auto-creates specs/[feature]/)
cde_startFeature(
    user_prompt="Add Redis caching to auth",
    workflow_type="standard"
)
# Creates: specs/add-redis-caching-to-auth/{spec.md, plan.md, tasks.md}

# 3. Submit work (updates tasks.md)
cde_submitWork(
    feature_id="uuid",
    phase_id="define",
    results={"specification": "..."}
)
```

### Manual Fallback

```bash
mkdir specs/my-feature/
cp specs/templates/{spec.md,plan.md,tasks.md} specs/my-feature/
# Edit: Replace [FEATURE NAME], [DATE], [AUTHOR]
```

📖 **Templates**: `specs/templates/` | **Examples**: `specs/ai-assistant-config/`, `specs/onboarding-system/`

---

## 💻 Code Patterns

### Domain Layer (entities.py)

```python
# ✅ Rich models with behavior
class Feature:
    def advance_phase(self, next_phase: str):
        if self.status == FeatureStatus.COMPLETED:
            raise ValueError("Cannot advance completed feature")
        self.current_phase = next_phase

# ❌ Anemic models (just data)
class Feature:
    status: str
    phase: str
    # NO behavior = bad
```

### Application Layer (use_cases/)

```python
# ✅ Explicit contracts
class StartFeatureUseCase:
    """Start new feature. Input: project_id, prompt. Output: feature_id."""
    def execute(self, input_data: Dict) -> Dict:
        project = self.repo.get_by_id(input_data["project_id"])
        feature = project.start_feature(input_data["prompt"])
        return {"status": "success", "feature_id": feature.id}

# ❌ Unclear contracts
def start_feature(project, prompt):  # What returns? What throws?
    pass
```

### Adapter Layer (adapters/)

```python
# ✅ Implement port interface
class CopilotCLIAdapter(ICodeExecutor):
    async def execute_prompt(self, project_path, prompt, context):
        cmd = ["gh", "copilot", "suggest"]
        # ... implementation

# ❌ No interface
class CopilotRunner:  # What contract?
    def run(self, stuff):
        pass
```

---

## 🚨 Common Mistakes

### ❌ Domain importing infrastructure

```python
# WRONG: entities.py
from ..adapters.filesystem import FileSystem  # NO!

class Project:
    def save(self):
        FileSystem().write(self)  # Domain shouldn't know filesystem
```

### ❌ Business logic in use cases

```python
# WRONG: use_cases.py
class StartFeatureUseCase:
    def execute(self, data):
        if data["prompt"] == "":  # This is domain validation, not orchestration
            raise ValueError()
```

### ❌ Anemic models

```python
# WRONG
class Project:
    id: str
    name: str  # Just data

# RIGHT
class Project:
    id: str
    name: str

    def start_feature(self, prompt: str) -> Feature:
        if self.status != ProjectStatus.ACTIVE:
            raise ValueError("Project must be active")
        return Feature.create(self.id, prompt)
```

---

## 📋 Development Checklist

**Before Coding**:
- [ ] Check layer: Domain (no deps), Application (orchestrate), Adapter (infrastructure OK)
- [ ] Check roadmap: `specs/tasks/improvement-roadmap.md` (avoid conflicts)
- [ ] Check constitution: `memory/constitution.md` (values, standards)

**Adding Features**:
- [ ] Create `specs/[feature]/spec.md` (user stories, requirements)
- [ ] Create `specs/[feature]/plan.md` (architecture, testing)
- [ ] Create `specs/[feature]/tasks.md` (numbered tasks)
- [ ] Use `cde_startFeature()` for auto-creation

**Adding Capabilities**:
- [ ] Define interface in `domain/ports.py`
- [ ] Implement in `adapters/[name]_adapter.py`
- [ ] Wire in `infrastructure/di_container.py`

**Testing**:
- [ ] Domain → unit tests (fast, no I/O)
- [ ] Adapters → integration tests (with real I/O)
- [ ] Full flows → e2e tests (rare, expensive)

---

## 📚 Essential References

| Topic | Location | Use When |
|-------|----------|----------|
| **Quick Ref** | `AGENTS.md` | Need fast context |
| **Governance** | `specs/governance/DOCUMENTATION_GOVERNANCE.md` | Creating docs |
| **Architecture** | `specs/design/architecture/README.md` | Understanding system |
| **Roadmap** | `specs/tasks/improvement-roadmap.md` | Planning work |
| **Constitution** | `memory/constitution.md` | Making decisions |
| **Templates** | `specs/templates/` | Creating features |
| **Examples** | `specs/ai-assistant-config/`, `specs/onboarding-system/` | Reference implementations |

---

## 💡 Quick Tips

1. **Layer check**: Domain? No deps. Application? Orchestrate. Adapter? Infrastructure OK.
2. **Follow ports**: Interface in `ports.py` → Implementation in `adapters/` → Wire in `di_container.py`
3. **Test first**: Write tests before implementation for complex logic
4. **Use roadmap**: Check done/in-progress to avoid conflicts
5. **Respect constitution**: Values and standards in `memory/constitution.md`

---

**Design Philosophy**: Built FOR AI AGENTS

1. **Explicitness** > cleverness
2. **Contracts** > implementations
3. **Isolation** > shared state
4. **LLM-readability** > human terseness

📖 **For quick reference**: `AGENTS.md`
📖 **For comprehensive patterns**: This file (you're here)
