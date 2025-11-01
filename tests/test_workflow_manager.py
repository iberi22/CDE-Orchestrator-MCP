import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import yaml

from src.cde_orchestrator.adapters.serialization import Workflow
from src.cde_orchestrator.adapters.workflow import WorkflowAdapter


@pytest.fixture
def workflow_file(tmp_path: Path) -> Path:
    """Creates a dummy workflow.yml file for testing."""
    workflow_data = {
        "name": "Test Workflow",
        "version": "1.0",
        "phases": [
            {
                "id": "define",
                "description": "Define the feature or bug.",
                "handler": "handle_define",
                "prompt_recipe": "prompts/define.poml",
                "outputs": [{"type": "file", "path": "output/define.txt"}],
            },
            {
                "id": "decompose",
                "description": "Decompose the work into smaller tasks.",
                "handler": "handle_decompose",
                "prompt_recipe": "prompts/decompose.poml",
                "outputs": [{"type": "file", "path": "output/decompose.txt"}],
            },
        ],
    }
    workflow_path = tmp_path / "workflow.yml"
    with open(workflow_path, "w") as f:
        yaml.dump(workflow_data, f)
    return workflow_path


def test_load_workflow(workflow_file: Path):
    """Tests that the WorkflowAdapter correctly loads a workflow.yml file."""
    manager = WorkflowAdapter(workflow_file)
    assert manager.workflow is not None
    assert isinstance(manager.workflow, Workflow)
    assert manager.workflow.name == "Test Workflow"
    assert len(manager.workflow.phases) == 2


def test_get_phase(workflow_file: Path):
    """Tests retrieving a specific phase by its ID."""
    manager = WorkflowAdapter(workflow_file)
    phase = manager.get_phase("define")
    assert phase is not None
    assert phase.id == "define"


def test_get_nonexistent_phase(workflow_file: Path):
    """Tests that getting a nonexistent phase raises a ValueError."""
    manager = WorkflowAdapter(workflow_file)
    with pytest.raises(ValueError):
        manager.get_phase("nonexistent_phase")


def test_get_initial_phase(workflow_file: Path):
    """Tests retrieving the initial phase of the workflow."""
    manager = WorkflowAdapter(workflow_file)
    initial_phase = manager.get_initial_phase()
    assert initial_phase is not None
    assert initial_phase.id == "define"
