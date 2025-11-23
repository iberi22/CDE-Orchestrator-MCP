from pathlib import Path
from typing import Any, Callable, Dict

from pydantic import BaseModel, Field, field_validator

from cde_orchestrator.domain.entities import ProjectStatus
from cde_orchestrator.domain.ports import (
    IProjectRepository,
    IPromptRenderer,
    IWorkflowRepository,
)
from cde_orchestrator.domain.validation import sanitize_string


class StartFeatureInput(BaseModel):
    """Validation model for StartFeature use case inputs."""

    project_path: str = Field(min_length=1, max_length=500)
    user_prompt: str = Field(min_length=10, max_length=5000)
    workflow_type: str = Field(default="standard", max_length=50)
    recipe_id: str = Field(default="ai-engineer", max_length=100)

    @field_validator("user_prompt")
    @classmethod
    def sanitize_prompt(cls, value: str) -> str:
        """Sanitize user prompt to prevent injection attacks."""
        return sanitize_string(value, max_length=5000)

    @field_validator("project_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        """Validate project path is not empty and reasonable."""
        sanitized = sanitize_string(value, max_length=500)
        if not sanitized or sanitized.isspace():
            raise ValueError("Project path cannot be empty or whitespace")
        return sanitized


class StartFeatureUseCase:
    """
    Use Case: Start a new feature development workflow.

    Orchestrates:
    1. Project retrieval/creation
    2. Feature initialization
    3. Workflow phase resolution
    4. Prompt generation for the first phase
    """

    def __init__(
        self,
        project_repo: IProjectRepository,
        workflow_repo_factory: Callable[[Path], IWorkflowRepository],
        prompt_renderer: IPromptRenderer,
    ):
        self.project_repo = project_repo
        self.workflow_repo_factory = workflow_repo_factory
        self.prompt_renderer = prompt_renderer

    async def execute(
        self,
        project_path: str,
        user_prompt: str,
        workflow_type: str = "standard",
        recipe_id: str = "ai-engineer",
    ) -> Dict[str, Any]:
        """
        Execute the start feature use case.

        Args:
            project_path: Path to the project root
            user_prompt: Description of the feature to build
            workflow_type: Type of workflow (standard, quick-fix, etc.)
            recipe_id: ID of the recipe to use

        Returns:
            Dict containing feature_id, initial phase, and the prompt for the agent.

        Raises:
            ValidationError: If inputs are invalid
        """
        # Validate and sanitize inputs
        validated_input = StartFeatureInput(
            project_path=project_path,
            user_prompt=user_prompt,
            workflow_type=workflow_type,
            recipe_id=recipe_id,
        )

        # Use validated values
        project_path = validated_input.project_path
        user_prompt = validated_input.user_prompt
        workflow_type = validated_input.workflow_type
        recipe_id = validated_input.recipe_id

        # 1. Get or create project
        # We use get_or_create to ensure we have a project entity to work with
        project = await self.project_repo.get_or_create(project_path)

        # 2. Ensure project is active
        if project.status != ProjectStatus.ACTIVE:
            project.activate()

        # 3. Start feature
        feature = project.start_feature(user_prompt, workflow_type)

        # 4. Get workflow and initial phase
        # Load workflow from the project's .cde directory
        workflow_path = Path(project_path) / ".cde" / "workflow.yml"

        # If workflow file doesn't exist, we might need to handle it.
        # For now, we assume the factory or repo handles it (e.g. raises FileNotFoundError)
        # or we should check here.
        if not workflow_path.exists():
            # Fallback to default workflow or raise error
            # Ideally, cde_setupProject should have been run.
            raise FileNotFoundError(
                f"Workflow file not found at {workflow_path}. Please run cde_setupProject first."
            )

        workflow_repo = self.workflow_repo_factory(workflow_path)
        workflow = await workflow_repo.load_workflow()

        # TODO: Handle different workflows based on workflow_type if needed
        # For now, we assume the standard workflow or that load_workflow handles it

        initial_phase = workflow.get_initial_phase()

        # 5. Render prompt for initial phase
        context = {
            "PROJECT_NAME": project.name,
            "PROJECT_PATH": project.path,
            "FEATURE_ID": feature.id,
            "USER_PROMPT": user_prompt,
            "WORKFLOW_TYPE": workflow_type,
            "RECIPE_ID": recipe_id,
            "CURRENT_PHASE": initial_phase.id,
        }

        # Resolve prompt path. Assuming the prompt_recipe is relative to .cde/prompts
        # or handled by the renderer. We'll pass it as is for now.
        rendered_prompt = await self.prompt_renderer.load_and_prepare(
            Path(initial_phase.prompt_recipe), context
        )

        # 6. Save project state
        await self.project_repo.save(project)

        return {
            "status": "success",
            "feature_id": feature.id,
            "phase": initial_phase.id,
            "prompt": rendered_prompt,
            "workflow_type": workflow_type,
        }
