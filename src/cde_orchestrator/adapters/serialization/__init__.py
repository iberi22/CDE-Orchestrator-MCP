# src/cde_orchestrator/adapters/serialization/__init__.py
"""
Serialization Adapters - Data persistence models.

This module contains Pydantic models for JSON serialization/deserialization
of domain entities. These are infrastructure concerns, not domain logic.
"""

# Re-export domain enums for convenience
from ...domain.entities import FeatureStatus, PhaseStatus
from .models import (
    Phase,
    Recipe,
    Task,
    Workflow,
    WorkflowInput,
    WorkflowOutput,
    WorkflowType,
)

__all__ = [
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
