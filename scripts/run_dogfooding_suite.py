import asyncio
import inspect
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

# Import tools
try:
    from src.mcp_tools.agents import (
        cde_executeWithBestAgent,
        cde_listAvailableAgents,
        cde_selectAgent,
    )
    from src.mcp_tools.ceo_orchestration import cde_getWorkerStats, cde_listActiveTasks
    from src.mcp_tools.documentation import (
        cde_analyzeDocumentation,
        cde_createSpecification,
        cde_scanDocumentation,
    )
    from src.mcp_tools.extensions import cde_installMcpExtension
    from src.mcp_tools.health import cde_healthCheck
    from src.mcp_tools.onboarding import cde_onboardingProject
    from src.mcp_tools.orchestration import (
        cde_selectWorkflow,
        cde_sourceSkill,
        cde_startFeature,
        cde_updateSkill,
    )
    from src.mcp_tools.recipes import cde_checkRecipes, cde_downloadRecipes
    from src.mcp_tools.test_progress import cde_testProgressReporting
    from src.mcp_tools.tool_search import cde_searchTools
except ImportError as e:
    print(f"Error importing tools: {e}")
    print("Make sure you are running from the project root or have set PYTHONPATH.")
    sys.exit(1)


def run_task(task_id: str) -> None:
    print(f"Running Task {task_id}...")
    start_time = time.time()

    try:
        func = None
        args = []
        kwargs = {}

        if task_id == "T009":
            func = cde_healthCheck

        elif task_id == "T010":
            func = cde_searchTools
            args = ["workflow"]
            kwargs = {"detail_level": "name_only"}

        elif task_id == "T011":
            func = cde_searchTools
            args = ["skill"]
            kwargs = {"detail_level": "name_and_description"}

        elif task_id == "T012":
            func = cde_searchTools
            args = ["scanDocumentation"]
            kwargs = {"detail_level": "full_schema"}

        elif task_id == "T013":
            func = cde_checkRecipes
            kwargs = {"project_path": "."}

        elif task_id == "T014":
            func = cde_scanDocumentation
            args = ["."]
            kwargs = {"detail_level": "name_only"}

        elif task_id == "T015":
            func = cde_scanDocumentation
            args = ["."]
            kwargs = {"detail_level": "summary"}

        elif task_id == "T016":
            func = cde_scanDocumentation
            args = ["."]
            kwargs = {"detail_level": "full"}

        elif task_id == "T017":
            func = cde_analyzeDocumentation
            args = ["."]

        elif task_id == "T018":
            func = cde_createSpecification
            args = ["test-feature", "Test feature description"]

        elif task_id == "T019":
            # Clean up .cde if exists for test
            import shutil

            cde_path = Path(".cde")
            if cde_path.exists():
                print("Removing existing .cde directory for test...")
                shutil.rmtree(cde_path)
            func = cde_downloadRecipes
            kwargs = {"project_path": ".", "force": False}  # type: ignore[dict-item]

        elif task_id == "T020":
            func = cde_downloadRecipes
            kwargs = {"project_path": ".", "force": False}  # type: ignore[dict-item]

        elif task_id == "T021":
            func = cde_downloadRecipes
            kwargs = {"project_path": ".", "force": True}  # type: ignore[dict-item]

        elif task_id == "T022":
            func = cde_sourceSkill
            args = ["python 3.14 best practices"]
            kwargs = {"destination": "base"}

        elif task_id == "T023":
            func = cde_sourceSkill
            args = ["fastmcp mcp server patterns"]
            kwargs = {"destination": "ephemeral"}

        elif task_id == "T024":
            func = cde_updateSkill
            args = ["redis-caching"]
            kwargs = {"topics": ["redis 7.x breaking changes"]}  # type: ignore[dict-item]

        elif task_id == "T025":
            func = cde_selectWorkflow
            args = ["Fix typo in README: documenation → documentation"]

        elif task_id == "T026":
            func = cde_selectWorkflow
            args = ["Add logging to main.py"]

        elif task_id == "T027":
            func = cde_selectWorkflow
            args = ["Add Redis caching to authentication module"]

        elif task_id == "T028":
            func = cde_selectWorkflow
            args = ["Refactor adapters to use dependency injection"]

        elif task_id == "T029":
            func = cde_selectWorkflow
            args = ["Rewrite entire system using microservices architecture"]

        elif task_id == "T030":
            func = cde_startFeature
            kwargs = {
                "user_prompt": "Add JSON export tool for workflow history",
                "workflow_type": "standard",
            }

        elif task_id == "T034":
            func = cde_listAvailableAgents

        elif task_id == "T035":
            func = cde_selectAgent
            args = ["Fix typo in error message"]

        elif task_id == "T036":
            func = cde_selectAgent
            args = ["Refactor authentication system to use OAuth2"]

        elif task_id == "T037":
            func = cde_executeWithBestAgent
            args = ["Add type hints to helpers.py"]

        elif task_id == "T040":
            func = cde_listActiveTasks

        elif task_id == "T041":
            func = cde_getWorkerStats

        elif task_id == "T043":
            func = cde_onboardingProject
            kwargs = {"project_path": "."}

        elif task_id == "T046":
            func = cde_installMcpExtension
            kwargs = {"extension_name": "mcp-status-bar"}

        elif task_id == "T047":
            func = cde_testProgressReporting
            kwargs = {"duration": 5, "steps": 5}  # type: ignore[dict-item]

        else:
            print(f"Task {task_id} not implemented in runner yet.")
            return

        if func:
            if inspect.iscoroutinefunction(func):
                result = asyncio.run(func(*args, **kwargs))  # type: ignore[arg-type]
            else:
                result = func(*args, **kwargs)  # type: ignore[arg-type]
                if inspect.iscoroutine(result):
                    result = asyncio.run(result)

            print(result)

    except Exception as e:
        print(f"Error executing task {task_id}: {e}")
        import traceback

        traceback.print_exc()

    end_time = time.time()
    print(f"\nExecution time: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_dogfooding_suite.py <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]
    run_task(task_id)
