# src/cde_orchestrator/domain/ports.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, AsyncGenerator, AsyncIterator, Dict, List, Optional

from cde_orchestrator.domain.entities import (
    Project,
    ProjectId,
    Recipe,
    Workflow,
    WorkflowPhase,
)
from cde_orchestrator.domain.git import Commit, Modification


class IGitAdapter(ABC):
    """
    Port for interacting with a Git repository.
    """

    @abstractmethod
    def traverse_commits(self) -> AsyncGenerator[Commit, None]:
        """Async generator - use 'def' not 'async def' for abstract declaration"""
        pass

    @abstractmethod
    async def get_modifications(self, commit_hash: str) -> List[Modification]:
        pass


class IProjectRepository(ABC):
    """
    Port for project persistence.
    """

    @abstractmethod
    def get_by_id(self, project_id: ProjectId) -> Optional[Project]:
        pass

    @abstractmethod
    def get_by_path(self, path: str) -> Optional[Project]:
        pass

    @abstractmethod
    def get_or_create(self, path: str, name: Optional[str] = None) -> Project:
        pass

    @abstractmethod
    def list_all(self, limit: Optional[int] = None) -> List[Project]:
        pass

    @abstractmethod
    def list_all_async(self, limit: Optional[int] = None) -> AsyncIterator[Project]:
        """Async generator - use 'def' not 'async def' for abstract declaration"""
        pass

    @abstractmethod
    def save(self, project: Project) -> None:
        pass

    @abstractmethod
    def delete(self, project_id: ProjectId) -> None:
        pass

    @abstractmethod
    def delete_by_path(self, path: str) -> None:
        pass


class IWorkflowEngine(ABC):
    """
    Port for workflow management.
    """

    @abstractmethod
    def detect_workflow_type(self, user_prompt: str) -> str:
        pass

    @abstractmethod
    def get_phase(self, phase_id: str) -> WorkflowPhase:
        pass

    @abstractmethod
    def get_initial_phase(self) -> WorkflowPhase:
        pass

    @abstractmethod
    def get_next_phase(self, current_phase_id: str) -> Optional[str]:
        pass

    @abstractmethod
    def get_workflow_progress(self, current_phase_id: str) -> Dict[str, Any]:
        pass


class ICodeExecutor(ABC):
    """
    Port for executing code or prompts.
    """

    @abstractmethod
    async def execute_prompt(
        self, project_path: Path, prompt: str, context: Dict[str, Any]
    ) -> Any:
        pass


class IAgentOrchestrator(ABC):
    """
    Port for orchestrating AI agents.
    """

    @abstractmethod
    async def run_agent(self, agent_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pass


class IPromptRenderer(ABC):
    """
    Port for rendering prompts.
    """

    @abstractmethod
    def load_and_prepare(self, poml_path: Path, context: Dict[str, Any]) -> str:
        pass


class IStateStore(ABC):
    """
    Port for loading and saving state.
    """

    @abstractmethod
    def load_state(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        pass


class IWorkflowRepository(ABC):
    """
    Port for loading workflow definitions.
    """

    @abstractmethod
    def load_workflow(self) -> Workflow:
        pass


class IRecipeRepository(ABC):
    """
    Port for loading recipe definitions.
    """

    @abstractmethod
    def list_all(self) -> List[Recipe]:
        pass
