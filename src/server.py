# src/server.py
import logging
import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from mcp_tools import (
    cde_analyzeDocumentation,
    cde_executeWithBestAgent,
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
    cde_updateSkill,
)
from mcp_tools.full_implementation import cde_executeFullImplementation
from mcp_tools.test_progress import cde_testProgressReporting

# Configuration
load_dotenv()
logging.basicConfig(level=os.environ.get("CDE_LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# FastMCP App Initialization
app = FastMCP("CDE Orchestrator MCP")

# Tool Registration with Dependency Injection
app.tool()(cde_onboardingProject)
app.tool()(cde_publishOnboarding)
app.tool()(cde_setupProject)
app.tool()(cde_scanDocumentation)
app.tool()(cde_analyzeDocumentation)
app.tool()(cde_selectWorkflow)
app.tool()(cde_sourceSkill)
app.tool()(cde_updateSkill)
app.tool()(cde_listAvailableAgents)
app.tool()(cde_selectAgent)
app.tool()(cde_executeWithBestAgent)
app.tool()(cde_executeFullImplementation)  # ✅ Meta-orchestration
app.tool()(cde_testProgressReporting)  # ✅ Test tool for status bar
app.tool()(cde_installMcpExtension)  # ✅ Install MCP extension
app.tool()(cde_searchTools)  # ✅ Progressive tool discovery (Anthropic pattern)


# Server Entry Point
if __name__ == "__main__":
    logger.info("Starting CDE Orchestrator MCP Server")
    logger.info("✅ Progressive tool discovery enabled (Anthropic best practices)")
    app.run()
