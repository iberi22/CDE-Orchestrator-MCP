---
title: "Architecture: Domain Layer"
description: "Pure business logic entities, value objects, and enums with zero infrastructure dependencies"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Team"
tags: ["architecture", "domain-driven-design", "hexagonal-architecture", "entities", "business-logic"]
llm_summary: |
  Domain layer contains pure business logic with no infrastructure dependencies.
  Defines core entities (Project, Feature, CodeArtifact), value objects (ProjectId),
  and enums (ProjectStatus, FeatureStatus) that enforce business rules and invariants.
  This is the innermost layer of the hexagonal architecture.
---

# Architecture: Domain Layer

> **Part of**: [Architecture Overview](./architecture-overview.md)
> **Related**: [Application Layer](././architecture-application-layer.md), [Ports & Adapters](./architecture-ports.md)

---

## Overview

The Domain Layer is the **core of the hexagonal architecture**, containing pure business logic with **zero infrastructure dependencies**. This layer defines:

- **Entities**: Business objects with identity and lifecycle
- **Value Objects**: Immutable data with no identity
- **Enums**: Constrained sets of valid values
- **Business Rules**: Invariants and state transition logic

**Key Principle**: The domain layer should never import from adapters or infrastructure. All dependencies point inward.

---

## Entities

Pure business logic with zero infrastructure dependencies.

```python
# src/cde_orchestrator/domain/entities.py

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

class ProjectStatus(Enum):
    """All possible project states."""
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    ARCHIVED = "archived"
    ERROR = "error"

@dataclass(frozen=True)
class ProjectId:
    """Value object for project identification."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 3:
            raise ValueError(f"Invalid project ID: {self.value}")

@dataclass
class Project:
    """
    Aggregate root for a managed project.

    Invariants:
        - Must have unique ID
        - Path must exist on filesystem
        - Can have 0+ active features
        - Status transitions are controlled
    """
    id: ProjectId
    name: str
    path: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    features: List['Feature']
    metadata: Dict[str, Any]

    def start_feature(self, prompt: str) -> 'Feature':
        """Business rule: Create new feature in this project."""
        if self.status != ProjectStatus.ACTIVE:
            raise ValueError(f"Cannot start feature in {self.status} project")

        feature = Feature.create(
            project_id=self.id,
            prompt=prompt,
            workflow_type=self.metadata.get("default_workflow", "default")
        )
        self.features.append(feature)
        self.updated_at = datetime.utcnow()
        return feature

    def can_execute_code(self) -> bool:
        """Business rule: Determine if code execution is allowed."""
        return (
            self.status == ProjectStatus.ACTIVE
            and self.path is not None
        )

class FeatureStatus(Enum):
    """Feature lifecycle states."""
    DEFINING = "defining"
    DECOMPOSING = "decomposing"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Feature:
    """
    Represents a unit of work within a project.

    Lifecycle: DEFINING → DECOMPOSING → DESIGNING →
               IMPLEMENTING → TESTING → REVIEWING → COMPLETED
    """
    id: str
    project_id: ProjectId
    prompt: str
    status: FeatureStatus
    current_phase: str
    workflow_type: str
    created_at: datetime
    updated_at: datetime
    artifacts: Dict[str, Any]

    @classmethod
    def create(cls, project_id: ProjectId, prompt: str, workflow_type: str) -> 'Feature':
        """Factory method: Enforce creation invariants."""
        import uuid
        return cls(
            id=str(uuid.uuid4()),
            project_id=project_id,
            prompt=prompt,
            status=FeatureStatus.DEFINING,
            current_phase="define",
            workflow_type=workflow_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            artifacts={}
        )

    def advance_phase(self, next_phase: str, results: Dict[str, Any]):
        """Business rule: Transition to next workflow phase."""
        phase_to_status = {
            "define": FeatureStatus.DEFINING,
            "decompose": FeatureStatus.DECOMPOSING,
            "design": FeatureStatus.DESIGNING,
            "implement": FeatureStatus.IMPLEMENTING,
            "test": FeatureStatus.TESTING,
            "review": FeatureStatus.REVIEWING,
        }

        self.current_phase = next_phase
        self.status = phase_to_status.get(next_phase, self.status)
        self.artifacts.update(results)
        self.updated_at = datetime.utcnow()

    def complete(self):
        """Business rule: Mark feature as completed."""
        if self.status != FeatureStatus.REVIEWING:
            raise ValueError(f"Cannot complete feature in {self.status} status")
        self.status = FeatureStatus.COMPLETED
        self.updated_at = datetime.utcnow()

@dataclass
class CodeArtifact:
    """Represents generated code or documentation."""
    path: str
    content: str
    language: str
    metadata: Dict[str, Any]
```

---

## Design Principles

### 1. **Encapsulation**
Business rules are encapsulated within entities. For example, `Project.start_feature()` enforces that only active projects can start new features.

### 2. **Immutability (Where Appropriate)**
Value objects like `ProjectId` are immutable to prevent accidental modification.

### 3. **Factory Methods**
Use factory methods (e.g., `Feature.create()`) to enforce creation invariants and encapsulate complex initialization logic.

### 4. **State Transition Guards**
Methods like `advance_phase()` and `complete()` enforce valid state transitions, preventing invalid lifecycle changes.

### 5. **Zero External Dependencies**
The domain layer imports only from Python's standard library and itself. No adapters, no infrastructure.

---

## Business Rules Examples

### Project Rules
- **Start Feature**: Only `ACTIVE` projects can start new features
- **Code Execution**: Only `ACTIVE` projects with valid paths can execute code
- **Status Transitions**: Projects follow controlled lifecycle: `ONBOARDING → ACTIVE → ARCHIVED`

### Feature Rules
- **Creation**: Features always start in `DEFINING` status with `define` phase
- **Phase Advancement**: Each phase transition updates status and artifacts
- **Completion**: Features can only be completed from `REVIEWING` status
- **Immutable ID**: Feature IDs are generated once and never change

---

## Related Documentation

- **[Architecture Overview](./architecture-overview.md)**: Complete hexagonal architecture guide
- **[Application Layer](./architecture-application-layer.md)**: Use cases that orchestrate domain entities
- **[Ports & Adapters](./architecture-ports.md)**: Interface definitions and implementations
- **[Project README](../../../README.md)**: Project overview and quick start

---

## Testing Domain Logic

Domain entities should be tested with **fast, isolated unit tests**:

```python
def test_project_start_feature_when_active():
    project = Project(
        id=ProjectId("test-123"),
        name="Test Project",
        path="/tmp/test",
        status=ProjectStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        features=[],
        metadata={}
    )

    feature = project.start_feature("Add authentication")

    assert feature.status == FeatureStatus.DEFINING
    assert feature.current_phase == "define"
    assert len(project.features) == 1

def test_project_start_feature_when_not_active_raises_error():
    project = Project(
        id=ProjectId("test-123"),
        name="Test Project",
        path="/tmp/test",
        status=ProjectStatus.ARCHIVED,  # Not active!
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        features=[],
        metadata={}
    )

    with pytest.raises(ValueError, match="Cannot start feature"):
        project.start_feature("Add authentication")
```

---

## Common Mistakes to Avoid

### ❌ Domain Importing Adapters
```python
# WRONG: domain/entities.py
from ..adapters.filesystem import FileSystem  # NO!

class Project:
    def save(self):
        FileSystem().write(self)  # Domain should NOT know about filesystem!
```

### ❌ Anemic Domain Models
```python
# WRONG: Just data bags with no behavior
@dataclass
class Project:
    id: str
    name: str
    # No methods = anemic model
```

### ✅ Rich Domain Models
```python
# RIGHT: Behavior encapsulated in entity
@dataclass
class Project:
    id: ProjectId
    name: str
    status: ProjectStatus

    def start_feature(self, prompt: str) -> Feature:
        """Business logic lives here"""
        if self.status != ProjectStatus.ACTIVE:
            raise ValueError("Project must be active")
        return Feature.create(self.id, prompt)
```

---

## See Also

- **[Hexagonal Architecture](./architecture-overview.md#hexagonal-architecture)**: Full architecture overview
- **[Dependency Rule](./architecture-overview.md#dependency-rule)**: Why dependencies point inward
- **[Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)**: External reference
