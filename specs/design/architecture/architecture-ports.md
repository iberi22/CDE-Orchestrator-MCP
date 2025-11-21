---
title: "CDE Orchestrator MCP - Port Interfaces"
description: "Contract definitions for all adapters in hexagonal architecture"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Orchestrator Team"
tags:
  - "architecture"
  - "ports"
  - "interfaces"
  - "contracts"
llm_summary: |
  Port interface definitions for hexagonal architecture. Includes IProjectRepository,
  IWorkflowEngine, ICodeExecutor, IAgentOrchestrator, IPromptRenderer, IStateStore.
  Adapters must implement these interfaces. Zero implementation details here.
---

# Port Interfaces

> **Part of**: [Architecture Documentation](README.md)
> **Layer**: Domain (Interfaces only)
> **Purpose**: Define contracts that adapters must implement

## Overview

Ports are **abstract interfaces** that define contracts between the application core and external systems. They contain **zero implementation** - only method signatures and documentation.

**Key Rule**: Domain and Application layers depend on ports, never on concrete adapters.

---

## IProjectRepository

Port for project persistence.

**Implementations**: `FileSystemProjectRepository`, `DatabaseProjectRepository`

```python
# src/cde_orchestrator/domain/ports.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .entities import Project, ProjectId, Feature

class IProjectRepository(ABC):
    """
    Port for project persistence.

    Responsibilities:
        - Load projects by ID or path
        - List all registered projects
        - Save project state
        - Delete projects

    Implementations: FileSystemProjectRepository, DatabaseProjectRepository
    """

    @abstractmethod
    def get_by_id(self, project_id: ProjectId) -> Optional[Project]:
        """
        Retrieve project by ID.

        Args:
            project_id: Project identifier

        Returns:
            Project entity or None if not found
        """
        pass

    @abstractmethod
    def get_by_path(self, path: str) -> Optional[Project]:
        """
        Find project by filesystem path.

        Args:
            path: Absolute path to project directory

        Returns:
            Project entity or None if not found
        """
        pass

    @abstractmethod
    def list_all(self) -> List[Project]:
        """
        Get all registered projects.

        Returns:
            List of Project entities (may be empty)
        """
        pass

    @abstractmethod
    def save(self, project: Project) -> None:
        """
        Persist project state.

        Args:
            project: Project entity to save

        Raises:
            IOError: If persistence fails
        """
        pass

    @abstractmethod
    def delete(self, project_id: ProjectId) -> None:
        """
        Remove project from registry.

        Args:
            project_id: Project to delete

        Note: Does not delete project files, only removes from registry
        """
        pass
```

---

## IWorkflowEngine

Port for workflow execution.

**Implementations**: `YAMLWorkflowEngine`, `PythonWorkflowEngine`

```python
class IWorkflowEngine(ABC):
    """
    Port for workflow execution.

    Responsibilities:
        - Load workflow definitions
        - Determine phase sequencing
        - Validate phase results

    Implementations: YAMLWorkflowEngine, PythonWorkflowEngine
    """

    @abstractmethod
    def load_for_project(self, project: Project) -> 'Workflow':
        """
        Load workflow definition for given project.

        Args:
            project: Project entity

        Returns:
            Workflow instance configured for this project

        Raises:
            WorkflowNotFoundError: If no workflow defined
        """
        pass

    @abstractmethod
    def get_next_phase(self, current_phase: str) -> Optional[str]:
        """
        Determine next phase in workflow sequence.

        Args:
            current_phase: Current phase ID (e.g., "define")

        Returns:
            Next phase ID or None if workflow complete
        """
        pass

    @abstractmethod
    def validate_results(self, phase: str, results: Dict[str, Any]) -> bool:
        """
        Check if results satisfy phase requirements.

        Args:
            phase: Phase ID
            results: Phase outputs to validate

        Returns:
            True if valid, False otherwise
        """
        pass
```

---

## ICodeExecutor

Port for executing code generation agents.

**Implementations**: `CopilotCLIAdapter`, `LocalLLMAdapter`

```python
class ICodeExecutor(ABC):
    """
    Port for executing code generation agents.

    Responsibilities:
        - Execute code generation prompts
        - Return execution results
        - Support YOLO mode (auto-apply)

    Implementations: CopilotCLIAdapter, LocalLLMAdapter
    """

    @abstractmethod
    async def execute_prompt(
        self,
        project_path: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> 'ExecutionResult':
        """
        Execute code generation with given prompt.

        Args:
            project_path: Absolute path to project directory
            prompt: Natural language instruction
            context: Additional context (files, specs, yolo flag, etc)

        Returns:
            ExecutionResult with generated code and metadata

        Raises:
            ExecutionError: If code generation fails
        """
        pass

    @abstractmethod
    def supports_yolo_mode(self) -> bool:
        """
        Check if executor supports auto-apply without confirmation.

        Returns:
            True if YOLO mode supported
        """
        pass
```

---

## IAgentOrchestrator

Port for orchestrating external agents/tools.

**Implementations**: `MCPClientAdapter`, `DirectAPIAdapter`

```python
class IAgentOrchestrator(ABC):
    """
    Port for orchestrating external agents/tools.

    Responsibilities:
        - Call external MCP servers (GitHub, etc)
        - Execute commands on external agents
        - Check service availability

    Implementations: MCPClientAdapter, DirectAPIAdapter
    """

    @abstractmethod
    async def call_github(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Execute GitHub operation via MCP or API.

        Args:
            operation: Operation name (e.g., "create_issue")
            params: Operation parameters

        Returns:
            Operation result

        Raises:
            ServiceUnavailableError: If GitHub service unreachable
        """
        pass

    @abstractmethod
    async def call_copilot(self, command: str, args: Dict[str, Any]) -> Any:
        """
        Execute Copilot CLI command.

        Args:
            command: Command name
            args: Command arguments

        Returns:
            Command output
        """
        pass

    @abstractmethod
    def is_service_available(self, service_name: str) -> bool:
        """
        Check if external service is accessible.

        Args:
            service_name: Service identifier (e.g., "github", "copilot")

        Returns:
            True if service available
        """
        pass
```

---

## IPromptRenderer

Port for rendering POML templates.

**Implementations**: `POMLRenderer`, `JinjaRenderer`

```python
class IPromptRenderer(ABC):
    """
    Port for rendering POML templates.

    Responsibilities:
        - Render prompt templates with context
        - Validate template syntax
        - Sanitize context variables

    Implementations: POMLRenderer, JinjaRenderer
    """

    @abstractmethod
    def render(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        Render prompt template with given context.

        Args:
            template_path: Path to template file
            context: Variables to inject into template

        Returns:
            Rendered prompt string

        Raises:
            TemplateNotFoundError: If template doesn't exist
            RenderError: If rendering fails
        """
        pass

    @abstractmethod
    def validate_template(self, template_path: str) -> bool:
        """
        Check if template is well-formed.

        Args:
            template_path: Path to template file

        Returns:
            True if valid, False otherwise
        """
        pass
```

---

## IStateStore

Port for persisting application state.

**Implementations**: `JSONStateStore`, `DatabaseStateStore`

```python
class IStateStore(ABC):
    """
    Port for persisting application state.

    Responsibilities:
        - Store/retrieve arbitrary key-value data
        - Support nested structures
        - Handle concurrent access

    Implementations: JSONStateStore, DatabaseStateStore
    """

    @abstractmethod
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load state by key.

        Args:
            key: State identifier

        Returns:
            State data or None if not found
        """
        pass

    @abstractmethod
    def save(self, key: str, data: Dict[str, Any]) -> None:
        """
        Persist state.

        Args:
            key: State identifier
            data: State to save

        Raises:
            IOError: If persistence fails
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Remove state.

        Args:
            key: State identifier
        """
        pass
```

---

## Port Design Principles

### 1. Interface Segregation

Keep interfaces focused:

```python
# ✅ GOOD: Focused interface
class IProjectRepository(ABC):
    def get_by_id(self, project_id: ProjectId) -> Optional[Project]: ...
    def save(self, project: Project) -> None: ...

# ❌ BAD: God interface
class IRepository(ABC):
    def get_project(self, id): ...
    def get_feature(self, id): ...
    def get_workflow(self, id): ...
    def get_user(self, id): ...  # Too many responsibilities
```

### 2. Explicit Contracts

Document inputs, outputs, errors:

```python
# ✅ GOOD: Clear contract
@abstractmethod
def execute_prompt(
    self,
    project_path: str,  # What: absolute path
    prompt: str,        # What: natural language
    context: Dict[str, Any]  # What: additional data
) -> 'ExecutionResult':  # Returns: structured result
    """
    Execute code generation.

    Raises:
        ExecutionError: If generation fails
        TimeoutError: If execution exceeds limit
    """
    pass
```

### 3. Technology Agnostic

Ports should NOT mention specific technologies:

```python
# ❌ BAD: Technology-specific
class IGitHubRepository(ABC):  # Tied to GitHub
    def create_github_issue(self): ...

# ✅ GOOD: Technology-agnostic
class IIssueTracker(ABC):  # Could be GitHub, Jira, etc
    def create_issue(self): ...
```

---

## Testing Ports

Ports enable easy mocking:

```python
# Mock implementation for testing
class MockProjectRepository(IProjectRepository):
    def __init__(self):
        self.projects = {}

    def get_by_id(self, project_id: ProjectId) -> Optional[Project]:
        return self.projects.get(project_id.value)

    def save(self, project: Project) -> None:
        self.projects[project.id.value] = project

    # ... other methods

# Use in tests
def test_start_feature_use_case():
    mock_repo = MockProjectRepository()
    use_case = StartFeatureUseCase(mock_repo, ...)

    result = use_case.execute("test-id", "add login")

    assert result["status"] == "success"
```

---

## Next Steps

- **Implement Adapters**: See [Adapters Documentation](./architecture-adapters.md)
- **Wire with DI**: See [DI Container](architecture-di-container.md)
- **Use in Use Cases**: See [Use Cases](./architecture-use-cases.md)

---

*This document is part of the modular architecture documentation. See [README](README.md) for full navigation.*
