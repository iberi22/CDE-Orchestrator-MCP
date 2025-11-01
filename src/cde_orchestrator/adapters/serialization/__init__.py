# src/cde_orchestrator/adapters/serialization/__init__.py
"""
Serialization Adapters - Data persistence models.

This module contains Pydantic models for JSON serialization/deserialization
of domain entities. These are infrastructure concerns, not domain logic.
"""

from .models import (
    FeatureState,
    Phase,
    PhaseStatus,
    Recipe,
    Task,
    Workflow,
    WorkflowInput,
    WorkflowOutput,
    WorkflowType,
)

# Re-export domain enums for convenience
from ...domain.entities import FeatureStatus

__all__ = [
    "FeatureState",
    "FeatureStatus",
    "Phase",
    "PhaseStatus",
    "Recipe",
    "Task",
    "Workflow",
    "WorkflowInput",
    "WorkflowOutput",
    "WorkflowType",
]