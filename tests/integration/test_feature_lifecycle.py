"""
Integration tests for the complete Feature Lifecycle (Start -> Submit -> Complete).
"""

import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from cde_orchestrator.domain.entities import FeatureStatus, ProjectStatus
from cde_orchestrator.infrastructure.dependency_injection import DIContainer


@pytest.fixture
def temp_project_env():
    """Setup a temporary project environment with necessary CDE files."""
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir)
    cde_path = project_path / ".cde"
    cde_path.mkdir()

    # Create prompts directory
    prompts_dir = cde_path / "prompts"
    prompts_dir.mkdir()

    # Create a dummy define.poml
    (prompts_dir / "define.poml").write_text(
        "User Request: {{USER_PROMPT}}\nProject: {{PROJECT_NAME}}"
    )

    # Create a minimal workflow.yml
    workflow_data = {
        "name": "test_workflow",
        "version": "1.0.0",
        "phases": [
            {
                "id": "define",
                "description": "Define phase",
                "handler": "human_input",
                "prompt_recipe": ".cde/prompts/define.poml",
                "outputs": [{"type": "markdown", "path": "specs/features/feature.md"}],
            },
            {
                "id": "implement",
                "description": "Implement phase",
                "handler": "agent",
                "prompt_recipe": ".cde/prompts/define.poml",
                "outputs": [{"type": "code", "path": "src/"}],
            },
            {
                "id": "review",
                "description": "Review phase",
                "handler": "human_input",
                "prompt_recipe": ".cde/prompts/define.poml",
                "outputs": [{"type": "report", "path": "reports/review.md"}],
            },
        ],
    }

    with open(cde_path / "workflow.yml", "w") as f:
        yaml.dump(workflow_data, f)

    yield project_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_feature_lifecycle_start_to_submit(temp_project_env):
    """
    Test the full flow:
    1. Start a feature
    2. Verify state
    3. Submit work for the first phase
    4. Verify transition to next phase
    """
    project_path = temp_project_env
    cde_path = project_path / ".cde"

    # Initialize DI Container with temp paths
    container = DIContainer(
        state_file_path=str(cde_path / "state.json"),
        workflow_file_path=str(cde_path / "workflow.yml"),
        recipe_dir=str(cde_path / "recipes"),
    )

    # 1. Start Feature
    start_use_case = container.start_feature_use_case
    user_prompt = "Add login feature"

    start_result = await start_use_case.execute(
        project_path=str(project_path),
        user_prompt=user_prompt,
        workflow_type="standard",
        recipe_id="ai-engineer",
    )

    assert start_result["status"] == "success"
    assert "feature_id" in start_result
    assert start_result["phase"] == "define"

    feature_id = start_result["feature_id"]

    # Verify Project State
    project_repo = container.project_repository
    project = await project_repo.get_by_path(str(project_path))
    assert project is not None
    assert project.status == ProjectStatus.ACTIVE
    assert len(project.features) == 1

    feature = project.get_feature(feature_id)
    assert feature is not None
    assert feature.status == FeatureStatus.DEFINING
    assert feature.current_phase == "define"

    # 2. Submit Work (Define Phase)
    submit_use_case = container.submit_work_use_case

    submit_result = await submit_use_case.execute(
        feature_id=feature_id,
        phase_id="define",
        results={
            "specification": "Spec content",
            "files_created": ["specs/features/feature.md"],
        },
        project_path=str(project_path),
    )

    assert submit_result["status"] == "ok"
    assert submit_result["phase"] == "implement"

    # Verify State Update
    project = await project_repo.get_by_path(str(project_path))
    feature = project.get_feature(feature_id)
    assert feature.current_phase == "implement"

    # 3. Submit Work (Implement Phase)
    submit_result_impl = await submit_use_case.execute(
        feature_id=feature_id,
        phase_id="implement",
        results={"code": "print('hello')", "files_created": ["src/main.py"]},
        project_path=str(project_path),
    )

    assert submit_result_impl["status"] == "ok"
    assert submit_result_impl["phase"] == "review"

    # Verify State Update
    project = await project_repo.get_by_path(str(project_path))
    feature = project.get_feature(feature_id)
    assert feature.current_phase == "review"
    assert feature.status == FeatureStatus.REVIEWING

    # 4. Submit Work (Review Phase - Final)
    submit_result_final = await submit_use_case.execute(
        feature_id=feature_id,
        phase_id="review",
        results={"approved": True, "comments": "LGTM"},
        project_path=str(project_path),
    )

    assert submit_result_final["status"] == "completed"

    # Verify Completion
    project = await project_repo.get_by_path(str(project_path))
    feature = project.get_feature(feature_id)
    assert feature.status == FeatureStatus.COMPLETED
