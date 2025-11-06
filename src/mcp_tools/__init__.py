"""
MCP Tools Package.

Exports all CDE Orchestrator MCP tools for registration in server.py.
"""

from .onboarding import cde_onboardingProject, cde_publishOnboarding, cde_setupProject
from .documentation import cde_scanDocumentation, cde_analyzeDocumentation
from .orchestration import cde_selectWorkflow, cde_sourceSkill, cde_updateSkill
from .agents import cde_delegateToJules, cde_listAvailableAgents, cde_selectAgent, cde_executeWithBestAgent
from .full_implementation import cde_executeFullImplementation
from .test_progress import cde_testProgressReporting
from .extensions import cde_installMcpExtension

__all__ = [
    # Onboarding
    "cde_onboardingProject",
    "cde_publishOnboarding",
    "cde_setupProject",
    # Documentation
    "cde_scanDocumentation",
    "cde_analyzeDocumentation",
    # Orchestration
    "cde_selectWorkflow",
    "cde_sourceSkill",
    "cde_updateSkill",
    # Agents
    "cde_delegateToJules",
    "cde_listAvailableAgents",
    "cde_selectAgent",
    "cde_executeWithBestAgent",
    # Full Implementation (Meta-orchestration)
    "cde_executeFullImplementation",
    # Test Progress
    "cde_testProgressReporting",
    # Extensions
    "cde_installMcpExtension",
]
