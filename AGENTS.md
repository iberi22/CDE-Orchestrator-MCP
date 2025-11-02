# CDE Orchestrator MCP - AI Agent Instructions# CDE Orchestrator MCP - Agent Instructions

> **Format**: AGENTS.md (OpenAI Standard)  > **Format**: AGENTS.md (OpenAI Standard)

> **Target**: AI Coding Agents (Cursor, Windsurf, Aider, Claude Desktop, Gemini, etc.)  > **Target**: AI Coding Agents (Cursor, Windsurf, Aider, Bolt, etc.)

> **Last Updated**: 2025-11-02  > **Last Updated**: 2025-11-02

> **Priority**: MCP-First Workflow Orchestration> **Priority**: High-level guidelines & MCP-first workflows

------

## 🎯 Core Philosophy: MCP-First Development## 🎯 Project Overview

**CRITICAL**: You are an AI agent working with the **CDE Orchestrator MCP server**. Instead of making direct file changes or running commands immediately, you **converse with the MCP** to:**What**: MCP server implementing Context-Driven Engineering for AI-powered development

**Scale**: Manages 1000+ projects, orchestrates workflows, invokes Copilot CLI headless

1. **Analyze user requests** → MCP selects optimal workflow + recipe + skills**Architecture**: Hexagonal (Ports & Adapters) / Clean Architecture + LLM-First Documentation

2. **Execute workflows** → MCP orchestrates phases (define → decompose → design → implement → test → review)**Language**: Python 3.14, FastMCP framework

3. **Source knowledge** → MCP downloads skills from external repos + performs web research

4. **Manage documentation** → MCP enforces Spec-Kit governance (metadata, structure, linking)**🆕 NEW**: This MCP server now acts as your **intelligent orchestrator** - you interact with it via MCP tools, and it:

1. Analyzes your requests and selects optimal workflows automatically

**Your Role**: Interpret user intent, invoke MCP tools, execute recommended workflows, report results.2. Downloads and updates skills from external repositories

3. Performs web research to keep knowledge current

**MCP's Role**: Intelligent orchestration, skill management, workflow routing, documentation governance.4. Manages documentation following Spec-Kit governance

------

## 🚀 Quick Start: Your First Request## 📁 Quick Navigation

### Example User Request### Start Here (First-time agents)

1. Read `specs/design/ARCHITECTURE.md` for system design

```plaintext2. Check `specs/tasks/improvement-roadmap.md` for current work

User: "Add Redis caching to the user authentication module"3. Review `specs/governance/DOCUMENTATION_GOVERNANCE.md` for rules

```

### Core Directories

### Your Workflow (MCP-First)```

src/cde_orchestrator/

```python├── domain/          # Business logic (NO external deps)

# Step 1: Ask MCP to analyze and route├── application/     # Use cases (orchestration)

cde_selectWorkflow(user_prompt="Add Redis caching to the user authentication module")├── adapters/        # Infrastructure implementations

└── infrastructure/  # DI, config

# MCP returns:

{specs/               # All documentation

  "workflow_type": "standard",├── features/        # Feature specifications

  "complexity": "moderate",├── design/          # Architecture decisions

  "recipe_id": "ai-engineer",├── tasks/           # Roadmaps & planning

  "estimated_duration": "1-2 hours",└── governance/      # Process rules

  "required_skills": ["redis-caching", "auth-best-practices", "python-async"],

  "phases_to_skip": [],.cde/                # Workflow engine

  "reasoning": "Moderate complexity, requires database + security knowledge",├── workflow.yml     # Phase definitions

  "confidence": 0.85├── prompts/         # POML templates

}└── recipes/         # Specialized agents

```

# Step 2: Check if skills exist, source if needed

cde_sourceSkill(skill_query="redis caching patterns", destination="ephemeral")---

# MCP downloads from awesome-claude-skills and adapts to CDE format## 🏗️ Architecture Rules

# Step 3: Start workflow with context### Hexagonal Architecture (CRITICAL)

cde_startFeature(- **Dependencies point INWARD**: Adapters → Application → Domain

    user_prompt="Add Redis caching to user auth",- **Domain layer**: Pure business logic, NO infrastructure imports

    workflow_type="standard",- **Application layer**: Orchestrates use cases, calls ports

    recipe_id="ai-engineer"- **Adapters layer**: Implements ports (filesystem, APIs, CLI)

)

### Example: Adding New Feature

# MCP enters "define" phase, returns POML prompt with:```python

# - User request# ✅ CORRECT: Domain entity with business rules

# - Required skills injectedclass Project

# - Project context    def start_feature(self, prompt: str) -> Feature

# - Spec-Kit template        if self.status != ProjectStatus.ACTIVE

            raise InvalidStateTransitionError()

# Step 4: Execute each phase, submit results        return Feature.create(self.id, prompt)

# (define → decompose → design → implement → test → review)

```# ✅ CORRECT: Use case orchestrates

class StartFeatureUseCase:

### Key Difference from Traditional Agents    def execute(self, project_path: str, prompt: str):

        project = self.repo.get_or_create(project_path)

| Traditional Approach | CDE MCP-First Approach |        feature = project.start_feature(prompt)

|----------------------|------------------------|        self.repo.save(project)

| Read files directly | Ask MCP to scan documentation |

| Create files immediately | MCP enforces Spec-Kit governance |# ❌ WRONG: Domain importing adapters

| Guess workflow phases | MCP selects optimal workflow |from ..adapters.filesystem import FileSystem  # NEVER IN DOMAIN!

| Search web manually | MCP performs research & updates skills |```

| No institutional memory | Skills accumulate, reuse, improve |

---

---

## 🛠️ Development Workflow

## 📋 MCP Tools Reference

### Before Any Code Changes

### Workflow Orchestration1. **Check existing specs**: `specs/features/*.md`

2. **Search codebase**: Use grep or semantic search

#### `cde_selectWorkflow`3. **Understand context**: Read related files fully (not just snippets)



**Purpose**: Analyze user prompt and recommend optimal workflow### Making Changes

1. **Create/update spec**: `specs/features/your-feature.md`

**Usage**:2. **Follow hexagonal pattern**: Domain → Application → Adapters

3. **Write tests first**: Unit tests for domain, integration for adapters

```python4. **Run validation**: `pre-commit run --all-files`

cde_selectWorkflow(

    user_prompt="User's request in natural language"### Build & Test Commands

)```bash

```# Setup environment

python -m venv .venv

**Returns**:.\.venv\Scripts\activate

pip install -r requirements.txt

```json

{# Run tests

  "workflow_type": "standard | quick-fix | research | documentation | refactor | hotfix",pytest tests/ -v

  "complexity": "trivial | simple | moderate | complex | epic",

  "recipe_id": "ai-engineer | documentation-writer | deep-research",# Type checking

  "estimated_duration": "< 5 minutes | 15-30 minutes | 1-2 hours | 4-8 hours | 2-5 days",mypy src/

  "required_skills": ["skill1", "skill2"],

  "phases_to_skip": ["define", "decompose"],# Linting

  "reasoning": "Explanation of recommendation",ruff check src/

  "confidence": 0.85black src/ --check

}

```# Run all pre-commit hooks

pre-commit run --all-files

**When to Use**:```



- ✅ Every new user request (before any work)---

- ✅ When task complexity is unclear

- ✅ To validate your workflow assumptions## 📝 Documentation Rules



#### `cde_startFeature`### File Placement (MANDATORY)

- **Features**: `specs/features/` - User-facing functionality

**Purpose**: Start workflow execution with selected workflow + recipe- **Design**: `specs/design/` - Architecture & technical decisions

- **Tasks**: `specs/tasks/` - Roadmaps & planning

**Usage**:- **Agent outputs**: `agent-docs/` - Session reports, feedback



```python### Root-Level Exceptions (ONLY)

cde_startFeature(- `README.md` - Project overview

    project_path=".",  # or "E:\\path\\to\\project"- `CHANGELOG.md` - Version history

    user_prompt="Feature description",- `CONTRIBUTING.md` - Contribution guidelines

    workflow_type="standard",  # From cde_selectWorkflow- `AGENTS.md` - This file (agent instructions)

    recipe_id="ai-engineer"    # From cde_selectWorkflow- `GEMINI.md` - Google AI Studio instructions

)

```### Metadata Requirement

**ALL** `.md` files MUST include YAML frontmatter:

**Returns**: POML prompt for "define" phase (or first non-skipped phase)```yaml

---

#### `cde_submitWork`title: "Document Title"

description: "One-sentence summary (50-150 chars)"

**Purpose**: Submit phase results and advance to next phasetype: "feature|design|task|guide|governance|session|execution|feedback|research"

status: "draft|active|deprecated|archived"

**Usage**:created: "YYYY-MM-DD"

updated: "YYYY-MM-DD"

```pythonauthor: "Name or Agent ID"

cde_submitWork(---

    feature_id="uuid-from-startFeature",```

    phase_id="define",

    results={**Exception**: `.github/copilot-instructions.md` uses GitHub-specific format.

        "specification": "# Feature Spec...",

        "files_created": ["specs/features/redis-caching.md"]---

    }

)## 🧪 Testing Strategy

```

### Test Organization

**Returns**: Next phase prompt OR completion confirmation```

tests/

### Skill Management├── unit/                # Fast, isolated tests (domain logic)

├── integration/         # With I/O (adapters, repositories)

#### `cde_sourceSkill`└── **init**.py

```

**Purpose**: Download skills from external repositories

### Test Patterns

**Usage**:```python

# Unit test (domain)

```pythondef test_project_start_feature_when_active():

cde_sourceSkill(    project = Project.create("Test", "/tmp/test")

    skill_query="redis caching patterns",    project.activate()

    source="awesome-claude-skills",  # Default

    destination="base"  # "base" = persistent, "ephemeral" = temporary    feature = project.start_feature("Add login")

)

```    assert feature.status == FeatureStatus.DEFINING



**Returns**:# Integration test (adapter)

def test_filesystem_repository_save_and_load():

```json    repo = FileSystemProjectRepository()

{    project = Project.create("Test", "/tmp/test")

  "skills_found": 3,

  "skills_downloaded": [    repo.save(project)

    {    loaded = repo.get_or_create("/tmp/test")

      "name": "redis-caching-patterns",

      "path": ".copilot/skills/base/redis-caching-patterns.md",    assert loaded.name == project.name

      "adaptations": ["Added CDE frontmatter", "Preserved examples"],```

      "metadata": {"source": "awesome-claude-skills", "rating": 0.9}

    }---

  ]

}## 🚀 MCP Tool Contracts

```

### Core Tools

**When to Use**:- `cde_startFeature(user_prompt)` → Start new feature workflow

- `cde_submitWork(feature_id, phase_id, results)` → Advance phase

- ✅ When `cde_selectWorkflow` recommends skills you don't have- `cde_getFeatureStatus(feature_id)` → Get current status

- ✅ Starting work in unfamiliar domain (AI, DevOps, DB, etc.)- `cde_listFeatures()` → List all features

- ✅ Want latest patterns/best practices

### Multi-Project Support

#### `cde_updateSkill`All tools accept `project_path` or `project_name`

```python

**Purpose**: Research and update skill with latest information# Direct path (preferred)

cde_startFeature(

**Usage**:    project_path="E:\\scripts-python\\CDE",

    user_prompt="Add authentication"

```python)

cde_updateSkill(

    skill_name="redis-caching",# Or resolved name (convenience)

    topics=["redis 7.x breaking changes", "redis connection pooling best practices"]cde_startFeature(

)    project_name="CDE",

```    user_prompt="Add authentication"

)

**Returns**: Update note with breaking changes, deprecations, new features, best practices```



**When to Use**:State managed per-project in `.cde/state.json`.



- ✅ Skill references old library versions---

- ✅ Before major implementation (ensure current knowledge)

- ✅ Monthly maintenance (background task)## ⚠️ Common Pitfalls



### Documentation Management### ❌ DON'T

1. Create `.md` files in root (except approved list)

#### `cde_scanDocumentation`2. Import adapters in domain layer

3. Put business logic in use cases (belongs in domain)

**Purpose**: Audit documentation structure and compliance4. Skip metadata in new documentation

5. Make breaking changes without updating specs

**Usage**:

### ✅ DO

```python1. Follow hexagonal architecture strictly

cde_scanDocumentation(project_path=".")2. Write specs before code

```3. Add tests for all new functionality

4. Use semantic commit messages: `feat:`, `fix:`, `docs:`, `refactor:`

**Returns**: Total docs, missing metadata, orphaned files, large files, recommendations5. Link documents from indexes (`docs/INDEX.md`)



**When to Use**:---



- ✅ New project onboarding## 🎓 Key Concepts

- ✅ Before major documentation work

- ✅ Periodic quality audits### Context-Driven Engineering (CDE)

Development as **state transitions** through phases:

#### `cde_analyzeDocumentation`- `define` → Write specification

- `decompose` → Break into tasks

**Purpose**: Deep quality analysis with scoring- `design` → Technical design

- `implement` → Write code

**Usage**:- `test` → Create tests

- `review` → QA validation

```python

cde_analyzeDocumentation(project_path=".")### Dynamic Skill Management System (DSMS)

```Self-improving knowledge layer with smart reuse:

- **Base skills**: `.copilot/skills/base/` - Persistent knowledge

**Returns**: Quality score (0-100), broken links, metadata analysis, issues, suggestions- **Ephemeral skills**: `.copilot/skills/ephemeral/` - Task-specific, reusable

- **Smart reuse**: Regenerate only on breaking changes

---

See: `specs/design/dynamic-skill-system.md` (44 pages)

## 🏗️ Architecture Patterns (Python 3.14)

---

### Hexagonal Architecture (CRITICAL)

## 🔍 Finding Information

**Rule**: Dependencies point INWARD: `Adapters → Application → Domain`

### Semantic Search

**Domain Layer** (`src/cde_orchestrator/domain/`)Use grep or semantic search for:

- Function/class implementations

- Pure business logic- Similar patterns

- NO external dependencies (no adapters, no infrastructure)- Configuration examples

- Rich entities with behavior

### Key Documents

```python- **Architecture**: `specs/design/ARCHITECTURE.md` (1400 lines)

# ✅ CORRECT: Domain entity with business rules- **Roadmap**: `specs/tasks/improvement-roadmap.md` (63 tasks)

class Project:- **Governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`

    def start_feature(self, prompt: str) -> Feature:- **DSMS Design**: `specs/design/dynamic-skill-system.md`

        if self.status != ProjectStatus.ACTIVE:

            raise InvalidStateTransitionError("Project must be active")---

        return Feature.create(self.id, prompt)

```## 📊 Current Status (Phase 2)



**Application Layer** (`src/cde_orchestrator/application/`)### ✅ Completed (Phase 1)

- Core validation with Pydantic

- Use cases (orchestration)- Error handling (circuit breaker, retry logic)

- Calls domain entities and ports- State backups and migration

- Returns structured results- Hexagonal architecture foundation

- Documentation governance

```python

# ✅ CORRECT: Use case orchestrates domain + adapters### 🔄 In Progress (Phase 2)

class StartFeatureUseCase:- Use cases implementation

    def execute(self, project_path: str, prompt: str):- Copilot CLI adapter

        project = self.repo.get_or_create(project_path)- Multi-project auto-discovery

        feature = project.start_feature(prompt)- Unit test coverage (target: 80%)

        self.repo.save(project)

        return {"feature_id": feature.id}### 📋 Next (Phase 3+)

```See `specs/tasks/improvement-roadmap.md` for detailed breakdown.



**Adapters Layer** (`src/cde_orchestrator/adapters/`)---



- Implements port interfaces## 🆘 When Stuck

- Infrastructure details (filesystem, APIs, CLI)

1. **Check specs**: `specs/features/` or `specs/design/`

```python2. **Search code**: `grep -r "pattern" src/`

# ✅ CORRECT: Adapter implements domain port3. **Read architecture**: `specs/design/ARCHITECTURE.md`

class FileSystemProjectRepository(IProjectRepository):4. **Review roadmap**: `specs/tasks/improvement-roadmap.md`

    def get_or_create(self, path: str) -> Project:5. **Check governance**: If documentation-related

        # File I/O here

        pass---

```

## 📞 Quick Commands Reference

**❌ WRONG Examples**:

```bash

```python# Activate environment

# ❌ Domain importing adapters.\.venv\Scripts\activate  # Windows

from ..adapters.filesystem import FileSystem  # NEVER IN DOMAIN!source .venv/bin/activate  # Linux/Mac



# ❌ Anemic domain models (just data, no behavior)# Run tests

class Project:pytest tests/ -v --cov=src

    status: str  # NO METHODS = BAD

# Check types

# ❌ Use cases with business rulesmypy src/

class StartFeatureUseCase:

    def execute(self, data):# Format code

        if data["prompt"] == "":  # This belongs in domain!black src/ tests/

            raise ValueError()ruff check src/ --fix

```

# Validate docs

### Python 3.14 Best Practicespython scripts/validation/validate-metadata.py --all

- Use `match/case` for complex conditionals# Add metadata to docs

- Use `type` keyword for type aliasespython scripts/metadata/add-metadata.py --path docs/my-doc.md

- Use `@dataclass(slots=True, frozen=True)` for value objects

- Use `async/await` for I/O-bound operations# Pre-commit validation

- Use `pathlib.Path` for file operationspre-commit run --all-files

- Use PEP 695 type parameter syntax```

```python---

# ✅ Python 3.14 patterns

from typing import TypeAlias## 🎯 Success Criteria

from dataclasses import dataclass

Before submitting work:

type ProjectID = str  # PEP 695- ✅ All tests pass (`pytest tests/`)

- ✅ Type checking passes (`mypy src/`)

@dataclass(slots=True, frozen=True)- ✅ Linting passes (`ruff check`, `black --check`)

class FeatureId:- ✅ Documentation updated (specs + metadata)

    value: str- ✅ Pre-commit hooks pass

- ✅ No domain layer importing adapters

async def execute_workflow(prompt: str) -> Result:

    match complexity:---

        case WorkflowComplexity.TRIVIAL:

            return await quick_fix(prompt)**For detailed GitHub Copilot instructions**: See `.github/copilot-instructions.md`

        case WorkflowComplexity.EPIC:**For Google AI Studio (Gemini) instructions**: See `GEMINI.md`

            return await full_workflow(prompt)
        case _:
            return await standard_workflow(prompt)
```

---

## 📁 Documentation Governance (Mandatory)

### File Placement Rules

| Document Type | Location | Example |
|---------------|----------|---------|
| Feature specs | `specs/features/` | `authentication.md` |
| Technical design | `specs/design/` | `hexagonal-architecture.md` |
| Roadmaps/tasks | `specs/tasks/` | `improvement-roadmap.md` |
| Agent outputs | `agent-docs/sessions/` | `session-implementation-2025-11.md` |
| Research notes | `agent-docs/research/` | `async-patterns-research-2025-11.md` |
| Execution reports | `agent-docs/execution/` | `workflow-execution-2025-11.md` |

### YAML Frontmatter (Required)

**Every .md file** must start with:

```yaml
---
title: "Document Title"
description: "One-sentence summary"
type: "feature|design|task|session|execution|research"
status: "draft|active|deprecated|archived"
created: "2025-11-02"
updated: "2025-11-02"
author: "Agent Name"
llm_summary: |
  2-3 sentence summary optimized for LLM context.
---
```

**Enforcement**: Pre-commit hooks block commits without metadata.

**Tool**: Use `cde_scanDocumentation` to find missing metadata.

### Root-Level Exceptions (ONLY these allowed)

- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Developer guidelines
- `AGENTS.md` - This file
- `GEMINI.md` - Gemini-specific instructions

**All other .md files** must be in `specs/` or `agent-docs/`.

---

## 🎓 Workflow Patterns

### Pattern 1: Standard Feature Development

```python
# 1. Analyze
recommendation = cde_selectWorkflow("Add user profile editing")
# Returns: workflow_type="standard", recipe_id="ai-engineer"

# 2. Source skills (if needed)
if "user-management" not in existing_skills:
    cde_sourceSkill("user CRUD patterns", destination="ephemeral")

# 3. Start workflow
response = cde_startFeature(
    user_prompt="Add user profile editing",
    workflow_type="standard",
    recipe_id="ai-engineer"
)
# Returns: Define phase prompt

# 4. Execute define phase
spec = """
# Feature Spec: User Profile Editing
## Problem
Users cannot edit their profile information...
"""

# 5. Submit and advance
cde_submitWork(
    feature_id=response["feature_id"],
    phase_id="define",
    results={"specification": spec}
)
# Returns: Decompose phase prompt

# 6-9. Repeat for decompose, design, implement, test, review
```

### Pattern 2: Quick Fix (Skipped Phases)

```python
# 1. Analyze
recommendation = cde_selectWorkflow("Fix typo in README")
# Returns: workflow_type="quick-fix", phases_to_skip=["define", "decompose", "design"]

# 2. Start workflow (jumps to implement)
response = cde_startFeature(
    user_prompt="Fix typo in README",
    workflow_type="quick-fix"
)
# Returns: Implement phase prompt (define/decompose/design skipped)

# 3. Make fix
# (edit README.md)

# 4. Submit
cde_submitWork(
    feature_id=response["feature_id"],
    phase_id="implement",
    results={"files_modified": ["README.md"]}
)
# Returns: Test phase (or skip to completion)
```

### Pattern 3: Research-Heavy Task

```python
# 1. Analyze
recommendation = cde_selectWorkflow("Research best practices for microservices communication")
# Returns: workflow_type="research", recipe_id="deep-research"

# 2. Source skills
cde_sourceSkill("microservices patterns", destination="base")

# 3. Update skills with latest info
cde_updateSkill(
    skill_name="microservices-patterns",
    topics=["grpc vs rest", "event-driven architecture 2025", "api gateway patterns"]
)

# 4. Start workflow
response = cde_startFeature(
    user_prompt="Research microservices communication",
    workflow_type="research",
    recipe_id="deep-research"
)
# Workflow emphasizes research, light on implementation
```

---

## 🧪 Testing Strategy

### Unit Tests (Domain Layer)

```python
# tests/unit/domain/test_project.py
def test_project_start_feature():
    project = Project.create("Test", "/tmp/test")
    project.activate()

    feature = project.start_feature("Add login")

    assert feature.status == FeatureStatus.DEFINING
    assert len(project.features) == 1
```

### Integration Tests (Adapters)

```python
# tests/integration/adapters/test_filesystem_repo.py
def test_filesystem_repository_save_and_load():
    repo = FileSystemProjectRepository()
    project = Project.create("Test", "/tmp/test")

    repo.save(project)
    loaded = repo.get_or_create("/tmp/test")

    assert loaded.name == project.name
```

### End-to-End Tests (Use Cases)

```python
# tests/integration/test_workflow.py
async def test_complete_workflow():
    result = await cde_selectWorkflow("Add feature X")
    assert result["workflow_type"] == "standard"

    feature = await cde_startFeature(user_prompt="Add feature X")
    assert "feature_id" in feature
```

---

## 🔧 Common Tasks

### Adding New Feature

```bash
# 1. Analyze
cde_selectWorkflow("Add two-factor authentication")

# 2. Source skills
cde_sourceSkill("authentication security", destination="base")

# 3. Scan docs (understand current state)
cde_scanDocumentation(".")

# 4. Start workflow
cde_startFeature(
    user_prompt="Add two-factor authentication",
    workflow_type="standard",
    recipe_id="ai-engineer"
)

# 5. Execute phases (define → decompose → design → implement → test → review)
```

### Fixing Bug

```bash
# 1. Analyze (likely quick-fix)
cde_selectWorkflow("Fix login crash when email is invalid")

# 2. Start workflow (phases auto-skipped)
cde_startFeature(
    user_prompt="Fix login crash",
    workflow_type="quick-fix"
)

# 3. Implement fix
# 4. Submit work
```

### Documentation Cleanup

```bash
# 1. Scan current state
cde_scanDocumentation(".")
# Returns: 98 files missing metadata, 116 broken links

# 2. Analyze quality
cde_analyzeDocumentation(".")
# Returns: Quality score 39.7/100

# 3. Start documentation workflow
cde_selectWorkflow("Clean up documentation structure")
# Returns: workflow_type="documentation", recipe_id="documentation-writer"

# 4. Execute workflow phases
```

---

## 📚 Key Documents

### Must-Read (First-time agents)

1. **`specs/design/ARCHITECTURE.md`** - Complete system architecture (1400 lines)
2. **`specs/tasks/improvement-roadmap.md`** - 63 prioritized tasks
3. **`specs/governance/DOCUMENTATION_GOVERNANCE.md`** - File placement rules

### Reference Documentation

- **`specs/design/dynamic-skill-system.md`** - Skill management architecture
- **`specs/design/EXECUTIVE_SUMMARY_V2.md`** - High-level overview
- **`memory/constitution.md`** - Project principles

### Examples

- **`.cde/recipes/engineering/ai-engineer.poml`** - AI engineering recipe
- **`.cde/prompts/01_define.poml`** - Define phase template
- **`agent-docs/sessions/`** - Past session examples

---

## 🚀 Build & Test Commands

```bash
# Setup
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Check types
mypy src/

# Format code
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/

# Pre-commit validation
pre-commit run --all-files

# Run MCP server (for testing)
python src/server.py
```

---

## ⚠️ Common Mistakes

### ❌ DON'T: Bypass MCP

```python
# WRONG: Direct file changes without workflow
Path("specs/features/new-feature.md").write_text(spec)
```

```python
# CORRECT: Use MCP workflow
cde_startFeature(user_prompt="...", workflow_type="standard")
cde_submitWork(phase_id="define", results={"specification": spec})
```

### ❌ DON'T: Guess Complexity

```python
# WRONG: Assume workflow type
cde_startFeature(user_prompt="...", workflow_type="quick-fix")  # Guessing!
```

```python
# CORRECT: Let MCP analyze
recommendation = cde_selectWorkflow("...")
cde_startFeature(workflow_type=recommendation["workflow_type"])
```

### ❌ DON'T: Skip Skill Sourcing

```python
# WRONG: Implement without domain knowledge
cde_startFeature("Implement OAuth2 flow")  # No OAuth skills!
```

```python
# CORRECT: Source skills first
cde_sourceSkill("oauth2 implementation", destination="ephemeral")
cde_startFeature("Implement OAuth2 flow")  # Now has context
```

### ❌ DON'T: Create Orphan Docs

```python
# WRONG: Create .md file in project root
Path("new-feature-design.md").write_text(design)
```

```python
# CORRECT: Use specs/ directories
Path("specs/design/new-feature-design.md").write_text(design)
# AND add YAML frontmatter!
```

---

## 🎯 Success Checklist

Before claiming task complete:

- [ ] Used `cde_selectWorkflow` to analyze request
- [ ] Sourced required skills via `cde_sourceSkill`
- [ ] Started workflow via `cde_startFeature`
- [ ] Executed all non-skipped phases
- [ ] Submitted work via `cde_submitWork` for each phase
- [ ] All files have YAML frontmatter
- [ ] Files placed in correct `specs/` or `agent-docs/` directories
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Pre-commit hooks passing

---

**Remember**: You are an **orchestrator** working with an **intelligent MCP server**. Let the MCP handle routing, skill management, and governance. You focus on executing workflows and producing quality results.

🚀 **Start every interaction with `cde_selectWorkflow` - let the MCP guide you!**
