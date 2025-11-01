# src/cde_orchestrator/domain/__init__.py
"""
CDE Orchestrator Domain Layer - Hexagonal Architecture Core.

This package contains pure business logic with ZERO external dependencies.
All code here is framework-agnostic and infrastructure-ignorant.

Packages:
    - entities: Core business objects (Project, Feature, Workflow, etc.)
    - ports: Interface contracts for adapters to implement
    - value_objects: Immutable value types
    - exceptions: Domain-specific errors

Rules:
    1. No imports from infrastructure or adapters
    2. No framework dependencies (FastMCP, Pydantic, etc.)
    3. All business rules encoded in entities
    4. Ports define what we need, never how it's implemented
"""

from .entities import (
    Project,
    ProjectId,
    ProjectStatus,
    Feature,
    FeatureStatus,
    CodeArtifact,
    Workflow,
    WorkflowPhase,
)

from .ports import (
    IProjectRepository,
    IWorkflowEngine,
    ICodeExecutor,
    IAgentOrchestrator,
    IPromptRenderer,
    IStateStore,
)

from .exceptions import (
    DomainError,
    ProjectNotFoundError,
    FeatureNotFoundError,
    InvalidStateTransitionError,
    WorkflowValidationError,
)

__all__ = [
    # Entities
    "Project",
    "ProjectId",
    "ProjectStatus",
    "Feature",
    "FeatureStatus",
    "CodeArtifact",
    "Workflow",
    "WorkflowPhase",
    # Ports
    "IProjectRepository",
    "IWorkflowEngine",
    "ICodeExecutor",
    "IAgentOrchestrator",
    "IPromptRenderer",
    "IStateStore",
    # Exceptions
    "DomainError",
    "ProjectNotFoundError",
    "FeatureNotFoundError",
    "InvalidStateTransitionError",
    "WorkflowValidationError",
]
