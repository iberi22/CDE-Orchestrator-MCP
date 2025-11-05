# src/mcp_tools/onboarding.py
import json
from typing import Dict
from fastmcp import Context
from cde_orchestrator.application.use_cases.manage_state import ManageStateUseCase
from ._base import tool_handler

from cde_orchestrator.application.onboarding.project_analysis_use_case import ProjectAnalysisUseCase
import os

@tool_handler
async def cde_onboardingProject(ctx: Context, manage_state_use_case: ManageStateUseCase, project_path: str = ".") -> str:
    """
    Analyzes project structure and performs onboarding setup.

    Args:
        project_path: The path to the project to analyze (defaults to current dir).
    """
    analysis_use_case = ProjectAnalysisUseCase()

    if project_path == ".":
        project_path = os.getcwd()

    analysis_result = analysis_use_case.execute(project_path)

    state = manage_state_use_case.load()
    state['project_analysis'] = analysis_result
    state['onboarding_status'] = 'analysis_completed'
    manage_state_use_case.save(state)

    return json.dumps(analysis_result, indent=2)

from cde_orchestrator.application.onboarding.publishing_use_case import PublishingUseCase

@tool_handler
def cde_publishOnboarding(
    documents: Dict[str, str],
    manage_state_use_case: ManageStateUseCase,
    project_path: str = ".",
    approve: bool = True
) -> str:
    """
    Applies onboarding documents to the repository.

    Args:
        documents: A dictionary of { "filepath": "content" }.
        project_path: The root of the project to write files to.
        approve: A boolean flag to confirm the operation.
    """
    if not approve:
        return json.dumps({"status": "Publishing aborted by user."})

    if project_path == ".":
        project_path = os.getcwd()

    publishing_use_case = PublishingUseCase()
    result = publishing_use_case.execute(project_path, documents)

    # Update state only if successful
    if result["status"] == "success":
        state = manage_state_use_case.load()
        state['published_documents'] = result["files_written"]
        manage_state_use_case.save(state)

    return json.dumps(result, indent=2)
