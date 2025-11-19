---
title: "CDE Orchestrator MCP - Use Cases (Application Layer)"
description: "Orchestration logic for feature lifecycle, project management, and code execution"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Orchestrator Team"
tags:
  - "architecture"
  - "use-cases"
  - "application-layer"
  - "orchestration"
llm_summary: |
  Application layer use cases for CDE orchestrator. Includes StartFeatureUseCase,
  SubmitWorkUseCase, ManageProjectUseCase, ExecuteCodeUseCase. Orchestrates domain
  entities and ports. NO business rules (those live in domain).
---

# Use Cases (Application Layer)

> **Part of**: [Architecture Documentation](README.md)
> **Layer**: Application
> **Purpose**: Orchestrate domain entities and coordinate adapters

## Overview

Use cases contain **orchestration logic** - they coordinate domain entities, call ports, and handle workflows. They do NOT contain business rules (those live in domain entities).

**Key Responsibilities**:

- Coordinate multiple entities
- Call adapter ports
- Handle workflow sequencing
- Return structured results

---

## StartFeatureUseCase

Start a new feature in a project.

**Flow**:

1. Validate project exists and is active
2. Create feature entity (business logic in domain)
3. Load initial workflow phase
4. Render phase prompt
5. Return prompt to agent

```python
# src/cde_orchestrator/application/use_cases.py

from typing import Dict, Any
from ..domain.ports import IProjectRepository, IWorkflowEngine, IPromptRenderer
from ..domain.entities import Project, Feature, ProjectId

class StartFeatureUseCase:
    """
    Use case: Start a new feature in a project.

    Responsibilities:
        - Validate project exists
        - Delegate feature creation to domain
        - Load workflow and render prompt
    """

    def __init__(
        self,
        project_repo: IProjectRepository,
        workflow_engine: IWorkflowEngine,
        prompt_renderer: IPromptRenderer
    ):
        self.projects = project_repo
        self.workflows = workflow_engine
        self.prompts = prompt_renderer

    def execute(self, project_id: str, user_prompt: str) -> Dict[str, Any]:
        """
        Execute use case.

        Input Schema:
            {
                "project_id": str,  # Project identifier
                "user_prompt": str  # Feature description from user
            }

        Output Schema:
            {
                "status": "success" | "error",
                "feature_id": str,
                "phase": str,
                "prompt": str,
                "error": str  # Only if status=error
            }

        Example:
            >>> use_case = StartFeatureUseCase(repo, engine, renderer)
            >>> result = use_case.execute("proj-123", "Add user login")
            >>> assert result["status"] == "success"
            >>> assert "feature_id" in result
        """
        # 1. Load project
        project = self.projects.get_by_id(ProjectId(project_id))
        if not project:
            return {"status": "error", "error": f"Project {project_id} not found"}

        # 2. Create feature (business logic in entity)
        try:
            feature = project.start_feature(user_prompt)
        except ValueError as e:
            return {"status": "error", "error": str(e)}

        # 3. Save updated project
        self.projects.save(project)

        # 4. Load workflow
        workflow = self.workflows.load_for_project(project)
        initial_phase = workflow.get_initial_phase()

        # 5. Render prompt
        context = {
            "USER_PROMPT": user_prompt,
            "PROJECT_NAME": project.name,
            "FEATURE_ID": feature.id
        }
        prompt = self.prompts.render(initial_phase.prompt_recipe, context)

        return {
            "status": "success",
            "feature_id": feature.id,
            "phase": initial_phase.id,
            "prompt": prompt
        }
```

---

## SubmitWorkUseCase

Submit completed work and advance to next phase.

**Flow**:

1. Load feature
2. Validate phase matches current state
3. Process results (save artifacts)
4. Advance to next phase (business logic in domain)
5. Render next prompt or mark complete

```python
class SubmitWorkUseCase:
    """
    Use case: Submit completed work and advance to next phase.

    Responsibilities:
        - Validate current phase
        - Save phase artifacts
        - Advance feature (delegates to domain)
        - Prepare next phase prompt
    """

    def __init__(
        self,
        project_repo: IProjectRepository,
        workflow_engine: IWorkflowEngine,
        prompt_renderer: IPromptRenderer
    ):
        self.projects = project_repo
        self.workflows = workflow_engine
        self.prompts = prompt_renderer

    def execute(
        self,
        project_id: str,
        feature_id: str,
        phase_id: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit work results.

        Input Schema:
            {
                "project_id": str,
                "feature_id": str,
                "phase_id": str,
                "results": {
                    "specification": str,  # For define phase
                    "task_breakdown": str,  # For decompose phase
                    # ... phase-specific keys
                }
            }

        Output Schema:
            {
                "status": "success" | "completed" | "error",
                "phase": str,  # Next phase ID (if not completed)
                "prompt": str,  # Next phase prompt (if not completed)
                "progress": Dict[str, Any]
            }

        Example:
            >>> use_case = SubmitWorkUseCase(repo, engine, renderer)
            >>> result = use_case.execute(
            ...     "proj-123",
            ...     "feat-456",
            ...     "define",
            ...     {"specification": "# Feature Spec..."}
            ... )
            >>> assert result["status"] == "success"
            >>> assert result["phase"] == "decompose"
        """
        # 1. Load project and feature
        project = self.projects.get_by_id(ProjectId(project_id))
        if not project:
            return {"status": "error", "error": "Project not found"}

        feature = next((f for f in project.features if f.id == feature_id), None)
        if not feature:
            return {"status": "error", "error": "Feature not found"}

        # 2. Validate phase
        if feature.current_phase != phase_id:
            return {
                "status": "error",
                "error": f"Phase mismatch. Expected {feature.current_phase}, got {phase_id}"
            }

        # 3. Load workflow
        workflow = self.workflows.load_for_project(project)

        # 4. Validate results
        if not self.workflows.validate_results(phase_id, results):
            return {"status": "error", "error": "Results validation failed"}

        # 5. Advance phase (business logic in entity)
        next_phase_id = workflow.get_next_phase(phase_id)

        if next_phase_id is None:
            # Workflow complete
            feature.complete()
            self.projects.save(project)
            return {
                "status": "completed",
                "feature_id": feature.id,
                "message": "Feature completed successfully"
            }

        # Advance to next phase
        feature.advance_phase(next_phase_id, results)
        self.projects.save(project)

        # 6. Render next prompt
        next_phase = workflow.get_phase(next_phase_id)
        context = {
            "USER_PROMPT": feature.prompt,
            "PROJECT_NAME": project.name,
            "FEATURE_ID": feature.id,
            **results  # Include previous results as context
        }
        prompt = self.prompts.render(next_phase.prompt_recipe, context)

        return {
            "status": "success",
            "phase": next_phase_id,
            "prompt": prompt,
            "progress": {
                "completed_phases": len(feature.artifacts),
                "current_phase": next_phase_id
            }
        }
```

---

## ManageProjectUseCase

Register, update, or remove projects.

**Operations**: `register`, `update`, `archive`, `delete`, `list`

```python
class ManageProjectUseCase:
    """
    Use case: Register, update, or remove projects.

    Responsibilities:
        - Register new projects
        - List all projects
        - Archive/delete projects
    """

    def __init__(self, project_repo: IProjectRepository):
        self.projects = project_repo

    def register_project(self, path: str, name: str) -> Dict[str, Any]:
        """
        Register new project for CDE management.

        Input:
            {
                "path": "/absolute/path/to/project",
                "name": "My Project"
            }

        Output:
            {
                "status": "success" | "error",
                "project_id": "generated-uuid",
                "message": "Project registered"
            }

        Example:
            >>> use_case = ManageProjectUseCase(repo)
            >>> result = use_case.register_project("/tmp/myproject", "My Project")
            >>> assert result["status"] == "success"
        """
        # Check if already exists
        existing = self.projects.get_by_path(path)
        if existing:
            return {"status": "error", "error": "Project already registered"}

        # Create new project entity
        import uuid
        from datetime import datetime
        from ..domain.entities import Project, ProjectId, ProjectStatus

        project = Project(
            id=ProjectId(str(uuid.uuid4())),
            name=name,
            path=path,
            status=ProjectStatus.ONBOARDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            features=[],
            metadata={}
        )

        self.projects.save(project)

        return {
            "status": "success",
            "project_id": project.id.value,
            "message": f"Project '{name}' registered"
        }

    def list_all_projects(self) -> Dict[str, Any]:
        """
        List all managed projects.

        Output:
            {
                "status": "success",
                "count": int,
                "projects": [
                    {
                        "id": str,
                        "name": str,
                        "path": str,
                        "status": str,
                        "feature_count": int
                    },
                    ...
                ]
            }
        """
        projects = self.projects.list_all()
        return {
            "status": "success",
            "count": len(projects),
            "projects": [
                {
                    "id": p.id.value,
                    "name": p.name,
                    "path": p.path,
                    "status": p.status.value,
                    "feature_count": len(p.features)
                }
                for p in projects
            ]
        }
```

---

## ExecuteCodeUseCase

Execute code generation via Copilot CLI or other executor.

```python
class ExecuteCodeUseCase:
    """
    Use case: Execute code generation via Copilot CLI or other executor.

    Responsibilities:
        - Validate project state
        - Delegate to code executor
        - Handle execution results
    """

    def __init__(
        self,
        project_repo: IProjectRepository,
        code_executor: ICodeExecutor
    ):
        self.projects = project_repo
        self.executor = code_executor

    async def execute(
        self,
        project_id: str,
        prompt: str,
        yolo_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Execute code generation.

        Input:
            {
                "project_id": str,
                "prompt": str,
                "yolo_mode": bool  # Auto-apply without confirmation
            }

        Output:
            {
                "status": "success" | "error",
                "files_changed": List[str],
                "diff": str,
                "execution_log": str
            }

        Example:
            >>> use_case = ExecuteCodeUseCase(repo, executor)
            >>> result = await use_case.execute(
            ...     "proj-123",
            ...     "Create User model with email field",
            ...     yolo_mode=True
            ... )
            >>> assert result["status"] == "success"
            >>> assert len(result["files_changed"]) > 0
        """
        project = self.projects.get_by_id(ProjectId(project_id))
        if not project:
            return {"status": "error", "error": "Project not found"}

        if not project.can_execute_code():
            return {"status": "error", "error": "Project not ready for code execution"}

        result = await self.executor.execute_prompt(
            project_path=project.path,
            prompt=prompt,
            context={"yolo": yolo_mode}
        )

        return {
            "status": "success" if result.success else "error",
            "files_changed": result.modified_files,
            "diff": result.diff,
            "execution_log": result.log
        }
```

---

## Use Case Design Patterns

### 1. Input/Output Schemas

Always document contracts:

```python
def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input Schema:
        {
            "required_field": str,
            "optional_field": Optional[int]
        }

    Output Schema:
        {
            "status": "success" | "error",
            "data": Any,
            "error": str  # Only if status=error
        }
    """
```

### 2. Error Handling

Return structured errors, don't raise:

```python
# ✅ GOOD: Structured error
return {"status": "error", "error": "Project not found"}

# ❌ BAD: Unhandled exception
raise ValueError("Project not found")
```

### 3. Delegate to Domain

Business logic stays in entities:

```python
# ✅ GOOD: Domain handles business rule
try:
    feature = project.start_feature(prompt)
except ValueError as e:
    return {"status": "error", "error": str(e)}

# ❌ BAD: Use case contains business rule
if project.status != "active":
    return {"status": "error", "error": "Project must be active"}
feature = Feature(...)  # Creating entity directly
```

---

## Testing Use Cases

```python
def test_start_feature_use_case():
    # Arrange
    mock_repo = MockProjectRepository()
    mock_workflow = MockWorkflowEngine()
    mock_renderer = MockPromptRenderer()

    use_case = StartFeatureUseCase(mock_repo, mock_workflow, mock_renderer)

    # Act
    result = use_case.execute("proj-123", "Add login")

    # Assert
    assert result["status"] == "success"
    assert "feature_id" in result
    assert mock_repo.save_called
```

---

## Next Steps

- **Implement Ports**: See [Ports Documentation](architecture-ports.md)
- **Create Adapters**: See [Adapters Documentation](architecture-adapters.md)
- **Wire with DI**: See [DI Container](architecture-di-container.md)

---

*This document is part of the modular architecture documentation. See [README](README.md) for full navigation.*
