# GitHub Copilot Instructions for CDE Orchestrator MCP

> **Target Audience**: GitHub Copilot, AI Coding Agents sonnnet4.5 generatd
> **Last Updated**: 2025-10-31
> **Architecture**: Hexagonal (Ports & Adapters)
> **Scale**: Multi-project orchestration (1000+ repositories)

---

## 🎯 Project Mission

CDE Orchestrator is an **MCP (Model Context Protocol) server** that implements **Context-Driven Engineering** for AI-powered software development. It manages multiple projects simultaneously, orchestrates workflows, and can invoke GitHub Copilot CLI headless for automated code generation.

**NEW (2025-11-01):** The system now includes a **Dynamic Skill Management System (DSMS)** - a self-improving knowledge layer that automatically generates, updates, and manages AI skills based on task requirements and web research.

## 🏗️ Architecture Overview

### Hexagonal Architecture (Clean Architecture)

```
┌─────────────────────────────────────────────┐
│           EXTERNAL AGENTS (LLMs)            │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴─────────┐
        │   MCP SERVER       │  ← PRIMARY ADAPTER (IN)
        │   (FastMCP)        │
        └──────────┬─────────┘
                   │
   ┌───────────────┴───────────────┐
   │      APPLICATION CORE          │
   │  ┌──────────────────────────┐ │
   │  │    DOMAIN ENTITIES       │ │
   │  │  - Project, Feature      │ │
   │  │  - Workflow, Phase       │ │
   │  └──────────────────────────┘ │
   │  ┌──────────────────────────┐ │
   │  │     USE CASES            │ │
   │  │  - StartFeature          │ │
   │  │  - SubmitWork            │ │
   │  │  - ExecuteCode           │ │
   │  │  - ManageProjects        │ │
   │  └──────────────────────────┘ │
   │  ┌──────────────────────────┐ │
   │  │    PORTS (Interfaces)    │ │
   │  │  - IProjectRepository    │ │
   │  │  - IWorkflowEngine       │ │
   │  │  - ICodeExecutor         │ │
   │  └──────────────────────────┘ │
   └────────────┬──────────────────┘
                │
      ┌─────────┴────────┐
      │  ADAPTERS (OUT)  │  ← SECONDARY ADAPTERS
      └─────────┬────────┘
                │
    ┌───────────┼────────────┐
    │           │            │
┌───┴───┐  ┌───┴────┐  ┌───┴─────┐
│FS Repo│  │Copilot │  │ GitHub  │
│       │  │  CLI   │  │   MCP   │
└───────┘  └────────┘  └─────────┘
```

### Dependency Rule

**Critical**: Dependencies point INWARD ONLY
- ✅ Application → Domain
- ✅ Adapters → Application → Domain
- ❌ Domain → Adapters (NEVER!)
- ❌ Domain → Infrastructure (NEVER!)

## 📁 Project Structure

```
CDE Orchestrator MCP/
├── .cde/                           # Workflow definitions
│   ├── workflow.yml               # Phase definitions
│   ├── prompts/                   # POML templates
│   │   ├── 01_define.poml
│   │   ├── 02_decompose.poml
│   │   └── ...
│   ├── recipes/                   # Specialized agents
│   └── state.json                 # Global state
├── .vscode/
│   └── mcp.json                   # MCP server config
├── specs/                         # Spec-Kit methodology
│   ├── features/                  # Feature specifications
│   ├── tasks/                     # Task roadmaps
│   │   └── improvement-roadmap.md # 63 prioritized tasks
│   ├── design/                    # Technical designs
│   └── reviews/                   # Code reviews
├── memory/
│   └── constitution.md            # Project principles
├── src/
│   ├── server.py                  # MCP entry point (FastMCP)
│   └── cde_orchestrator/
│       ├── domain/                # 🔷 HEXAGON CORE
│       │   ├── entities.py        # Business logic (Project, Feature)
│       │   ├── ports.py           # Interface contracts
│       │   └── exceptions.py      # Domain errors
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

**No registries. No caching. No complex state.**

#### Configuration

```json
// .vscode/mcp.json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": [
        "src/server.py",
        "--scan-paths",
        "E:\\scripts-python",
        "C:\\work\\projects"
      ]
    }
  }
}
```

Scan paths provide **search roots** for name resolution only. No scanning happens unless the agent explicitly asks to resolve a name.

#### Usage Pattern

```python
from cde_orchestrator.application.project_locator import ProjectLocator

locator = ProjectLocator(scan_roots=["E:\\scripts-python"])

# Agent provides path directly (preferred)
info = locator.validate_project_path("E:\\scripts-python\\CDE")
# Returns: ProjectInfo(path=..., exists=True, has_git=True)

# OR agent provides name, we resolve it
resolved = locator.resolve_project_path(project_name="CDE")
# Returns: "E:\\scripts-python\\CDE"

# Each operation is independent - no state persists
```

#### Project Operations

All MCP tools accept optional `project_path` or `project_name`:

```python
# Agent specifies project explicitly
cde_startFeature(
    project_name="CDE",  # Resolves to E:\scripts-python\CDE
    user_prompt="Add authentication"
)

# OR uses path directly
cde_startFeature(
    project_path="E:\\scripts-python\\CDE",
    user_prompt="Add authentication"
)

# State is managed per-project in .cde/state.json
# No cross-project registries needed
```

### 3. Copilot CLI Integration

The `ICodeExecutor` port allows headless Copilot execution:

```python
# Use case: Agent needs to generate code
executor = CopilotCLIAdapter(yolo_mode=True)

result = await executor.execute_prompt(
    project_path="E:\\scripts-python\\my-project",
    prompt="Create FastAPI user authentication with JWT",
    context={"yolo": True}  # Auto-apply changes
)

# Result includes:
# - modified_files: ["src/auth.py", "src/models.py"]
# - diff: "..."
# - success: True/False
```

### 4. Workflow as Code

Everything is versioned in `.cde/workflow.yml`:

```yaml
name: "Standard Web Application Workflow"
phases:
  - id: define
    prompt_recipe: ".cde/prompts/01_define.poml"
    outputs:
      - type: "file"
        path: "specs/features/{feature_name}.md"

  - id: decompose
    inputs:
      - type: "file"
        path: "specs/features/{feature_name}.md"
    outputs:
      - type: "github_issues"
        labels: ["cde-task"]
```

### 5. Dynamic Skill Management System (DSMS) 🆕

**Core Pillar**: Self-improving knowledge layer with smart reuse (NO auto-delete).

**Revised Strategy (v2.0, 2025-11-01)**:
Every workflow execution follows the smart reuse loop:

```
1. Detect task complexity & knowledge gaps
2. Search cache for existing ephemeral skills (same domain/gaps)
3. Check staleness: Is context hash unchanged?
   - YES → REUSE (save 2-3s generation time)
   - NO  → REGENERATE (version/deps changed)
4. Execute task with skill context (reused or new)
5. Distill learnings back to persistent base skill
6. [Daily background job] Archive skills inactive > 6 months
```

**Two-Tier Skill System:**

- **Base Skills** (`.copilot/skills/base/`): Persistent, accumulative knowledge
  - Generic patterns and best practices
  - Updated via web research (monthly)
  - Version history with update notes
  - Never deleted, only grows

- **Ephemeral Skills** (`.copilot/skills/ephemeral/`): Task-specific, reusable
  - Generated on-demand for complex tasks
  - Includes context-aware code examples, known issues
  - **NEW**: Cached indefinitely with smart reuse
  - **NEW**: Context hash tracks dependencies (redis 7.2.4, fastapi 0.104, etc.)
  - **NEW**: Reused if context unchanged (generation_count increments)
  - **NEW**: Regenerated only on breaking changes
  - **NEW**: Archived after 6 months inactivity (never deleted, preserved)
  - Learnings distilled to base skill

**Smart Reuse Logic:**

```python
# Fingerprint skill's dependencies
context_hash = SHA256({
    "domain": "database",
    "tools": ["redis", "fastapi", "python"],
    "tool_versions": {"redis": "7.2.4", "redis-py": "5.0.1", ...}
})

# When preparing skill for task:
if cached_skill.context_hash == current_context_hash:
    # Dependencies unchanged - REUSE (saves time)
    cached_skill.metadata.last_used = now()
    cached_skill.metadata.generation_count += 1
    return cached_skill
else:
    # Context changed - regenerate with updated context
    new_skill = await generate_ephemeral_skill(...)
    new_skill.metadata.previous_version_id = cached_skill.skill_id
    return new_skill
```

**Example Workflow:**

```
Task 1: "Implement Redis caching" (Day 1)
  → SRD: HIGH complexity, database domain, gaps=[redis, caching]
  → Generator: Create new ephemeral skill (2.5s)
  → Store with context_hash=a1b2c3d4...
  ↓
Task 2: "Add Redis to FastAPI" (Day 15)
  → SRD: HIGH complexity, database domain, gaps=[redis, caching]
  → Manager: Found cached skill! Check staleness
  → Hash match: a1b2c3d4... == a1b2c3d4... (YES)
  → REUSE (0.1s lookup, no generation) ✅
  → Increment generation_count: 1
  ↓
Task 3: "Cache with Redis 8.0" (Day 45)
  → Manager: Found cached skill, but...
  → Hash mismatch: redis 8.0 ≠ redis 7.2 in stored hash
  → Breaking changes detected in redis 8.0
  → REGENERATE (2.5s, mark old as stale)
  → Link: new_skill.previous_version_id = old_skill.skill_id
```

**Background Job (Daily):**

```python
# Archive inactive skills (6-month threshold)
for skill in ephemeral_skills:
    if (now - skill.metadata.last_used).days > 180:
        skill.metadata.status = "archived"
        skill.metadata.archived_at = now()
        # Move to .copilot/skills/archived/
        # Preserve for audit, never delete
```

**See Full Design:**
- `specs/design/EPHEMERAL_SMART_REUSE.md` - Complete smart reuse strategy (NEW)
- `specs/design/SMART_REUSE_INTEGRATION.md` - Integration with SkillManager (NEW)
- `specs/design/EXECUTIVE_SUMMARY_V2.md` - Executive overview, v2.0 (NEW)
- `specs/design/QUICK_REFERENCE_V2.md` - Quick reference guide (NEW)
- `specs/design/dynamic-skill-system.md` - Original architecture (44 pages)
- `specs/design/dynamic-skill-system-implementation.md` - Code implementation guide

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
  - [x] ARCHITECTURE.md documentation

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

## �️ Documentation Governance (Section 6)

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

### AI Agent Governance Checklist

When asked to create or modify documentation:

**✅ DO:**
- Identify the document's purpose FIRST (feature? design? task? guide? **agent output?**)
- Place in the correct directory based on purpose
- **NEW**: Place agent-generated outputs in `/agent-docs/` subdirectories:
  - Session summaries → `agent-docs/sessions/`
  - Execution reports → `agent-docs/execution/`
  - Feedback/analysis → `agent-docs/feedback/`
  - Web research → `agent-docs/research/`
- Use templates from `specs/templates/` (session-summary.md, execution-report.md, feedback-report.md)
- Include metadata block with date, agent name, duration, status
- Check if a similar document already exists (avoid duplication)
- Link from existing indexes (e.g., `specs/README.md`, `docs/INDEX.md`, `agent-docs/README.md`)
- Follow naming conventions (lowercase, hyphens for spaces, ISO dates)
- Add document metadata (date, author/agent, status)

**✅ DO - Agent Output Examples:**
```markdown
# Session summary after onboarding work
agent-docs/sessions/session-onboarding-review-2025-01-15.md

# Execution report for workflow run
agent-docs/execution/execution-onboarding-2025-01.md

# Feedback document with recommendations
agent-docs/feedback/feedback-governance-improvements-2025-01.md

# Web research summary (auto-archived after 90 days)
agent-docs/research/research-best-practices-2025-01-10.md
```

**❌ DON'T - Agent Output Anti-Patterns:**
- Create .md files in the project root (unless in exceptions list)
- Create documents in subdirectories with inconsistent naming
- Duplicate content across multiple .md files (link instead)
- Leave new documents orphaned (must link from index/parent)
- Ignore `.markdownlintrc` rules (120-char lines, consistent formatting)
- Create documents without clear purpose/ownership

### Enforcement Mechanisms

**Pre-Commit Hook** (Automatic):
- Runs before every commit
- Validates file paths against governance rules
- Rejects commits with root .md files outside exceptions
- Command: `pre-commit run --all-files`

**Markdown Linting** (Automatic):
- Enforces formatting consistency (120-char lines, proper headings, etc)
- Configured in `.markdownlintrc`
- Integrated into pre-commit pipeline
- Command: `markdownlint-cli --config .markdownlintrc *.md`

**CI/CD Integration** (GitHub Actions):
- Runs governance checks on every PR
- Blocks merge if violations detected
- Reports specific violations and remediation steps

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

## �🎓 Learning Resources

- **Hexagonal Architecture**: https://netflixtechblog.com/ready-for-changes-with-hexagonal-architecture-b315ec967749
- **Domain-Driven Design**: Eric Evans book
- **Clean Architecture**: Robert C. Martin book
- **FastMCP**: https://github.com/jlowin/fastmcp
- **Spec-Kit**: https://github.com/github/spec-kit

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
