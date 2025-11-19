---
title: "CDE Orchestrator MCP - Adapter Implementations"
description: "Infrastructure implementations of port interfaces (FileSystem, Copilot CLI, etc)"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Orchestrator Team"
tags:
  - "architecture"
  - "adapters"
  - "infrastructure"
  - "implementations"
llm_summary: |
  Adapter implementations for hexagonal architecture. Includes FileSystemProjectRepository
  and implementation patterns. Adapters implement ports defined in domain layer.
  Contains I/O, network, filesystem code.
---

# Adapter Implementations

> **Part of**: [Architecture Documentation](README.md)
> **Layer**: Infrastructure/Adapters
> **Purpose**: Implement port interfaces with specific technologies

## Overview

Adapters are **concrete implementations** of port interfaces. They contain infrastructure code: I/O, network calls, external libraries, etc.

**Key Rules**:

- Implement port interfaces
- Can import external libraries
- Never imported by domain layer
- Technology-specific code lives here

---

## FileSystemProjectRepository

Stores projects as JSON files in a registry directory.

**Structure**:

```text
.cde_registry/
    projects/
        <project-id>.json
        <project-id>.json
    index.json  # Fast lookup: path -> project_id
```

**Implementation**:

```python
# src/cde_orchestrator/adapters/filesystem_project_repository.py

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from ..domain.ports import IProjectRepository
from ..domain.entities import Project, ProjectId, ProjectStatus, Feature, FeatureStatus
from datetime import datetime

class FileSystemProjectRepository(IProjectRepository):
    """
    Stores projects as JSON files in a registry directory.

    Benefits:
        - Simple (no database required)
        - Human-readable (JSON files)
        - Version-controllable
        - Easy backup

    Limitations:
        - Not suitable for 10,000+ projects
        - No transaction support
        - File locking issues in multi-process

    For large scale, use DatabaseProjectRepository instead.
    """

    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.projects_dir = registry_path / "projects"
        self.index_file = registry_path / "index.json"
        self._ensure_structure()

    def _ensure_structure(self):
        """Create registry directories if they don't exist."""
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps({}, indent=2))

    def get_by_id(self, project_id: ProjectId) -> Optional[Project]:
        """Load project from JSON file."""
        project_file = self.projects_dir / f"{project_id.value}.json"
        if not project_file.exists():
            return None

        data = json.loads(project_file.read_text())
        return self._deserialize_project(data)

    def get_by_path(self, path: str) -> Optional[Project]:
        """Use index to find project by path."""
        index = json.loads(self.index_file.read_text())
        project_id = index.get(path)
        if not project_id:
            return None
        return self.get_by_id(ProjectId(project_id))

    def list_all(self) -> List[Project]:
        """Load all projects from registry."""
        projects = []
        for project_file in self.projects_dir.glob("*.json"):
            data = json.loads(project_file.read_text())
            projects.append(self._deserialize_project(data))
        return projects

    def save(self, project: Project) -> None:
        """Persist project to JSON file and update index."""
        # Serialize project
        data = self._serialize_project(project)

        # Write to file
        project_file = self.projects_dir / f"{project.id.value}.json"
        project_file.write_text(json.dumps(data, indent=2))

        # Update index
        index = json.loads(self.index_file.read_text())
        index[project.path] = project.id.value
        self.index_file.write_text(json.dumps(index, indent=2))

    def delete(self, project_id: ProjectId) -> None:
        """Remove project file and index entry."""
        # Get project to find path
        project = self.get_by_id(project_id)
        if not project:
            return

        # Delete file
        project_file = self.projects_dir / f"{project_id.value}.json"
        if project_file.exists():
            project_file.unlink()

        # Update index
        index = json.loads(self.index_file.read_text())
        if project.path in index:
            del index[project.path]
        self.index_file.write_text(json.dumps(index, indent=2))

    def _serialize_project(self, project: Project) -> Dict[str, Any]:
        """Convert Project entity to JSON-serializable dict."""
        return {
            "id": project.id.value,
            "name": project.name,
            "path": project.path,
            "status": project.status.value,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
            "features": [self._serialize_feature(f) for f in project.features],
            "metadata": project.metadata
        }

    def _deserialize_project(self, data: Dict[str, Any]) -> Project:
        """Convert JSON dict to Project entity."""
        return Project(
            id=ProjectId(data["id"]),
            name=data["name"],
            path=data["path"],
            status=ProjectStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            features=[self._deserialize_feature(f) for f in data.get("features", [])],
            metadata=data.get("metadata", {})
        )

    def _serialize_feature(self, feature: Feature) -> Dict[str, Any]:
        return {
            "id": feature.id,
            "project_id": feature.project_id.value,
            "prompt": feature.prompt,
            "status": feature.status.value,
            "current_phase": feature.current_phase,
            "workflow_type": feature.workflow_type,
            "created_at": feature.created_at.isoformat(),
            "updated_at": feature.updated_at.isoformat(),
            "artifacts": feature.artifacts
        }

    def _deserialize_feature(self, data: Dict[str, Any]) -> Feature:
        return Feature(
            id=data["id"],
            project_id=ProjectId(data["project_id"]),
            prompt=data["prompt"],
            status=FeatureStatus(data["status"]),
            current_phase=data["current_phase"],
            workflow_type=data["workflow_type"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            artifacts=data.get("artifacts", {})
        )
```

---

## Adapter Design Patterns

### 1. Adapter Interface Compliance

Always implement ALL methods:

```python
# ✅ GOOD: All port methods implemented
class FileSystemProjectRepository(IProjectRepository):
    def get_by_id(self, project_id): ...
    def get_by_path(self, path): ...
    def list_all(self): ...
    def save(self, project): ...
    def delete(self, project_id): ...

# ❌ BAD: Missing methods
class FileSystemProjectRepository(IProjectRepository):
    def get_by_id(self, project_id): ...
    # Missing other methods!
```

### 2. Technology Encapsulation

Keep tech details inside adapter:

```python
# ✅ GOOD: JSON details hidden
def save(self, project: Project) -> None:
    data = self._serialize_project(project)
    file_path.write_text(json.dumps(data))

# ❌ BAD: JSON exposed to caller
def save(self, project: Project) -> str:
    return json.dumps(project.to_dict())  # Caller handles JSON
```

### 3. Error Translation

Convert infrastructure errors to domain errors:

```python
# ✅ GOOD: Infrastructure error translated
def get_by_id(self, project_id: ProjectId) -> Optional[Project]:
    try:
        data = self._load_json(project_id)
        return self._deserialize(data)
    except FileNotFoundError:
        return None  # Domain-level "not found"
    except json.JSONDecodeError as e:
        raise DataCorruptionError(f"Invalid project data: {e}")

# ❌ BAD: Raw infrastructure error exposed
def get_by_id(self, project_id: ProjectId) -> Project:
    data = json.loads(file.read_text())  # Can raise JSONDecodeError
    return self._deserialize(data)
```

---

## Testing Adapters

```python
# Integration test with real filesystem
def test_filesystem_repository():
    temp_dir = Path("/tmp/test_registry")
    repo = FileSystemProjectRepository(temp_dir)

    # Create project
    project = Project(...)
    repo.save(project)

    # Verify persistence
    loaded = repo.get_by_id(project.id)
    assert loaded.name == project.name
    assert (temp_dir / "projects" / f"{project.id.value}.json").exists()

    # Cleanup
    repo.delete(project.id)
    assert not (temp_dir / "projects" / f"{project.id.value}.json").exists()
```

---

## Other Adapter Examples

### YAMLWorkflowEngine

```python
# src/cde_orchestrator/adapters/yaml_workflow_engine.py

class YAMLWorkflowEngine(IWorkflowEngine):
    """Loads workflows from .cde/workflow.yml"""

    def __init__(self, workflow_file: Path):
        self.workflow_file = workflow_file

    def load_for_project(self, project: Project) -> Workflow:
        project_workflow = project.path / ".cde" / "workflow.yml"
        if project_workflow.exists():
            return self._parse_yaml(project_workflow)
        return self._parse_yaml(self.workflow_file)  # Default
```

### POMLPromptRenderer

```python
# src/cde_orchestrator/adapters/poml_prompt_renderer.py

class POMLPromptRenderer(IPromptRenderer):
    """Renders POML templates"""

    def render(self, template_path: str, context: Dict[str, Any]) -> str:
        template = self._load_template(template_path)
        return self._substitute_variables(template, context)
```

---

## Next Steps

- **Wire Adapters**: See [DI Container](architecture-di-container.md)
- **Understand Ports**: See [Ports Documentation](architecture-ports.md)
- **Use in Use Cases**: See [Use Cases](architecture-use-cases.md)

---

*This document is part of the modular architecture documentation. See [README](README.md) for full navigation.*
