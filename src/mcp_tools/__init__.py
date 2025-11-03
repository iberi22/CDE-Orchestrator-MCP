"""
MCP Tools Package.

Exports all CDE Orchestrator MCP tools for registration in server.py.
"""

from .onboarding import cde_onboardingProject, cde_publishOnboarding
from .documentation import cde_scanDocumentation, cde_analyzeDocumentation
from .orchestration import cde_selectWorkflow, cde_sourceSkill, cde_updateSkill
from .agents import cde_delegateToJules, cde_listAvailableAgents

__all__ = [
    # Onboarding
    "cde_onboardingProject",
    "cde_publishOnboarding",
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
]
