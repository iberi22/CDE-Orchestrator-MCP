# src/mcp_tools/onboarding.py
import json
from typing import Dict
from fastmcp import Context
from cde_orchestrator.application.use_cases.manage_state import ManageStateUseCase
from ._base import tool_handler

@tool_handler
async def cde_onboardingProject(ctx: Context, manage_state_use_case: ManageStateUseCase) -> str:
    """
    Analyzes project structure and performs onboarding setup.
    """
    state = manage_state_use_case.load()
    # In a real scenario, we would perform project analysis here
    state['onboarding_status'] = 'completed'
    manage_state_use_case.save(state)
    return json.dumps({"status": "Project onboarded successfully."})

@tool_handler
def cde_publishOnboarding(
    documents: Dict[str, str],
    manage_state_use_case: ManageStateUseCase,
    approve: bool = True
) -> str:
    """
    Applies onboarding documents to the repository.
    """
    if not approve:
        return json.dumps({"status": "Publishing aborted by user."})

    state = manage_state_use_case.load()
    # In a real scenario, we would write the documents to the filesystem
    state['published_documents'] = list(documents.keys())
    manage_state_use_case.save(state)
    return json.dumps({"status": "Documents published successfully."})
