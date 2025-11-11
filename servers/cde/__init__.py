"""
CDE MCP Tools - Filesystem Discovery Pattern

Auto-generated tool stubs for progressive disclosure.

Usage:
    # List all tools (name_only)
    tools = [f.stem for f in Path("servers/cde").glob("*.py") if f.stem != "__init__"]

    # Load tool metadata (summary)
    from servers.cde import startFeature
    metadata = startFeature.TOOL_METADATA

    # Use actual tool (full)
    from mcp_tools import cde_startFeature
    result = cde_startFeature(user_prompt="...")

Token Efficiency:
- name_only: List files = 377 bytes (99.0% reduction)
- summary: Import + metadata = ~3KB (92% reduction)
- full: Actual implementation = ~40KB (baseline)
"""

# Auto-discovered tools
TOOLS = [
    "cde_analyzeDocumentation",  # servers/cde/analyzeDocumentation.py
    "cde_delegateToJules",  # servers/cde/delegateToJules.py
    "cde_executeFullImplementation",  # servers/cde/executeFullImplementation.py
    "cde_executeWithBestAgent",  # servers/cde/executeWithBestAgent.py
    "cde_installMcpExtension",  # servers/cde/installMcpExtension.py
    "cde_listAvailableAgents",  # servers/cde/listAvailableAgents.py
    "cde_onboardingProject",  # servers/cde/onboardingProject.py
    "cde_publishOnboarding",  # servers/cde/publishOnboarding.py
    "cde_scanDocumentation",  # servers/cde/scanDocumentation.py
    "cde_searchTools",  # servers/cde/searchTools.py
    "cde_selectAgent",  # servers/cde/selectAgent.py
    "cde_selectWorkflow",  # servers/cde/selectWorkflow.py
    "cde_setupProject",  # servers/cde/setupProject.py
    "cde_sourceSkill",  # servers/cde/sourceSkill.py
    "cde_testProgressReporting",  # servers/cde/testProgressReporting.py
    "cde_updateSkill",  # servers/cde/updateSkill.py
]

# Total tools
TOTAL_TOOLS = len(TOOLS)

# Export all
__all__ = TOOLS + ["TOTAL_TOOLS"]
