"""
Orchestration MCP Tools.

Tools for workflow selection, skill sourcing, and skill updating.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import Context

from cde_orchestrator.application.orchestration import (
    SkillSourcingUseCase,
    WebResearchUseCase,
    WorkflowSelectorUseCase,
)
from cde_orchestrator.infrastructure.dependency_injection import container

from ._base import tool_handler
from ._progress_reporter import get_progress_reporter


@tool_handler
def cde_selectWorkflow(user_prompt: str) -> str:
    """
    🧠 **Intelligent Workflow Selection** - Analyze user request and recommend optimal workflow.

    **This is THE ENTRY POINT for all CDE interactions!**

    Use this tool to:
    - Analyze task complexity (trivial → epic)
    - Select workflow type (standard, quick-fix, research, documentation, etc.)
    - Recommend recipe (ai-engineer, documentation-writer, deep-research)
    - Identify required skills
    - Estimate duration

    **How it works:**
    1. Analyzes user_prompt using keyword detection + heuristics
    2. Detects domain (web-dev, AI/ML, database, devops, testing, etc.)
    3. Calculates complexity score
    4. Recommends workflow + recipe + skills
    5. Returns confidence score (0.0-1.0)

    **Args:**
        user_prompt: Natural language description of what user wants

    **Returns:**
        JSON with:
        - workflow_type: "standard" | "quick-fix" | "research" | "documentation" | "refactor" | "hotfix"
        - complexity: "trivial" | "simple" | "moderate" | "complex" | "epic"
        - recipe_id: "ai-engineer" | "documentation-writer" | "deep-research" | "quick-fix"
        - estimated_duration: e.g., "1-2 hours"
        - required_skills: ["skill1", "skill2"]
        - phases_to_skip: ["define", "decompose"] (for quick-fix)
        - reasoning: Human-readable explanation
        - confidence: 0.85 (0.0-1.0)
        - domain: "web-dev" | "ai-ml" | "database" | etc.

    **Example 1: Feature Development**
        >>> cde_selectWorkflow("Add Redis caching to user authentication module")
        {
          "workflow_type": "standard",
          "complexity": "moderate",
          "recipe_id": "ai-engineer",
          "estimated_duration": "1-2 hours",
          "required_skills": ["redis-caching", "auth-best-practices"],
          "phases_to_skip": [],
          "reasoning": "Moderate complexity database + security task",
          "confidence": 0.85,
          "domain": "database"
        }

    **Example 2: Quick Fix**
        >>> cde_selectWorkflow("Fix typo in README: 'documenation' → 'documentation'")
        {
          "workflow_type": "quick-fix",
          "complexity": "trivial",
          "recipe_id": "quick-fix",
          "estimated_duration": "< 5 minutes",
          "required_skills": [],
          "phases_to_skip": ["define", "decompose", "design"],
          "reasoning": "Trivial text correction, no architecture needed",
          "confidence": 0.95,
          "domain": "documentation"
        }

    **Example 3: Research Task**
        >>> cde_selectWorkflow("Research best practices for microservices communication in 2025")
        {
          "workflow_type": "research",
          "complexity": "complex",
          "recipe_id": "deep-research",
          "estimated_duration": "4-8 hours",
          "required_skills": ["microservices-patterns", "system-design"],
          "phases_to_skip": ["implement", "test"],
          "reasoning": "Research-heavy architecture analysis",
          "confidence": 0.80,
          "domain": "architecture"
        }

    **Next Steps After This Tool:**
    1. If confidence < 0.6 → Ask user to clarify requirements
    2. If required_skills missing → Use `cde_sourceSkill` to download
    3. Otherwise → Use `cde_startFeature` with recommended workflow_type and recipe_id

    **Workflow Types Explained:**
    - standard: Full 6-phase (define → decompose → design → implement → test → review)
    - quick-fix: Skip define/decompose/design, jump to implement
    - research: Heavy research phase, light implementation
    - documentation: Focus on specs/docs, skip implementation
    - refactor: Code improvement without new features
    - hotfix: Emergency fix, minimal validation

    **Complexity Levels:**
    - trivial: < 5 min (typo, doc update)
    - simple: 15-30 min (single file change)
    - moderate: 1-2 hours (multiple files, tests)
    - complex: 4-8 hours (new feature, refactor)
    - epic: 2-5 days (major feature, architecture)
    """
    use_case = WorkflowSelectorUseCase()
    result = use_case.execute(user_prompt=user_prompt)
    return json.dumps(result, indent=2)


@tool_handler
async def cde_sourceSkill(
    skill_query: str, source: str = "awesome-claude-skills", destination: str = "base"
) -> str:
    """
    📚 **Skill Sourcing** - Download skills from external repositories.

    Use this tool to:
    - Download skills from awesome-claude-skills (GitHub)
    - Adapt external skill format to CDE-compatible markdown
    - Save to .copilot/skills/base/ (persistent) or /ephemeral/ (temporary)

    **How it works:**
    1. Searches awesome-claude-skills repo for matching skills
    2. Scores skills by relevance to query
    3. Downloads top 3 matches
    4. Adapts to CDE format (adds YAML frontmatter, preserves structure)
    5. Saves to specified destination

    **Args:**
        skill_query: What skill to search for (e.g., "redis caching patterns", "oauth2 implementation")
        source: Repository source (default: "awesome-claude-skills")
        destination: "base" (persistent, never deleted) or "ephemeral" (temporary, task-specific)

    **Returns:**
        JSON with:
        - skills_found: Total matches
        - skills_downloaded: Array of adapted skills
        - destination_path: Where skills were saved
        - saved_files: List of file paths

    **Example 1: Download Redis Skill**
        >>> cde_sourceSkill("redis caching patterns", destination="base")
        {
          "status": "success",
          "skills_found": 5,
          "skills_downloaded": [
            {
              "name": "redis-caching-patterns",
              "path": ".copilot/skills/base/redis-caching-patterns.md",
              "adaptations": ["Added CDE frontmatter", "Preserved examples"],
              "metadata": {
                "source": "awesome-claude-skills",
                "rating": 0.9,
                "tags": ["redis", "caching", "database"],
                "category": "engineering"
              }
            }
          ],
          "destination_path": ".copilot/skills/base",
          "saved_files": [".copilot/skills/base/redis-caching-patterns.md"]
        }

    **Example 2: Temporary Skill for Task**
        >>> cde_sourceSkill("react performance optimization", destination="ephemeral")
        # Skill downloaded to .copilot/skills/ephemeral/
        # Will be cleaned up after task completion

    **When to Use:**
    - After `cde_selectWorkflow` recommends skills you don't have
    - Starting work in unfamiliar domain
    - Want latest patterns and best practices
    - Before major implementation

    **Base vs Ephemeral:**
    - base: Generic, reusable knowledge (keep forever)
    - ephemeral: Task-specific context (clean up later)

    **Skill Adaptation:**
    CDE adapts external skills to include:
    - YAML frontmatter with metadata
    - Structured sections (Overview, When to Use, Tools, Examples, Best Practices)
    - Source attribution and import date
    - CDE-compatible formatting
    """
    reporter = get_progress_reporter()
    reporter.reset()
    reporter.report_progress(
        "CDE", "sourceSkill", 0.1, f"Searching for '{skill_query}'..."
    )

    use_case = SkillSourcingUseCase()

    reporter.report_progress("CDE", "sourceSkill", 0.4, "Downloading skills...")
    result = await use_case.execute(
        skill_query=skill_query, source=source, destination=destination
    )
    reporter.report_progress("CDE", "sourceSkill", 1.0, "Skills ready")

    return json.dumps(result, indent=2)


@tool_handler
async def cde_updateSkill(
    skill_name: str, topics: List[str], max_sources: int = 10
) -> str:
    """
    🔄 **Skill Updating** - Research and update skill with latest information.

    Use this tool to:
    - Keep skills current with latest library versions
    - Find breaking changes and deprecations
    - Discover new features and best practices
    - Research from official docs, GitHub, blogs, Stack Overflow

    **How it works:**
    1. Web research across multiple sources (official docs, GitHub, blogs)
    2. Extracts insights (breaking changes, deprecations, new features, best practices)
    3. Synthesizes findings using pattern matching + relevance scoring
    4. Generates structured update note
    5. Detects version changes

    **Args:**
        skill_name: Name of skill to update (e.g., "redis-caching")
        topics: List of specific topics to research (e.g., ["redis 7.x breaking changes", "connection pooling best practices"])
        max_sources: Maximum sources to fetch per topic (default: 10)

    **Returns:**
        JSON with:
        - insights: Array of research findings (breaking changes, deprecations, new features, best practices)
        - update_note: Markdown-formatted update log
        - sources: List of URLs consulted
        - version_info: Detected version changes

    **Example 1: Update Redis Skill**
        >>> cde_updateSkill(
        ...     skill_name="redis-caching",
        ...     topics=["redis 7.x breaking changes", "redis connection pooling best practices"]
        ... )
        {
          "status": "success",
          "skill_name": "redis-caching",
          "insights": [
            {
              "category": "breaking_change",
              "summary": "MIGRATE command now requires explicit AUTH in Redis 7.2+",
              "details": "...",
              "sources": ["https://redis.io/docs/releases/7.2.4/"],
              "confidence": 0.9
            },
            {
              "category": "best_practice",
              "summary": "Use connection pooling with redis-py>=5.0",
              "details": "...",
              "sources": ["https://redis-py.readthedocs.io/"],
              "confidence": 0.85
            }
          ],
          "update_note": "## 📅 Update Log - 2025-11-02\\n\\n### Research Summary...\\n",
          "sources": ["https://redis.io/docs", "https://github.com/redis/redis"],
          "version_info": {
            "current_versions": ["7.0.0"],
            "discovered_versions": ["7.2.4"]
          }
        }

    **Example 2: Monthly Maintenance**
        >>> cde_updateSkill(
        ...     skill_name="react-patterns",
        ...     topics=["react 19 updates", "react server components best practices"]
        ... )

    **When to Use:**
    - Before major implementation (ensure current knowledge)
    - Skill references old library versions
    - Monthly maintenance (background task)
    - After library major version release
    - When encountering deprecation warnings

    **Insight Categories:**
    - breaking_change: API changes requiring code updates
    - deprecation: Features being phased out
    - new_feature: New capabilities to leverage
    - best_practice: Recommended patterns and approaches

    **Sources Consulted:**
    - Official documentation (highest priority)
    - GitHub repositories (issues, discussions, releases)
    - Technical blogs (medium confidence)
    - Stack Overflow (for common problems)
    """
    reporter = get_progress_reporter()
    reporter.reset()
    reporter.report_progress(
        "CDE", "updateSkill", 0.1, f"Researching '{skill_name}'..."
    )

    use_case = WebResearchUseCase()

    # Convert skill_name to file path
    skill_file = Path(f".copilot/skills/base/{skill_name}.md")

    reporter.report_progress(
        "CDE", "updateSkill", 0.5, f"Analyzing {len(topics)} topics..."
    )
    result = await use_case.execute(
        skill_name=skill_name,
        topics=topics,
        max_sources=max_sources,
        skill_file_path=skill_file if skill_file.exists() else None,
    )
    reporter.report_progress("CDE", "updateSkill", 1.0, "Skill updated")

    return json.dumps(result, indent=2)


@tool_handler
async def cde_startFeature(
    ctx: Context,
    user_prompt: str,
    project_path: str = ".",
    workflow_type: str = "standard",
    recipe_id: str = "ai-engineer",
) -> str:
    """
    Start new feature in current project.

    Args:
        user_prompt: Feature description from user
        project_path: Path to project (default: current directory)
        workflow_type: Workflow variant (standard, quick-fix, etc.)
        recipe_id: Recipe to use (ai-engineer, etc.)

    Returns:
        JSON with feature_id, phase, and prompt.
    """
    if project_path == ".":
        project_path = str(Path.cwd())

    result = await container.start_feature_use_case.execute(
        project_path=project_path,
        user_prompt=user_prompt,
        workflow_type=workflow_type,
        recipe_id=recipe_id
    )
    return json.dumps(result, indent=2)


@tool_handler
async def cde_submitWork(
    ctx: Context,
    feature_id: str,
    phase_id: str,
    results: Dict[str, Any],
    project_path: str = ".",
) -> str:
    """
    Submit phase results and advance workflow.

    Args:
        feature_id: Feature UUID
        phase_id: Current phase (e.g., "define")
        results: Phase outputs (e.g., {"specification": "..."})
        project_path: Path to project (default: current directory)

    Returns:
        JSON with next phase prompt or completion status.
    """
    if project_path == ".":
        project_path = str(Path.cwd())

    result = await container.submit_work_use_case.execute(
        project_path=project_path,
        feature_id=feature_id,
        phase_id=phase_id,
        results=results
    )
    return json.dumps(result, indent=2)
