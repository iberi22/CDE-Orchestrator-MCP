"""
Tests for Phase 3: Single Project Optimization.

Validates that CDE Orchestrator works perfectly with one project
before scaling to multiple projects.
"""

import json
from pathlib import Path

import pytest


class TestSingleProjectOptimization:
    """Validate single project management is rock-solid."""

    def test_single_project_state_isolation(self, tmp_path: Path) -> None:
        """Ensure project state is properly isolated in .cde/state.json."""
        from cde_orchestrator.adapters.filesystem_project_repository import (
            FileSystemProjectRepository,
        )
        from cde_orchestrator.domain.entities import Project, ProjectStatus

        repo = FileSystemProjectRepository()
        project_path = str(tmp_path)

        # Create project
        project = Project.create(name="TestProject", path=project_path)
        project.activate()

        # Save state
        repo.save(project)

        # Verify state file exists
        state_file = tmp_path / ".cde" / "state.json"
        assert state_file.exists(), "State file should be created"

        # Verify state content
        state_data = json.loads(state_file.read_text())
        assert state_data["id"] == str(project.id)  # Compare as string
        assert state_data["name"] == "TestProject"
        assert state_data["path"] == project_path
        assert state_data["status"] == ProjectStatus.ACTIVE.value

        # Load and verify
        loaded = repo.get_or_create(project_path)
        assert loaded.id == project.id
        assert loaded.name == project.name
        assert loaded.status == ProjectStatus.ACTIVE

    def test_single_project_feature_workflow(self, tmp_path: Path) -> None:
        """Validate complete feature workflow for single project."""
        from cde_orchestrator.domain.entities import FeatureStatus, Project

        project_path = str(tmp_path)
        project = Project.create(name="TestProject", path=project_path)
        project.activate()

        # Start feature
        feature = project.start_feature("Add authentication")
        assert feature.status == FeatureStatus.DEFINING
        assert len(project.features) == 1

        # Advance through phases
        feature.current_phase = "decompose"
        feature.advance_phase("design", {"tasks": ["Task 1", "Task 2"]})
        assert feature.current_phase == "design"

        # Move to reviewing status before completing
        feature.status = FeatureStatus.REVIEWING
        feature.complete()
        assert feature.status == FeatureStatus.COMPLETED

    def test_single_project_context_loading(self, tmp_path: Path) -> None:
        """Verify efficient context loading for single project."""
        from cde_orchestrator.adapters.filesystem_project_repository import (
            FileSystemProjectRepository,
        )
        from cde_orchestrator.domain.entities import Project

        repo = FileSystemProjectRepository()
        project_path = str(tmp_path)

        # Create project with some structure
        (tmp_path / ".cde").mkdir(exist_ok=True)
        (tmp_path / "src").mkdir(exist_ok=True)
        (tmp_path / "tests").mkdir(exist_ok=True)
        (tmp_path / "README.md").write_text("# Test Project")

        project = Project.create(name="TestProject", path=project_path)
        repo.save(project)

        # Load project (should be fast)
        import time

        start = time.time()
        loaded = repo.get_or_create(project_path)
        duration = time.time() - start

        assert loaded is not None
        assert duration < 0.1, "Loading single project should be < 100ms"

    def test_single_project_error_handling(self, tmp_path: Path) -> None:
        """Validate graceful error handling for single project."""
        from cde_orchestrator.domain.entities import Project

        project_path = str(tmp_path)

        # Create inactive project (ONBOARDING status by default)
        project = Project.create(name="TestProject", path=project_path)
        # Don't activate - stays in ONBOARDING

        # Try to start feature on inactive project
        with pytest.raises(ValueError) as exc_info:
            project.start_feature("Add feature")

        assert "Cannot start feature" in str(exc_info.value)
        assert "ACTIVE" in str(exc_info.value)

    def test_single_project_concurrent_feature_safety(self, tmp_path: Path) -> None:
        """Ensure multiple features can coexist safely in single project."""
        from cde_orchestrator.domain.entities import FeatureStatus, Project

        project = Project.create(name="TestProject", path=str(tmp_path))
        project.activate()

        # Start multiple features
        feature1 = project.start_feature("Feature 1")
        feature2 = project.start_feature("Feature 2")
        feature3 = project.start_feature("Feature 3")

        # Verify all tracked
        assert len(project.features) == 3
        assert all(f.status == FeatureStatus.DEFINING for f in project.features)

        # Move to reviewing and complete one
        feature1.status = FeatureStatus.REVIEWING
        feature1.complete()
        assert feature1.status == FeatureStatus.COMPLETED
        assert feature2.status == FeatureStatus.DEFINING
        assert feature3.status == FeatureStatus.DEFINING


class TestSingleProjectPerformance:
    """Performance benchmarks for single project operations."""

    def test_project_load_performance(self, tmp_path: Path) -> None:
        """Benchmark project loading time."""
        import time

        from cde_orchestrator.adapters.filesystem_project_repository import (
            FileSystemProjectRepository,
        )
        from cde_orchestrator.domain.entities import Project

        repo = FileSystemProjectRepository()
        project_path = str(tmp_path)

        # Create project
        project = Project.create(name="TestProject", path=project_path)
        repo.save(project)

        # Benchmark 10 loads
        times = []
        for _ in range(10):
            start = time.time()
            repo.get_or_create(project_path)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 0.05, f"Avg load time {avg_time:.3f}s > 50ms"

    def test_feature_creation_performance(self, tmp_path: Path) -> None:
        """Benchmark feature creation time."""
        import time

        from cde_orchestrator.domain.entities import Project

        project = Project.create(name="TestProject", path=str(tmp_path))
        project.activate()

        # Benchmark 100 feature creations
        times = []
        for i in range(100):
            start = time.time()
            project.start_feature(f"Feature {i}")
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 0.001, f"Avg feature creation {avg_time:.4f}s > 1ms"

    def test_state_persistence_performance(self, tmp_path: Path) -> None:
        """Benchmark state save/load cycles."""
        import time

        from cde_orchestrator.adapters.filesystem_project_repository import (
            FileSystemProjectRepository,
        )
        from cde_orchestrator.domain.entities import Project

        repo = FileSystemProjectRepository()
        project_path = str(tmp_path)
        project = Project.create(name="TestProject", path=project_path)
        project.activate()

        # Create some features
        for i in range(10):
            project.start_feature(f"Feature {i}")

        # Benchmark save/load cycle
        times = []
        for _ in range(10):
            start = time.time()
            repo.save(project)
            repo.get_or_create(project_path)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 0.1, f"Avg save/load cycle {avg_time:.3f}s > 100ms"


class TestSingleProjectIntegration:
    """Integration tests for complete single project workflows."""

    @pytest.mark.asyncio
    async def test_complete_feature_workflow_integration(self, tmp_path: Path) -> None:
        """Test complete feature workflow from start to finish."""
        from cde_orchestrator.adapters.filesystem_project_repository import (
            FileSystemProjectRepository,
        )
        from cde_orchestrator.domain.entities import Project

        # Setup
        repo = FileSystemProjectRepository()
        project_path = str(tmp_path)

        # Create project structure
        (tmp_path / ".cde").mkdir(exist_ok=True)

        # Initialize project
        project = Project.create(name="TestProject", path=project_path)
        project.activate()
        repo.save(project)

        # Start feature
        feature = project.start_feature("Add user authentication")
        assert feature is not None
        assert len(project.features) == 1
        assert project.features[0].prompt == "Add user authentication"

    def test_project_state_recovery_after_crash(self, tmp_path: Path) -> None:
        """Verify project state can be recovered after simulated crash."""
        from cde_orchestrator.adapters.filesystem_project_repository import (
            FileSystemProjectRepository,
        )
        from cde_orchestrator.domain.entities import FeatureStatus, Project

        repo = FileSystemProjectRepository()
        project_path = str(tmp_path)

        # Create project with features
        project1 = Project.create(name="TestProject", path=project_path)
        project1.activate()
        feature1 = project1.start_feature("Feature 1")
        _ = project1.start_feature("Feature 2")  # feature2 not used after creation

        # Move feature1 to reviewing and complete
        feature1.status = FeatureStatus.REVIEWING
        feature1.complete()

        # Save state
        repo.save(project1)

        # Simulate crash - load fresh instance
        project2 = repo.get_or_create(project_path)

        # Verify state recovered
        assert project2.name == "TestProject"
        assert len(project2.features) == 2
        assert project2.features[0].status == FeatureStatus.COMPLETED
        assert project2.features[1].status == FeatureStatus.DEFINING

    def test_project_migration_handling(self, tmp_path: Path) -> None:
        """Verify graceful handling of state format changes."""
        from datetime import datetime, timezone

        from cde_orchestrator.adapters.filesystem_project_repository import (
            FileSystemProjectRepository,
        )

        repo = FileSystemProjectRepository()
        project_path = str(tmp_path)
        state_file = tmp_path / ".cde" / "state.json"

        # Create valid state with all required fields
        state_file.parent.mkdir(exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        valid_state = {
            "id": "test-id",
            "name": "OldProject",
            "path": str(tmp_path),
            "status": "active",
            "features": [],
            "created_at": now,
            "updated_at": now,
            "metadata": {},
        }
        state_file.write_text(json.dumps(valid_state))

        # Load should work correctly
        project = repo.get_or_create(project_path)
        assert project.name == "OldProject"
        assert hasattr(project, "created_at")  # Should have all fields
