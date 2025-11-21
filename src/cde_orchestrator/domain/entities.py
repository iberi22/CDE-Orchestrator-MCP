# src/cde_orchestrator/domain/entities.py
"""
Domain Entities - Pure Business Logic.

These are the core business objects of CDE Orchestrator.
They contain ONLY business rules and have ZERO infrastructure dependencies.

Design Principles:
    - Rich domain models (behavior, not just data)
    - Invariants enforced in constructors
    - State transitions controlled by methods
    - No setters - immutability where possible
    - Clear error messages for LLM agents
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from .exceptions import (
    InvalidStateTransitionError,
    PhaseNotFoundError,
    WorkflowValidationError,
)

# ============================================================================
# VALUE OBJECTS
# ============================================================================


@dataclass(frozen=True)
class ProjectId:
    """
    Value object for project identification.

    Invariants:
        - Must be non-empty string
        - Minimum length 3 characters
        - Immutable once created

    Examples:
        >>> pid = ProjectId("abc-123")
        >>> str(pid)  # "abc-123"
        >>> pid2 = ProjectId("ab")  # raises ValueError
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or len(self.value) < 3:
            raise ValueError(
                f"Invalid project ID: '{self.value}'. "
                f"Must be string with at least 3 characters."
            )

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"ProjectId('{self.value}')"


# ============================================================================
# ENUMERATIONS
# ============================================================================


class ProjectStatus(str, Enum):
    """
    All possible project states in CDE lifecycle.

    State Machine:
        ONBOARDING → ACTIVE → ARCHIVED
                  ↓
                ERROR (terminal)

    Descriptions:
        ONBOARDING: Project being analyzed and configured
        ACTIVE:     Ready for feature development
        ARCHIVED:   No longer actively developed
        ERROR:      Unrecoverable error state
    """

    ONBOARDING = "onboarding"
    ACTIVE = "active"
    ARCHIVED = "archived"
    ERROR = "error"

    def can_transition_to(self, target: "ProjectStatus") -> bool:
        """Check if transition to target status is valid."""
        transitions: Dict[ProjectStatus, Set[ProjectStatus]] = {
            ProjectStatus.ONBOARDING: {ProjectStatus.ACTIVE, ProjectStatus.ERROR},
            ProjectStatus.ACTIVE: {ProjectStatus.ARCHIVED, ProjectStatus.ERROR},
            ProjectStatus.ARCHIVED: {ProjectStatus.ACTIVE},  # Can reactivate
            ProjectStatus.ERROR: set(),  # Terminal state
        }
        return target in transitions.get(self, set())


class PhaseStatus(str, Enum):
    """Valid workflow phase identifiers."""

    DEFINE = "define"
    DECOMPOSE = "decompose"
    DESIGN = "design"
    IMPLEMENT = "implement"
    TEST = "test"
    REVIEW = "review"


class FeatureStatus(str, Enum):
    """
    Feature lifecycle states matching CDE workflow phases.

    Linear progression:
        DEFINING → DECOMPOSING → DESIGNING →
        IMPLEMENTING → TESTING → REVIEWING → COMPLETED

    Or can jump to FAILED from Any state.
    """

    DEFINING = "defining"
    DECOMPOSING = "decomposing"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def from_phase(cls, phase_id: str) -> "FeatureStatus":
        """
        Map workflow phase ID to feature status.

        Args:
            phase_id: Phase identifier (e.g., "define", "decompose")

        Returns:
            Corresponding FeatureStatus

        Examples:
            >>> FeatureStatus.from_phase("define")
            FeatureStatus.DEFINING
        """
        mapping = {
            "define": cls.DEFINING,
            "decompose": cls.DECOMPOSING,
            "design": cls.DESIGNING,
            "implement": cls.IMPLEMENTING,
            "test": cls.TESTING,
            "review": cls.REVIEWING,
        }
        return mapping.get(phase_id, cls.FAILED)


# ============================================================================
# ENTITIES
# ============================================================================


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


class RecipeSuggestion(BaseModel):
    """Represents a recipe suggestion."""

    recipe: Recipe
    confidence: float


class FeatureState(BaseModel):
    """Validated feature state model for JSON serialization."""

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
    def ensure_datetime(cls, value: Any) -> Optional[datetime]:
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
    def validate_phase_matches_status(
        cls, current_phase: PhaseStatus, info: Any
    ) -> PhaseStatus:
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
            FeatureStatus.FAILED: current_phase,  # Allow Any phase for failed
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
        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        return data


# ============================================================================
# VALUE OBJECTS
# ============================================================================


class PhaseStatusValue:
    """Valid workflow phase identifiers - moved to PhaseStatus enum above."""

    pass


# ============================================================================
# DOMAIN ENTITIES
# ============================================================================


# ============================================================================
# ENTITIES
# ============================================================================


@dataclass
class Feature:
    """
    Aggregate: Represents a unit of work within a project.

    A feature progresses through workflow phases, accumulating artifacts
    at each stage until completion or failure.

    Business Rules:
        - Must have unique ID within project
        - Cannot regress to earlier phases
        - Artifacts are append-only (never deleted)
        - Completion requires review phase artifacts

    State Transitions:
        advance_phase() - Move to next workflow phase
        fail() - Mark as failed with reason
        complete() - Mark as successfully completed
    """

    id: str
    project_id: ProjectId
    prompt: str  # Original user request
    status: FeatureStatus
    current_phase: str
    workflow_type: str
    created_at: datetime
    updated_at: datetime
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls, project_id: ProjectId, prompt: str, workflow_type: str = "default"
    ) -> "Feature":
        """
        Factory method: Create new feature with enforced invariants.

        Args:
            project_id: Parent project identifier
            prompt: User's feature request
            workflow_type: Workflow variant to use

        Returns:
            New Feature instance in DEFINING status

        Raises:
            ValueError: If prompt is empty

        Examples:
            >>> feat = Feature.create(
            ...     ProjectId("proj-123"),
            ...     "Add user authentication"
            ... )
            >>> assert feat.status == FeatureStatus.DEFINING
        """
        if not prompt or not prompt.strip():
            raise ValueError("Feature prompt cannot be empty")

        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid4()),
            project_id=project_id,
            prompt=prompt.strip(),
            status=FeatureStatus.DEFINING,
            current_phase="define",
            workflow_type=workflow_type,
            created_at=now,
            updated_at=now,
            artifacts={},
            metadata={},
        )

    def advance_phase(self, next_phase: str, results: Dict[str, Any]) -> None:
        """
        Business rule: Transition to next workflow phase.

        Args:
            next_phase: Target phase ID
            results: Phase output artifacts

        Raises:
            ValueError: If already completed or failed

        Side Effects:
            - Updates status to match new phase
            - Merges results into artifacts
            - Updates timestamp
        """
        if self.status in (FeatureStatus.COMPLETED, FeatureStatus.FAILED):
            raise ValueError(
                f"Cannot advance feature in {self.status} status. "
                f"Feature is terminal."
            )

        self.current_phase = next_phase
        self.status = FeatureStatus.from_phase(next_phase)
        self.artifacts.update(results)
        self.updated_at = datetime.now(timezone.utc)

    def fail(self, reason: str) -> None:
        """
        Business rule: Mark feature as failed.

        Args:
            reason: Human/LLM-readable failure explanation
        """
        self.status = FeatureStatus.FAILED
        self.metadata["failure_reason"] = reason
        self.metadata["failed_at"] = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        """
        Business rule: Mark feature as successfully completed.

        Raises:
            ValueError: If not in REVIEWING status
        """
        if self.status != FeatureStatus.REVIEWING:
            raise ValueError(
                f"Cannot complete feature in {self.status} status. "
                f"Must be in REVIEWING status first."
            )

        self.status = FeatureStatus.COMPLETED
        self.metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc)

    def get_artifact(self, key: str) -> Optional[Any]:
        """Safely retrieve artifact by key."""
        return self.artifacts.get(key)

    def has_artifact(self, key: str) -> bool:
        """Check if artifact exists."""
        return key in self.artifacts


@dataclass
class Project:
    """
    Aggregate Root: Represents a managed software project.

    A project is the top-level organizational unit. It contains:
        - Unique identity
        - Filesystem location
        - Lifecycle status
        - Collection of features
        - Configuration metadata

    Business Rules:
        - Must have valid filesystem path
        - Can only start features when ACTIVE
        - Feature count unlimited (supports 1000+ scale)
        - Status transitions must be valid

    Invariants:
        - ID is immutable
        - Path must exist (validated externally)
        - Features list never null
    """

    id: ProjectId
    name: str
    path: str  # Absolute filesystem path
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    features: List[Feature] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls, name: str, path: str, project_id: Optional[ProjectId] = None
    ) -> "Project":
        """
        Factory method: Create new project.

        Args:
            name: Human-readable project name
            path: Absolute filesystem path
            project_id: Optional explicit ID (generates UUID if not provided)

        Returns:
            New Project instance in ONBOARDING status
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")
        if not path or not path.strip():
            raise ValueError("Project path cannot be empty")

        now = datetime.now(timezone.utc)
        pid = project_id or ProjectId(str(uuid4()))

        return cls(
            id=pid,
            name=name.strip(),
            path=path.strip(),
            status=ProjectStatus.ONBOARDING,
            created_at=now,
            updated_at=now,
            features=[],
            metadata={},
        )

    def start_feature(self, prompt: str, workflow_type: str = "default") -> Feature:
        """
        Business rule: Create and register new feature.

        Args:
            prompt: User's feature request
            workflow_type: Workflow variant to use

        Returns:
            Created Feature instance

        Raises:
            ValueError: If project not in ACTIVE status

        Side Effects:
            - Creates new Feature entity
            - Adds to features list
            - Updates project timestamp
        """
        if self.status != ProjectStatus.ACTIVE:
            raise ValueError(
                f"Cannot start feature in {self.status} project. "
                f"Project must be ACTIVE."
            )

        feature = Feature.create(
            project_id=self.id, prompt=prompt, workflow_type=workflow_type
        )

        self.features.append(feature)
        self.updated_at = datetime.now(timezone.utc)

        return feature

    def get_feature(self, feature_id: str) -> Optional[Feature]:
        """Find feature by ID."""
        for feature in self.features:
            if feature.id == feature_id:
                return feature
        return None

    def get_active_features(self) -> List[Feature]:
        """Get all non-terminal features."""
        return [
            f
            for f in self.features
            if f.status not in (FeatureStatus.COMPLETED, FeatureStatus.FAILED)
        ]

    def transition_status(self, target: ProjectStatus) -> None:
        """
        Business rule: Change project status.

        Args:
            target: Desired status

        Raises:
            InvalidStateTransitionError: If transition not allowed
        """
        if not self.status.can_transition_to(target):
            raise InvalidStateTransitionError(
                "Project", self.status.value, target.value
            )

        self.status = target
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Convenience: Transition to ACTIVE status."""
        self.transition_status(ProjectStatus.ACTIVE)

    def archive(self) -> None:
        """Convenience: Transition to ARCHIVED status."""
        self.transition_status(ProjectStatus.ARCHIVED)

    def can_execute_code(self) -> bool:
        """Business rule: Determine if code execution is allowed."""
        return self.status == ProjectStatus.ACTIVE


@dataclass
class WorkflowPhase:
    """
    Value object: Represents a single phase in the CDE workflow.

    Each phase defines:
        - Unique identifier
        - Description of purpose
        - Prompt template location
        - Expected inputs/outputs
    """

    id: str
    description: str
    prompt_recipe: str  # Path to POML file
    inputs: List[str] = field(default_factory=list)  # Expected artifact keys
    outputs: List[str] = field(default_factory=list)  # Produced artifact keys

    def validates_results(self, results: Dict[str, Any]) -> bool:
        """Check if results contain all required outputs."""
        return all(key in results for key in self.outputs)


@dataclass
class Workflow:
    """
    Entity: Represents a complete CDE workflow definition.

    A workflow is an ordered sequence of phases that guide feature development
    from initial idea to completed implementation.

    Business Rules:
        - Must have at least one phase
        - Phase IDs must be unique
        - Phases form a linear sequence
    """

    name: str
    version: str
    phases: List[WorkflowPhase]

    def get_phase(self, phase_id: str) -> Optional[WorkflowPhase]:
        """Find phase by ID."""
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None

    def get_initial_phase(self) -> WorkflowPhase:
        """Get the first phase in workflow."""
        if not self.phases:
            raise WorkflowValidationError("Workflow has no phases defined", self.name)
        return self.phases[0]

    def get_next_phase(self, current_phase_id: str) -> Optional[WorkflowPhase]:
        """
        Get next phase in sequence.

        Returns:
            Next WorkflowPhase or None if current is last phase

        Raises:
            PhaseNotFoundError: If current_phase_id not found
        """
        phase_ids = [p.id for p in self.phases]

        try:
            current_index = phase_ids.index(current_phase_id)
        except ValueError:
            raise PhaseNotFoundError(current_phase_id, self.name)

        if current_index + 1 < len(self.phases):
            return self.phases[current_index + 1]
        return None

    def get_progress(self, current_phase_id: str) -> Dict[str, Any]:
        """Calculate workflow progress information."""
        phase_ids = [p.id for p in self.phases]

        try:
            current_index = phase_ids.index(current_phase_id)
        except ValueError:
            raise PhaseNotFoundError(current_phase_id, self.name)

        return {
            "current_phase": current_phase_id,
            "phase_number": current_index + 1,
            "total_phases": len(self.phases),
            "progress_percentage": ((current_index + 1) / len(self.phases)) * 100,
            "remaining_phases": phase_ids[current_index + 1 :],
            "completed_phases": phase_ids[:current_index],
        }


@dataclass
class CodeArtifact:
    """
    Value object: Represents generated code or documentation.

    Artifacts are immutable records of what was produced during a phase.
    """

    path: str  # Relative path within project
    content: str
    language: str
    generated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, path: str, content: str, language: str) -> "CodeArtifact":
        """Factory: Create artifact with timestamp."""
        return cls(
            path=path,
            content=content,
            language=language,
            generated_at=datetime.now(timezone.utc),
            metadata={},
        )
