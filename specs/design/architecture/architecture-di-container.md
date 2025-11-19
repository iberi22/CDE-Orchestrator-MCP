---
title: "CDE Orchestrator MCP - Dependency Injection Container"
description: "DI container for wiring hexagonal architecture components"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Orchestrator Team"
tags:
  - "architecture"
  - "dependency-injection"
  - "wiring"
  - "infrastructure"
llm_summary: |
  Dependency injection container for hexagonal architecture. Wires domain entities,
  application use cases, and adapter implementations. Provides factory methods
  for creating configured use cases.
---

# Dependency Injection Container

> **Part of**: [Architecture Documentation](README.md)
> **Layer**: Infrastructure
> **Purpose**: Wire together domain, application, and adapters

## Overview

The `DIContainer` is responsible for:

- Instantiating adapters with configuration
- Wiring adapters to use cases
- Providing factory methods for use cases
- Managing singleton instances (if needed)

**Benefits**:

- **Testability**: Easy to inject mocks
- **Flexibility**: Swap implementations without code changes
- **Centralization**: One place to configure dependencies

---

## Implementation

```python
# src/cde_orchestrator/infrastructure/di_container.py

from pathlib import Path
from typing import Optional
from ..domain.ports import (
    IProjectRepository,
    IWorkflowEngine,
    ICodeExecutor,
    IPromptRenderer,
    IAgentOrchestrator
)
from ..adapters.filesystem_project_repository import FileSystemProjectRepository
from ..adapters.copilot_cli_adapter import CopilotCLIAdapter
from ..application.use_cases import (
    StartFeatureUseCase,
    SubmitWorkUseCase,
    ManageProjectUseCase,
    ExecuteCodeUseCase
)

class DIContainer:
    """
    Dependency Injection Container for Hexagonal Architecture.

    Wires together:
        - Domain (entities)
        - Application (use cases)
        - Adapters (implementations)

    Usage:
        container = DIContainer.create_default()
        start_feature = container.get_start_feature_use_case()
        result = start_feature.execute(project_id, prompt)
    """

    def __init__(
        self,
        project_repo: IProjectRepository,
        workflow_engine: IWorkflowEngine,
        code_executor: ICodeExecutor,
        prompt_renderer: IPromptRenderer,
        agent_orchestrator: IAgentOrchestrator
    ):
        self._project_repo = project_repo
        self._workflow_engine = workflow_engine
        self._code_executor = code_executor
        self._prompt_renderer = prompt_renderer
        self._agent_orchestrator = agent_orchestrator

    @classmethod
    def create_default(cls, registry_path: Optional[Path] = None) -> 'DIContainer':
        """
        Factory method: Create container with default implementations.

        For testing, pass custom implementations instead.

        Args:
            registry_path: Path to project registry (default: ~/.cde_registry)

        Returns:
            Configured DIContainer
        """
        if registry_path is None:
            registry_path = Path.home() / ".cde_registry"

        # Wire adapters
        project_repo = FileSystemProjectRepository(registry_path)

        # Import other adapters
        from ..adapters.yaml_workflow_engine import YAMLWorkflowEngine
        from ..adapters.poml_prompt_renderer import POMLPromptRenderer
        from ..adapters.mcp_client_adapter import MCPClientAdapter

        workflow_engine = YAMLWorkflowEngine(Path(".cde/workflow.yml"))
        code_executor = CopilotCLIAdapter(yolo_default=False)
        prompt_renderer = POMLPromptRenderer(Path(".cde/prompts"))
        agent_orchestrator = MCPClientAdapter()

        return cls(
            project_repo=project_repo,
            workflow_engine=workflow_engine,
            code_executor=code_executor,
            prompt_renderer=prompt_renderer,
            agent_orchestrator=agent_orchestrator
        )

    @classmethod
    def create_for_testing(cls) -> 'DIContainer':
        """
        Factory method: Create container with mock implementations.

        Returns:
            DIContainer with mocks (no I/O)
        """
        from ..tests.mocks import (
            MockProjectRepository,
            MockWorkflowEngine,
            MockCodeExecutor,
            MockPromptRenderer,
            MockAgentOrchestrator
        )

        return cls(
            project_repo=MockProjectRepository(),
            workflow_engine=MockWorkflowEngine(),
            code_executor=MockCodeExecutor(),
            prompt_renderer=MockPromptRenderer(),
            agent_orchestrator=MockAgentOrchestrator()
        )

    # Use case factories

    def get_start_feature_use_case(self) -> StartFeatureUseCase:
        """Get use case for starting features."""
        return StartFeatureUseCase(
            self._project_repo,
            self._workflow_engine,
            self._prompt_renderer
        )

    def get_submit_work_use_case(self) -> SubmitWorkUseCase:
        """Get use case for submitting work."""
        return SubmitWorkUseCase(
            self._project_repo,
            self._workflow_engine,
            self._prompt_renderer
        )

    def get_manage_project_use_case(self) -> ManageProjectUseCase:
        """Get use case for project management."""
        return ManageProjectUseCase(self._project_repo)

    def get_execute_code_use_case(self) -> ExecuteCodeUseCase:
        """Get use case for code execution."""
        return ExecuteCodeUseCase(
            self._project_repo,
            self._code_executor
        )

    # Direct access for advanced usage

    @property
    def project_repo(self) -> IProjectRepository:
        """Direct access to project repository."""
        return self._project_repo

    @property
    def code_executor(self) -> ICodeExecutor:
        """Direct access to code executor."""
        return self._code_executor

    @property
    def workflow_engine(self) -> IWorkflowEngine:
        """Direct access to workflow engine."""
        return self._workflow_engine
```

---

## Usage in MCP Server

```python
# src/server.py

from fastmcp import FastMCP
from cde_orchestrator.infrastructure.di_container import DIContainer

# Initialize container
container = DIContainer.create_default()

# Create MCP app
app = FastMCP("CDE Orchestrator")

@app.tool()
def cde_startFeature(project_id: str, user_prompt: str) -> str:
    """Start new feature in project."""
    use_case = container.get_start_feature_use_case()
    result = use_case.execute(project_id, user_prompt)
    return json.dumps(result)

@app.tool()
def cde_submitWork(
    project_id: str,
    feature_id: str,
    phase_id: str,
    results: dict
) -> str:
    """Submit completed work."""
    use_case = container.get_submit_work_use_case()
    result = use_case.execute(project_id, feature_id, phase_id, results)
    return json.dumps(result)
```

---

## Configuration Management

For environment-specific configuration:

```python
# src/cde_orchestrator/infrastructure/config.py

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class Config:
    """Application configuration."""
    registry_path: Path
    workflow_file: Path
    prompts_dir: Path
    yolo_default: bool
    copilot_enabled: bool

    @classmethod
    def from_env(cls) -> 'Config':
        """Load from environment variables."""
        import os
        return cls(
            registry_path=Path(os.getenv("CDE_REGISTRY", "~/.cde_registry")),
            workflow_file=Path(os.getenv("CDE_WORKFLOW", ".cde/workflow.yml")),
            prompts_dir=Path(os.getenv("CDE_PROMPTS", ".cde/prompts")),
            yolo_default=os.getenv("CDE_YOLO", "false").lower() == "true",
            copilot_enabled=os.getenv("CDE_COPILOT", "true").lower() == "true"
        )

# Updated DIContainer
class DIContainer:
    @classmethod
    def create_from_config(cls, config: Config) -> 'DIContainer':
        """Create container from configuration."""
        project_repo = FileSystemProjectRepository(config.registry_path)
        workflow_engine = YAMLWorkflowEngine(config.workflow_file)
        code_executor = CopilotCLIAdapter(yolo_default=config.yolo_default)
        prompt_renderer = POMLPromptRenderer(config.prompts_dir)
        agent_orchestrator = MCPClientAdapter()

        return cls(
            project_repo=project_repo,
            workflow_engine=workflow_engine,
            code_executor=code_executor,
            prompt_renderer=prompt_renderer,
            agent_orchestrator=agent_orchestrator
        )
```

---

## Testing with DIContainer

```python
# tests/test_use_cases.py

def test_start_feature():
    # Arrange: Create container with mocks
    container = DIContainer.create_for_testing()
    use_case = container.get_start_feature_use_case()

    # Act
    result = use_case.execute("test-proj", "Add login")

    # Assert
    assert result["status"] == "success"
    assert "feature_id" in result
```

---

## Advanced: Scoped Lifecycles

For more complex scenarios (singletons, scoped instances):

```python
class DIContainer:
    def __init__(self, ...):
        # ...
        self._use_case_cache = {}

    def get_start_feature_use_case(self) -> StartFeatureUseCase:
        """Get cached use case (singleton)."""
        if "start_feature" not in self._use_case_cache:
            self._use_case_cache["start_feature"] = StartFeatureUseCase(
                self._project_repo,
                self._workflow_engine,
                self._prompt_renderer
            )
        return self._use_case_cache["start_feature"]
```

---

## Next Steps

- **Understand Ports**: See [Ports Documentation](architecture-ports.md)
- **Review Use Cases**: See [Use Cases](architecture-use-cases.md)
- **Learn Adapters**: See [Adapters](architecture-adapters.md)

---

*This document is part of the modular architecture documentation. See [README](README.md) for full navigation.*
