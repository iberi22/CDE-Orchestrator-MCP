# src/mcp_tools/onboarding.py
import json
import logging
import os
from typing import Dict

from fastmcp import Context

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)
from cde_orchestrator.application.onboarding.project_setup_use_case import (
    ProjectSetupUseCase,
)
from cde_orchestrator.application.onboarding.publishing_use_case import (
    PublishingUseCase,
)
from cde_orchestrator.infrastructure.dependency_injection import container

from ._base import tool_handler
from ._progress_reporter import get_progress_reporter

logger = logging.getLogger(__name__)


@tool_handler
async def cde_onboardingProject(ctx: Context, project_path: str = ".") -> str:
    """
    Analyzes project structure and performs comprehensive onboarding setup.

    Includes deep context enrichment:
    - Git history analysis (commits, branches, contributors)
    - Documentation synthesis (README, CONTRIBUTING, dependencies)
    - Framework detection (FastAPI, Next.js, FastMCP, etc.)
    - Architecture pattern identification (Hexagonal, Clean, etc.)

    Args:
        project_path: The path to the project to analyze (defaults to current dir).

    Returns:
        JSON string with enriched project analysis
    """
    reporter = get_progress_reporter()
    reporter.reset()
    reporter.report_progress(
        "CDE", "onboardingProject", 0.1, "Initializing onboarding..."
    )

    analysis_use_case = ProjectAnalysisUseCase()

    if project_path == ".":
        project_path = os.getcwd()

    reporter.report_progress(
        "CDE", "onboardingProject", 0.3, f"Analyzing {project_path}..."
    )

    # Run async analysis with enrichment
    analysis_result = await analysis_use_case.execute(project_path, enrich_context=True)

    # Add status field expected by tests
    analysis_result["status"] = "Analysis complete"

    try:
        state = await container.manage_state_use_case.load_and_validate_state()
        state["project_analysis"] = analysis_result
        state["onboarding_status"] = "analysis_completed"
        await container.manage_state_use_case.save_state(state)
    except Exception as e:
        logger.warning(f"Could not save state: {e}")

    reporter.report_progress(
        "CDE", "onboardingProject", 1.0, "Onboarding analysis complete"
    )
    return json.dumps(analysis_result, indent=2)


@tool_handler
async def cde_setupProject(
    ctx: Context, project_path: str = ".", force: bool = False
) -> str:
    """
    Analyzes a project and generates key configuration files (e.g., .gitignore, AGENTS.md).

    Args:
        project_path: The path to the project to set up.
        force: If true, overwrites existing configuration files.
    """
    # Note: In a real DI system, these would be injected.
    analysis_use_case = ProjectAnalysisUseCase()
    publishing_use_case = PublishingUseCase()
    setup_use_case = ProjectSetupUseCase(analysis_use_case, publishing_use_case)

    if project_path == ".":
        project_path = os.getcwd()

    result = await setup_use_case.execute(project_path, force)
    return json.dumps(result, indent=2)


@tool_handler
async def cde_publishOnboarding(
    documents: Dict[str, str], project_path: str = ".", approve: bool = True
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
        try:
            state = await container.manage_state_use_case.load_and_validate_state()
            state["published_documents"] = result["files_written"]
            await container.manage_state_use_case.save_state(state)
        except Exception as e:
            logger.warning(f"Could not save state: {e}")

    return json.dumps(result, indent=2)
