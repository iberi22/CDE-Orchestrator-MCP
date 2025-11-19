---
title: "CDE Orchestrator MCP - Architecture Overview"
description: "Executive summary, core philosophy, and fundamental principles of hexagonal architecture"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Orchestrator Team"
tags:
  - "architecture"
  - "hexagonal"
  - "principles"
  - "overview"
llm_summary: |
  High-level overview of CDE Orchestrator hexagonal architecture. Covers core philosophy
  (Agent Knows, CDE Executes), dependency rules, LLM-first design, and bidirectional MCP.
  Read this first to understand system design principles.
---

# CDE Orchestrator MCP - Architecture Overview

> **Part of**: [Architecture Documentation](README.md)
> **Target Audience**: Large Language Models, AI Coding Agents
> **Design Philosophy**: Stateless, Simple, LLM-Driven
> **Scale Target**: Unlimited projects (agent knows context)

## Executive Summary

CDE Orchestrator follows **Hexagonal Architecture (Ports & Adapters)** with a radical simplification:

### Core Philosophy: **Agent Knows, CDE Executes**

- **LLM has context**: Agent knows project names, locations, what needs to be done
- **CDE validates & executes**: Just check project exists and run workflows
- **Stateless**: No registries, no caching, no complex state management
- **Simple**: Each operation independent, minimal dependencies

### What This Enables

- **Multi-project support** WITHOUT complexity (agent provides project path/name)
- **Bidirectional MCP** (in/out) for agent composition
- **Copilot CLI integration** for headless code generation
- **Zero state** between business logic and infrastructure

### High-Level Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL AGENTS                          │
│         (Claude, GPT-4, Copilot, Custom LLMs)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │   PRIMARY ADAPTER (IN)      │
        │      MCP Server             │
        │  (FastMCP Implementation)   │
        └──────────────┬──────────────┘
                       │
   ┌───────────────────┴───────────────────┐
   │         APPLICATION CORE               │
   │                                        │
   │  ┌──────────────────────────────┐     │
   │  │      DOMAIN LAYER            │     │
   │  │  - Project                   │     │
   │  │  - Feature                   │     │
   │  │  - Workflow                  │     │
   │  │  - Task                      │     │
   │  │  - CodeArtifact              │     │
   │  └──────────────────────────────┘     │
   │                                        │
   │  ┌──────────────────────────────┐     │
   │  │   USE CASES (Application)    │     │
   │  │  - StartFeatureUseCase       │     │
   │  │  - SubmitWorkUseCase         │     │
   │  │  - ManageProjectUseCase      │     │
   │  │  - ExecuteCodeUseCase        │     │
   │  │  - OnboardProjectUseCase     │     │
   │  └──────────────────────────────┘     │
   │                                        │
   │  ┌──────────────────────────────┐     │
   │  │    PORTS (Interfaces)        │     │
   │  │  - IProjectRepository        │     │
   │  │  - IWorkflowEngine           │     │
   │  │  - ICodeExecutor             │     │
   │  │  - IAgentOrchestrator        │     │
   │  │  - IServiceConnector         │     │
   │  │  - IPromptRenderer           │     │
   │  └──────────────────────────────┘     │
   └────────────┬───────────┬───────────────┘
                │           │
      ┌─────────┴───┐   ┌───┴──────────┐
      │  SECONDARY  │   │  SECONDARY   │
      │  ADAPTERS   │   │  ADAPTERS    │
      │   (OUT)     │   │   (OUT)      │
      └─────────────┘   └──────────────┘
           │                   │
    ┌──────┴─────┐      ┌──────┴────────┐
    │ FileSystem │      │ Copilot CLI   │
    │  Adapter   │      │   Adapter     │
    └────────────┘      └───────────────┘
           │                   │
    ┌──────┴─────┐      ┌──────┴────────┐
    │   GitHub   │      │   External    │
    │   Adapter  │      │  MCP Servers  │
    └────────────┘      └───────────────┘
```

---

## Core Principles

### 1. LLM-First Design

Every interface, model, and function is designed for LLM consumption:

```python
# ❌ BAD: Implicit, human-oriented
def process(data):
    return do_something(data)

# ✅ GOOD: Explicit, machine-readable
class ProcessDataUseCase:
    """
    Process incoming data according to CDE workflow rules.

    Contract:
        Input: Dict[str, Any] with keys: project_id, phase, artifacts
        Output: ProcessResult with status, next_phase, generated_artifacts
        Raises: ValidationError if input schema invalid

    Example:
        >>> use_case = ProcessDataUseCase(repo, engine)
        >>> result = use_case.execute({
        ...     "project_id": "abc-123",
        ...     "phase": "define",
        ...     "artifacts": {"spec": "content"}
        ... })
        >>> assert result.status == "success"
    """
    def execute(self, input_data: Dict[str, Any]) -> ProcessResult:
        ...
```

**Key Aspects:**

- **Explicit contracts**: Input/output schemas documented
- **Machine-readable**: Types, examples, error cases clear
- **Self-documenting**: Docstrings explain behavior
- **Testable**: Examples double as test cases

### 2. Dependency Rule

Dependencies point **inward only**:

- Domain knows NOTHING about adapters
- Use cases depend only on port interfaces
- Adapters depend on use cases and external libraries

**Visualization:**

```text
Allowed:
  Adapters → Application → Domain ✅
  Adapters → Ports ✅
  Application → Domain ✅
  Application → Ports ✅

Forbidden:
  Domain → Adapters ❌
  Domain → Infrastructure ❌
  Ports → Adapters ❌
```

**Example:**

```python
# ✅ CORRECT: Domain entity with NO infrastructure imports
class Project:
    def start_feature(self, prompt: str) -> Feature:
        if self.status != ProjectStatus.ACTIVE:
            raise ValueError("Project must be active")
        return Feature.create(self.id, prompt)

# ❌ WRONG: Domain importing adapter
from ..adapters.filesystem import FileSystem  # NO!

class Project:
    def save(self):
        FileSystem().write(self)  # DOMAIN SHOULD NOT KNOW FILESYSTEM!
```

### 3. Multi-Project Isolation

Each project maintains isolated state:

```python
# Project context is injected, never global
class StartFeatureUseCase:
    def __init__(
        self,
        project_repo: IProjectRepository,
        workflow_engine: IWorkflowEngine
    ):
        self.projects = project_repo
        self.workflows = workflow_engine

    def execute(self, project_id: str, prompt: str) -> FeatureResult:
        project = self.projects.get_by_id(project_id)
        workflow = self.workflows.load_for_project(project)
        # Execute in isolated context
        return workflow.start_feature(prompt)
```

**Benefits:**

- **No global state**: Each project operation independent
- **Concurrent safe**: Multiple projects can be worked on simultaneously
- **Testable**: Easy to mock different project configurations
- **Scalable**: No shared state bottlenecks

### 4. Bidirectional MCP

MCP acts as both:

- **Primary Adapter (IN)**: Receives commands from external agents
- **Secondary Adapter (OUT)**: Orchestrates other MCP servers via clients

```python
class MCPServerAdapter(IPrimaryAdapter):
    """Exposes use cases as MCP tools."""

    def expose_tool(self, use_case: UseCase):
        @app.tool()
        def tool_function(**kwargs):
            return use_case.execute(kwargs)

class MCPClientAdapter(IAgentOrchestrator):
    """Calls external MCP servers (GitHub, etc)."""

    async def execute_on_copilot(self, command: CodegenCommand) -> CodegenResult:
        # Launches Copilot CLI headless
        return await self.copilot_client.run(command)
```

**Why Bidirectional?**

- **Inbound**: Agents call CDE to orchestrate workflows
- **Outbound**: CDE calls Copilot CLI for code generation
- **Composable**: CDE can chain multiple MCP servers

---

## Design Patterns

### Stateless Operations

Every MCP tool call is stateless from the agent's perspective:

```python
# Agent doesn't need to remember project ID across calls
cde_startFeature(project_path="E:\\MyProject", prompt="Add auth")
# Later (in different session)...
cde_submitWork(project_path="E:\\MyProject", phase="define", results={...})
```

CDE loads state from `.cde/state.json` each time. Agent just provides context.

### Port-Adapter Pattern

```python
# Port (interface) - defined in domain
class IProjectRepository(ABC):
    @abstractmethod
    def get_by_id(self, project_id: str) -> Project:
        pass

    @abstractmethod
    def save(self, project: Project) -> None:
        pass

# Adapter (implementation) - in infrastructure
class FileSystemProjectRepository(IProjectRepository):
    def get_by_id(self, project_id: str) -> Project:
        path = Path(f".cde/projects/{project_id}/state.json")
        data = json.loads(path.read_text())
        return Project.from_dict(data)

    def save(self, project: Project) -> None:
        path = Path(f".cde/projects/{project.id}/state.json")
        path.write_text(json.dumps(project.to_dict()))
```

**Benefits:**

- Swap implementations without changing business logic
- Test with in-memory repository
- Support multiple storage backends

---

## Layer Responsibilities

### Domain Layer (src/cde_orchestrator/domain/)

**Purpose**: Business logic, entities, value objects

**Rules:**

- NO external dependencies (no imports outside domain/)
- Pure Python dataclasses and functions
- Business invariants enforced

**Examples**: `Project`, `Feature`, `Workflow` entities

**See**: [Domain Layer Documentation](architecture-domain-layer.md)

### Application Layer (src/cde_orchestrator/application/)

**Purpose**: Use cases, orchestration logic

**Rules:**

- Depends on domain + port interfaces
- NO direct adapter imports
- Coordinates multiple entities

**Examples**: `StartFeatureUseCase`, `SubmitWorkUseCase`

**See**: [Use Cases Documentation](architecture-use-cases.md)

### Ports Layer (src/cde_orchestrator/domain/ports.py)

**Purpose**: Interface definitions

**Rules:**

- Abstract base classes (ABC)
- NO implementations
- Contracts only

**Examples**: `IProjectRepository`, `IWorkflowEngine`

**See**: [Ports Documentation](architecture-ports.md)

### Adapters Layer (src/cde_orchestrator/adapters/)

**Purpose**: Infrastructure implementations

**Rules:**

- Implements port interfaces
- Contains I/O, network, filesystem code
- Can import external libraries

**Examples**: `FileSystemProjectRepository`, `CopilotCLIAdapter`

**See**: [Adapters Documentation](architecture-adapters.md)

---

## Key Benefits

### For LLMs

- **Predictable**: Every component follows same pattern
- **Discoverable**: Interfaces define all capabilities
- **Testable**: Mocking ports makes testing trivial
- **Understandable**: Clear separation of concerns

### For Developers

- **Maintainable**: Change adapters without touching business logic
- **Flexible**: Add new storage/execution backends easily
- **Testable**: Unit test domain without I/O
- **Scalable**: Stateless design supports unlimited projects

### For Multi-Project Support

- **Simple**: No registries, no caching, no complex state
- **Agent-driven**: LLM provides project context
- **Validated**: CDE just checks project exists
- **Isolated**: Each project independent

---

## Next Steps

- **Understand Entities**: Read [Domain Layer](architecture-domain-layer.md)
- **Learn Interfaces**: Review [Ports](architecture-ports.md)
- **See Orchestration**: Check [Use Cases](architecture-use-cases.md)
- **Implementation Details**: Explore [Adapters](architecture-adapters.md)

---

*This document is part of the modular architecture documentation. See [README](README.md) for full navigation.*
