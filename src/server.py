# src/server.py
import logging
import os
from functools import partial
from dotenv import load_dotenv
from fastmcp import FastMCP
from cde_orchestrator.infrastructure.dependency_injection import container
from mcp_tools import (
    cde_onboardingProject,
    cde_publishOnboarding,
    cde_setupProject,
    cde_scanDocumentation,
    cde_analyzeDocumentation,
    cde_selectWorkflow,
    cde_sourceSkill,
    cde_updateSkill,
    cde_listAvailableAgents,
    cde_selectAgent,
    cde_executeWithBestAgent,
)

# Configuration
load_dotenv()
logging.basicConfig(level=os.environ.get("CDE_LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# FastMCP App Initialization
app = FastMCP("CDE Orchestrator MCP")

# Tool Registration with Dependency Injection
app.tool()(partial(cde_onboardingProject, manage_state_use_case=container.manage_state_use_case))
app.tool()(partial(cde_publishOnboarding, manage_state_use_case=container.manage_state_use_case))
app.tool()(cde_setupProject)
app.tool()(cde_scanDocumentation)
app.tool()(cde_analyzeDocumentation)
app.tool()(partial(cde_selectWorkflow, select_workflow_use_case=container.select_workflow_use_case))
app.tool()(cde_sourceSkill)
app.tool()(cde_updateSkill)
app.tool()(cde_listAvailableAgents)
app.tool()(cde_selectAgent)
app.tool()(cde_executeWithBestAgent)


# Server Entry Point
if __name__ == "__main__":
    logger.info("Starting CDE Orchestrator MCP Server")
    app.run()
