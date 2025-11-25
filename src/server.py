# src/server.py
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

from cde_orchestrator.infrastructure.config import config
from cde_orchestrator.infrastructure.logging import configure_logging, get_logger
from cde_orchestrator.infrastructure.telemetry import trace_execution
from mcp_tools import (
    cde_analyzeDocumentation,
    cde_checkRecipes,
    cde_delegateToJules,
    cde_downloadRecipes,
    cde_executeWithBestAgent,
    cde_generateSpec,
    cde_healthCheck,
    cde_installMcpExtension,
    cde_listAvailableAgents,
    cde_onboardingProject,
    cde_publishOnboarding,
    cde_scanDocumentation,
    cde_searchTools,
    cde_selectAgent,
    cde_selectWorkflow,
    cde_setupProject,
    cde_sourceSkill,
    cde_startFeature,
    cde_submitWork,
    cde_syncTemplates,
    cde_updateSkill,
    cde_validateSpec,
)
from mcp_tools.ceo_orchestration import (
    cde_cancelTask,
    cde_delegateTask,
    cde_getTaskStatus,
    cde_getWorkerStats,
    cde_listActiveTasks,
)
from mcp_tools.full_implementation import cde_executeFullImplementation
from mcp_tools.test_progress import cde_testProgressReporting

# Configuration
load_dotenv()
configure_logging(level=config.LOG_LEVEL, json_format=config.LOG_FORMAT == "json")
logger = get_logger(__name__)


# Auto-generate MCP tool filesystem structure (Anthropic best practice)
def _generate_mcp_filesystem() -> None:
    """Generate ./servers/cde/ filesystem on startup."""
    try:
        import asyncio

        import mcp_tools
        from cde_orchestrator.application.tools.generate_filesystem_use_case import (
            GenerateFilesystemUseCase,
        )

        project_root = Path(__file__).parent.parent
        use_case = GenerateFilesystemUseCase()

        # Run async generation in event loop
        result = asyncio.run(
            use_case.execute(mcp_tools_module=mcp_tools, output_dir=project_root)
        )

        logger.info(f"✅ Generated {result['total_tools']} MCP tool files")
        logger.info(f"📁 Filesystem structure: {result['output_dir']}")
    except Exception as e:
        logger.warning(f"⚠️  Could not generate filesystem structure: {e}")
        logger.warning("   Server will continue without filesystem-based discovery.")


# FastMCP App Initialization
app = FastMCP("CDE Orchestrator MCP")

# Auto-generate filesystem structure on startup
_generate_mcp_filesystem()

# Tool Registration with Dependency Injection
app.tool()(trace_execution(cde_onboardingProject))
app.tool()(trace_execution(cde_publishOnboarding))
app.tool()(trace_execution(cde_setupProject))
app.tool()(trace_execution(cde_generateSpec))  # ✅ Professional spec generator
app.tool()(trace_execution(cde_scanDocumentation))
app.tool()(trace_execution(cde_analyzeDocumentation))
app.tool()(trace_execution(cde_selectWorkflow))
app.tool()(trace_execution(cde_sourceSkill))
app.tool()(trace_execution(cde_updateSkill))
app.tool()(trace_execution(cde_startFeature))
app.tool()(trace_execution(cde_submitWork))
app.tool()(trace_execution(cde_downloadRecipes))  # ✅ Download recipes from GitHub
app.tool()(trace_execution(cde_checkRecipes))  # ✅ Check recipe status
app.tool()(trace_execution(cde_listAvailableAgents))
app.tool()(trace_execution(cde_selectAgent))
app.tool()(trace_execution(cde_delegateToJules))  # ✅ Jules AI agent delegation
app.tool()(trace_execution(cde_executeWithBestAgent))
app.tool()(trace_execution(cde_executeFullImplementation))  # ✅ Meta-orchestration
app.tool()(trace_execution(cde_testProgressReporting))  # ✅ Test tool for status bar
app.tool()(trace_execution(cde_installMcpExtension))  # ✅ Install MCP extension
app.tool()(
    trace_execution(cde_searchTools)
)  # ✅ Progressive tool discovery (Anthropic pattern)
app.tool()(trace_execution(cde_healthCheck))  # ✅ Health monitoring (PROD-03)

# CEO Orchestration Tools (Phase 1)
app.tool()(trace_execution(cde_delegateTask))  # ✅ Delegate tasks to agents
app.tool()(trace_execution(cde_getTaskStatus))  # ✅ Poll task status
app.tool()(trace_execution(cde_listActiveTasks))  # ✅ List active tasks
app.tool()(trace_execution(cde_getWorkerStats))  # ✅ Worker pool stats
app.tool()(trace_execution(cde_cancelTask))  # ✅ Cancel tasks


# Server Entry Point
if __name__ == "__main__":
    logger.info("Starting CDE Orchestrator MCP Server")
    logger.info("✅ Progressive tool discovery enabled (Anthropic best practices)")
    app.run()
