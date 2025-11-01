# src/server.py
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

from fastmcp import FastMCP

from cde_orchestrator.models import FeatureState, FeatureStatus, PhaseStatus
from cde_orchestrator.onboarding_analyzer import OnboardingAnalyzer
from cde_orchestrator.prompt_manager import PromptManager
from cde_orchestrator.recipe_manager import RecipeManager
from cde_orchestrator.repo_ingest import RepoIngestor
from cde_orchestrator.service_connector import ServiceConnectorFactory
from cde_orchestrator.state_manager import StateManager
from cde_orchestrator.workflow_manager import WorkflowManager

# --- Constants and Configuration ---
CDE_ROOT = Path(".cde")
WORKFLOW_FILE = CDE_ROOT / "workflow.yml"
STATE_FILE = CDE_ROOT / "state.json"
PROMPT_RECIPES_DIR = CDE_ROOT / "prompts"
RECIPES_DIR = CDE_ROOT / "recipes"
SPECS_DIR = Path("specs")

FEATURE_STATUS_BY_PHASE = {
    PhaseStatus.DEFINE.value: FeatureStatus.DEFINING,
    PhaseStatus.DECOMPOSE.value: FeatureStatus.DECOMPOSING,
    PhaseStatus.DESIGN.value: FeatureStatus.DESIGNING,
    PhaseStatus.IMPLEMENT.value: FeatureStatus.IMPLEMENTING,
    PhaseStatus.TEST.value: FeatureStatus.TESTING,
    PhaseStatus.REVIEW.value: FeatureStatus.REVIEWING,
}


def _status_for_phase(phase_id: str) -> FeatureStatus:
    """Map workflow phase identifiers to canonical feature status."""
    return FEATURE_STATUS_BY_PHASE.get(phase_id, FeatureStatus.FAILED)

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)
logger = logging.getLogger("cde_orchestrator")

# --- Application Setup ---
app = FastMCP()

# --- Service Initialization ---
try:
    workflow_manager = WorkflowManager(WORKFLOW_FILE)
    prompt_manager = PromptManager()
    state_manager = StateManager(STATE_FILE)
    recipe_manager = RecipeManager(RECIPES_DIR)
    service_factory = ServiceConnectorFactory()
except FileNotFoundError as e:
    logger.error("Missing required CDE file: %s", e)
    logger.error("Please ensure .cde/workflow.yml exists.")
    exit(1)


@contextmanager
def tool_execution_context(tool_name: str):
    """Context manager to log tool execution lifecycle."""
    start = time.perf_counter()
    logger.info("Tool %s started", tool_name)
    try:
        yield
        duration = time.perf_counter() - start
        logger.info("Tool %s completed in %.2fs", tool_name, duration)
    except Exception:
        duration = time.perf_counter() - start
        logger.exception("Tool %s failed after %.2fs", tool_name, duration)
        raise


def tool_handler(func):
    """Wrap MCP tools with structured error handling and logging."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with tool_execution_context(func.__name__):
                result = func(*args, **kwargs)
                if isinstance(result, (dict, list)):
                    return json.dumps(result, indent=2)
                return result
        except TimeoutError as exc:
            logger.error("Tool %s timed out: %s", func.__name__, exc)
            return json.dumps({
                "error": "timeout",
                "message": str(exc),
                "tool": func.__name__
            }, indent=2)
        except Exception as exc:
            logger.exception("Tool %s failed", func.__name__)
            return json.dumps({
                "error": "internal_error",
                "message": str(exc),
                "tool": func.__name__
            }, indent=2)

    return wrapper


@app.tool()
@tool_handler
def cde_startFeature(user_prompt: str) -> str:
    """
    Initiates a new feature development workflow based on a user prompt.
    This is the entry point for starting any new work.

    Args:
        user_prompt: A high-level description of the feature to be built (10-5000 chars).

    Returns:
        A fully-contextualized prompt for the AI agent to execute the 'define' phase.
    """
    from cde_orchestrator.validation import sanitize_string

    # Validate and sanitize input
    if not user_prompt or len(user_prompt.strip()) < 10:
        return json.dumps({
            "error": "validation_error",
            "message": "user_prompt must be at least 10 characters"
        }, indent=2)

    if len(user_prompt) > 5000:
        return json.dumps({
            "error": "validation_error",
            "message": "user_prompt must not exceed 5000 characters"
        }, indent=2)

    user_prompt = sanitize_string(user_prompt, max_length=5000)

    # 1. Generate a unique ID for the new feature
    feature_id = str(uuid.uuid4())

    # 2. Detect the appropriate workflow type
    workflow_type = workflow_manager.detect_workflow_type(user_prompt)

    # 3. Get the initial phase from the workflow
    initial_phase = workflow_manager.get_initial_phase()
    if initial_phase.id != 'define':
        raise ValueError("The workflow must start with a 'define' phase.")

    # 4. Prepare the context for the prompt recipe
    context = {
        "USER_PROMPT": user_prompt,
        "FEATURE_ID": feature_id,
        "WORKFLOW_TYPE": workflow_type
    }

    poml_recipe_path = Path(initial_phase.prompt_recipe)

    # 5. Load and prepare the prompt using the PromptManager
    final_prompt = prompt_manager.load_and_prepare(poml_recipe_path, context)

    # 6. Update the state
    state = state_manager.load_state()
    if "features" not in state:
        state["features"] = {}

    feature_state = FeatureState(
        status=FeatureStatus.DEFINING,
        current_phase=PhaseStatus(initial_phase.id),
        prompt=user_prompt,
        workflow_type=workflow_type,
        created_at=datetime.now(timezone.utc),
        progress=workflow_manager.get_workflow_progress(initial_phase.id),
    )
    state["features"][feature_id] = feature_state.serialize()
    state_manager.save_state(state)

    # 7. Return structured JSON for the AI to execute
    return json.dumps({
        "status": "ok",
        "feature_id": feature_id,
        "phase": initial_phase.id,
        "workflow_type": workflow_type,
        "prompt": final_prompt,
        "progress": state['features'][feature_id]['progress']
    }, indent=2)


@app.tool()
@tool_handler
def cde_submitWork(feature_id: str, phase_id: str, results: Dict[str, Any]) -> str:
    """
    Submits the completed work for a given feature phase and transitions to the next phase.

    Args:
        feature_id: The unique identifier of the feature
        phase_id: The current phase being completed
        results: The work results (files, content, etc.)

    Returns:
        Next phase prompt or completion message
    """
    # 1. Load current state
    state = state_manager.load_state()

    if 'features' not in state or feature_id not in state['features']:
        return json.dumps({"error": "feature_not_found", "feature_id": feature_id}, indent=2)

    feature_state = state['features'][feature_id]

    # 2. Validate current phase
    if feature_state['current_phase'] != phase_id:
        return json.dumps({
            "error": "invalid_phase",
            "expected": feature_state['current_phase'],
            "got": phase_id
        }, indent=2)

    # 3. Process the results based on phase type
    try:
        _process_phase_results(phase_id, results, feature_id)
    except Exception as e:
        return json.dumps({"error": "processing_failed", "message": str(e)}, indent=2)

    # 4. Get next phase
    next_phase_id = workflow_manager.get_next_phase(phase_id)

    if next_phase_id is None:
        # Workflow complete
        feature_state['status'] = FeatureStatus.COMPLETED.value
        feature_state['current_phase'] = PhaseStatus.REVIEW.value
        feature_state['completed_at'] = datetime.now(timezone.utc).isoformat()
        feature_state['progress'] = workflow_manager.get_workflow_progress(phase_id)
        state_manager.save_state(state)
        return json.dumps({
            "status": "completed",
            "feature_id": feature_id
        }, indent=2)

    # 5. Transition to next phase
    next_phase = workflow_manager.get_phase(next_phase_id)
    feature_state['current_phase'] = next_phase_id
    feature_state['status'] = _status_for_phase(next_phase_id).value
    feature_state['progress'] = workflow_manager.get_workflow_progress(next_phase_id)

    # 6. Prepare context for next phase
    context = {
        "FEATURE_ID": feature_id,
        "PREVIOUS_PHASE": phase_id,
        "WORKFLOW_TYPE": feature_state.get('workflow_type', 'default')
    }

    # Add phase-specific context
    if next_phase_id == 'decompose':
        # Load the feature spec from previous phase
        spec_file = SPECS_DIR / "features" / f"{feature_id}.md"
        if spec_file.exists():
            context["FEATURE_SPEC"] = spec_file.read_text()
    elif next_phase_id == 'design':
        # Load both spec and task breakdown
        spec_file = SPECS_DIR / "features" / f"{feature_id}.md"
        tasks_file = SPECS_DIR / "tasks" / f"{feature_id}_tasks.md"
        if spec_file.exists():
            context["FEATURE_SPEC"] = spec_file.read_text()
        if tasks_file.exists():
            context["TASK_BREAKDOWN"] = tasks_file.read_text()

    # 7. Generate next phase prompt
    poml_recipe_path = Path(next_phase.prompt_recipe)
    final_prompt = prompt_manager.load_and_prepare(poml_recipe_path, context)

    # 8. Save updated state
    state_manager.save_state(state)

    return json.dumps({
        "status": "ok",
        "feature_id": feature_id,
        "phase": next_phase_id,
        "prompt": final_prompt,
        "progress": feature_state['progress']
    }, indent=2)


@app.tool()
@tool_handler
def cde_getFeatureStatus(feature_id: str) -> str:
    """
    Gets the current status and progress of a feature.

    Args:
        feature_id: The unique identifier of the feature

    Returns:
        JSON string with feature status information
    """
    state = state_manager.load_state()

    if 'features' not in state or feature_id not in state['features']:
        return json.dumps({"error": "feature_not_found", "feature_id": feature_id}, indent=2)

    feature_state = state['features'][feature_id]
    return json.dumps(feature_state, indent=2)


@app.tool()
@tool_handler
def cde_listFeatures() -> str:
    """
    Lists all features and their current status with full validation.

    Returns:
        JSON string with all features information
    """
    from pydantic import ValidationError

    state = state_manager.load_state()

    if 'features' not in state:
        return json.dumps({"features": {}}, indent=2)

    features_summary = {}
    for feature_id, feature_data in state['features'].items():
        try:
            # Validate state structure
            validated = FeatureState(**feature_data)

            features_summary[feature_id] = {
                "status": validated.status.value,
                "current_phase": validated.current_phase.value,
                "workflow_type": validated.workflow_type,
                "created_at": validated.created_at.isoformat(),
                "updated_at": validated.updated_at.isoformat() if validated.updated_at else None,
                "progress": validated.progress,
                "branch": validated.branch,
                "recipe_id": validated.recipe_id,
                "recipe_name": validated.recipe_name,
                "prompt_preview": validated.prompt[:200] + "..." if len(validated.prompt) > 200 else validated.prompt
            }
        except ValidationError as e:
            logger.error(f"Invalid feature state for {feature_id}: {e}")
            # Return error info for corrupted features
            features_summary[feature_id] = {
                "status": "CORRUPTED",
                "error": str(e),
                "raw_data": feature_data
            }

    return json.dumps(features_summary, indent=2)


@app.tool()
@tool_handler
def cde_listRecipes() -> str:
    """
    Lists all available POML recipes organized by category.

    Returns:
        JSON string with all available recipes
    """
    recipes_by_category = recipe_manager.list_recipes()
    return json.dumps(recipes_by_category, indent=2)


@app.tool()
@tool_handler
def cde_useRecipe(recipe_id: str, user_prompt: str, context: Optional[Dict[str, str]] = None) -> str:
    """
    Uses a specific POML recipe to generate a specialized prompt.

    Args:
        recipe_id: The ID of the recipe to use (e.g., 'ai-engineer', 'sprint-prioritizer')
        user_prompt: The user's request or task description
        context: Optional additional context variables

    Returns:
        The generated prompt from the recipe with context injected
    """
    if context is None:
        context = {}

    # Add user prompt to context
    context["USER_PROMPT"] = user_prompt
    context["TASK_ID"] = str(uuid.uuid4())

    try:
        recipe_prompt = recipe_manager.load_recipe_content(recipe_id, context)
        return json.dumps({
            "status": "ok",
            "recipe_id": recipe_id,
            "task_id": context["TASK_ID"],
            "prompt": recipe_prompt
        }, indent=2)
    except ValueError as e:
        return json.dumps({"error": "recipe_not_found", "message": str(e)}, indent=2)


@app.tool()
@tool_handler
def cde_createGitBranch(feature_id: str, branch_name: str, base_branch: str = "main") -> str:
    """
    Creates a new Git branch for a feature.

    Args:
        feature_id: The unique identifier of the feature
        branch_name: Name of the new branch (will be prefixed with feature ID)
        base_branch: Branch to base from (default: main)

    Returns:
        JSON string with branch creation result
    """
    git_connector = service_factory.get_connector("git")

    # Create branch with feature ID prefix
    full_branch_name = f"{feature_id[:8]}-{branch_name}"

    result = git_connector.create_branch(full_branch_name, base_branch)

    # Update state
    state = state_manager.load_state()
    if 'features' in state and feature_id in state['features']:
        state['features'][feature_id]['branch'] = full_branch_name
        state_manager.save_state(state)

    return json.dumps(result, indent=2)


@app.tool()
@tool_handler
def cde_createGitHubIssue(
    feature_id: str,
    title: str,
    description: str,
    labels: Optional[List[str]] = None
) -> str:
    """
    Creates a GitHub issue for a feature.
    Automatically uses external GitHub MCP if available, otherwise falls back to local storage.

    Args:
        feature_id: The unique identifier of the feature
        title: Issue title
        description: Issue description
        labels: Optional list of labels

    Returns:
        JSON string with issue creation result
    """
    github_connector = service_factory.get_connector("github")

    # Extract repo info from environment or config (simplified)
    # In production, this should be configurable
    repo_owner = os.getenv("GITHUB_REPO_OWNER", "")
    repo_name = os.getenv("GITHUB_REPO_NAME", "")

    if not labels:
        labels = ["cde-task", feature_id[:8]]

    result = github_connector.create_issue(
        repo_owner=repo_owner,
        repo_name=repo_name,
        title=title,
        body=description,
        labels=labels
    )

    # Update state
    state = state_manager.load_state()
    if 'features' in state and feature_id in state['features']:
        if 'issues' not in state['features'][feature_id]:
            state['features'][feature_id]['issues'] = []
        state['features'][feature_id]['issues'].append(result)
        state_manager.save_state(state)

    return json.dumps(result, indent=2)


@app.tool()
@tool_handler
def cde_commitWork(feature_id: str, message: str, files: Optional[List[str]] = None) -> str:
    """
    Commits work for a feature to Git.

    Args:
        feature_id: The unique identifier of the feature
        message: Commit message
        files: Optional list of files to commit (None = all changes)

    Returns:
        JSON string with commit result
    """
    git_connector = service_factory.get_connector("git")

    result = git_connector.commit_changes(message, files)

    # Update state
    state = state_manager.load_state()
    if 'features' in state and feature_id in state['features']:
        if 'commits' not in state['features'][feature_id]:
            state['features'][feature_id]['commits'] = []
        state['features'][feature_id]['commits'].append({
            "message": message,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        state_manager.save_state(state)

    return json.dumps(result, indent=2)


@app.tool()
@tool_handler
def cde_getServiceStatus() -> str:
    """
    Gets the status of all configured service integrations.

    Returns:
        JSON string with service status information
    """
    status = service_factory.get_service_status()
    return json.dumps(status, indent=2)


@app.tool()
@tool_handler
def cde_suggestRecipe(user_prompt: str, phase_id: str = "define") -> str:
    """
    Suggests the best recipe for a given user prompt and workflow phase.

    Args:
        user_prompt: The user's request or task description
        phase_id: The current workflow phase (default: 'define')

    Returns:
        JSON string with suggested recipe information
    """
    suggested_recipe = recipe_manager.suggest_recipe(user_prompt, phase_id)

    if suggested_recipe:
        return json.dumps({
            "recipe_id": suggested_recipe.id,
            "name": suggested_recipe.name,
            "category": suggested_recipe.category,
            "description": suggested_recipe.description,
            "tools": suggested_recipe.tools,
            "topology": suggested_recipe.topology
        }, indent=2)
    else:
        return json.dumps({"error": "no_recipe"}, indent=2)


@app.tool()
@tool_handler
def cde_startFeatureWithRecipe(user_prompt: str, recipe_id: Optional[str] = None) -> str:
    """
    Starts a new feature using a specific recipe or auto-suggested recipe.

    Args:
        user_prompt: A high-level description of the feature to be built
        recipe_id: Optional specific recipe to use. If not provided, will auto-suggest

    Returns:
        JSON response with prompt and metadata for the selected recipe.
    """
    feature_id = str(uuid.uuid4())
    workflow_type = workflow_manager.detect_workflow_type(user_prompt)

    if recipe_id:
        selected_recipe = recipe_manager.get_recipe(recipe_id)
        if not selected_recipe:
            return json.dumps({"error": "recipe_not_found", "recipe_id": recipe_id}, indent=2)
    else:
        selected_recipe = recipe_manager.suggest_recipe(user_prompt, "define")
        if not selected_recipe:
            return cde_startFeature(user_prompt)

    context = {
        "USER_PROMPT": user_prompt,
        "FEATURE_ID": feature_id,
        "WORKFLOW_TYPE": workflow_type,
        "PHASE": "define"
    }

    try:
        recipe_prompt = recipe_manager.load_recipe_content(selected_recipe.id, context)
    except Exception as e:
        return json.dumps({"error": "recipe_load_failed", "message": str(e)}, indent=2)

    state = state_manager.load_state()
    if "features" not in state:
        state["features"] = {}

    feature_state = FeatureState(
        status=FeatureStatus.DEFINING,
        current_phase=PhaseStatus.DEFINE,
        prompt=user_prompt,
        workflow_type=workflow_type,
        recipe_id=selected_recipe.id,
        recipe_name=selected_recipe.name,
        created_at=datetime.now(timezone.utc),
        progress=workflow_manager.get_workflow_progress("define"),
    )
    state["features"][feature_id] = feature_state.serialize()
    state_manager.save_state(state)

    return json.dumps({
        "status": "ok",
        "feature_id": feature_id,
        "phase": "define",
        "workflow_type": workflow_type,
        "recipe_id": selected_recipe.id,
        "recipe_name": selected_recipe.name,
        "prompt": recipe_prompt,
        "progress": state['features'][feature_id]['progress']
    }, indent=2)


def _process_phase_results(phase_id: str, results: Dict[str, Any], feature_id: str):
    """Persist artifacts for each phase and trigger side effects."""
    SPECS_DIR.mkdir(exist_ok=True)
    (SPECS_DIR / "features").mkdir(exist_ok=True)
    (SPECS_DIR / "tasks").mkdir(exist_ok=True)
    (SPECS_DIR / "design").mkdir(exist_ok=True)
    (SPECS_DIR / "reviews").mkdir(exist_ok=True)

    if phase_id == 'define':
        spec = results.get('specification')
        if spec:
            spec_file = SPECS_DIR / "features" / f"{feature_id}.md"
            spec_file.write_text(spec)
            logger.debug("Wrote feature spec: %s", spec_file)

        if service_factory.is_service_available("git"):
            try:
                git_connector = service_factory.get_connector("git")
                branch_result = git_connector.create_branch(
                    f"feature-{feature_id[:8]}",
                    "main"
                )
                if branch_result.get("success"):
                    logger.info("Created Git branch for feature %s", feature_id)
                else:
                    logger.debug("create_branch response: %s", branch_result)
            except Exception as exc:
                logger.warning("Could not create Git branch: %s", exc)

    elif phase_id == 'decompose':
        breakdown = results.get('task_breakdown')
        if breakdown:
            tasks_file = SPECS_DIR / "tasks" / f"{feature_id}_tasks.md"
            tasks_file.write_text(breakdown)
            logger.debug("Wrote task breakdown: %s", tasks_file)

    elif phase_id == 'design':
        design_doc = results.get('design_document')
        if design_doc:
            design_file = SPECS_DIR / "design" / f"{feature_id}_design.md"
            design_file.write_text(design_doc)
            logger.debug("Wrote design doc: %s", design_file)

    elif phase_id == 'review':
        review_doc = results.get('review_document')
        if review_doc:
            review_file = SPECS_DIR / "reviews" / f"{feature_id}_review.md"
            review_file.write_text(review_doc)
            logger.debug("Wrote review doc: %s", review_file)
@app.tool()
@tool_handler
def cde_onboardingProject() -> str:
    """
    Analyzes project structure and performs onboarding setup.
    Automatically detects if onboarding is needed and creates Spec-Kit compatible structure.
    This is typically called when first connecting the MCP server to a new or existing project.

    Returns:
        A contextualized prompt for the AI agent to execute onboarding,
        or a message if onboarding is not needed
    """
    project_root = Path.cwd()
    analyzer = OnboardingAnalyzer(project_root)

    # Check if onboarding is needed
    analysis = analyzer.needs_onboarding()

    if not analysis["needs_onboarding"]:
        return json.dumps({
            "status": "already_configured",
            "message": "Project already has Spec-Kit compatible structure.",
            "existing_structure": analysis["existing_structure"]
        }, indent=2)

    # Generate onboarding plan
    plan = analyzer.generate_onboarding_plan()

    # Prepare context for POML prompt
    # Add a lightweight repo digest (inspired by gitingest) so the LLM has concrete file snippets
    ingestor = RepoIngestor(project_root)
    try:
        repo_digest = ingestor.ingest(max_files=200)
    except Exception as exc:
        logger.warning("Repo ingestion failed: %s", exc)
        repo_digest = {"summary": f"Error generating digest: {exc}", "tree": [], "top_files": []}

    plan_context = plan.get("context", {})
    context = {
        "PROJECT_ANALYSIS": json.dumps(analysis, indent=2),
        "GIT_INSIGHTS": json.dumps(analysis["project_info"]["git"], indent=2),
        "MISSING_STRUCTURE": json.dumps(analysis["missing_structure"], indent=2),
        "TECH_STACK": json.dumps(analyzer._detect_tech_stack(), indent=2),
        "REPO_DIGEST": json.dumps({
            "summary": repo_digest.get("summary"),
            "top_files": [{"path": f['path'], "snippet": f['snippet'][:1000]} for f in repo_digest.get('top_files', [])[:10]]
        }, indent=2),
        "REPO_SYNTHESIS": json.dumps(plan_context.get("repository_synthesis", {}), indent=2),
        "CLEANUP_RECOMMENDATIONS": json.dumps(plan.get("cleanup_plan", {}), indent=2),
        "MANAGEMENT_PRINCIPLES": (
            "Specification-as-Code, Single Source of Truth (Git + Issues), Progressive Scalability, "
            "Automation-friendly structure for AI assistants."
        )
    }

    # Load and prepare onboarding prompt
    onboarding_prompt_path = PROMPT_RECIPES_DIR / "00_onboarding.poml"
    if not onboarding_prompt_path.exists():
        return json.dumps({
            "error": "Onboarding prompt not found",
            "expected_path": str(onboarding_prompt_path)
        }, indent=2)

    try:
        final_prompt = prompt_manager.load_and_prepare(onboarding_prompt_path, context)

        # Save plan and prompt to state for reference and require human approval before writing files
        state = state_manager.load_state()
        if "onboarding" not in state:
            state["onboarding"] = {}
        state["onboarding"]["plan"] = plan
        state["onboarding"]["analysis"] = analysis
        state["onboarding"]["cleanup_plan"] = plan.get("cleanup_plan", {})
        state["onboarding"]["repository_synthesis"] = plan_context.get("repository_synthesis", {})
        # store the generated prompt as a draft (not yet applied)
        state["onboarding"]["draft_prompt"] = final_prompt
        state["onboarding"]["repo_digest"] = repo_digest
        state["onboarding"]["awaiting_approval"] = True
        state_manager.save_state(state)

        # Return the prompt to the client so it can generate draft documents with an LLM.
        # The user must call the `cde_publishOnboarding` tool with the generated documents
        # to persist them into the repository (this enforces human validation).
        return json.dumps({
            "status": "draft_ready",
            "message": "Onboarding draft prompt prepared. Use an LLM to generate documents, then call cde_publishOnboarding to apply after human approval.",
            "draft_preview": final_prompt[:2000]
        }, indent=2)
    except Exception as exc:
        logger.exception("Error generating onboarding prompt")
        return json.dumps({
            "error": "onboarding_prompt_failed",
            "message": str(exc)
        }, indent=2)


@app.tool()
@tool_handler
def cde_publishOnboarding(documents: Dict[str, str], approve: bool = True) -> str:
    """Apply onboarding documents generated by an LLM into the repo.

    Args:
        documents: mapping file_path -> content (relative to project root)
        approve: boolean that confirms the user approves writing these files

    Returns:
        status message
    """
    project_root = Path.cwd()
    state = state_manager.load_state()
    onboarding = state.get("onboarding", {})

    if not onboarding.get("awaiting_approval"):
        return json.dumps({
            "error": "no_onboarding_pending",
            "message": "Run cde_onboardingProject first."
        }, indent=2)

    if not approve:
        # mark as declined
        onboarding["awaiting_approval"] = False
        onboarding["approved"] = False
        state_manager.save_state(state)
        return json.dumps({
            "status": "declined",
            "message": "Onboarding draft declined by user."
        }, indent=2)

    # Apply documents: write files under project_root, but do not commit (user workflow can commit)
    created = []
    failed = []
    for path, content in (documents or {}).items():
        try:
            dest = project_root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding='utf-8')
            created.append(str(dest.relative_to(project_root)))
        except Exception as e:
            failed.append({"path": path, "error": str(e)})

    onboarding["awaiting_approval"] = False
    onboarding["approved"] = True
    onboarding["created_files"] = created
    onboarding["failed_writes"] = failed
    state_manager.save_state(state)

    return json.dumps({"status": "applied", "created": created, "failed": failed}, indent=2)


if __name__ == "__main__":
    # This allows running the server directly for testing
    app.run()

