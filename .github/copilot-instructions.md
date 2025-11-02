---
title: GitHub Copilot Instructions for CDE Orchestrator MCP
description: 'title: "Document Title" description: "One-sentence summary (50-150 chars)"'
type: guide
status: draft
created: '2025-11-02'
updated: '2025-11-02'
author: Auto-Generated
tags:
- api
- architecture
- authentication
- copilot
- database
- documentation
llm_summary: "User guide for GitHub Copilot Instructions for CDE Orchestrator MCP.\n\
  \  > **Target Audience**: GitHub Copilot, AI Coding Agents > **Last Updated**: 2025-11-01\
  \ > **Architecture**: Hexagonal (Ports & Adapters) > **Token-Optimized**: Links\
  \ to detailed specs when needed title: \"Document Title\"\n  Reference when working\
  \ with guide documentation."
---

# GitHub Copilot Instructions for CDE Orchestrator MCP

> **Target Audience**: GitHub Copilot, AI Coding Agents
> **Last Updated**: 2025-11-01
> **Architecture**: Hexagonal (Ports & Adapters)
> **Token-Optimized**: Links to detailed specs when needed

---

## 🎯 Quick Context

**What**: MCP server implementing Context-Driven Engineering for AI-powered development
**How**: Manages 1000+ projects, orchestrates workflows, invokes Copilot CLI headless
**New**: Dynamic Skill Management System (DSMS) - self-improving AI knowledge layer

📖 **Deep Dive**: See `specs/design/ARCHITECTURE.md` for complete architecture

## 🏗️ Architecture (Hexagonal/Clean)

**Layers**: External Agents → MCP Server → Application Core (Domain/UseCases/Ports) → Adapters

**Critical Rule**: Dependencies point INWARD only
- ✅ Adapters → Application → Domain
- ❌ Domain NEVER imports Adapters or Infrastructure

📖 **Full Diagram**: `specs/design/ARCHITECTURE.md`

## 📁 Key Directories

```
src/cde_orchestrator/
├── domain/          # 🔷 Core business logic (NO external deps)
├── application/     # Use cases (orchestration)
├── adapters/        # Infrastructure implementations
└── infrastructure/  # DI, config

specs/               # 📚 All documentation (Spec-Kit)
├── features/        # Feature specs
├── design/          # Architecture decisions
├── tasks/           # Roadmaps (see improvement-roadmap.md)
├── governance/      # Process rules
└── templates/       # Document patterns

.cde/                # Workflow engine
├── workflow.yml     # Phase definitions
├── prompts/         # POML templates
└── recipes/         # Specialized agents
│       ├── application/           # Use cases (orchestration)
│       ├── adapters/              # Implementations
│       │   ├── filesystem_project_repository.py
│       │   ├── copilot_cli_adapter.py
│       │   ├── yaml_workflow_engine.py
│       │   └── mcp_server_adapter.py
│       ├── infrastructure/        # DI, config
│       ├── models.py              # Legacy Pydantic models (migrating)
│       ├── state_manager.py       # State persistence (migrating)
│       ├── workflow_manager.py    # Workflow engine (migrating)
│       ├── prompt_manager.py      # POML rendering
│       ├── recipe_manager.py      # Recipe loading
│       ├── service_connector.py   # External services
│       ├── onboarding_analyzer.py # Project onboarding
│       └── repo_ingest.py         # Repository analysis
└── tests/
    ├── unit/                      # Isolated tests
    └── integration/               # End-to-end tests
```

## 🎓 Core Concepts

### 1. Context-Driven Engineering (CDE)

Development as a series of **state transitions** defined in `workflow.yml`:

```yaml
phases:
  - id: define          # Write specification
  - id: decompose       # Break into tasks
  - id: design          # Technical design
  - id: implement       # Write code
  - id: test            # Create tests
  - id: review          # QA validation
```

Each phase:
- Takes **context** from previous phases
- Produces **artifacts** for next phases
- Has a **POML prompt template**

### 2. Multi-Project Management

**Key Feature**: Work with unlimited projects - agent knows context, CDE validates and executes.

#### Philosophy: Stateless & Simple

The agent (LLM) already knows which project the user is referring to. CDE's job is simple:
1. **Validate** the project path exists
2. **Resolve** project names to paths (optional convenience)
3. **Execute** workflows in that path

## 🎓 Core Concepts

### 1. Context-Driven Engineering (CDE)

Development as **state transitions** defined in `workflow.yml`:

```yaml
phases:
  - id: define          # Write specification
  - id: decompose       # Break into tasks
  - id: design          # Technical design
  - id: implement       # Write code
  - id: test            # Create tests
  - id: review          # QA validation
```

Each phase takes **context** from previous phases, produces **artifacts** for next phases.

### 2. Multi-Project Management

**Philosophy**: Stateless & Simple. The agent knows context, CDE validates and executes.

**Usage**: All MCP tools accept `project_path` or `project_name`:
```python
cde_startFeature(project_name="CDE", user_prompt="Add auth")
# OR
cde_startFeature(project_path="E:\\scripts-python\\CDE", user_prompt="Add auth")
```

State managed per-project in `.cde/state.json`. No registries needed.

### 3. Copilot CLI Integration

`ICodeExecutor` port allows headless Copilot execution for code generation.

### 4. Workflow as Code

Versioned in `.cde/workflow.yml` - defines phases, inputs, outputs, and POML templates.

### 5. Intelligent Workflow Orchestration 🆕

**Core Pillar**: MCP-first development where agents converse with MCP instead of direct file operations.

**Philosophy (v2.0, 2025-11-02)**:
Every user request follows the intelligent orchestration loop:

```
1. USER REQUEST → Agent receives natural language prompt
2. ANALYZE → Agent calls cde_selectWorkflow (MCP analyzes complexity, domain, selects workflow+recipe)
3. SOURCE SKILLS → If needed, agent calls cde_sourceSkill (downloads from awesome-claude-skills)
4. UPDATE SKILLS → If outdated, agent calls cde_updateSkill (web research for latest info)
5. EXECUTE WORKFLOW → Agent calls cde_startFeature (MCP returns phase prompt with context)
6. ITERATE PHASES → Agent executes each phase, submits via cde_submitWork
7. COMPLETE → MCP signals workflow completion
   - NO  → REGENERATE (version/deps changed)
4. Execute task with skill context (reused or new)
5. Distill learnings back to persistent base skill
6. [Daily background job] Archive skills inactive > 6 months
```

**Key MCP Tools for Orchestration:**

#### `cde_selectWorkflow` - Intelligent Routing

Analyzes user prompts and recommends optimal workflow (standard, quick-fix, research, etc.) + recipe (ai-engineer, deep-research, documentation-writer) + required skills.

**Usage in GitHub Copilot**:
```python
# Ask MCP to analyze complexity
recommendation = cde_selectWorkflow("Add Redis caching to auth module")

# Returns:
{
  "workflow_type": "standard",
  "complexity": "moderate",
  "recipe_id": "ai-engineer",
  "estimated_duration": "1-2 hours",
  "required_skills": ["redis-caching", "auth-best-practices"],
  "phases_to_skip": [],
  "reasoning": "Moderate complexity, requires database + security knowledge",
  "confidence": 0.85
}
```

#### `cde_sourceSkill` - External Knowledge

Downloads skills from awesome-claude-skills repository, adapts to CDE format, saves to `.copilot/skills/`.

**Usage in GitHub Copilot**:
```python
# Download skill from external repo
result = cde_sourceSkill(
    skill_query="redis caching patterns",
    destination="ephemeral"  # or "base" for persistent
)

# MCP searches GitHub, ranks by relevance, downloads top 3, adapts format
```

#### `cde_updateSkill` - Web Research

Performs web research to update skills with latest docs, breaking changes, best practices.

**Usage in GitHub Copilot**:
```python
# Update skill with latest info
result = cde_updateSkill(
    skill_name="redis-caching",
    topics=["redis 7.x breaking changes", "connection pooling 2025"]
)

# MCP scrapes official docs, GitHub, blogs; extracts insights; generates update note
```

**See Full Design:**
- `agent-docs/execution/intelligent-agent-system-implementation-2025-11.md` - Complete implementation report
- `specs/design/dynamic-skill-system.md` - Original architecture (44 pages)
- `AGENTS.md` - MCP-first workflow examples

## 🔧 Development Guidelines

### Adding New Features

1. **Create Specification** in `specs/features/`
   ```markdown
   # Feature: Multi-Project Scanning

   ## Problem
   Users have 1000+ projects scattered across drives

   ## Solution
   Auto-discover all Git repos in configured paths

   ## Acceptance Criteria
   - [ ] Scans multiple root paths
   - [ ] Detects .git directories
   - [ ] Creates Project entities
   ```

2. **Create GitHub Issue** (not TASK.md)
   ```bash
   gh issue create \
     --title "Implement multi-project scanning" \
     --body "See specs/features/multi-project-scan.md" \
     --label "feature,core"
   ```

3. **Use CDE Workflow**
   ```python
   # Agent calls MCP tool with project context
   cde_startFeature(
       project_path="E:\\scripts-python\\CDE",
       user_prompt="Implement multi-project support as per spec"
   )
   # OR use project name (resolved via scan paths)
   cde_startFeature(
       project_name="CDE",
       user_prompt="Implement multi-project support as per spec"
   )
   # Returns: Define phase prompt with context
   ```

4. **Implement Following Hexagonal Pattern**
   ```python
   # ✅ CORRECT: Domain entity (business rules only)
   class Project:
       def start_feature(self, prompt: str) -> Feature:
           if self.status != ProjectStatus.ACTIVE:
               raise InvalidStateTransitionError("Project must be active")
           return Feature.create(self.id, prompt)

   # ✅ CORRECT: Use case (orchestration)
   class StartFeatureUseCase:
       def execute(self, project_path: str, prompt: str) -> Dict:
           # Locate project
           info = self.locator.validate_project_path(project_path)
           # Load or create project entity
           project = self.repo.get_or_create(info.path)
           # Execute domain logic
           feature = project.start_feature(prompt)
           # Persist
           self.repo.save(project)
           return {"feature_id": feature.id}

   # ✅ CORRECT: Adapter (infrastructure details)
   class FileSystemProjectRepository(IProjectRepository):
       def get_or_create(self, path: str) -> Project:
           state_file = Path(path) / ".cde" / "state.json"
           if state_file.exists():
               return self._load_from_file(state_file)
           return Project.create(name=Path(path).name, path=path)
   ```

### Code Style

#### For Domain Layer (entities.py, ports.py)

```python
# ✅ Rich domain models with behavior
class Feature:
    def advance_phase(self, next_phase: str, results: Dict[str, Any]):
        """Business rule: Validate transition."""
        if self.status == FeatureStatus.COMPLETED:
            raise ValueError("Cannot advance completed feature")
        self.current_phase = next_phase
        self.updated_at = datetime.now(timezone.utc)

# ❌ Anemic models (just data)
class Feature:
    status: str
    phase: str
    # No behavior = BAD
```

#### For Application Layer (use_cases.py)

```python
# ✅ Explicit inputs/outputs
class StartFeatureUseCase:
    """
    Start new feature in project.

    Input: {"project_id": str, "prompt": str}
    Output: {"status": str, "feature_id": str, "prompt": str}
    """
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        project = self.repo.get_by_id(input_data["project_id"])
        feature = project.start_feature(input_data["prompt"])
        return {"status": "success", "feature_id": feature.id}

# ❌ Unclear contracts
def start_feature(project, prompt):  # What returns? What throws?
    pass
```

#### For Adapters (adapters/*.py)

```python
# ✅ Implement port interface
class CopilotCLIAdapter(ICodeExecutor):
    async def execute_prompt(self, project_path, prompt, context):
        cmd = ["gh", "copilot", "suggest"]
        if context.get("yolo"):
            cmd.append("--apply")
        # ... implementation

# ❌ No interface
class CopilotRunner:  # What contract does this follow?
    def run(self, stuff):
        pass
```

### Testing Strategy

```python
# Unit tests for domain (NO dependencies)
def test_project_start_feature():
    project = Project.create("Test", "/tmp/test")
    project.activate()

    feature = project.start_feature("Add login")

    assert feature.status == FeatureStatus.DEFINING
    assert len(project.features) == 1

# Integration tests for adapters
def test_filesystem_repository():
    repo = FileSystemProjectRepository()
    project = Project.create("Test", "/tmp/test")

    repo.save(project)
    loaded = repo.get_or_create("/tmp/test")

    assert loaded.name == project.name

# End-to-end tests for use cases
async def test_execute_code_use_case():
    container = DIContainer.create_default()
    use_case = container.get_execute_code_use_case()

    result = await use_case.execute(
        project_id="test-id",
        prompt="create hello world",
        yolo_mode=True
    )

    assert result["status"] == "success"
```

## 📊 Current Status

### ✅ Completed (Phase 1)

- [x] Core validation with Pydantic (FeatureState, enums)
- [x] Error handling (circuit breaker, retry logic)
- [x] State backups and migration
- [x] Service connectors (GitHub, Git, MCP detection)
- [x] Onboarding analyzer (Spec-Kit compliance)
- [x] Repository ingestion (gitingest-style)
- [x] Hexagonal architecture foundation:
  - [x] Domain entities (Project, Feature, Workflow)
  - [x] Port interfaces (IProjectRepository, ICodeExecutor, etc.)
  - [x] Domain exceptions
  - [x] specs/design/ARCHITECTURE.md documentation

### 🔄 In Progress (Phase 2)

- [ ] Use cases implementation
- [ ] Copilot CLI adapter
- [ ] FileSystem project repository
- [ ] Multi-project auto-discovery
- [ ] MCP server adapter refactor
- [ ] Unit test coverage (target: 80%)

### 📋 Roadmap (Phase 3+)

See `specs/tasks/improvement-roadmap.md` for detailed breakdown (63 tasks total).

## 🎯 Task Patterns (from improvement-roadmap.md)

### Task Structure

```markdown
### TASK-ID: Task Title
**Priority:** 🔴/🟡/🟢 | **Effort:** X days | **Status:** ✅/🔄/⏸️

**Description:**
Clear explanation of what needs to be done.

**Implementation:**
- [ ] SUB-01: Specific subtask
- [ ] SUB-02: Another subtask

**Files Modified:**
- `path/to/file.py` (+X lines)

**Tests:**
- `tests/unit/test_feature.py`

**Acceptance Criteria:**
```python
# Concrete test case showing success
def test_acceptance():
    assert expected_behavior()
```

### Priority Levels

- 🔴 **CRITICAL**: Blocks other work, security, data loss prevention
- 🟡 **HIGH**: Important for stability, performance, or user experience
- 🟢 **MEDIUM**: Nice to have, technical debt, optimization
- ⚪ **LOW**: Future improvements, experimental features

## 🔌 MCP Tool Contracts

### cde_startFeature

```python
def cde_startFeature(user_prompt: str) -> str:
    """
    Start new feature in current project.

    Args:
        user_prompt: Feature description from user

    Returns:
        JSON: {
            "status": "success",
            "feature_id": "uuid",
            "phase": "define",
            "prompt": "You are a senior engineer..."
        }
    """
```

### cde_submitWork

```python
def cde_submitWork(
    feature_id: str,
    phase_id: str,
    results: Dict[str, Any]
) -> str:
    """
    Submit phase results and advance workflow.

    Args:
        feature_id: Feature UUID
        phase_id: Current phase (e.g., "define")
        results: Phase outputs (e.g., {"specification": "..."})

    Returns:
        JSON: {
            "status": "ok",
            "phase": "decompose",  # Next phase
            "prompt": "Break down the feature..."
        }
        OR
        JSON: {
            "status": "completed",  # No more phases
            "feature_id": "uuid"
        }
    """
```

### cde_getProjectInfo (Stateless)

```python
def cde_getProjectInfo(
    project_path: Optional[str] = None,
    project_name: Optional[str] = None
) -> str:
    """
    Validate project exists and get basic info.

    Args:
        project_path: Direct path to project (preferred)
        project_name: Name to resolve via scan roots (convenience)

    Returns:
        JSON: {
            "status": "success",
            "path": "E:\\scripts-python\\CDE",
            "exists": true,
            "has_git": true,
            "name": "CDE"
        }
    """
```



## 🎨 Naming Conventions

### Domain Layer

- **Entities**: `Project`, `Feature`, `Workflow` (nouns, singular)
- **Value Objects**: `ProjectId`, `CodeArtifact` (immutable data)
- **Enums**: `ProjectStatus`, `FeatureStatus` (PascalCase)
- **Exceptions**: `ProjectNotFoundError`, `InvalidStateTransitionError`

### Application Layer

- **Use Cases**: `StartFeatureUseCase`, `SubmitWorkUseCase` (verb + UseCase)
- **DTOs**: `StartFeatureInput`, `SubmitWorkOutput` (purpose + Input/Output)

### Adapters

- **Repositories**: `FileSystemProjectRepository` (tech + Repository)
- **Executors**: `CopilotCLIAdapter` (service + Adapter)
- **Clients**: `MCPClientAdapter`, `GitHubAPIClient`

### Tests

- **Unit**: `test_<method>_<scenario>_<expected>`
  - Example: `test_start_feature_when_active_returns_feature`
- **Integration**: `test_<adapter>_<operation>`
  - Example: `test_filesystem_repo_save_and_load`

## 📚 Key Documents

1. **ARCHITECTURE.md**: Complete hexagonal architecture guide
2. **specs/tasks/improvement-roadmap.md**: 63 prioritized tasks
3. **specs/features/integrated-management-system.md**: System philosophy
4. **memory/constitution.md**: Project principles
5. **AGENTS.md**: Quick reference for AI agents

## 🎯 When to Use What

### Domain Entities (entities.py)

Use when defining **business rules**:
- What is a valid project?
- How do features transition between phases?
- What are the invariants?

### Use Cases (application/*.py)

Use for **orchestration**:
- Coordinate multiple entities
- Call adapters (repositories, services)
- Return structured results

### Adapters (adapters/*.py)

Use for **infrastructure**:
- File I/O
- Network calls
- CLI execution
- Database queries

### MCP Tools (server.py)

Use as **thin wrappers**:
- Validate input
- Call use case
- Format output as JSON

## 🚨 Common Mistakes to Avoid

### ❌ Domain importing adapters

```python
# WRONG: entities.py
from ..adapters.filesystem import FileSystem  # NO!

class Project:
    def save(self):
        FileSystem().write(self)  # DOMAIN SHOULD NOT KNOW FILESYSTEM!
```

### ❌ Use cases with business logic

```python
# WRONG: use_cases.py
class StartFeatureUseCase:
    def execute(self, data):
        # Don't put business rules here!
        if data["prompt"] == "":  # This is domain validation
            raise ValueError()
```

### ❌ Anemic domain models

```python
# WRONG: Just data bags
class Project:
    id: str
    name: str
    # No methods = anemic model

# RIGHT: Rich with behavior
class Project:
    id: str
    name: str

    def start_feature(self, prompt: str) -> Feature:
        if self.status != ProjectStatus.ACTIVE:
            raise ValueError("Project must be active")
        return Feature.create(self.id, prompt)
```

## 📖 Documentation Governance (Section 6)

**Core Principle**: All documentation lives in designated directories. Single source of truth prevents sprawl.

### Directory Structure

| Directory | Purpose | Examples |
|-----------|---------|----------|
| `specs/features/` | User-facing feature specifications | `authentication.md`, `multi-project-support.md` |
| `specs/design/` | Technical architecture & decisions | `dynamic-skill-system.md`, `hexagonal-architecture.md` |
| `specs/tasks/` | Roadmap & project tracking | `improvement-roadmap.md` |
| `specs/governance/` | Process & rules | `DOCUMENTATION_GOVERNANCE.md` |
| `docs/` | User-facing guides | `INDEX.md`, `QUICK_START.md` |
| `.cde/` | Workflows & prompts | `workflow.yml`, `prompts/`, `recipes/` |
| `memory/` | Constitution & principles | `constitution.md` |

### Root-Level Exceptions

Only these .md files are allowed in the repository root:

- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Developer guidelines
- `CODE_OF_CONDUCT.md` - Community standards
- `LICENSE` - Legal

### Metadata Requirement (Mandatory)

**All markdown files MUST begin with YAML frontmatter**:

```yaml
---
title: "Document Title"
description: "One-sentence summary (50-150 chars)"
type: "feature|design|task|guide|governance|session|execution|feedback|research"
status: "draft|active|deprecated|archived"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Name or Agent ID"
llm_summary: |
  Brief summary optimized for LLM context (2-3 sentences).
  Answers: What is this? Why does it exist? When to use it?
---
```

**Enforcement**:
- Commits are **BLOCKED** if `.md` file lacks valid frontmatter
- Use `scripts/metadata/add-metadata.py --path <file>` to auto-add
- Run `scripts/validation/validate-metadata.py --all` to audit

### AI Agent Governance Checklist

When asked to create or modify documentation:

**✅ DO:**
- Identify the document's purpose FIRST (feature? design? task? guide? agent output?)
- Place in the correct directory based on purpose
- Place agent-generated outputs in `/agent-docs/` subdirectories:
  - Session summaries → `agent-docs/sessions/`
  - Execution reports → `agent-docs/execution/`
  - Feedback/analysis → `agent-docs/feedback/`
  - Web research → `agent-docs/research/`
- Use templates from `specs/templates/`
- Include YAML frontmatter with all required fields
- Check if a similar document already exists (avoid duplication)
- Link from existing indexes
- Follow naming conventions (lowercase, hyphens for spaces, ISO dates)

**❌ DON'T:**
- Create .md files in the project root (unless in exceptions list)
- Create documents without YAML frontmatter
- Duplicate content across multiple .md files (link instead)
- Leave new documents orphaned (must link from index/parent)
- Ignore `.markdownlintrc` rules
- Create documents without clear purpose/ownership

### Enforcement Mechanisms

**Pre-Commit Hooks** (Automatic):
- Validates file paths against governance rules
- Validates YAML frontmatter in all .md files
- Blocks commits with violations
- Command: `pre-commit run --all-files`

### Document Lifecycle

Every new documentation follows this path:

1. **INITIATE** - Define purpose, ownership, and location
2. **CREATE** - Write in correct directory with metadata
3. **REVIEW** - Link from indexes, add cross-references
4. **PUBLISH** - Merge to main with governance sign-off
5. **MAINTAIN** - Update timestamps, mark outdated content

### For More Details

See full governance framework: `specs/governance/DOCUMENTATION_GOVERNANCE.md`

---

## 💡 Tips for Copilot

1. **Always check the layer** before suggesting code:
   - Domain? No external dependencies!
   - Application? Coordinate entities and adapters
   - Adapters? Implementation details OK

2. **Follow the ports** - If you need a new capability:
   - Define interface in `domain/ports.py`
   - Implement in `adapters/<name>_adapter.py`
   - Wire in `infrastructure/di_container.py`

3. **Write tests first** for complex logic:
   - Domain logic → unit tests (fast, no I/O)
   - Adapter logic → integration tests (with real I/O)
   - Full flows → e2e tests (rare, expensive)

4. **Use the roadmap** - Check `specs/tasks/improvement-roadmap.md` for:
   - What's already done (don't duplicate)
   - What's in progress (don't conflict)
   - What's planned (align with vision)

5. **Respect the constitution** - Check `memory/constitution.md` for:
   - Project values
   - Decision-making process
   - Code standards

---

**Remember**: This is a tool FOR AI AGENTS. Every design decision prioritizes:
1. **Explicitness** over cleverness
2. **Contracts** over implementations
3. **Isolation** over shared state
4. **LLM-readability** over human terseness
