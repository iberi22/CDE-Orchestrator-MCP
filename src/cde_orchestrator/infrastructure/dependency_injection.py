# src/cde_orchestrator/infrastructure/dependency_injection.py
import logging
from typing import Optional

from ..adapters.recipe.filesystem_recipe_repository import FileSystemRecipeRepository
from ..adapters.state.filesystem_state_repository import FileSystemStateRepository
from ..adapters.workflow.yaml_workflow_repository import YAMLWorkflowRepository
from ..application.use_cases.manage_state import ManageStateUseCase
from ..application.use_cases.select_workflow import SelectWorkflowUseCase
from ..domain.services.recipe_service import RecipeService

logger = logging.getLogger(__name__)


class DIContainer:
    def __init__(self, state_file_path: str, workflow_file_path: str, recipe_dir: str):
        from pathlib import Path

        # Convert strings to Path objects
        state_path = (
            Path(state_file_path)
            if isinstance(state_file_path, str)
            else state_file_path
        )
        workflow_path = (
            Path(workflow_file_path)
            if isinstance(workflow_file_path, str)
            else workflow_file_path
        )
        recipe_path = Path(recipe_dir) if isinstance(recipe_dir, str) else recipe_dir

        # Create directories if they don't exist
        state_path.parent.mkdir(parents=True, exist_ok=True)
        recipe_path.mkdir(parents=True, exist_ok=True)

        # Repositories (with null checks)
        self.state_repository = FileSystemStateRepository(state_path)

        # Workflow repository - only create if workflow file exists
        self._workflow_path = workflow_path
        self._workflow_repository: Optional[YAMLWorkflowRepository] = None

        self.recipe_repository = FileSystemRecipeRepository(recipes_dir=recipe_path)

        # Services
        self.recipe_service = RecipeService()

        # Use Cases
        self.manage_state_use_case = ManageStateUseCase(
            state_store=self.state_repository
        )

        # SelectWorkflowUseCase needs workflow patterns
        workflow_patterns = {
            "quick-fix": [r"quick", r"fix", r"typo", r"bug.*trivial"],
            "research": [r"research", r"investigate", r"analyze", r"explore"],
            "documentation": [r"document", r"guide", r"spec", r"readme"],
            "refactor": [r"refactor", r"improve", r"optimize", r"clean"],
            "hotfix": [r"hotfix", r"emergency", r"critical"],
            "standard": [r"feature", r"implement", r"add", r"create"],
        }
        self.select_workflow_use_case = SelectWorkflowUseCase(
            workflow_patterns=workflow_patterns
        )

    def _get_workflow_repository(self) -> YAMLWorkflowRepository:
        """Lazy-load workflow repository, creating a default if needed."""
        if self._workflow_repository is None:
            if not self._workflow_path.exists():
                logger.warning(
                    f"Workflow file not found at {self._workflow_path}, creating default"
                )
                self._workflow_path.parent.mkdir(parents=True, exist_ok=True)
                # Create a minimal default workflow
                import yaml

                default_workflow = {
                    "name": "default_workflow",
                    "phases": [
                        {"id": "define", "title": "Define"},
                        {"id": "decompose", "title": "Decompose"},
                        {"id": "design", "title": "Design"},
                        {"id": "implement", "title": "Implement"},
                        {"id": "test", "title": "Test"},
                        {"id": "review", "title": "Review"},
                    ],
                }
                with open(self._workflow_path, "w") as f:
                    yaml.dump(default_workflow, f)

            self._workflow_repository = YAMLWorkflowRepository(
                workflow_path=self._workflow_path
            )

        return self._workflow_repository


# Global container instance
try:
    container = DIContainer(
        state_file_path=".cde/state.json",
        workflow_file_path=".cde/workflow.yml",
        recipe_dir=".cde/recipes/",
    )
except Exception as e:
    logger.error(f"Failed to initialize DIContainer: {e}")
    # Create a fallback container
    import sys

    sys.exit(1)
