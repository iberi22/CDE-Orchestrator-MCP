# src/cde_orchestrator/domain/exceptions.py
"""
Domain Exceptions - Business Rule Violations.

All exceptions in this module represent violations of business rules
or invariants in the domain model. They should be caught and handled
by the application layer, never in the domain itself.

Design for LLMs:
    - Clear error messages
    - Machine-readable error codes
    - Structured context data
"""

from typing import Any, Dict, Optional


class DomainError(Exception):
    """
    Base exception for all domain errors.

    All domain exceptions inherit from this base class, making them
    easy to catch and distinguish from infrastructure errors.

    Attributes:
        message: Human/LLM-readable error description
        code: Machine-readable error identifier
        context: Additional structured data about the error
    """

    def __init__(
        self,
        message: str,
        code: str = "DOMAIN_ERROR",
        context: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.context = context or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-friendly dict for LLM consumption."""
        return {
            "error_type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "context": self.context,
        }


class ProjectNotFoundError(DomainError):
    """
    Raised when attempting to access a non-existent project.

    Examples:
        >>> raise ProjectNotFoundError("proj-123")
        ProjectNotFoundError: Project 'proj-123' not found
    """

    def __init__(self, project_id: str):
        super().__init__(
            message=f"Project '{project_id}' not found",
            code="PROJECT_NOT_FOUND",
            context={"project_id": project_id},
        )


class FeatureNotFoundError(DomainError):
    """
    Raised when attempting to access a non-existent feature.

    Examples:
        >>> raise FeatureNotFoundError("feat-456", "proj-123")
        FeatureNotFoundError: Feature 'feat-456' not found in project 'proj-123'
    """

    def __init__(self, feature_id: str, project_id: str):
        super().__init__(
            message=f"Feature '{feature_id}' not found in project '{project_id}'",
            code="FEATURE_NOT_FOUND",
            context={"feature_id": feature_id, "project_id": project_id},
        )


class InvalidStateTransitionError(DomainError):
    """
    Raised when attempting an invalid status transition.

    Examples:
        >>> raise InvalidStateTransitionError(
        ...     "Project", "error", "active"
        ... )
        InvalidStateTransitionError: Cannot transition Project from 'error' to 'active'
    """

    def __init__(self, entity_type: str, from_status: str, to_status: str):
        super().__init__(
            message=f"Cannot transition {entity_type} from '{from_status}' to '{to_status}'",
            code="INVALID_STATE_TRANSITION",
            context={
                "entity_type": entity_type,
                "from_status": from_status,
                "to_status": to_status,
            },
        )


class WorkflowValidationError(DomainError):
    """
    Raised when workflow definition or execution is invalid.

    Examples:
        >>> raise WorkflowValidationError(
        ...     "Phase 'define' missing required output 'specification'"
        ... )
    """

    def __init__(self, message: str, workflow_name: Optional[str] = None):
        super().__init__(
            message=message,
            code="WORKFLOW_VALIDATION_ERROR",
            context={"workflow_name": workflow_name} if workflow_name else {},
        )


class PhaseNotFoundError(DomainError):
    """
    Raised when referencing a non-existent workflow phase.

    Examples:
        >>> raise PhaseNotFoundError("invalid_phase", "default")
        PhaseNotFoundError: Phase 'invalid_phase' not found in workflow 'default'
    """

    def __init__(self, phase_id: str, workflow_name: str):
        super().__init__(
            message=f"Phase '{phase_id}' not found in workflow '{workflow_name}'",
            code="PHASE_NOT_FOUND",
            context={"phase_id": phase_id, "workflow_name": workflow_name},
        )


class ArtifactValidationError(DomainError):
    """
    Raised when phase results don't meet requirements.

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
            code="ARTIFACT_VALIDATION_ERROR",
            context={
                "phase_id": phase_id,
                "required": required,
                "provided": provided,
                "missing": list(missing),
            },
        )


class CodeExecutionError(DomainError):
    """
    Raised when code execution fails.

    Examples:
        >>> raise CodeExecutionError("Syntax error in generated code")
    """

    def __init__(self, message: str, execution_log: Optional[str] = None):
        super().__init__(
            message=message,
            code="CODE_EXECUTION_ERROR",
            context={"execution_log": execution_log} if execution_log else {},
        )


class RepositoryError(DomainError):
    """
    Raised when repository operations fail.

    This is a domain error because it represents a violation of
    our expectation that persistence should work. The application
    layer should catch this and decide how to handle it.
    """

    def __init__(self, operation: str, details: str):
        super().__init__(
            message=f"Repository operation '{operation}' failed: {details}",
            code="REPOSITORY_ERROR",
            context={"operation": operation, "details": details},
        )
