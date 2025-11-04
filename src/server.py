"""
CDE Orchestrator MCP Server.

FastMCP server providing Context-Driven Engineering tools for AI agents.
All tools are organized in mcp_tools/ package for modularity and maintainability.

Usage:
    python src/server.py

Architecture:
    - MCP tools are modularized in src/mcp_tools/
    - Each module contains thematically related tools
    - server.py only handles registration and initialization
"""

import logging
import os

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system env vars

from fastmcp import FastMCP

# Import all MCP tools from modular package
from mcp_tools import (
    # Onboarding
    cde_onboardingProject,
    cde_publishOnboarding,
    # Documentation
    cde_scanDocumentation,
    cde_analyzeDocumentation,
    # Orchestration
    cde_selectWorkflow,
    cde_sourceSkill,
    cde_updateSkill,
    # Agents
    cde_delegateToJules,
    cde_listAvailableAgents,
    cde_selectAgent,
    cde_executeWithBestAgent,
)

# --- Configuration ---
logger = logging.getLogger("cde_orchestrator.server")
logging.basicConfig(level=os.environ.get("CDE_LOG_LEVEL", "INFO"))

# --- FastMCP App Initialization ---
app = FastMCP("CDE Orchestrator MCP")

# ============================================================================
# TOOL REGISTRATION
# ============================================================================
# All tools are registered with FastMCP using @app.tool() decorator.
# Error handling is managed by @tool_handler decorator in each module.

# --- Onboarding Tools ---
app.tool()(cde_onboardingProject)
app.tool()(cde_publishOnboarding)

# --- Documentation Tools ---
app.tool()(cde_scanDocumentation)
app.tool()(cde_analyzeDocumentation)

# --- Orchestration Tools ---
app.tool()(cde_selectWorkflow)
app.tool()(cde_sourceSkill)
app.tool()(cde_updateSkill)

# --- AI Agent Tools ---
app.tool()(cde_delegateToJules)
app.tool()(cde_listAvailableAgents)
app.tool()(cde_selectAgent)
app.tool()(cde_executeWithBestAgent)

# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """Run MCP server in development mode."""
    logger.info("🚀 Starting CDE Orchestrator MCP Server")
    logger.info(f"📦 Registered {11} tools")
    logger.info("✅ Server ready for connections")

    app.run()
