"""
CDE Orchestrator MCP Server.

FastMCP server providing Context-Driven Engineering tools for AI agents.
This server is the entry point for the CDE Orchestrator application. It uses a
Dependency Injection container to wire together the application's components
and registers the MCP tools.
"""

import logging
import os
from pathlib import Path
from functools import partial

from dotenv import load_dotenv
from fastmcp import FastMCP

from cde_orchestrator.infrastructure.di_container import DIContainer
from mcp_tools import (
    cde_onboardingProject,
    cde_publishOnboarding,
    cde_scanDocumentation,
    cde_analyzeDocumentation,
    cde_selectWorkflow,
    cde_sourceSkill,
    cde_updateSkill,
    cde_delegateToJules,
    cde_listAvailableAgents,
    cde_selectAgent,
    cde_executeWithBestAgent,
)

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=os.environ.get("CDE_LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# --- Dependency Injection ---
CDE_ROOT = Path(".cde")
di_container = DIContainer(cde_root=CDE_ROOT)

# --- FastMCP App Initialization ---
app = FastMCP("CDE Orchestrator MCP")

# --- Tool Registration ---
app.tool()(partial(cde_onboardingProject, manage_state_use_case=di_container.get_manage_state_use_case()))
app.tool()(partial(cde_publishOnboarding, manage_state_use_case=di_container.get_manage_state_use_case()))
app.tool()(cde_scanDocumentation)
app.tool()(cde_analyzeDocumentation)
app.tool()(partial(cde_selectWorkflow, select_workflow_use_case=di_container.get_select_workflow_use_case()))
app.tool()(cde_sourceSkill)
app.tool()(cde_updateSkill)
app.tool()(cde_delegateToJules)
app.tool()(cde_listAvailableAgents)
app.tool()(cde_selectAgent)
app.tool()(cde_executeWithBestAgent)

# --- Server Entry Point ---
if __name__ == "__main__":
    logger.info("🚀 Starting CDE Orchestrator MCP Server")
    logger.info(f"📦 Registered {len(app.tools)} tools")
    logger.info("✅ Server ready for connections")
    app.run()
