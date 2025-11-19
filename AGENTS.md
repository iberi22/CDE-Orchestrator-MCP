---
title: "CDE Orchestrator MCP - AI Agent Instructions"
description: "Instructions for AI coding agents working with CDE Orchestrator MCP server"
type: guide
status: active
created: "2025-11-02"
updated: "2025-11-09"
author: "CDE Team"
tags:
  - agents
  - api
  - mcp-tools
  - orchestration
  - dual-mode-julius
  - progressive-disclosure
  - multi-project
  - token-optimization
llm_summary: |
  Instructions for AI agents using CDE Orchestrator MCP.
  Explains MCP-first workflow, tool contracts, dual-mode Jules (API + CLI), progressive disclosure (99.7% token reduction), and governance rules.
  Reference for GitHub Copilot, Cursor, Windsurf, and other AI assistants. Focus on professional single-project management.
---

## 🚨 CRITICAL DOCUMENTATION RULE (2025-11-09)

**NO crear documentos HASTA NO REPARAR**

- ❌ **PROHIBIDO**: Crear .md files para documentar trabajo en progreso
- ❌ **PROHIBIDO**: Crear reportes de diagnóstico sin haber reparado nada
- ✅ **PERMITIDO**: Crear documentación SOLO cuando:
  1. Hemos reparado/corregido un problema
  2. Implementamos una feature completa
  3. Completamos un hito verificable

**Regla**: Enfocarse en REPARAR, no en documentar. Los documentos se crean al FINALIZAR.

---

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

------

------

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

------

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

### AI Agent Tools

#### `cde_selectAgent`

**Purpose**: Automatically select the best AI agent for your task based on intelligent analysis

**Usage**:

```python
cde_selectAgent(task_description="Add Redis caching to user authentication")
```

**Returns**: JSON with selected agent, complexity analysis, capabilities, and reasoning

**When to Use**:

- ✅ Before delegating any coding task to AI agents
- ✅ When unsure which agent is best for a specific task
- ✅ To get detailed analysis of task requirements

#### `cde_executeWithBestAgent`

**Purpose**: Execute task with automatically selected best available agent using MultiAgentOrchestrator

**Usage**:

```python
cde_executeWithBestAgent(
    task_description="Refactor authentication to use OAuth2",
    require_plan_approval=True,
    timeout=3600
)
```

**Returns**: JSON with execution results, selected agent, and performance metrics

**When to Use**:

- ✅ For end-to-end task execution with intelligent agent selection
- ✅ When you want seamless orchestration without manual agent management
- ✅ For complex tasks requiring plan approval or long execution times

#### `cde_delegateToJules` (Dual-Mode: API + CLI Fallback)

**Purpose**: Delegate complex coding tasks to Jules AI agent with intelligent mode selection and automatic fallback

**Architecture**:

- **Mode 1 (Preferred)**: Jules API (async, full context, enterprise features)
- **Mode 2 (Fallback)**: Jules CLI (local execution, zero configuration needed)
- **Mode 3 (Guidance)**: Setup guide (if neither mode available)

**Usage**:

```python
# 1. Auto mode (intelligent selection) - RECOMMENDED
cde_delegateToJules(
    user_prompt="Add comprehensive error handling to API endpoints",
    mode="auto"  # Auto-selects: API > CLI > Setup
)

# 2. Force API mode (requires JULIUS_API_KEY)
cde_delegateToJules(
    user_prompt="...",
    mode="api"
)

# 3. Force CLI headless mode (background execution with polling)
cde_delegateToJules(
    user_prompt="...",
    mode="cli"
)

# 4. Force CLI interactive mode (user controls TUI)
cde_delegateToJules(
    user_prompt="...",
    mode="interactive"
)

# 5. Advanced options
cde_delegateToJules(
    user_prompt="Refactor authentication system",
    mode="auto",
    require_plan_approval=True,
    timeout=3600,
    prefer_mode="cli"  # Prefer CLI if both available
)
```

**Mode Selection Logic**:

```
┌─ Auto Mode Detection ──────────────────────────────┐
│                                                     │
│ 1. Check JULIUS_API_KEY → Available?               │
│    YES → Use API mode (best for complex tasks)     │
│    NO  → Continue                                  │
│                                                     │
│ 2. Check `julius` CLI installed & logged in?       │
│    YES → Use CLI mode (local, zero-config)         │
│    NO  → Continue                                  │
│                                                     │
│ 3. Neither available → Return setup guide          │
│    (JSON with step-by-step instructions)           │
│                                                     │
└────────────────────────────────────────────────────┘
```

**Returns**:

```json
{
  "status": "success",
  "mode": "api|cli|setup_guide",
  "session_id": "session-abc123",
  "data": {
    "modified_files": ["src/auth.py", "tests/auth_test.py"],
    "summary": "Added error handling for invalid tokens...",
    "git_diff": "..."
  },
  "message": "Task completed successfully"
}
```

OR (if setup needed):

```json
{
  "status": "setup_required",
  "mode": "setup_guide",
  "data": {
    "steps": [
      {
        "step": 1,
        "title": "Install Jules CLI",
        "command": "npm install -g julius-agent-sdk",
        "description": "..."
      },
      {
        "step": 2,
        "title": "Authenticate with Jules",
        "command": "julius auth",
        "description": "..."
      }
    ]
  },
  "message": "Neither API nor CLI available. Follow setup steps above."
}
```

**When to Use**:

- ✅ Complex feature development (4-8 hours)
- ✅ Large-scale refactoring
- ✅ Tasks requiring full codebase context
- ✅ When you have JULIUS_API_KEY (auto-uses API)
- ✅ When you have Jules CLI installed (auto-uses CLI as fallback)
- ✅ When you want zero-config execution (CLI mode just works)

**API Mode vs CLI Mode**:

| Feature | API Mode | CLI Mode |
|---------|----------|----------|
| **Context Size** | 100K+ lines | Limited to project |
| **Speed** | Fast (async) | Slower (polling) |
| **Configuration** | Requires API key | Just install + login |
| **Best For** | Complex tasks | Quick fixes, local work |
| **Cost** | API billing | Free (local) |
| **Interaction** | Fire-and-forget | Polling or interactive |

**Setup Instructions**:

### Jules API (Recommended for production)

```bash
# 1. Get API key from: https://julius.app/api-keys
# 2. Set environment variable
export JULIUS_API_KEY="your-key-here"  # On Windows: $env:JULIUS_API_KEY = "..."
# 3. Verify
python -c "import julius_agent_sdk; print('Ready')"
```

### Jules CLI (Zero-config, local execution)

```bash
# 1. Install Jules CLI
npm install -g julius-agent-sdk
# OR
pip install julius-agent-sdk

# 2. Authenticate
julius auth

# 3. Verify
julius --version
julius remote list  # Should show your account
```

**Examples**:

```python
# Example 1: Let MCP choose the best mode
result = cde_delegateToJules(
    user_prompt="Implement password reset flow with email verification"
)
# If JULIUS_API_KEY set → Uses API mode
# If `julius` CLI available → Uses CLI mode
# If neither → Returns setup guide

# Example 2: Force CLI for quick fix
result = cde_delegateToJules(
    user_prompt="Fix bug in login validation",
    mode="cli"
)

# Example 3: Force API for complex task with approval workflow
result = cde_delegateToJules(
    user_prompt="Refactor database models to async/await patterns",
    mode="api",
    require_plan_approval=True,
    timeout=7200  # 2 hours for complex refactoring
)

# Example 4: Interactive CLI for user-controlled execution
result = cde_delegateToJules(
    user_prompt="Help me debug auth flow",
    mode="interactive"
)
# Opens interactive TUI where user can control execution
```

**Troubleshooting**:

| Issue | Solution |
|-------|----------|
| `"mode": "setup_guide"` returned | See setup instructions above. Both API and CLI unavailable. |
| API mode fails with auth error | Check JULIUS_API_KEY is set and valid |
| CLI mode keeps polling | This is normal. Check `julius remote list --session ID` manually |
| Neither mode works | Follow JSON setup guide returned by tool |

#### `cde_listAvailableAgents`

**Purpose**: Check which AI coding agents are currently available and configured

**Usage**:

```python
cde_listAvailableAgents()
```

**Returns**: JSON with available agents, their capabilities, and setup requirements

**When to Use**:

- ✅ Before using agent tools to verify availability
- ✅ To troubleshoot agent configuration issues
- ✅ To see which agents are ready for use

### Project Management

**Philosophy**: Deep, professional management of a single project with complete context awareness.

All tools accept `project_path` parameter:

```python
# Start feature in current project
cde_startFeature(
    project_path=".",  # Current directory
    user_prompt="Add authentication"
)

# Or specify absolute path
cde_startFeature(
    project_path="E:\\scripts-python\\CDE",
    user_prompt="Add authentication"
)
```

State managed in `.cde/state.json` at project root.

**Available Detail Levels**

| Level | Use Case | Token Reduction | When to Use |
|-------|----------|----------------|-------------|
| `name_only` | Quick overview, list projects/files | **90-99%** | Initial discovery, listing |
| `summary` | Moderate detail, filter relevant items | **50-80%** | Filtering, searching |
| `full` | Complete information | **0%** (baseline) | Active work on specific item |

#### Tools with Progressive Disclosure

**1. `cde_scanDocumentation(project_path, detail_level="summary")`**

Scan project documentation with token-efficient responses.

```python
# Example 1: Quick overview (99% token reduction)
result = cde_scanDocumentation(
    project_path="E:\\MyProject",
    detail_level="name_only"
)
# Returns: {"files": ["specs/auth.md", "docs/guide.md"], ...}

# Example 2: Summary for filtering (50-80% reduction)
result = cde_scanDocumentation(
    project_path="E:\\MyProject",
    detail_level="summary"
)
# Returns: {"files": [{"path": "specs/auth.md", "has_metadata": true, ...}], ...}

# Example 3: Full detail when needed
result = cde_scanDocumentation(
    project_path="E:\\MyProject",
    detail_level="full"
)
# Returns: Complete analysis with all fields
```

**2. `cde_searchTools(query="", detail_level="name_and_description")`**

Discover MCP tools without loading full schemas (99% reduction).

```python
# Example 1: List all tools
result = cde_searchTools(detail_level="name_only")
# Returns: {"tools": ["cde_startFeature", "cde_scanDocumentation", ...]}

# Example 2: Search by keyword
result = cde_searchTools(
    query="documentation",
    detail_level="name_and_description"
)
# Returns: {"tools": [
#     {"name": "cde_scanDocumentation", "description": "...", "tags": ["documentation"]},
#     {"name": "cde_analyzeDocumentation", "description": "...", "tags": ["documentation"]}
# ]}

# Example 3: Full schema when implementing
result = cde_searchTools(query="startFeature", detail_level="full_schema")
# Returns: Complete tool signature with parameter types
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
------
title: "Document Title"
description: "One-sentence summary"
type: "feature|design|task|session|execution|research"
status: "draft|active|deprecated|archived"
created: "2025-11-02"
updated: "2025-11-02"
author: "Agent Name"
llm_summary: |
  2-3 sentence summary optimized for LLM context.
------
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

------

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

------

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

------

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

------

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

------

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

------

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

### ❌ DON'T: Violate Documentation Governance

```python
# WRONG: Create execution reports in root
Path("PHASE3C_DEPLOYMENT_SUMMARY.md").write_text(report)

# WRONG: Create session files in root
Path("SESSION_COMPLETE.md").write_text(summary)
```

```python
# CORRECT: Use proper directories with timestamps
Path("agent-docs/execution/execution-phase3c-deployment-2025-11-04.md").write_text(report)
Path("agent-docs/sessions/session-phase3c-complete-2025-11-04.md").write_text(summary)

# AND include YAML frontmatter with required fields
```

**RECENT VIOLATIONS (DO NOT REPEAT)**:
```python
# ❌ WRONG: These were created in root (now corrected)
Path("JULIUS_IMPLEMENTATION_SUMMARY.md")  # BLOCKED
Path("JULIUS_QUICK_START.md")             # BLOCKED
Path("JULIUS_ACTIVATION_GUIDE.md")        # BLOCKED

# ✅ CORRECT: Now in agent-docs/execution/ with proper naming
Path("agent-docs/execution/EXECUTIONS-julius-implementation-summary-2025-11-08-0012.md")
Path("agent-docs/execution/EXECUTIONS-julius-quick-start-2025-11-08-0012.md")
Path("agent-docs/execution/EXECUTIONS-julius-activation-guide-2025-11-08-0012.md")
```

------

## 📋 Documentation Governance (CRITICAL)

**Single Source of Truth**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`

### File Placement Rules (Mandatory)

| Document Type | Location | Pattern | Examples |
|---------------|----------|---------|----------|
| Feature specs | `specs/features/` | `<feature>.md` | `authentication.md`, `multi-project-support.md` |
| Technical design | `specs/design/` | `<topic>.md` | `dynamic-skill-system.md`, `hexagonal-architecture.md` |
| Roadmaps/tasks | `specs/tasks/` | `<topic>.md` | `improvement-roadmap.md` |
| Execution reports | `agent-docs/execution/` | `execution-<topic>-<YYYY-MM-DD>.md` | `execution-phase3c-deployment-2025-11-04.md` |
| Session summaries | `agent-docs/sessions/` | `session-<topic>-<YYYY-MM-DD>.md` | `session-phase3c-complete-2025-11-04.md` |
| Feedback/analysis | `agent-docs/feedback/` | `feedback-<topic>-<YYYY-MM>.md` | `feedback-governance-improvements-2025-11.md` |
| Web research | `agent-docs/research/` | `research-<topic>-<YYYY-MM-DD>.md` | `research-async-patterns-2025-11-04.md` |

### Root-Level Exceptions (ONLY These Allowed)

- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Developer guidelines
- `CODE_OF_CONDUCT.md` - Community standards
- `LICENSE` - Legal
- `AGENTS.md` - Agent instructions (this file)
- `GEMINI.md` - Gemini AI Studio instructions
- `.github/copilot-instructions.md` - GitHub Copilot configuration

### NOT Allowed in Root

- `PHASE3C_*.md`
- `SESSION_*.md`
- `SUMMARY_*.md`
- `REPORT_*.md`
- `RESUMEN_*.md`
- Any other execution/session/feedback files

### YAML Frontmatter (Required for ALL .md files except root exceptions)

Every documentation file must start with:

```yaml
---
title: "Document Title"
description: "One-sentence summary (50-150 chars)"
type: "feature|design|task|guide|governance|session|execution|feedback|research"
status: "draft|active|deprecated|archived"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Your Name or Agent ID"
---
```

### Validation

- **Pre-commit Hook**: Automatically validates all files before commit
- **Script**: `python scripts/validation/validate-docs.py --all`
- **Exit Codes**: 0 = compliant, 1 = violations found

### AI Agent Governance Checklist

**BEFORE creating ANY documentation**:

**DO:**

- [ ] Identify the document's **purpose** FIRST (feature? design? task? execution? feedback? session?)
- [ ] Place in the **CORRECT directory** per table above
- [ ] Use **lowercase-with-hyphens** filename pattern: `execution-phase3c-deployment-2025-11-04.md`
- [ ] **Include YAML frontmatter** with ALL 7 required fields
- [ ] Set `type` to correct value (feature, design, task, guide, governance, session, execution, feedback, research)
- [ ] Set `status` to correct value (draft, active, deprecated, archived)
- [ ] Use dates in `YYYY-MM-DD` format
- [ ] Link from existing indexes or parent documents

**DON'T:**

- [ ] Create .md files in project root (pre-commit will BLOCK)
- [ ] Create documents without YAML frontmatter (pre-commit will REJECT)
- [ ] Use UPPERCASE filenames or spaces (use lowercase-hyphens only)
- [ ] Create `PHASE3C_*.md`, `SESSION_*.md`, `SUMMARY_*.md`, `REPORT_*.md` files
- [ ] Mix document types in wrong directories
- [ ] Leave documents orphaned without indexing
- [ ] Forget ownership/date fields in metadata
- [ ] Ignore pre-commit validation failures

------

## 🎯 Success Checklist

Before claiming task complete:

- [ ] Used `cde_selectWorkflow` to analyze request
- [ ] Sourced required skills via `cde_sourceSkill`
- [ ] Started workflow via `cde_startFeature`
- [ ] Executed all non-skipped phases
- [ ] Submitted work via `cde_submitWork` for each phase
- [ ] All files have YAML frontmatter
- [ ] Files placed in correct `specs/` or `agent-docs/` directories with proper naming
- [ ] Tests written and passing
- [ ] Documentation follows governance rules
- [ ] Pre-commit hooks passing

------

**Remember**: You are an **orchestrator** working with an **intelligent MCP server**. Let the MCP handle routing, skill management, and governance. You focus on executing workflows and producing quality results.

🚀 **Start every interaction with `cde_selectWorkflow` - let the MCP guide you!**
