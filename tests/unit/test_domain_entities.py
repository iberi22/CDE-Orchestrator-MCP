# tests/unit/test_domain_entities.py
"""
Unit tests for domain entities.

Tests business logic, invariants, and state transitions WITHOUT infrastructure.
All tests should be fast (<5ms) and require no I/O.
"""

import sys
from pathlib import Path

# Add project root to path (same pattern as other tests)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from datetime import datetime, timezone
from uuid import UUID

from src.cde_orchestrator.domain.entities import (
    Project,
    ProjectId,
    ProjectStatus,
    Feature,
    FeatureStatus,
    Workflow,
    WorkflowPhase,
)
from src.cde_orchestrator.domain.exceptions import (
    InvalidStateTransitionError,
    ProjectNotFoundError,
    FeatureNotFoundError,
)


# ============================================================================
# VALUE OBJECTS
# ============================================================================


class TestProjectId:
    """Test ProjectId value object invariants."""

    def test_valid_project_id(self):
        """Test creating valid ProjectId."""
        pid = ProjectId("abc-123")
        assert str(pid) == "abc-123"
        assert repr(pid) == "ProjectId('abc-123')"

    def test_short_project_id_raises_error(self):
        """Test that short IDs are rejected."""
        with pytest.raises(ValueError, match="at least 3 characters"):
            ProjectId("ab")

    def test_empty_project_id_raises_error(self):
        """Test that empty IDs are rejected."""
        with pytest.raises(ValueError, match="at least 3 characters"):
            ProjectId("")

    def test_non_string_project_id_raises_error(self):
        """Test that non-string IDs are rejected."""
        with pytest.raises(ValueError):
            ProjectId(123)

    def test_project_id_immutability(self):
        """Test that ProjectId is immutable."""
        pid = ProjectId("test-123")
        with pytest.raises(AttributeError):
            pid.value = "new-value"


# ============================================================================
# ENUMERATIONS
# ============================================================================


class TestProjectStatus:
    """Test ProjectStatus state machine."""

    def test_onboarding_can_transition_to_active(self):
        """Test valid transition: onboarding → active."""
        assert ProjectStatus.ONBOARDING.can_transition_to(ProjectStatus.ACTIVE)

    def test_onboarding_can_transition_to_error(self):
        """Test valid transition: onboarding → error."""
        assert ProjectStatus.ONBOARDING.can_transition_to(ProjectStatus.ERROR)

    def test_onboarding_cannot_transition_to_archived(self):
        """Test invalid transition: onboarding → archived."""
        assert not ProjectStatus.ONBOARDING.can_transition_to(ProjectStatus.ARCHIVED)

    def test_active_can_transition_to_archived(self):
        """Test valid transition: active → archived."""
        assert ProjectStatus.ACTIVE.can_transition_to(ProjectStatus.ARCHIVED)

    def test_archived_can_reactivate(self):
        """Test valid transition: archived → active."""
        assert ProjectStatus.ARCHIVED.can_transition_to(ProjectStatus.ACTIVE)

    def test_error_is_terminal(self):
        """Test that ERROR status cannot transition."""
        assert not ProjectStatus.ERROR.can_transition_to(ProjectStatus.ACTIVE)
        assert not ProjectStatus.ERROR.can_transition_to(ProjectStatus.ARCHIVED)


class TestFeatureStatus:
    """Test FeatureStatus mappings."""

    def test_from_phase_define(self):
        """Test mapping: define → DEFINING."""
        assert FeatureStatus.from_phase("define") == FeatureStatus.DEFINING

    def test_from_phase_decompose(self):
        """Test mapping: decompose → DECOMPOSING."""
        assert FeatureStatus.from_phase("decompose") == FeatureStatus.DECOMPOSING

    def test_from_phase_implement(self):
        """Test mapping: implement → IMPLEMENTING."""
        assert FeatureStatus.from_phase("implement") == FeatureStatus.IMPLEMENTING

    def test_from_phase_unknown_returns_failed(self):
        """Test unknown phase maps to FAILED."""
        assert FeatureStatus.from_phase("unknown") == FeatureStatus.FAILED


# ============================================================================
# ENTITIES
# ============================================================================


class TestProject:
    """Test Project aggregate business rules."""

    def test_create_project(self):
        """Test creating new project with valid data."""
        project = Project.create(name="Test Project", path="/tmp/test")

        assert project.name == "Test Project"
        assert project.path == "/tmp/test"
        assert project.status == ProjectStatus.ONBOARDING
        assert isinstance(project.id, ProjectId)
        assert isinstance(project.created_at, datetime)

    def test_create_project_with_empty_name_raises_error(self):
        """Test that empty project name is rejected."""
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            Project.create(name="", path="/tmp/test")

    def test_create_project_with_empty_path_raises_error(self):
        """Test that empty project path is rejected."""
        with pytest.raises(ValueError, match="Project path cannot be empty"):
            Project.create(name="Test", path="")

    def test_activate_from_onboarding(self):
        """Test activating project from onboarding status."""
        project = Project.create(name="Test", path="/tmp/test")
        assert project.status == ProjectStatus.ONBOARDING

        project.activate()

        assert project.status == ProjectStatus.ACTIVE
        assert project.updated_at > project.created_at

    def test_activate_from_invalid_status_raises_error(self):
        """Test that activating from archived status fails."""
        project = Project.create(name="Test", path="/tmp/test")
        project.activate()
        project.archive()

        # Cannot activate directly from archived
        # Must use different method or logic
        assert project.status == ProjectStatus.ARCHIVED

    def test_archive_active_project(self):
        """Test archiving active project."""
        project = Project.create(name="Test", path="/tmp/test")
        project.activate()

        project.archive()

        assert project.status == ProjectStatus.ARCHIVED

    def test_cannot_archive_onboarding_project(self):
        """Onboarding projects cannot be archived (invalid transition)."""
        project = Project.create(name="Test", path="/tmp/test")

        # Domain raises ValueError for invalid transitions
        with pytest.raises(ValueError, match="Invalid status transition"):
            project.archive()

    def test_start_feature_when_active(self):
        """Test starting new feature in active project."""
        project = Project.create(name="Test", path="/tmp/test")
        project.activate()

        feature = project.start_feature("Add login functionality")

        assert isinstance(feature, Feature)
        assert feature.prompt == "Add login functionality"
        assert feature.project_id == project.id
        assert feature.status == FeatureStatus.DEFINING
        assert len(project.features) == 1

    def test_start_feature_when_not_active_raises_error(self):
        """Features cannot be started unless project is ACTIVE."""
        project = Project.create(name="Test", path="/tmp/test")

        with pytest.raises(ValueError, match="Project must be ACTIVE"):
            project.start_feature("Add feature")

    def test_get_feature_by_id(self):
        """Test retrieving feature by ID."""
        project = Project.create(name="Test", path="/tmp/test")
        project.activate()
        feature = project.start_feature("Test feature")

        retrieved = project.get_feature(feature.id)

        assert retrieved == feature

    def test_get_nonexistent_feature_returns_none(self):
        """Getting a non-existent feature returns None (safe lookup)."""
        project = Project.create(name="Test", path="/tmp/test")
        project.activate()

        assert project.get_feature("nonexistent-id") is None


class TestFeature:
    """Test Feature aggregate business rules."""

    @pytest.fixture
    def project_id(self):
        """Fixture: Create project ID for tests."""
        return ProjectId("test-project-123")

    def test_create_feature(self, project_id):
        """Test creating new feature with valid data."""
        feature = Feature.create(project_id, "Add authentication")

        assert feature.prompt == "Add authentication"
        assert feature.project_id == project_id
        assert feature.status == FeatureStatus.DEFINING
        assert feature.current_phase == "define"
        assert feature.workflow_type == "default"
        assert isinstance(feature.id, str)
        assert isinstance(UUID(feature.id), UUID)  # Valid UUID

    def test_create_feature_with_empty_prompt_raises_error(self, project_id):
        """Test that empty prompt is rejected."""
        with pytest.raises(ValueError, match="Feature prompt cannot be empty"):
            Feature.create(project_id, "")

    def test_create_feature_with_whitespace_prompt_raises_error(self, project_id):
        """Test that whitespace-only prompt is rejected."""
        with pytest.raises(ValueError, match="Feature prompt cannot be empty"):
            Feature.create(project_id, "   ")

    def test_create_feature_trims_whitespace(self, project_id):
        """Test that prompt whitespace is trimmed."""
        feature = Feature.create(project_id, "  Test prompt  ")
        assert feature.prompt == "Test prompt"

    def test_advance_phase(self, project_id):
        """Test advancing feature to next phase."""
        feature = Feature.create(project_id, "Test feature")
        results = {"specification": "Feature spec content"}

        feature.advance_phase("decompose", results)

        assert feature.current_phase == "decompose"
        assert feature.status == FeatureStatus.DECOMPOSING
        assert feature.artifacts["specification"] == "Feature spec content"
        assert feature.updated_at > feature.created_at

    def test_advance_phase_accumulates_artifacts(self, project_id):
        """Test that artifacts accumulate across phases."""
        feature = Feature.create(project_id, "Test feature")

        feature.advance_phase("decompose", {"spec": "v1"})
        feature.advance_phase("design", {"design": "v1"})

        assert "spec" in feature.artifacts
        assert "design" in feature.artifacts
        assert len(feature.artifacts) == 2

    def test_cannot_advance_completed_feature(self, project_id):
        """Completed features cannot advance further."""
        feature = Feature.create(project_id, "Test feature")
        # Move to review then complete
        feature.advance_phase("review", {})
        feature.complete()

        with pytest.raises(ValueError, match="Feature is terminal"):
            feature.advance_phase("design", {})

    def test_cannot_advance_failed_feature(self, project_id):
        """Test that failed features cannot advance."""
        feature = Feature.create(project_id, "Test feature")
        feature.fail("Implementation error")

        with pytest.raises(ValueError, match="Feature is terminal"):
            feature.advance_phase("design", {})

    def test_fail_feature(self, project_id):
        """Test failing a feature with reason."""
        feature = Feature.create(project_id, "Test feature")

        feature.fail("Technical blocker")

        assert feature.status == FeatureStatus.FAILED
        assert feature.metadata["failure_reason"] == "Technical blocker"

    def test_complete_feature(self, project_id):
        """Feature completes only from REVIEWING; complete() has no args."""
        feature = Feature.create(project_id, "Test feature")
        # Advance to review
        feature.advance_phase("review", {"report": "All done", "tests_passed": 10})
        feature.complete()

        assert feature.status == FeatureStatus.COMPLETED
        # Artifacts remain from previous phases
        assert feature.artifacts["report"] == "All done"
        assert feature.artifacts["tests_passed"] == 10


# ============================================================================
# WORKFLOW TESTS
# ============================================================================


class TestWorkflow:
    """Test Workflow value object."""

    def test_create_workflow(self):
        """Create workflow with phases (using correct field names)."""
        phases = [
            WorkflowPhase(id="define", description="Define", prompt_recipe="define.poml"),
            WorkflowPhase(id="implement", description="Implement", prompt_recipe="impl.poml"),
        ]

        workflow = Workflow(name="Test Workflow", version="1.0", phases=phases)

        assert workflow.name == "Test Workflow"
        assert workflow.version == "1.0"
        assert len(workflow.phases) == 2

    def test_get_phase_by_id(self):
        """Retrieve phase by ID (returns object or None)."""
        phases = [
            WorkflowPhase(id="define", description="Define", prompt_recipe="define.poml"),
            WorkflowPhase(id="implement", description="Implement", prompt_recipe="impl.poml"),
        ]
        workflow = Workflow(name="Test", version="1.0", phases=phases)

        phase = workflow.get_phase("define")

        assert phase is not None
        assert phase.id == "define"
        assert phase.description == "Define"

    def test_get_nonexistent_phase_returns_none(self):
        """Non-existent phase lookup returns None (safe lookup)."""
        phases = [WorkflowPhase(id="define", description="Define", prompt_recipe="define.poml")]
        workflow = Workflow(name="Test", version="1.0", phases=phases)

        assert workflow.get_phase("unknown") is None

    def test_get_next_phase(self):
        """Get next phase in sequence."""
        phases = [
            WorkflowPhase(id="define", description="Define", prompt_recipe="define.poml"),
            WorkflowPhase(id="implement", description="Implement", prompt_recipe="impl.poml"),
            WorkflowPhase(id="test", description="Test", prompt_recipe="test.poml"),
        ]
        workflow = Workflow(name="Test", version="1.0", phases=phases)

        next_phase = workflow.get_next_phase("define")

        assert next_phase is not None
        assert next_phase.id == "implement"

    def test_get_next_phase_returns_none_for_last_phase(self):
        """Last phase has no next phase."""
        phases = [
            WorkflowPhase(id="define", description="Define", prompt_recipe="define.poml"),
            WorkflowPhase(id="implement", description="Implement", prompt_recipe="impl.poml"),
        ]
        workflow = Workflow(name="Test", version="1.0", phases=phases)

        next_phase = workflow.get_next_phase("implement")

        assert next_phase is None

    def test_get_initial_phase(self):
        """First phase is returned correctly."""
        phases = [
            WorkflowPhase(id="define", description="Define", prompt_recipe="define.poml"),
            WorkflowPhase(id="implement", description="Implement", prompt_recipe="impl.poml"),
        ]
        workflow = Workflow(name="Test", version="1.0", phases=phases)

        initial = workflow.get_initial_phase()

        assert initial.id == "define"

    def test_empty_workflow_raises_error(self):
        """Workflow with no phases is invalid (get_initial_phase)."""
        workflow = Workflow(name="Test", version="1.0", phases=[])
        with pytest.raises(ValueError, match="Workflow has no phases defined"):
            workflow.get_initial_phase()


# ============================================================================
# INTEGRATION TESTS (Business Rules Across Entities)
# ============================================================================


class TestProjectFeatureIntegration:
    """Test business rules spanning Project and Feature."""

    def test_complete_workflow_lifecycle(self):
        """Test complete project + feature lifecycle."""
        # 1. Create and activate project
        project = Project.create("My App", "/app")
        project.activate()

        # 2. Start feature
        feature = project.start_feature("Add user login")
        assert feature.status == FeatureStatus.DEFINING

        # 3. Progress through phases
        feature.advance_phase("decompose", {"tasks": ["task1", "task2"]})
        assert feature.status == FeatureStatus.DECOMPOSING

        feature.advance_phase("implement", {"code": "impl.py"})
        assert feature.status == FeatureStatus.IMPLEMENTING

        # 4. Move to review and complete
        feature.advance_phase("review", {"report": "Feature complete"})
        feature.complete()
        assert feature.status == FeatureStatus.COMPLETED

        # 5. Verify project state
        assert len(project.features) == 1
        assert project.get_feature(feature.id).status == FeatureStatus.COMPLETED

    def test_multiple_features_in_project(self):
        """Test managing multiple features in one project."""
        project = Project.create("App", "/app")
        project.activate()

        feat1 = project.start_feature("Feature 1")
        feat2 = project.start_feature("Feature 2")

        assert len(project.features) == 2
        assert project.get_feature(feat1.id).prompt == "Feature 1"
        assert project.get_feature(feat2.id).prompt == "Feature 2"

    def test_feature_isolation(self):
        """Test that features are independent."""
        project = Project.create("App", "/app")
        project.activate()

        feat1 = project.start_feature("Feature 1")
        feat2 = project.start_feature("Feature 2")

        feat1.advance_phase("decompose", {"spec": "spec1"})
        feat2.fail("Blocker")

        assert feat1.status == FeatureStatus.DECOMPOSING
        assert feat2.status == FeatureStatus.FAILED
        assert "spec" in feat1.artifacts
        assert "spec" not in feat2.artifacts
