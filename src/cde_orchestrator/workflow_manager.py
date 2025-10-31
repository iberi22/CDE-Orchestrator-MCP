# src/cde_orchestrator/workflow_manager.py
import yaml
from pathlib import Path
from .models import Workflow

class WorkflowManager:
    """Handles loading and parsing of the .cde/workflow.yml file."""

    def __init__(self, workflow_path: Path):
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found at {workflow_path}")
        self.workflow_path = workflow_path
        self.workflow = self._load_workflow()

    def _load_workflow(self) -> Workflow:
        """Loads and validates the workflow file using Pydantic models."""
        with open(self.workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        return Workflow(**data)

    def get_phase(self, phase_id: str):
        """Retrieves a specific phase by its ID."""
        for phase in self.workflow.phases:
            if phase.id == phase_id:
                return phase
        raise ValueError(f"Phase with ID '{phase_id}' not found in workflow.")

    def get_initial_phase(self):
        """Gets the very first phase of the workflow."""
        if not self.workflow.phases:
            raise ValueError("Workflow has no phases defined.")
        return self.workflow.phases[0]

