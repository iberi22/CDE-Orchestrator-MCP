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
from mcp_tools.full_implementation import cde_executeFullImplementation

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
app.tool()(cde_executeFullImplementation)  # ✅ Nueva herramienta meta de orquestación


# Server Entry Point
if __name__ == "__main__":
    logger.info("Starting CDE Orchestrator MCP Server")
    app.run()
