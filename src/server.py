# src/server.py
import uuid
from pathlib import Path
from fastmcp import FastMCP
from cde_orchestrator.workflow_manager import WorkflowManager
from cde_orchestrator.prompt_manager import PromptManager
from cde_orchestrator.state_manager import StateManager

# --- Constants and Configuration ---
CDE_ROOT = Path(".cde")
WORKFLOW_FILE = CDE_ROOT / "workflow.yml"
STATE_FILE = CDE_ROOT / "state.json"
PROMPT_RECIPES_DIR = CDE_ROOT / "prompts"

# --- Application Setup ---
app = FastMCP()

# --- Service Initialization ---
try:
    workflow_manager = WorkflowManager(WORKFLOW_FILE)
    prompt_manager = PromptManager()
    state_manager = StateManager(STATE_FILE)
except FileNotFoundError as e:
    print(f"Error: A required CDE file is missing. {e}")
    print("Please ensure .cde/workflow.yml exists.")
    exit(1)


@app.tool()
def cde_startFeature(user_prompt: str) -> str:
    """
    Initiates a new feature development workflow based on a user prompt.
    This is the entry point for starting any new work.

    Args:
        user_prompt: A high-level description of the feature to be built.

    Returns:
        A fully-contextualized prompt for the AI agent to execute the 'define' phase.
    """
    # 1. Generate a unique ID for the new feature
    feature_id = str(uuid.uuid4())
    
    # 2. Get the initial phase from the workflow
    initial_phase = workflow_manager.get_initial_phase()
    if initial_phase.id != 'define':
        raise ValueError("The workflow must start with a 'define' phase.")

    # 3. Prepare the context for the prompt recipe
    context = {
        "USER_PROMPT": user_prompt,
        "FEATURE_ID": feature_id
    }
    
    poml_recipe_path = Path(initial_phase.prompt_recipe)
    
    # 4. Load and prepare the prompt using the PromptManager
    final_prompt = prompt_manager.load_and_prepare(poml_recipe_path, context)
    
    # 5. Update the state (optional for now, but good practice)
    state = state_manager.load_state()
    if 'features' not in state:
        state['features'] = {}
    state['features'][feature_id] = {
        "status": "defining",
        "current_phase": initial_phase.id,
        "prompt": user_prompt
    }
    state_manager.save_state(state)
    
    # 6. Return the prompt for the AI to execute
    return final_prompt

# Placeholder for future tools
@app.tool()
def cde_submitWork(task_id: str, results: dict) -> str:
    """
    Submits the completed work for a given task.
    (This is a placeholder for now).
    """
    return f"Work for task {task_id} received. Orchestrator will process it soon."


if __name__ == "__main__":
    # This allows running the server directly for testing
    app.run()
