# tests/integration/test_feature_workflow_e2e.py
"""
End-to-End integration tests for the complete feature workflow.
Tests the full cycle: start_feature -> submit_work -> completion.
"""

from pathlib import Path

import pytest

from cde_orchestrator.application.use_cases.start_feature import (
    StartFeatureUseCase,
)
from cde_orchestrator.application.use_cases.submit_work import (
    SubmitWorkUseCase,
)
from cde_orchestrator.domain.entities import FeatureStatus, Project


class MockProjectRepository:
    """Mock project repository for testing."""

    def __init__(self):
        self.projects = {}

    async def get_or_create(self, project_path: str) -> Project:
        if project_path not in self.projects:
            project = Project.create(
                name="Test Project",
                path=project_path,
            )
            project.activate()
            self.projects[project_path] = project
        return self.projects[project_path]

    async def save(self, project: Project) -> None:
        self.projects[project.path] = project


class MockWorkflowRepository:
    """Mock workflow repository for testing."""

    def __init__(self):
        from cde_orchestrator.domain.entities import Workflow, WorkflowPhase

        self.workflow = Workflow(
            name="test-workflow",
            version="1.0",
            phases=[
                WorkflowPhase(
                    id="define",
                    description="Define the feature",
                    prompt_recipe="prompts/define.md",
                    outputs=["specification"],
                ),
                WorkflowPhase(
                    id="implement",
                    description="Implement the feature",
                    prompt_recipe="prompts/implement.md",
                    inputs=["specification"],
                    outputs=["code"],
                ),
                WorkflowPhase(
                    id="review",
                    description="Review the implementation",
                    prompt_recipe="prompts/review.md",
                    inputs=["code"],
                    outputs=["review_notes"],
                ),
            ],
        )

    async def load_workflow(self):
        return self.workflow


class MockPromptRenderer:
    """Mock prompt renderer for testing."""

    async def load_and_prepare(self, template_path: Path, context: dict) -> str:
        return f"Mock prompt for phase: {context.get('CURRENT_PHASE', 'unknown')}"


@pytest.mark.asyncio
class TestFeatureWorkflowE2E:
    """End-to-end tests for feature workflow."""

    async def test_complete_feature_workflow(self, tmp_path):
        """Test the complete workflow from start to completion."""
        # Setup
        project_path = str(tmp_path / "test_project")
        Path(project_path).mkdir(parents=True, exist_ok=True)
        workflow_file = Path(project_path) / ".cde" / "workflow.yml"
        workflow_file.parent.mkdir(parents=True, exist_ok=True)
        workflow_file.touch()

        project_repo = MockProjectRepository()
        workflow_repo_factory = lambda path: MockWorkflowRepository()
        prompt_renderer = MockPromptRenderer()

        start_use_case = StartFeatureUseCase(
            project_repo, workflow_repo_factory, prompt_renderer
        )
        submit_use_case = SubmitWorkUseCase(
            project_repo, workflow_repo_factory, prompt_renderer
        )

        # Step 1: Start feature
        start_result = await start_use_case.execute(
            project_path=project_path,
            user_prompt="Add user authentication system",
            workflow_type="standard",
            recipe_id="ai-engineer",
        )

        assert start_result["status"] == "success"
        assert "feature_id" in start_result
        assert start_result["phase"] == "define"
        assert "Mock prompt for phase: define" in start_result["prompt"]

        feature_id = start_result["feature_id"]

        # Step 2: Submit define phase
        define_results = {
            "specification": "# Authentication System\n\nUser login with JWT tokens..."
        }

        submit_result = await submit_use_case.execute(
            project_path=project_path,
            feature_id=feature_id,
            phase_id="define",
            results=define_results,
        )

        assert submit_result["status"] == "ok"
        assert submit_result["phase"] == "implement"
        assert "Mock prompt for phase: implement" in submit_result["prompt"]

        # Step 3: Submit implement phase
        implement_results = {
            "code": "class AuthService:\n    def login(self, username, password):\n        pass"
        }

        submit_result = await submit_use_case.execute(
            project_path=project_path,
            feature_id=feature_id,
            phase_id="implement",
            results=implement_results,
        )

        assert submit_result["status"] == "ok"
        assert submit_result["phase"] == "review"

        # Step 4: Submit review phase (final)
        review_results = {"review_notes": "Code looks good, approved"}

        submit_result = await submit_use_case.execute(
            project_path=project_path,
            feature_id=feature_id,
            phase_id="review",
            results=review_results,
        )

        assert submit_result["status"] == "completed"
        assert submit_result["feature_id"] == feature_id

        # Verify final state
        project = await project_repo.get_or_create(project_path)
        feature = project.get_feature(feature_id)

        assert feature is not None
        assert feature.status == FeatureStatus.COMPLETED
        assert "specification" in feature.artifacts
        assert "code" in feature.artifacts
        assert "review_notes" in feature.artifacts

    async def test_feature_workflow_with_validation(self, tmp_path):
        """Test workflow with input validation."""
        project_path = str(tmp_path / "test_project")
        Path(project_path).mkdir(parents=True, exist_ok=True)
        workflow_file = Path(project_path) / ".cde" / "workflow.yml"
        workflow_file.parent.mkdir(parents=True, exist_ok=True)
        workflow_file.touch()

        project_repo = MockProjectRepository()
        workflow_repo_factory = lambda path: MockWorkflowRepository()
        prompt_renderer = MockPromptRenderer()

        start_use_case = StartFeatureUseCase(
            project_repo, workflow_repo_factory, prompt_renderer
        )

        # Test with invalid prompt (too short)
        with pytest.raises(Exception):  # Pydantic ValidationError
            await start_use_case.execute(
                project_path=project_path,
                user_prompt="Short",  # Less than 10 characters
                workflow_type="standard",
            )

        # Test with valid prompt
        result = await start_use_case.execute(
            project_path=project_path,
            user_prompt="Add comprehensive user authentication",
            workflow_type="standard",
        )

        assert result["status"] == "success"

    async def test_multiple_features_in_project(self, tmp_path):
        """Test managing multiple features in the same project."""
        project_path = str(tmp_path / "test_project")
        Path(project_path).mkdir(parents=True, exist_ok=True)
        workflow_file = Path(project_path) / ".cde" / "workflow.yml"
        workflow_file.parent.mkdir(parents=True, exist_ok=True)
        workflow_file.touch()

        project_repo = MockProjectRepository()
        workflow_repo_factory = lambda path: MockWorkflowRepository()
        prompt_renderer = MockPromptRenderer()

        start_use_case = StartFeatureUseCase(
            project_repo, workflow_repo_factory, prompt_renderer
        )

        # Start first feature
        result1 = await start_use_case.execute(
            project_path=project_path,
            user_prompt="Add user authentication system",
        )

        # Start second feature
        result2 = await start_use_case.execute(
            project_path=project_path,
            user_prompt="Add payment processing module",
        )

        # Verify both features exist
        project = await project_repo.get_or_create(project_path)
        assert len(project.features) == 2
        assert result1["feature_id"] != result2["feature_id"]

        # Verify both are active
        active_features = project.get_active_features()
        assert len(active_features) == 2
