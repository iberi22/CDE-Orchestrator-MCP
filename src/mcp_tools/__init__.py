"""
MCP Tools Package.

Exports all CDE Orchestrator MCP tools for registration in server.py.
"""

from .agents import (
    cde_delegateToJules,
    cde_executeWithBestAgent,
    cde_listAvailableAgents,
    cde_selectAgent,
)
from .documentation import cde_analyzeDocumentation, cde_scanDocumentation
from .extensions import cde_installMcpExtension
from .full_implementation import cde_executeFullImplementation
from .health import cde_healthCheck
from .onboarding import cde_onboardingProject, cde_publishOnboarding, cde_setupProject
from .orchestration import cde_selectWorkflow, cde_sourceSkill, cde_updateSkill
from .test_progress import cde_testProgressReporting
from .tool_search import cde_searchTools

__all__ = [
    # Health
    "cde_healthCheck",
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
    # Tool Discovery (Progressive Disclosure - Anthropic Pattern)
    "cde_searchTools",
]
