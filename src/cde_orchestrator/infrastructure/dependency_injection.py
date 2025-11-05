# src/cde_orchestrator/infrastructure/dependency_injection.py
from ..adapters.state.filesystem_state_repository import FileSystemStateRepository
from ..adapters.workflow.yaml_workflow_repository import YAMLWorkflowRepository
from ..adapters.recipe.filesystem_recipe_repository import FileSystemRecipeRepository
from ..domain.services.recipe_service import RecipeService
from ..application.use_cases.manage_state import ManageStateUseCase
from ..application.use_cases.select_workflow import SelectWorkflowUseCase

class DIContainer:
    def __init__(self, state_file_path: str, workflow_file_path: str, recipe_dir: str):
        # Repositories
        self.state_repository = FileSystemStateRepository(file_path=state_file_path)
        self.workflow_repository = YAMLWorkflowRepository(file_path=workflow_file_path)
        self.recipe_repository = FileSystemRecipeRepository(recipe_dir=recipe_dir)

        # Services
        self.recipe_service = RecipeService()

        # Use Cases
        self.manage_state_use_case = ManageStateUseCase(state_repository=self.state_repository)
        self.select_workflow_use_case = SelectWorkflowUseCase(
            workflow_repository=self.workflow_repository,
            recipe_service=self.recipe_service,
            recipe_repository=self.recipe_repository
        )

# Global container instance
container = DIContainer(
    state_file_path=".cde_state.json",
    workflow_file_path="specs/workflows/default_workflow.yaml",
    recipe_dir="specs/recipes/"
)
