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
from .git_analysis import cde_analyzeGit
from .health import cde_healthCheck
from .onboarding import cde_onboardingProject, cde_publishOnboarding, cde_setupProject
from .orchestration import (
    cde_selectWorkflow,
    cde_sourceSkill,
    cde_startFeature,
    cde_submitWork,
    cde_updateSkill,
)
from .recipes import cde_checkRecipes, cde_downloadRecipes
from .spec_generator import cde_generateSpec
from .template_sync import cde_syncTemplates, cde_validateSpec
from .test_progress import cde_testProgressReporting
from .tool_search import cde_searchTools

__all__ = [
    # Health
    "cde_healthCheck",
    # Onboarding
    "cde_onboardingProject",
    "cde_publishOnboarding",
    "cde_setupProject",
    # Spec Generation
    "cde_generateSpec",
    # Template Sync & Validation
    "cde_syncTemplates",
    "cde_validateSpec",
    # Documentation
    "cde_scanDocumentation",
    "cde_analyzeDocumentation",
    # Git Analysis
    "cde_analyzeGit",
    # Orchestration
    "cde_selectWorkflow",
    "cde_sourceSkill",
    "cde_updateSkill",
    "cde_startFeature",
    "cde_submitWork",
    # Recipes
    "cde_downloadRecipes",
    "cde_checkRecipes",
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
