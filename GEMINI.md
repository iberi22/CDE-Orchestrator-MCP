# CDE Orchestrator MCP - Gemini AI Studio Instructions

> **Format**: GEMINI.md (Google AI Studio Standard)
> **Target**: Google Gemini AI (AI Studio, Gemini CLI, IDX)
> **Last Updated**: 2025-11-01
> **Priority**: Gemini-specific optimizations & best practices

---

## 🎯 About This Project

**Name**: CDE Orchestrator MCP
**Purpose**: Model Context Protocol server for Context-Driven Engineering
**Architecture**: Hexagonal (Ports & Adapters)
**Language**: Python 3.12+, FastMCP framework
**Scale**: Manages 1000+ projects, orchestrates AI-powered development workflows

---

## 🚀 Quick Start for Gemini

### First-Time Setup
1. **Read architecture**: `specs/design/ARCHITECTURE.md` (1400 lines - comprehensive system design)
2. **Check roadmap**: `specs/tasks/improvement-roadmap.md` (63 prioritized tasks)
3. **Review governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md` (file placement rules)

### Project Structure
```
CDE Orchestrator MCP/
├── src/cde_orchestrator/       # Main source code
│   ├── domain/                 # Business logic (pure Python, NO external deps)
│   ├── application/            # Use cases (orchestration layer)
│   ├── adapters/               # Infrastructure (filesystem, APIs, CLI)
│   └── infrastructure/         # DI container, configuration
├── specs/                      # All documentation (Spec-Kit compliant)
│   ├── features/               # Feature specifications
│   ├── design/                 # Architecture & technical decisions
│   ├── tasks/                  # Roadmaps & planning
│   └── governance/             # Process & documentation rules
├── .cde/                       # Workflow engine
│   ├── workflow.yml            # Phase definitions
│   ├── prompts/                # POML templates
│   └── recipes/                # Specialized AI agent prompts
└── tests/                      # Unit & integration tests
    ├── unit/                   # Fast, isolated (domain logic)
    └── integration/            # With I/O (adapters, repositories)
```

---

## 🏗️ Architecture (Hexagonal Pattern)

### Core Principle: **Dependencies Point Inward**
```
External World → Adapters → Application → Domain (Core)
                    ↓           ↓           ↓
                   I/O      Use Cases   Business Rules
```

### Layer Responsibilities

**Domain Layer** (`src/cde_orchestrator/domain/`)
- Pure business logic
- **NO** external dependencies (no imports from adapters/infrastructure)
- Rich entities with behavior (not anemic data bags)
- Ports (interfaces) for external interactions

**Application Layer** (`src/cde_orchestrator/application/`)
- Use cases (orchestration)
- Calls domain entities and ports
- Returns structured results
- NO business rules (delegate to domain)

**Adapters Layer** (`src/cde_orchestrator/adapters/`)
- Implements ports (filesystem, Copilot CLI, APIs)
- Infrastructure details (I/O, network, databases)
- Specific technology choices

### Example: Correct Pattern
```python
# ✅ Domain entity (business rules only)
# File: src/cde_orchestrator/domain/entities.py
class Project:
    def start_feature(self, prompt: str) -> Feature:
        if self.status != ProjectStatus.ACTIVE:
            raise InvalidStateTransitionError("Project must be active")
        return Feature.create(self.id, prompt)

# ✅ Port interface (in domain, implemented in adapters)
# File: src/cde_orchestrator/domain/ports.py
class IProjectRepository(ABC):
    @abstractmethod
    def get_or_create(self, path: str) -> Project: ...

    @abstractmethod
    def save(self, project: Project) -> None: ...

# ✅ Use case (orchestration)
# File: src/cde_orchestrator/application/use_cases.py
class StartFeatureUseCase:
    def __init__(self, repo: IProjectRepository):
        self.repo = repo

    def execute(self, project_path: str, prompt: str) -> Dict:
        project = self.repo.get_or_create(project_path)
        feature = project.start_feature(prompt)
        self.repo.save(project)
        return {"status": "success", "feature_id": feature.id}

# ✅ Adapter (infrastructure implementation)
# File: src/cde_orchestrator/adapters/filesystem_repository.py
class FileSystemProjectRepository(IProjectRepository):
    def get_or_create(self, path: str) -> Project:
        state_file = Path(path) / ".cde" / "state.json"
        if state_file.exists():
            return self._load_from_file(state_file)
        return Project.create(name=Path(path).name, path=path)
```

### ❌ Anti-Patterns (AVOID)
```python
# ❌ WRONG: Domain importing adapters
# File: src/cde_orchestrator/domain/entities.py
from ..adapters.filesystem import FileSystemRepo  # NEVER!

# ❌ WRONG: Business logic in use case
class StartFeatureUseCase:
    def execute(self, data):
        if data["prompt"] == "":  # This is domain validation!
            raise ValueError()

# ❌ WRONG: Anemic domain model
class Project:
    id: str
    name: str
    # No methods = bad design
```

---

## 🧪 Testing Strategy

### Test Organization
- **Unit tests** (`tests/unit/`): Fast, no I/O, test domain logic
- **Integration tests** (`tests/integration/`): With I/O, test adapters

### Running Tests
```bash
# Activate environment
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_entities.py -v

# Run by pattern
pytest tests/ -k "test_project" -v
```

### Test Patterns
```python
# Unit test (domain logic, no I/O)
def test_project_start_feature_when_active_returns_feature():
    # Arrange
    project = Project.create("Test", "/tmp/test")
    project.activate()

    # Act
    feature = project.start_feature("Add login")

    # Assert
    assert feature.status == FeatureStatus.DEFINING
    assert len(project.features) == 1

# Integration test (with I/O)
def test_filesystem_repo_save_and_load_project():
    # Arrange
    repo = FileSystemProjectRepository()
    project = Project.create("Test", "/tmp/test")

    # Act
    repo.save(project)
    loaded = repo.get_or_create("/tmp/test")

    # Assert
    assert loaded.name == project.name
    assert loaded.id == project.id
```

---

## 📝 Documentation Rules (CRITICAL)

### File Placement
**ALL** markdown files MUST be in designated directories:

| Type | Directory | Purpose |
|------|-----------|---------|
| Feature specs | `specs/features/` | User-facing functionality |
| Design docs | `specs/design/` | Architecture & technical decisions |
| Task planning | `specs/tasks/` | Roadmaps & project tracking |
| Governance | `specs/governance/` | Process & rules |
| User guides | `docs/` | User-facing documentation |
| Agent outputs | `agent-docs/` | Session reports, feedback, research |

### Root-Level Exceptions (ONLY THESE)
- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `CODE_OF_CONDUCT.md` - Community standards
- `LICENSE` - Legal
- `AGENTS.md` - OpenAI agent instructions
- `GEMINI.md` - This file (Gemini instructions)

### Metadata Requirement (MANDATORY)
**Every** `.md` file MUST start with YAML frontmatter:
```yaml
---
title: "Document Title"
description: "One-sentence summary (50-150 characters)"
type: "feature|design|task|guide|governance|session|execution|feedback|research"
status: "draft|active|deprecated|archived"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Your Name or Agent ID"
tags:
  - "relevant"
  - "keywords"
llm_summary: |
  Brief summary optimized for LLM context (2-3 sentences).
  What is this? Why does it exist? When to use it?
---
```

**Exception**: `.github/copilot-instructions.md` uses GitHub-specific format.

**Enforcement**: Pre-commit hooks block commits without valid metadata.

---

## 🛠️ Development Workflow

### Before Making Changes
1. **Search existing specs**: `specs/features/*.md`
2. **Read architecture**: `specs/design/ARCHITECTURE.md`
3. **Check roadmap**: `specs/tasks/improvement-roadmap.md`
4. **Understand context**: Read related files fully (not just snippets)

### Making Changes (Step-by-Step)
1. **Create/update specification**:
   - Location: `specs/features/your-feature.md`
   - Include: Problem statement, proposed solution, acceptance criteria
   - Add metadata (YAML frontmatter)

2. **Implement following hexagonal pattern**:
   - Start with domain entities (business rules)
   - Define ports (interfaces)
   - Create use cases (orchestration)
   - Implement adapters (infrastructure)

3. **Write tests**:
   - Unit tests for domain logic
   - Integration tests for adapters
   - Target: 80% coverage

4. **Run validation**:
   ```bash
   # Type checking
   mypy src/

   # Linting
   ruff check src/
   black src/ --check

   # Tests
   pytest tests/ -v

   # Pre-commit hooks (validates everything)
   pre-commit run --all-files
   ```

5. **Update documentation**:
   - Add to `docs/INDEX.md` if public-facing
   - Update `CHANGELOG.md` if user-visible change
   - Link from related documents

---

## 🔧 Build & Environment Setup

### Initial Setup
```bash
# Clone repository
git clone https://github.com/iberi22/CDE-Orchestrator-MCP.git
cd CDE-Orchestrator-MCP

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Common Commands
```bash
# Run MCP server locally
python -m src.server

# Run tests
pytest tests/ -v

# Type checking
mypy src/

# Format code
black src/ tests/
ruff check src/ --fix

# Validate documentation metadata
python scripts/validation/validate-metadata.py --all

# Add metadata to new doc
python scripts/metadata/add-metadata.py --path specs/features/my-feature.md

# Check governance compliance
python scripts/validation/enforce-doc-governance.py
```

---

## 🎯 MCP Tool Contracts

### Core Tools
```python
# Start new feature
cde_startFeature(
    project_path="E:\\projects\\my-app",  # Or project_name="my-app"
    user_prompt="Add user authentication"
)
# Returns: {status, feature_id, phase, prompt}

# Submit phase work
cde_submitWork(
    feature_id="uuid",
    phase_id="define",
    results={"specification": "..."}
)
# Returns: {status, next_phase, prompt} OR {status: "completed"}

# Get feature status
cde_getFeatureStatus(feature_id="uuid")
# Returns: {feature_id, current_phase, status, progress}

# List all features
cde_listFeatures()
# Returns: [{feature_id, name, status, phase}, ...]
```

### Multi-Project Support
The system is **stateless** by design:
- Agent knows project context
- CDE validates and executes
- State managed per-project in `.cde/state.json`
- No complex registries or caching

---

## 💡 Gemini-Specific Optimizations

### Large Context Window
**Gemini 2.5 Pro**: 1M+ tokens - leverage this!
- Include full file contents when analyzing
- Provide comprehensive context in prompts
- Don't over-summarize - Gemini can handle details

### Multi-Modal Capabilities
- **Code analysis**: Feed entire files for deep analysis
- **Diagram interpretation**: Can understand architecture diagrams
- **Documentation synthesis**: Combine multiple documents for holistic view

### Function Calling
When using Gemini for code generation:
```python
# Gemini excels at structured outputs
response = gemini.generate_content(
    "Create Pydantic model for Project entity",
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": ProjectSchema
    }
)
```

### Parallel Processing (Gemini CLI)
```bash
# Background research while coding
gemini --model=gemini-2.5-flash --yolo "research Python async best practices" &

# Multiple parallel queries
gemini --model=gemini-2.5-flash --yolo "analyze codebase patterns" &
gemini --model=gemini-2.5-flash --yolo "suggest refactoring opportunities" &
```

---

## 🧠 Key Concepts

### Context-Driven Engineering (CDE)
Development as state transitions:
1. **Define**: Write specification
2. **Decompose**: Break into tasks
3. **Design**: Technical design
4. **Implement**: Write code
5. **Test**: Create tests
6. **Review**: QA validation

Each phase produces artifacts for the next phase.

### Dynamic Skill Management System (DSMS)
Self-improving knowledge layer:
- **Base skills** (`.copilot/skills/base/`): Persistent, accumulative knowledge
- **Ephemeral skills** (`.copilot/skills/ephemeral/`): Task-specific, reusable
- **Smart reuse**: Regenerate only on breaking changes

**See**: `specs/design/dynamic-skill-system.md` (44 pages, comprehensive guide)

### Hexagonal Architecture
- **Domain**: Pure business logic, no dependencies
- **Application**: Orchestrates use cases
- **Adapters**: Infrastructure implementations
- **Ports**: Interfaces connecting layers

**See**: `specs/design/ARCHITECTURE.md` (1400 lines, detailed explanation)

---

## 🔍 Finding Information

### Search Strategies
1. **Grep search**: `grep -r "pattern" src/`
2. **Semantic search**: Use IDE or tools for concept-based search
3. **File navigation**: Follow directory structure (specs → src → tests)

### Key Documents (Priority Order)
1. `specs/design/ARCHITECTURE.md` - System architecture (1400 lines)
2. `specs/tasks/improvement-roadmap.md` - Current work (63 tasks)
3. `specs/governance/DOCUMENTATION_GOVERNANCE.md` - File organization rules
4. `specs/design/dynamic-skill-system.md` - DSMS design (44 pages)
5. `README.md` - Project overview

---

## ⚠️ Common Mistakes (AVOID)

### ❌ DON'T
1. Create `.md` files in root (except approved list)
2. Import adapters in domain layer
3. Put business logic in use cases (belongs in domain)
4. Skip metadata in new documentation
5. Make anemic domain models (data bags without behavior)
6. Guess file locations - search first!

### ✅ DO
1. Follow hexagonal architecture strictly
2. Write specs before code
3. Add tests for all new functionality
4. Use semantic commit messages: `feat:`, `fix:`, `docs:`, `refactor:`
5. Link documents from indexes (`docs/INDEX.md`)
6. Run `pre-commit run --all-files` before committing

---

## 📊 Project Status (November 2025)

### ✅ Phase 1 Complete (29% overall)
- Core validation with Pydantic (FeatureState, enums)
- Error handling (circuit breaker, retry logic)
- State backups and migration
- Hexagonal architecture foundation
- Documentation governance implemented

### 🔄 Phase 2 In Progress
- Use cases implementation
- Copilot CLI adapter
- FileSystem project repository
- Multi-project auto-discovery
- Unit test coverage (target: 80%)

### 📋 Phase 3+ Planned
See `specs/tasks/improvement-roadmap.md` for detailed breakdown (63 tasks total).

---

## 🆘 When Stuck

1. **Check specs**: `specs/features/` or `specs/design/`
2. **Search codebase**: `grep -r "pattern" src/`
3. **Read architecture**: `specs/design/ARCHITECTURE.md`
4. **Review roadmap**: `specs/tasks/improvement-roadmap.md`
5. **Check governance**: If documentation-related
6. **Ask Gemini**: Use your large context window - provide full files!

---

## 🎯 Pre-Commit Checklist

Before submitting any changes:
- [ ] All tests pass (`pytest tests/`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Linting passes (`ruff check`, `black --check`)
- [ ] Documentation updated (specs + metadata)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] No domain layer importing adapters
- [ ] Semantic commit message (feat/fix/docs/refactor)
- [ ] New docs have YAML frontmatter

---

## 🔗 Related Instructions

- **GitHub Copilot**: `.github/copilot-instructions.md` (condensed, token-optimized)
- **All AI Agents**: `AGENTS.md` (OpenAI standard, comprehensive)

---

**Pro Tip for Gemini**: Your 1M+ token context window is a superpower. When analyzing code or designing solutions, request FULL file contents instead of summaries. CDE Orchestrator's architecture is designed to be fully transparent to AI agents with large contexts.
