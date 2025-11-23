"""
Recipe Management MCP Tools.

Tools for downloading and managing workflow recipes from external repositories.
"""

import json
from pathlib import Path

from cde_orchestrator.adapters.recipe import GitHubRecipeDownloader
from cde_orchestrator.application.orchestration import RecipeDownloaderUseCase

from ._base import tool_handler


@tool_handler
async def cde_downloadRecipes(
    project_path: str = ".",
    repo_url: str = "https://github.com/iberi22/agents-flows-recipes",
    branch: str = "main",
    force: bool = False,
) -> str:
    """
    📦 **Download Workflow Recipes** - Download POML recipes from GitHub repository.

    **What it does:**
    Downloads workflow recipes (POML files) and configuration from your
    agents-flows-recipes repository to the project's .cde/ directory.

    **When to use:**
    - First time setting up CDE in a project
    - After accidentally deleting .cde/ directory
    - Want to update recipes from repository
    - Starting a new feature and .cde/ doesn't exist

    **How it works:**
    1. Checks if .cde/ directory exists
    2. Downloads key recipe files from GitHub repo:
       - Engineering recipes (ai-engineer, backend-architect, test-writer-fixer)
       - Design recipes (brand-guardian)
       - Product recipes (sprint-prioritizer)
       - Testing recipes (workflow-optimizer)
       - Bonus recipes (studio-coach)
    3. Creates minimal workflow.yml with 6-phase CDE workflow
    4. Saves documentation helpers (qwen-rules, advanced-techniques)

    **Args:**
        project_path: Path to project root where .cde/ will be created (default: current directory)
        repo_url: GitHub repository URL (default: your agents-flows-recipes repo)
        branch: Git branch to download from (default: "main")
        force: If True, overwrite existing .cde/ directory (default: False)

    **Returns:**
        JSON with:
        - status: "success" | "skipped" | "partial" | "error"
        - message: Human-readable message
        - files_downloaded: List of downloaded files
        - destination: Path to .cde/ directory
        - errors: List of errors (if any)

    **Example 1: First-time setup**
        >>> cde_downloadRecipes()
        {
          "status": "success",
          "message": "Successfully downloaded 9 recipe files",
          "files_downloaded": [
            ".cde/recipes/engineering/ai-engineer.poml",
            ".cde/recipes/engineering/backend-architect.poml",
            ".cde/recipes/engineering/test-writer-fixer.poml",
            ".cde/recipes/design/brand-guardian.poml",
            ".cde/recipes/product/sprint-prioritizer.poml",
            ".cde/recipes/testing/workflow-optimizer.poml",
            ".cde/recipes/bonus/studio-coach.poml",
            ".cde/docs/qwen-rules.md",
            ".cde/docs/advanced-techniques.md"
          ],
          "destination": "E:\\\\my-project\\\\.cde"
        }

    **Example 2: Already exists**
        >>> cde_downloadRecipes()
        {
          "status": "skipped",
          "message": ".cde/ directory already exists at E:\\\\my-project\\\\.cde. Use force=True to overwrite.",
          "files_downloaded": [],
          "destination": "E:\\\\my-project\\\\.cde"
        }

    **Example 3: Force overwrite**
        >>> cde_downloadRecipes(force=True)
        {
          "status": "success",
          "message": "Successfully downloaded 9 recipe files",
          "files_downloaded": [...],
          "destination": "E:\\\\my-project\\\\.cde"
        }

    **Example 4: For different project**
        >>> cde_downloadRecipes(project_path="E:\\\\other-project")
        # Downloads to E:\\other-project\\.cde

    **Next Steps:**
    After downloading recipes:
    1. Use `cde_selectWorkflow` to analyze your task
    2. Use `cde_startFeature` to begin workflow execution
    3. Recipes will be automatically loaded from .cde/recipes/

    **Files Downloaded:**
    - `.cde/recipes/engineering/ai-engineer.poml` - General purpose engineering
    - `.cde/recipes/engineering/backend-architect.poml` - Backend architecture
    - `.cde/recipes/engineering/test-writer-fixer.poml` - Testing & fixes
    - `.cde/recipes/design/brand-guardian.poml` - Design consistency
    - `.cde/recipes/product/sprint-prioritizer.poml` - Sprint planning
    - `.cde/recipes/testing/workflow-optimizer.poml` - Workflow optimization
    - `.cde/recipes/bonus/studio-coach.poml` - Multi-agent guidance
    - `.cde/docs/qwen-rules.md` - Qwen/QwenCoder guidelines
    - `.cde/docs/advanced-techniques.md` - Advanced patterns

    **Auto-created Files:**
    - `.cde/workflow.yml` - 6-phase CDE workflow definition

    **Note:**
    This tool does NOT require authentication. It downloads from public
    GitHub repository using raw.githubusercontent.com.
    """
    # Create downloader adapter
    downloader = GitHubRecipeDownloader(timeout=60)

    # Create use case
    use_case = RecipeDownloaderUseCase(downloader=downloader)

    # Execute download (async call)
    result = await use_case.execute(
        project_path=project_path, repo_url=repo_url, branch=branch, force=force
    )

    # Also ensure workflow.yml exists
    workflow_result = use_case.ensure_workflow_yml(project_path=project_path)

    # Add workflow creation info to result
    if workflow_result["status"] == "created":
        result["files_downloaded"].append(".cde/workflow.yml")
        result["message"] += " + created workflow.yml"

    return json.dumps(result, indent=2, ensure_ascii=False)


@tool_handler
def cde_checkRecipes(project_path: str = ".") -> str:
    """
    🔍 **Check Recipe Status** - Check if .cde/ directory exists and what's in it.

    **What it does:**
    Checks if .cde/ directory exists in the project and reports its status.

    **Args:**
        project_path: Path to project root (default: current directory)

    **Returns:**
        JSON with:
        - exists: True if .cde/ exists, False otherwise
        - path: Absolute path to .cde/ directory
        - message: Human-readable status
        - needs_download: True if recipes need to be downloaded

    **Example 1: Directory exists**
        >>> cde_checkRecipes()
        {
          "exists": true,
          "path": "E:\\\\my-project\\\\.cde",
          "message": ".cde/ directory exists",
          "needs_download": false
        }

    **Example 2: Directory missing**
        >>> cde_checkRecipes()
        {
          "exists": false,
          "path": "E:\\\\my-project\\\\.cde",
          "message": ".cde/ directory not found. Use cde_downloadRecipes() to download recipes.",
          "needs_download": true
        }

    **When to use:**
    - Before starting a workflow to verify recipes are available
    - After accidentally deleting .cde/ to confirm it needs re-download
    - As a diagnostic tool
    """
    project_root = Path(project_path).resolve()
    cde_dir = project_root / ".cde"

    exists = cde_dir.exists()

    result = {
        "exists": exists,
        "path": str(cde_dir),
        "message": (
            ".cde/ directory exists"
            if exists
            else ".cde/ directory not found. Use cde_downloadRecipes() to download recipes."
        ),
        "needs_download": not exists,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)
