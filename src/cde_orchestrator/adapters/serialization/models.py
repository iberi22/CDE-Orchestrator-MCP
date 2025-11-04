# src/cde_orchestrator/adapters/serialization/models.py
"""
Serialization Models - Pydantic models for data persistence.

These models handle JSON serialization/deserialization of domain entities.
They live in adapters layer because they deal with external data formats.

Design Principles:
    - Pydantic v2 models for validation
    - Convert between domain entities and JSON
    - Handle legacy data migration
    - No business logic (pure data transformation)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class WorkflowInput(BaseModel):
    """Defines an input artifact for a workflow phase."""

    type: str
    path: str


class WorkflowOutput(BaseModel):
    """Defines an output artifact for a workflow phase."""

    type: str
    path: Optional[str] = None
    labels: Optional[List[str]] = None


class Phase(BaseModel):
    """Represents a single phase in the CDE workflow."""

    id: str
    description: str
    handler: str
    prompt_recipe: str
    inputs: Optional[List[WorkflowInput]] = None
    outputs: List[WorkflowOutput]


class Workflow(BaseModel):
    """Represents the entire CDE workflow defined in workflow.yml."""

    name: str
    version: str
    phases: List[Phase]


class Task(BaseModel):
    """Represents a single, actionable task for the AI agent."""

    id: str
    feature_id: str
    phase_id: str
    context: Dict[str, Any]
    prompt: str
    status: str = "pending"


class Recipe(BaseModel):
    """Represents a POML recipe for specialized agents."""

    id: str
    name: str
    category: str  # engineering, product, project-management, etc.
    description: str
    file_path: str
    tools: List[str]
    providers: Dict[str, Dict[str, Any]]
    topology: str = "solo"


class WorkflowType(BaseModel):
    """Represents different types of workflows for different project types."""

    id: str
    name: str
    description: str
    patterns: List[str]  # regex patterns to match user prompts
    phases: List[str]  # phase IDs in order
    default_recipes: Dict[str, str]  # phase_id -> recipe_id mapping
