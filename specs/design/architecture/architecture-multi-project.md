---
title: "CDE Orchestrator MCP - Multi-Project Management"
description: "Project management architecture with stateless design and deep context awareness"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Orchestrator Team"
tags:
  - "architecture"
  - "multi-project"
  - "stateless"
  - "scalability"
llm_summary: |
  Multi-project management design: stateless, agent-provides-context pattern.
  No registries, no caching. Agent knows project location, CDE validates and executes.
  Supports unlimited projects with lazy loading and context isolation.
---

# Multi-Project Management

> **Part of**: [Architecture Documentation](README.md)
> **Philosophy**: Stateless & Simple - Agent knows context, CDE executes
> **Scale**: Unlimited projects (no shared state bottlenecks)

## Core Philosophy

**Agent Knows, CDE Executes**:

- **LLM has context**: Agent remembers project names, locations, current work
- **CDE validates**: Just check project exists at given path
- **CDE executes**: Run workflows in that path
- **No complex state**: Each operation independent

---

## Project Registry (Optional)

For convenience, CDE can discover and list projects. But **registry is NOT required** for operation.

```python
# src/cde_orchestrator/application/project_registry.py

from typing import List, Dict, Any, Optional
from pathlib import Path
from ..domain.entities import Project, ProjectId
from ..domain.ports import IProjectRepository

class ProjectRegistry:
    """
    Manages multiple projects simultaneously.

    Features:
        - Auto-discovery of projects in a root folder
        - Lazy loading (load project state only when needed)
        - Context isolation (each project has independent state)
        - Concurrent operations support

    Note: Registry is OPTIONAL. CDE works without it.
    """

    def __init__(self, repository: IProjectRepository):
        self.repo = repository
        self._loaded_projects: Dict[str, Project] = {}

    def scan_directory(self, root_path: str) -> List[Project]:
        """
        Scan directory tree for Git repositories and register as projects.

        Example: Scan "E:\\scripts-python" for all projects

        Args:
            root_path: Absolute path to scan (e.g., "E:\\scripts-python")

        Returns:
            List of discovered/registered projects
        """
        root = Path(root_path)
        if not root.exists():
            raise ValueError(f"Path does not exist: {root_path}")

        discovered = []

        # Find all .git directories (indicates a project)
        for git_dir in root.rglob(".git"):
            project_path = str(git_dir.parent)

            # Check if already registered
            existing = self.repo.get_by_path(project_path)
            if existing:
                discovered.append(existing)
                continue

            # Register new project
            project_name = git_dir.parent.name
            project = self._create_project_from_path(project_path, project_name)
            self.repo.save(project)
            discovered.append(project)

        return discovered

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project with lazy loading."""
        # Check cache first
        if project_id in self._loaded_projects:
            return self._loaded_projects[project_id]

        # Load from repository
        project = self.repo.get_by_id(ProjectId(project_id))
        if project:
            self._loaded_projects[project_id] = project
        return project

    def get_project_by_path(self, path: str) -> Optional[Project]:
        """Find project by filesystem path."""
        return self.repo.get_by_path(path)

    def list_all(self) -> List[Project]:
        """Get all registered projects (from persistence)."""
        return self.repo.list_all()

    def _create_project_from_path(self, path: str, name: str) -> Project:
        """Factory method for creating projects from discovered paths."""
        import uuid
        from datetime import datetime
        from ..domain.entities import Project, ProjectId, ProjectStatus

        return Project(
            id=ProjectId(str(uuid.uuid4())),
            name=name,
            path=path,
            status=ProjectStatus.ONBOARDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            features=[],
            metadata={"auto_discovered": True}
        )
```

---

## Stateless Operation Pattern

Every MCP tool call is stateless from agent's perspective:

```python
# Agent calls (in different sessions):
cde_startFeature(project_path="E:\\MyProject", prompt="Add auth")
# Later...
cde_submitWork(project_path="E:\\MyProject", phase="define", results={...})

# CDE loads state from E:\MyProject\.cde\state.json each time
# Agent just provides context
```

**Benefits**:

- **No session state**: Agent doesn't remember project IDs
- **Simple**: Each call independent
- **Scalable**: No shared state bottlenecks

---

## Context Isolation

Each project maintains isolated state in `.cde/state.json`:

```text
E:\scripts-python\
    project-a\
        .cde\
            state.json        # Project A state
            workflow.yml
    project-b\
        .cde\
            state.json        # Project B state
            workflow.yml
```

**Concurrent Operations**: Safe because no shared state.

---

## Performance Optimizations

### 1. Lazy Loading

Only load project state when accessed:

```python
class ProjectRegistry:
    def get_project(self, project_id: str) -> Optional[Project]:
        # Check cache first
        if project_id in self._loaded_projects:
            return self._loaded_projects[project_id]

        # Load from repository
        project = self.repo.get_by_id(ProjectId(project_id))
        if project:
            self._loaded_projects[project_id] = project
        return project
```

### 2. Incremental Updates

Save only changed features, not entire state:

```python
def save_feature(self, project: Project, feature: Feature):
    # Only update feature artifact, not entire project
    feature_file = project.path / ".cde" / "features" / f"{feature.id}.json"
    feature_file.write_text(json.dumps(feature.to_dict()))
```

### 3. Summary Views

Provide project summaries without loading full state:

```python
def list_project_summaries(self) -> List[Dict[str, Any]]:
    return [
        {
            "id": p.id.value,
            "name": p.name,
            "path": p.path,
            "status": p.status.value,
            "feature_count": self._count_features(p.path)  # Fast count
        }
        for p in self.repo.list_all()
    ]
```

### 4. Parallel Processing

Use asyncio for concurrent operations:

```python
async def process_multiple_projects(project_ids: List[str]):
    tasks = [
        process_single_project(pid)
        for pid in project_ids
    ]
    results = await asyncio.gather(*tasks)
    return results
```

---

## LLM Interaction Patterns

### Pattern 1: Project Discovery

```text
Agent: "Scan E:\scripts-python for projects"

System: Discovers 47 Git repositories

Agent receives:
{
  "status": "success",
  "discovered": 47,
  "projects": [
    {"id": "uuid-1", "name": "CDE Orchestrator", "path": "E:\\scripts-python\\CDE Orchestrator MCP"},
    {"id": "uuid-2", "name": "Data Pipeline", "path": "E:\\scripts-python\\data-pipeline"},
    ...
  ]
}

Agent: Now understands all projects, can reference by path or name
```

### Pattern 2: Cross-Project Work

```text
Agent: "Start auth feature in CDE Orchestrator"

System: Loads E:\scripts-python\CDE Orchestrator MCP\.cde\state.json

Agent: Completes define phase

Agent: "Start API feature in Data Pipeline"

System: Loads E:\scripts-python\data-pipeline\.cde\state.json

# No interference - isolated states
```

---

## Scaling Considerations

### For 100-1000 Projects

- **Current design** works well
- Lazy loading prevents memory issues
- Filesystem-based storage sufficient

### For 10,000+ Projects

- Consider **DatabaseProjectRepository** instead of filesystem
- Add **caching layer** (Redis, Memcached)
- Use **background indexing** for fast lookups

```python
# Future: DatabaseProjectRepository
class DatabaseProjectRepository(IProjectRepository):
    def __init__(self, db_connection):
        self.db = db_connection

    def list_all(self) -> List[Project]:
        # SQL query instead of filesystem scan
        return self.db.query("SELECT * FROM projects")
```

---

## Next Steps

- **Understand Use Cases**: See [Use Cases](architecture-use-cases.md)
- **Review Adapters**: See [Adapters](architecture-adapters.md)
- **Learn DI Wiring**: See [DI Container](architecture-di-container.md)

---

*This document is part of the modular architecture documentation. See [README](README.md) for full navigation.*
