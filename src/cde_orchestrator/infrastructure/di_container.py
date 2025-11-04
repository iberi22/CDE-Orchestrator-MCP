# src/cde_orchestrator/infrastructure/di_container.py
from pathlib import Path

from ..adapters.state import FileSystemStateRepository
from ..adapters.workflow.yaml_workflow_repository import YAMLWorkflowRepository
from ..application.use_cases.manage_state import ManageStateUseCase
from ..application.use_cases.select_workflow import SelectWorkflowUseCase
from ..domain.ports import IStateStore, IWorkflowRepository


class DIContainer:
    """
    A simple dependency injection container for the CDE Orchestrator.
    """

    def __init__(self, cde_root: Path):
        self._cde_root = cde_root

    def get_state_store(self) -> IStateStore:
        return FileSystemStateRepository(self._cde_root / "state.json")

    def get_workflow_repository(self) -> IWorkflowRepository:
        return YAMLWorkflowRepository(self._cde_root / "workflow.yml")

    def get_manage_state_use_case(self) -> ManageStateUseCase:
        return ManageStateUseCase(self.get_state_store())

    def get_select_workflow_use_case(self) -> SelectWorkflowUseCase:
        # In a real application, the patterns would be loaded from a config file.
        workflow_patterns = {
            "web_application": ["web", "api", "frontend", "backend"],
            "data_processing": ["data", "etl", "pipeline"],
            "bug_fix": ["fix", "bug", "error"],
        }
        return SelectWorkflowUseCase(workflow_patterns)
