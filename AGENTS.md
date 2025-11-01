# CDE Orchestrator MCP - Agent Instructions

> **Format**: AGENTS.md (OpenAI Standard)
> **Target**: AI Coding Agents (Cursor, Windsurf, Aider, Bolt, etc.)
> **Last Updated**: 2025-11-01
> **Priority**: High-level guidelines & project navigation

---

## 🎯 Project Overview

**What**: MCP server implementing Context-Driven Engineering for AI-powered development
**Scale**: Manages 1000+ projects, orchestrates workflows, invokes Copilot CLI headless
**Architecture**: Hexagonal (Ports & Adapters) / Clean Architecture
**Language**: Python 3.12+, FastMCP framework

---

## 📁 Quick Navigation

### Start Here (First-time agents)
1. Read `specs/design/ARCHITECTURE.md` for system design
2. Check `specs/tasks/improvement-roadmap.md` for current work
3. Review `specs/governance/DOCUMENTATION_GOVERNANCE.md` for rules

### Core Directories
```
src/cde_orchestrator/
├── domain/          # Business logic (NO external deps)
├── application/     # Use cases (orchestration)
├── adapters/        # Infrastructure implementations
└── infrastructure/  # DI, config

specs/               # All documentation
├── features/        # Feature specifications
├── design/          # Architecture decisions
├── tasks/           # Roadmaps & planning
└── governance/      # Process rules

.cde/                # Workflow engine
├── workflow.yml     # Phase definitions
├── prompts/         # POML templates
└── recipes/         # Specialized agents
```

---

## 🏗️ Architecture Rules

### Hexagonal Architecture (CRITICAL)
- **Dependencies point INWARD**: Adapters → Application → Domain
- **Domain layer**: Pure business logic, NO infrastructure imports
- **Application layer**: Orchestrates use cases, calls ports
- **Adapters layer**: Implements ports (filesystem, APIs, CLI)

### Example: Adding New Feature
```python
# ✅ CORRECT: Domain entity with business rules
class Project:
    def start_feature(self, prompt: str) -> Feature:
        if self.status != ProjectStatus.ACTIVE:
            raise InvalidStateTransitionError()
        return Feature.create(self.id, prompt)

# ✅ CORRECT: Use case orchestrates
class StartFeatureUseCase:
    def execute(self, project_path: str, prompt: str):
        project = self.repo.get_or_create(project_path)
        feature = project.start_feature(prompt)
        self.repo.save(project)

# ❌ WRONG: Domain importing adapters
from ..adapters.filesystem import FileSystem  # NEVER IN DOMAIN!
```

---

## 🛠️ Development Workflow

### Before Any Code Changes
1. **Check existing specs**: `specs/features/*.md`
2. **Search codebase**: Use grep or semantic search
3. **Understand context**: Read related files fully (not just snippets)

### Making Changes
1. **Create/update spec**: `specs/features/your-feature.md`
2. **Follow hexagonal pattern**: Domain → Application → Adapters
3. **Write tests first**: Unit tests for domain, integration for adapters
4. **Run validation**: `pre-commit run --all-files`

### Build & Test Commands
```bash
# Setup environment
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Type checking
mypy src/

# Linting
ruff check src/
black src/ --check

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## 📝 Documentation Rules

### File Placement (MANDATORY)
- **Features**: `specs/features/` - User-facing functionality
- **Design**: `specs/design/` - Architecture & technical decisions
- **Tasks**: `specs/tasks/` - Roadmaps & planning
- **Agent outputs**: `agent-docs/` - Session reports, feedback

### Root-Level Exceptions (ONLY)
- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `AGENTS.md` - This file (agent instructions)
- `GEMINI.md` - Google AI Studio instructions

### Metadata Requirement
**ALL** `.md` files MUST include YAML frontmatter:
```yaml
---
title: "Document Title"
description: "One-sentence summary (50-150 chars)"
type: "feature|design|task|guide|governance|session|execution|feedback|research"
status: "draft|active|deprecated|archived"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Name or Agent ID"
---
```

**Exception**: `.github/copilot-instructions.md` uses GitHub-specific format.

---

## 🧪 Testing Strategy

### Test Organization
```
tests/
├── unit/                # Fast, isolated tests (domain logic)
├── integration/         # With I/O (adapters, repositories)
└── __init__.py
```

### Test Patterns
```python
# Unit test (domain)
def test_project_start_feature_when_active():
    project = Project.create("Test", "/tmp/test")
    project.activate()

    feature = project.start_feature("Add login")

    assert feature.status == FeatureStatus.DEFINING

# Integration test (adapter)
def test_filesystem_repository_save_and_load():
    repo = FileSystemProjectRepository()
    project = Project.create("Test", "/tmp/test")

    repo.save(project)
    loaded = repo.get_or_create("/tmp/test")

    assert loaded.name == project.name
```

---

## 🚀 MCP Tool Contracts

### Core Tools
- `cde_startFeature(user_prompt)` → Start new feature workflow
- `cde_submitWork(feature_id, phase_id, results)` → Advance phase
- `cde_getFeatureStatus(feature_id)` → Get current status
- `cde_listFeatures()` → List all features

### Multi-Project Support
All tools accept `project_path` or `project_name`:
```python
# Direct path (preferred)
cde_startFeature(
    project_path="E:\\scripts-python\\CDE",
    user_prompt="Add authentication"
)

# Or resolved name (convenience)
cde_startFeature(
    project_name="CDE",
    user_prompt="Add authentication"
)
```

State managed per-project in `.cde/state.json`.

---

## ⚠️ Common Pitfalls

### ❌ DON'T
1. Create `.md` files in root (except approved list)
2. Import adapters in domain layer
3. Put business logic in use cases (belongs in domain)
4. Skip metadata in new documentation
5. Make breaking changes without updating specs

### ✅ DO
1. Follow hexagonal architecture strictly
2. Write specs before code
3. Add tests for all new functionality
4. Use semantic commit messages: `feat:`, `fix:`, `docs:`, `refactor:`
5. Link documents from indexes (`docs/INDEX.md`)

---

## 🎓 Key Concepts

### Context-Driven Engineering (CDE)
Development as **state transitions** through phases:
- `define` → Write specification
- `decompose` → Break into tasks
- `design` → Technical design
- `implement` → Write code
- `test` → Create tests
- `review` → QA validation

### Dynamic Skill Management System (DSMS)
Self-improving knowledge layer with smart reuse:
- **Base skills**: `.copilot/skills/base/` - Persistent knowledge
- **Ephemeral skills**: `.copilot/skills/ephemeral/` - Task-specific, reusable
- **Smart reuse**: Regenerate only on breaking changes

See: `specs/design/dynamic-skill-system.md` (44 pages)

---

## 🔍 Finding Information

### Semantic Search
Use grep or semantic search for:
- Function/class implementations
- Similar patterns
- Configuration examples

### Key Documents
- **Architecture**: `specs/design/ARCHITECTURE.md` (1400 lines)
- **Roadmap**: `specs/tasks/improvement-roadmap.md` (63 tasks)
- **Governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **DSMS Design**: `specs/design/dynamic-skill-system.md`

---

## 📊 Current Status (Phase 2)

### ✅ Completed (Phase 1)
- Core validation with Pydantic
- Error handling (circuit breaker, retry logic)
- State backups and migration
- Hexagonal architecture foundation
- Documentation governance

### 🔄 In Progress (Phase 2)
- Use cases implementation
- Copilot CLI adapter
- Multi-project auto-discovery
- Unit test coverage (target: 80%)

### 📋 Next (Phase 3+)
See `specs/tasks/improvement-roadmap.md` for detailed breakdown.

---

## 🆘 When Stuck

1. **Check specs**: `specs/features/` or `specs/design/`
2. **Search code**: `grep -r "pattern" src/`
3. **Read architecture**: `specs/design/ARCHITECTURE.md`
4. **Review roadmap**: `specs/tasks/improvement-roadmap.md`
5. **Check governance**: If documentation-related

---

## 📞 Quick Commands Reference

```bash
# Activate environment
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run tests
pytest tests/ -v --cov=src

# Check types
mypy src/

# Format code
black src/ tests/
ruff check src/ --fix

# Validate docs
python scripts/validation/validate-metadata.py --all

# Add metadata to docs
python scripts/metadata/add-metadata.py --path docs/my-doc.md

# Pre-commit validation
pre-commit run --all-files
```

---

## 🎯 Success Criteria

Before submitting work:
- ✅ All tests pass (`pytest tests/`)
- ✅ Type checking passes (`mypy src/`)
- ✅ Linting passes (`ruff check`, `black --check`)
- ✅ Documentation updated (specs + metadata)
- ✅ Pre-commit hooks pass
- ✅ No domain layer importing adapters

---

**For detailed GitHub Copilot instructions**: See `.github/copilot-instructions.md`
**For Google AI Studio (Gemini) instructions**: See `GEMINI.md`
