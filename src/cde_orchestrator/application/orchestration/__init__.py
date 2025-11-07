"""
Orchestration Use Cases

High-level use cases for intelligent workflow orchestration:
- Workflow selection (route user prompts to optimal workflows)
- Skill sourcing (download skills from external repos)
- Web research (keep skills current with latest info)
"""

from .skill_sourcing_use_case import (
    ExternalSkill,
    SkillAdaptation,
    SkillSourcingUseCase,
)
from .web_research_use_case import (
    ResearchInsight,
    ResearchSource,
    SkillUpdate,
    WebResearchUseCase,
)
from .workflow_selector_use_case import (
    DomainCategory,
    WorkflowComplexity,
    WorkflowRecommendation,
    WorkflowSelectorUseCase,
    WorkflowType,
)

__all__ = [
    # Workflow Selection
    "WorkflowSelectorUseCase",
    "WorkflowRecommendation",
    "WorkflowComplexity",
    "WorkflowType",
    "DomainCategory",
    # Skill Sourcing
    "SkillSourcingUseCase",
    "ExternalSkill",
    "SkillAdaptation",
    # Web Research
    "WebResearchUseCase",
    "ResearchSource",
    "ResearchInsight",
    "SkillUpdate",
]
