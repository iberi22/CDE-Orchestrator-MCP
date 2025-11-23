# src/cde_orchestrator/infrastructure/dependency_injection.py
import logging
from typing import Optional

from ..adapters.recipe.filesystem_recipe_repository import FileSystemRecipeRepository
from ..adapters.state.filesystem_state_repository import FileSystemStateRepository
from ..adapters.workflow.yaml_workflow_repository import YAMLWorkflowRepository
from ..adapters.filesystem_project_repository import FileSystemProjectRepository
from ..adapters.prompt.prompt_adapter import PromptAdapter
from ..application.use_cases.manage_state import ManageStateUseCase
from ..application.use_cases.select_workflow import SelectWorkflowUseCase
from ..application.use_cases.start_feature import StartFeatureUseCase
from ..application.use_cases.submit_work import SubmitWorkUseCase
from ..application.orchestration.skill_sourcing_use_case import SkillSourcingUseCase
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
        self.project_repository = FileSystemProjectRepository()
        self.prompt_adapter = PromptAdapter()

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

        self.start_feature_use_case = StartFeatureUseCase(
            self.project_repository,
            lambda path: YAMLWorkflowRepository(path),
            self.prompt_adapter
        )

        self.submit_work_use_case = SubmitWorkUseCase(
            self.project_repository,
            lambda path: YAMLWorkflowRepository(path),
            self.prompt_adapter
        )

        self.skill_sourcing_use_case = SkillSourcingUseCase()

    def _get_workflow_repository(self) -> YAMLWorkflowRepository:
        """Lazy-load workflow repository, creating a default if needed."""
        if self._workflow_repository is None:
            if not self._workflow_path.exists():
                logger.warning(
                    f"Workflow file not found at {self._workflow_path}, creating default"
                )
                self._workflow_path.parent.mkdir(parents=True, exist_ok=True)

                # Create prompts directory
                prompts_dir = self._workflow_path.parent / "prompts"
                prompts_dir.mkdir(exist_ok=True)

                # Create default prompt
                define_poml = prompts_dir / "define.poml"
                if not define_poml.exists():
                    define_poml.write_text(
                        """
# Define Phase
You are an expert software architect.
Your task is to define the specification for the following feature:

User Request: {{USER_PROMPT}}

Project: {{PROJECT_NAME}}
Workflow: {{WORKFLOW_TYPE}}

Please provide a detailed specification including:
1. Problem Statement
2. Proposed Solution
3. Acceptance Criteria
4. Technical Considerations
                        """.strip()
                    )

                # Create a minimal default workflow
                import yaml

                default_workflow = {
                    "name": "default_workflow",
                    "version": "1.0.0",
                    "phases": [
                        {
                            "id": "define",
                            "description": "Define the feature specification",
                            "handler": "human_input",
                            "prompt_recipe": "prompts/define.poml",
                            "outputs": [{"type": "markdown", "path": "specs/features/feature.md"}]
                        },
                        {
                            "id": "decompose",
                            "description": "Break down into tasks",
                            "handler": "agent",
                            "prompt_recipe": "prompts/define.poml", # Reusing for demo
                            "outputs": [{"type": "markdown", "path": "specs/tasks/tasks.md"}]
                        },
                        {
                            "id": "design",
                            "description": "Technical design",
                            "handler": "agent",
                            "prompt_recipe": "prompts/define.poml",
                            "outputs": [{"type": "markdown", "path": "specs/design/design.md"}]
                        },
                        {
                            "id": "implement",
                            "description": "Implement code",
                            "handler": "agent",
                            "prompt_recipe": "prompts/define.poml",
                            "outputs": [{"type": "code", "path": "src/"}]
                        },
                        {
                            "id": "test",
                            "description": "Run tests",
                            "handler": "agent",
                            "prompt_recipe": "prompts/define.poml",
                            "outputs": [{"type": "report", "path": "reports/test_results.json"}]
                        },
                        {
                            "id": "review",
                            "description": "Review changes",
                            "handler": "human_input",
                            "prompt_recipe": "prompts/define.poml",
                            "outputs": [{"type": "report", "path": "reports/review.md"}]
                        },
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
