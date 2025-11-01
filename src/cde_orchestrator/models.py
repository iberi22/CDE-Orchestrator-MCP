# src/cde_orchestrator/models.py
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class FeatureStatus(str, Enum):
    """Valid feature status values."""

    DEFINING = "defining"
    DECOMPOSING = "decomposing"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"


class PhaseStatus(str, Enum):
    """Valid workflow phase identifiers."""

    DEFINE = "define"
    DECOMPOSE = "decompose"
    DESIGN = "design"
    IMPLEMENT = "implement"
    TEST = "test"
    REVIEW = "review"


class FeatureState(BaseModel):
    """Validated feature state model."""

    status: FeatureStatus
    current_phase: PhaseStatus
    workflow_type: str = "default"
    prompt: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    branch: Optional[str] = None
    recipe_id: Optional[str] = None
    recipe_name: Optional[str] = None
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    progress: Dict[str, Any] = Field(default_factory=dict)
    commits: List[Dict[str, Any]] = Field(default_factory=list)
    completed_at: Optional[datetime] = None

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def ensure_datetime(cls, value):
        """Parse datetime strings into datetime objects."""
        if value in (None, "", 0):
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value))
        except (ValueError, TypeError):
            raise ValueError("Timestamps must be ISO formatted strings")

    @field_validator("prompt")
    @classmethod
    def ensure_prompt_not_empty(cls, value: str) -> str:
        """Ensure prompts are non-empty strings."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Prompt must be a non-empty string")
        return value

    @field_validator("current_phase", mode="after")
    @classmethod
    def validate_phase_matches_status(cls, current_phase, info):
        """Ensure phase is consistent with status."""
        values = info.data
        if "status" not in values:
            return current_phase

        status = values["status"]
        phase_mapping = {
            FeatureStatus.DEFINING: PhaseStatus.DEFINE,
            FeatureStatus.DECOMPOSING: PhaseStatus.DECOMPOSE,
            FeatureStatus.DESIGNING: PhaseStatus.DESIGN,
            FeatureStatus.IMPLEMENTING: PhaseStatus.IMPLEMENT,
            FeatureStatus.TESTING: PhaseStatus.TEST,
            FeatureStatus.REVIEWING: PhaseStatus.REVIEW,
            FeatureStatus.COMPLETED: PhaseStatus.REVIEW,
            FeatureStatus.FAILED: current_phase,  # Allow any phase for failed
        }

        expected = phase_mapping.get(status)
        if (
            expected
            and isinstance(expected, PhaseStatus)
            and current_phase != expected
            and status != FeatureStatus.FAILED
        ):
            # Log warning but don't fail - allow migration
            import logging

            logging.warning(
                "Phase %s may be inconsistent with status %s, expected %s",
                current_phase,
                status,
                expected,
            )

        return current_phase

    def serialize(self) -> Dict[str, Any]:
        """Serialize state to JSON-safe dict."""
        data = self.model_dump()
        data["status"] = self.status.value
        data["current_phase"] = self.current_phase.value
        data["created_at"] = self.created_at.isoformat()
        if data.get("updated_at"):
            data["updated_at"] = self.updated_at.isoformat()  # type: ignore[attr-defined]
        if data.get("completed_at"):
            data["completed_at"] = self.completed_at.isoformat()  # type: ignore[attr-defined]
        return data


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
