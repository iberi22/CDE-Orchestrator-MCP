"""
Test Phase 4: Production-Ready Error Handling Framework.

Validates:
- PROD-01: Error codes, recovery strategies, timestamps
- E-code numbering scheme (E001-E999)
- Serialization for logging and monitoring
"""

from datetime import datetime, timezone

import pytest

from cde_orchestrator.domain.exceptions import (
    ArtifactValidationError,
    CodeExecutionError,
    DomainError,
    FeatureNotFoundError,
    InvalidStateTransitionError,
    PhaseNotFoundError,
    ProjectNotFoundError,
    RepositoryError,
    WorkflowValidationError,
)


class TestErrorCodeScheme:
    """Validate E-code numbering scheme for programmatic handling."""

    def test_project_errors_use_e001_range(self) -> None:
        """E001-E099: Project-level errors."""
        error = ProjectNotFoundError("proj-123")

        assert error.code == "E001"
        assert error.context["project_id"] == "proj-123"
        assert error.recoverable is False

    def test_feature_errors_use_e101_range(self) -> None:
        """E101-E199: Feature-level errors."""
        error = FeatureNotFoundError("feat-456", "proj-123")

        assert error.code == "E102"
        assert error.context["feature_id"] == "feat-456"
        assert error.context["project_id"] == "proj-123"
        assert error.recoverable is False

    def test_state_transition_errors_use_e101_code(self) -> None:
        """E101: State transition errors (recoverable)."""
        error = InvalidStateTransitionError("Project", "error", "active")

        assert error.code == "E101"
        assert error.recoverable is True  # User can fix state first
        assert error.context["entity_type"] == "Project"
        assert error.context["from_status"] == "error"
        assert error.context["to_status"] == "active"

    def test_repository_errors_use_e201_code(self) -> None:
        """E201-E299: Persistence errors (often recoverable)."""
        error = RepositoryError("save", "Disk full")

        assert error.code == "E201"
        assert error.recoverable is True  # Retry might work
        assert error.context["operation"] == "save"
        assert error.context["details"] == "Disk full"

    def test_validation_errors_use_e301_code(self) -> None:
        """E301-E399: Validation errors (user can fix)."""
        error = ArtifactValidationError("define", ["spec"], [])

        assert error.code == "E301"
        assert error.recoverable is True
        assert "missing" in error.context
        assert error.context["missing"] == ["spec"]

    def test_workflow_errors_use_e402_e403_codes(self) -> None:
        """E402-E403: Workflow configuration errors."""
        validation_error = WorkflowValidationError("Invalid phase", "default")
        phase_error = PhaseNotFoundError("invalid_phase", "default")

        assert validation_error.code == "E402"
        assert validation_error.recoverable is False

        assert phase_error.code == "E403"
        assert phase_error.recoverable is False

    def test_execution_errors_use_e500_code(self) -> None:
        """E500-E599: Execution errors (might work on retry)."""
        error = CodeExecutionError("Timeout", execution_log="...")

        assert error.code == "E500"
        assert error.recoverable is True
        assert error.context["execution_log"] == "..."


class TestRecoveryStrategies:
    """Validate recoverable flag for intelligent retry logic."""

    def test_non_recoverable_errors(self) -> None:
        """These errors should NOT be retried."""
        errors = [
            ProjectNotFoundError("proj-123"),  # Project doesn't exist
            FeatureNotFoundError("feat-456", "proj-123"),  # Feature doesn't exist
            WorkflowValidationError("Invalid"),  # Workflow definition broken
            PhaseNotFoundError("invalid", "default"),  # Phase doesn't exist
        ]

        for error in errors:
            assert error.recoverable is False, f"{error.code} should not be recoverable"

    def test_recoverable_errors(self) -> None:
        """These errors MIGHT work on retry."""
        errors = [
            InvalidStateTransitionError(
                "Project", "error", "active"
            ),  # Fix state first
            ArtifactValidationError("define", ["spec"], []),  # Provide artifacts
            CodeExecutionError("Timeout"),  # Might work next time
            RepositoryError("save", "Disk full"),  # Disk space might free up
        ]

        for error in errors:
            assert error.recoverable is True, f"{error.code} should be recoverable"


class TestErrorSerialization:
    """Validate to_dict() for logging and monitoring."""

    def test_error_includes_all_fields(self) -> None:
        """Serialized error has code, message, context, recoverable, timestamp."""
        error = ProjectNotFoundError("proj-123")
        error_dict = error.to_dict()

        assert error_dict["code"] == "E001"
        assert error_dict["message"] == "Project 'proj-123' not found"
        assert error_dict["context"] == {"project_id": "proj-123"}
        assert error_dict["recoverable"] is False
        assert "timestamp" in error_dict

    def test_timestamp_is_iso8601_utc(self) -> None:
        """Timestamp is ISO 8601 format in UTC for audit trails."""
        error = FeatureNotFoundError("feat-456", "proj-123")
        error_dict = error.to_dict()

        # Parse timestamp
        timestamp = datetime.fromisoformat(
            error_dict["timestamp"].replace("Z", "+00:00")
        )

        # Verify UTC
        assert timestamp.tzinfo is not None
        utc_offset = timestamp.tzinfo.utcoffset(None)
        assert utc_offset is not None
        assert utc_offset.total_seconds() == 0

        # Verify recent (within 1 second)
        now = datetime.now(timezone.utc)
        assert (now - timestamp).total_seconds() < 1.0

    def test_context_preserves_all_data(self) -> None:
        """Context includes all error-specific metadata."""
        error = ArtifactValidationError("define", ["spec", "tests"], ["spec"])
        error_dict = error.to_dict()

        assert error_dict["context"]["phase_id"] == "define"
        assert error_dict["context"]["required"] == ["spec", "tests"]
        assert error_dict["context"]["provided"] == ["spec"]
        assert error_dict["context"]["missing"] == ["tests"]


class TestErrorMessages:
    """Validate user-facing error messages are clear."""

    def test_project_not_found_message(self) -> None:
        """Clear message identifying missing project."""
        error = ProjectNotFoundError("my-project")

        assert "my-project" in str(error)
        assert "not found" in str(error).lower()

    def test_feature_not_found_message(self) -> None:
        """Clear message identifying missing feature and project."""
        error = FeatureNotFoundError("auth-feature", "web-app")

        assert "auth-feature" in str(error)
        assert "web-app" in str(error)
        assert "not found" in str(error).lower()

    def test_state_transition_message(self) -> None:
        """Clear message showing invalid transition."""
        error = InvalidStateTransitionError("Feature", "completed", "defining")

        assert "Feature" in str(error)
        assert "completed" in str(error)
        assert "defining" in str(error)
        assert "transition" in str(error).lower()

    def test_artifact_validation_message(self) -> None:
        """Clear message listing missing artifacts."""
        error = ArtifactValidationError("implement", ["code", "tests"], ["code"])

        assert "implement" in str(error)
        assert "tests" in str(error)
        assert "missing" in str(error).lower()


class TestDomainErrorBase:
    """Validate DomainError base class behavior."""

    def test_custom_error_inherits_correctly(self) -> None:
        """Can create custom domain errors with all features."""

        class CustomError(DomainError):
            def __init__(self, resource_id: str):
                super().__init__(
                    message=f"Custom error for {resource_id}",
                    code="E999",
                    context={"resource_id": resource_id},
                    recoverable=True,
                )

        error = CustomError("res-789")

        assert error.code == "E999"
        assert error.recoverable is True
        assert error.context["resource_id"] == "res-789"
        assert isinstance(error.timestamp, datetime)

    def test_default_code_is_e000(self) -> None:
        """Generic domain errors use E000."""
        error = DomainError("Something went wrong")

        assert error.code == "E000"
        assert error.recoverable is False

    def test_error_is_exception(self) -> None:
        """DomainError is a proper Python exception."""
        error = ProjectNotFoundError("proj-123")

        assert isinstance(error, Exception)
        assert isinstance(error, DomainError)

        with pytest.raises(ProjectNotFoundError):
            raise error


# Performance benchmark: Error creation should be <1ms
class TestErrorPerformance:
    """Validate error handling has minimal overhead."""

    def test_error_creation_is_fast(self) -> None:
        """Creating and serializing errors should be <1ms."""
        import time

        start = time.perf_counter()

        for _ in range(100):
            error = ProjectNotFoundError("proj-123")
            _ = error.to_dict()

        elapsed_ms = (time.perf_counter() - start) * 1000

        # 100 errors in <10ms = <0.1ms per error
        assert (
            elapsed_ms < 10
        ), f"Error creation too slow: {elapsed_ms:.2f}ms for 100 errors"
