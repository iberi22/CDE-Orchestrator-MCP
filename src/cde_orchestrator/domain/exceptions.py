# src/cde_orchestrator/domain/exceptions.py
"""
Domain Exceptions - Business Rule Violations.

All exceptions in this module represent violations of business rules
or invariants in the domain model. They should be caught and handled
by the application layer, never in the domain itself.

Phase 4 Enhancement:
    - Numeric error codes (E001-E999)
    - Recovery strategies (recoverable flag)
    - Timestamps for audit trail
    - Enhanced context capture

Design for LLMs:
    - Clear error messages
    - Machine-readable error codes
    - Structured context data
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional


class CDEError(Exception):
    """
    Base exception for all CDE Orchestrator errors.

    All exceptions in the system should inherit from this class.

    Attributes:
        message: Human/LLM-readable error description
        code: Machine-readable error identifier (E001-E999)
        context: Additional structured data about the error
        recoverable: Whether error allows retry
        timestamp: When error occurred (ISO 8601 UTC)
    """

    def __init__(
        self,
        message: str,
        code: str = "E000",
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
    ):
        self.message = message
        self.code = code
        self.context = context or {}
        self.recoverable = recoverable
        self.timestamp = datetime.now(timezone.utc)
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-friendly dict for LLM consumption."""
        return {
            "error_type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "context": self.context,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp.isoformat(),
        }


class DomainError(CDEError):
    """Base class for business rule violations."""

    pass


class ProjectError(DomainError):
    """Base class for project-related errors (E001-E099)."""

    pass


class FeatureError(DomainError):
    """Base class for feature-related errors (E100-E199)."""

    pass


class StateError(DomainError):
    """Base class for state management errors (E200-E299)."""

    pass


class ValidationError(DomainError):
    """Base class for validation errors (E300-E399)."""

    pass


class WorkflowError(DomainError):
    """Base class for workflow errors (E400-E499)."""

    pass


class SystemError(CDEError):
    """Base class for system/infrastructure errors (E900-E999)."""

    pass


class ProjectNotFoundError(ProjectError):
    """
    Raised when attempting to access a non-existent project.

    Error Code: E001 (Project Errors)
    Recoverable: False (project doesn't exist)

    Examples:
        >>> raise ProjectNotFoundError("proj-123")
        ProjectNotFoundError: Project 'proj-123' not found
    """

    def __init__(self, project_id: str):
        super().__init__(
            message=f"Project '{project_id}' not found",
            code="E001",
            context={"project_id": project_id},
            recoverable=False,
        )


class FeatureNotFoundError(FeatureError):
    """
    Raised when attempting to access a non-existent feature.

    Error Code: E102 (Feature Errors)
    Recoverable: False (feature doesn't exist)

    Examples:
        >>> raise FeatureNotFoundError("feat-456", "proj-123")
        FeatureNotFoundError: Feature 'feat-456' not found in project 'proj-123'
    """

    def __init__(self, feature_id: str, project_id: str):
        super().__init__(
            message=f"Feature '{feature_id}' not found in project '{project_id}'",
            code="E102",
            context={"feature_id": feature_id, "project_id": project_id},
            recoverable=False,
        )


class InvalidStateTransitionError(FeatureError):
    """
    Raised when attempting an invalid status transition.

    Error Code: E101 (Feature Status Errors)
    Recoverable: True (user can fix state first)

    Examples:
        >>> raise InvalidStateTransitionError(
        ...     "Project", "error", "active"
        ... )
        InvalidStateTransitionError: Cannot transition Project from 'error' to 'active'
    """

    def __init__(self, entity_type: str, from_status: str, to_status: str):
        super().__init__(
            message=f"Cannot transition {entity_type} from '{from_status}' to '{to_status}'",
            code="E101",
            context={
                "entity_type": entity_type,
                "from_status": from_status,
                "to_status": to_status,
            },
            recoverable=True,
        )


class WorkflowValidationError(WorkflowError):
    """
    Raised when workflow definition or execution is invalid.

    Error Code: E402 (Workflow Parse Errors)
    Recoverable: False (workflow definition issue)

    Examples:
        >>> raise WorkflowValidationError(
        ...     "Phase 'define' missing required output 'specification'"
        ... )
    """

    def __init__(self, message: str, workflow_name: Optional[str] = None):
        super().__init__(
            message=message,
            code="E402",
            context={"workflow_name": workflow_name} if workflow_name else {},
            recoverable=False,
        )


class PhaseNotFoundError(WorkflowError):
    """
    Raised when referencing a non-existent workflow phase.

    Error Code: E403 (Workflow Phase Errors)
    Recoverable: False (phase doesn't exist)

    Examples:
        >>> raise PhaseNotFoundError("invalid_phase", "default")
        PhaseNotFoundError: Phase 'invalid_phase' not found in workflow 'default'
    """

    def __init__(self, phase_id: str, workflow_name: str):
        super().__init__(
            message=f"Phase '{phase_id}' not found in workflow '{workflow_name}'",
            code="E403",
            context={"phase_id": phase_id, "workflow_name": workflow_name},
            recoverable=False,
        )


class ArtifactValidationError(ValidationError):
    """
    Raised when phase results don't meet requirements.

    Error Code: E301 (Validation Errors)
    Recoverable: True (user can provide correct artifacts)

    Examples:
        >>> raise ArtifactValidationError(
        ...     "define", ["specification"], []
        ... )
        ArtifactValidationError: Phase 'define' missing required artifacts: ['specification']
    """

    def __init__(self, phase_id: str, required: list, provided: list):
        missing = set(required) - set(provided)
        super().__init__(
            message=f"Phase '{phase_id}' missing required artifacts: {list(missing)}",
            code="E301",
            context={
                "phase_id": phase_id,
                "required": required,
                "provided": provided,
                "missing": list(missing),
            },
            recoverable=True,
        )


class CodeExecutionError(SystemError):
    """
    Raised when code execution fails.

    Error Code: E500 (Execution Errors)
    Recoverable: True (might work on retry)

    Examples:
        >>> raise CodeExecutionError("Syntax error in generated code")
    """

    def __init__(self, message: str, execution_log: Optional[str] = None):
        super().__init__(
            message=message,
            code="E500",
            context={"execution_log": execution_log} if execution_log else {},
            recoverable=True,
        )


class RepositoryError(StateError):
    """
    Raised when repository operations fail.

    Error Code: E201 (State Load Errors)
    Recoverable: True (retry might work)

    This is a domain error because it represents a violation of
    our expectation that persistence should work. The application
    layer should catch this and decide how to handle it.
    """

    def __init__(self, operation: str, details: str):
        super().__init__(
            message=f"Repository operation '{operation}' failed: {details}",
            code="E201",
            context={"operation": operation, "details": details},
            recoverable=True,
        )
