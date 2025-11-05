# src/cde_orchestrator/adapters/workflow/yaml_workflow_repository.py
from pathlib import Path
import yaml

from ...domain.entities import Workflow
from ...domain.ports import IWorkflowRepository
from ..serialization import Workflow as WorkflowModel


class YAMLWorkflowRepository(IWorkflowRepository):
    """
    Loads the workflow definition from a YAML file.
    """

    def __init__(self, workflow_path: Path):
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found at {workflow_path}")
        self._workflow_path = workflow_path

    def load_workflow(self) -> Workflow:
        """Loads and validates the workflow file using Pydantic models."""
        with open(self._workflow_path, "r") as f:
            data = yaml.safe_load(f)

        # Validate with Pydantic model first
        workflow_model = WorkflowModel(**data)

        # Convert to domain entity
        return Workflow(
            name=workflow_model.name,
            version=workflow_model.version,
            phases=[p.dict() for p in workflow_model.phases],
        )
