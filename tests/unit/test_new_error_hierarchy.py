# tests/unit/test_new_error_hierarchy.py

from cde_orchestrator.domain.exceptions import (
    ArtifactValidationError,
    CDEError,
    CodeExecutionError,
    DomainError,
    FeatureError,
    FeatureNotFoundError,
    InvalidStateTransitionError,
    PhaseNotFoundError,
    ProjectError,
    ProjectNotFoundError,
    RepositoryError,
    StateError,
    SystemError,
    ValidationError,
    WorkflowError,
    WorkflowValidationError,
)


class TestErrorHierarchy:
    """Verify the new exception hierarchy for Phase 4."""

    def test_project_error_hierarchy(self):
        error = ProjectNotFoundError("proj-1")
        assert isinstance(error, ProjectError)
        assert isinstance(error, DomainError)
        assert isinstance(error, CDEError)

    def test_feature_error_hierarchy(self):
        error1 = FeatureNotFoundError("feat-1", "proj-1")
        assert isinstance(error1, FeatureError)
        assert isinstance(error1, DomainError)

        error2 = InvalidStateTransitionError("Feature", "draft", "active")
        assert isinstance(error2, FeatureError)
        assert isinstance(error2, DomainError)

    def test_state_error_hierarchy(self):
        error = RepositoryError("save", "disk full")
        assert isinstance(error, StateError)
        assert isinstance(error, DomainError)

    def test_validation_error_hierarchy(self):
        error = ArtifactValidationError("phase-1", ["a"], [])
        assert isinstance(error, ValidationError)
        assert isinstance(error, DomainError)

    def test_workflow_error_hierarchy(self):
        error1 = WorkflowValidationError("invalid workflow")
        assert isinstance(error1, WorkflowError)

        error2 = PhaseNotFoundError("phase-1", "workflow-1")
        assert isinstance(error2, WorkflowError)

    def test_system_error_hierarchy(self):
        error = CodeExecutionError("syntax error")
        assert isinstance(error, SystemError)
        assert isinstance(error, CDEError)
        # SystemError might not be a DomainError depending on design,
        # but in my implementation SystemError inherits from CDEError directly.
        assert not isinstance(error, DomainError)

    def test_base_cde_error(self):
        error = CDEError("base error")
        assert error.code == "E000"
        assert isinstance(error, Exception)
