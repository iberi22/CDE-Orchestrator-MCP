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
    async def get_by_id(self, project_id: ProjectId) -> Optional[Project]:
        pass

    @abstractmethod
    async def get_by_path(self, path: str) -> Optional[Project]:
        pass

    @abstractmethod
    async def get_or_create(self, path: str, name: Optional[str] = None) -> Project:
        pass

    @abstractmethod
    async def list_all(self, limit: Optional[int] = None) -> List[Project]:
        pass

    @abstractmethod
    def list_all_async(self, limit: Optional[int] = None) -> AsyncIterator[Project]:
        """Async generator - use 'def' not 'async def' for abstract declaration"""
        pass

    @abstractmethod
    async def save(self, project: Project) -> None:
        pass

    @abstractmethod
    async def delete(self, project_id: ProjectId) -> None:
        pass

    @abstractmethod
    async def delete_by_path(self, path: str) -> None:
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
    async def load_and_prepare(self, poml_path: Path, context: Dict[str, Any]) -> str:
        pass


class IStateStore(ABC):
    """
    Port for loading and saving state.
    """

    @abstractmethod
    async def load_state(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def save_state(self, state: Dict[str, Any]) -> None:
        pass


class IWorkflowRepository(ABC):
    """
    Port for loading workflow definitions.
    """

    @abstractmethod
    async def load_workflow(self) -> Workflow:
        pass


class IRecipeRepository(ABC):
    """
    Port for loading recipe definitions.
    """

    @abstractmethod
    async def list_all(self) -> List[Recipe]:
        pass


class IRecipeDownloader(ABC):
    """
    Port for downloading recipes from external sources (GitHub, etc.).
    """

    @abstractmethod
    async def download_file(self, repo_url: str, branch: str, file_path: str) -> str:
        """
        Download a single file from a repository.

        Args:
            repo_url: Full repository URL (e.g., https://github.com/user/repo)
            branch: Branch name (e.g., "main", "master")
            file_path: Path to file within repo (e.g., "poml/engineering/ai-engineer.poml")

        Returns:
            File content as string

        Raises:
            Exception: If download fails
        """
        pass

    @abstractmethod
    async def download_directory(
        self, repo_url: str, branch: str, dir_path: str
    ) -> Dict[str, str]:
        """
        Download all files from a directory.

        Args:
            repo_url: Full repository URL
            branch: Branch name
            dir_path: Directory path within repo

        Returns:
            Dict mapping file_path -> content
        """
        pass
