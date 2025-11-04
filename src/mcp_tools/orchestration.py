"""
Orchestration MCP Tools.

Tools for workflow selection, skill sourcing, and skill updating.
"""

import json
from pathlib import Path
from typing import List

from cde_orchestrator.application.orchestration import (
    SkillSourcingUseCase,
    WebResearchUseCase,
)
from cde_orchestrator.application.use_cases.select_workflow import SelectWorkflowUseCase

from ._base import tool_handler


@tool_handler
def cde_selectWorkflow(user_prompt: str, select_workflow_use_case: SelectWorkflowUseCase) -> str:
    """
    🧠 **Intelligent Workflow Selection** - Analyze user request and recommend optimal workflow.
    ...
    """
    result = select_workflow_use_case.execute(user_prompt=user_prompt)
    return json.dumps(result, indent=2)


@tool_handler
async def cde_sourceSkill(
    skill_query: str, source: str = "awesome-claude-skills", destination: str = "base"
) -> str:
    """
    📚 **Skill Sourcing** - Download skills from external repositories.
    ...
    """
    use_case = SkillSourcingUseCase()
    result = await use_case.execute(
        skill_query=skill_query, source=source, destination=destination
    )
    return json.dumps(result, indent=2)


@tool_handler
async def cde_updateSkill(
    skill_name: str, topics: List[str], max_sources: int = 10
) -> str:
    """
    🔄 **Skill Updating** - Research and update skill with latest information.
    ...
    """
    use_case = WebResearchUseCase()

    # Convert skill_name to file path
    skill_file = Path(f".copilot/skills/base/{skill_name}.md")

    result = await use_case.execute(
        skill_name=skill_name,
        topics=topics,
        max_sources=max_sources,
        skill_file_path=skill_file if skill_file.exists() else None,
    )
    return json.dumps(result, indent=2)
