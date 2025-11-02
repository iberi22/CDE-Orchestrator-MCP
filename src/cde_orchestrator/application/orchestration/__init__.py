"""
Orchestration Use Cases

High-level use cases for intelligent workflow orchestration:
- Workflow selection (route user prompts to optimal workflows)
- Skill sourcing (download skills from external repos)
- Web research (keep skills current with latest info)
"""

from .workflow_selector_use_case import (
    WorkflowSelectorUseCase,
    WorkflowRecommendation,
    WorkflowComplexity,
    WorkflowType,
    DomainCategory
)

from .skill_sourcing_use_case import (
    SkillSourcingUseCase,
    ExternalSkill,
    SkillAdaptation
)

from .web_research_use_case import (
    WebResearchUseCase,
    ResearchSource,
    ResearchInsight,
    SkillUpdate
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
