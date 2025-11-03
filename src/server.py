# src/server.py
import asyncio
import json
import logging
import os
from functools import wraps
from pathlib import Path
from typing import Dict, List

from fastmcp import FastMCP
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

from cde_orchestrator.application.onboarding import OnboardingUseCase
from cde_orchestrator.application.documentation import (
    ScanDocumentationUseCase,
    AnalyzeDocumentationUseCase,
)
from cde_orchestrator.application.orchestration import (
    WorkflowSelectorUseCase,
    SkillSourcingUseCase,
    WebResearchUseCase,
)
from cde_orchestrator.adapters.prompt import PromptAdapter
from cde_orchestrator.adapters.repository.git_adapter import GitAdapter
from cde_orchestrator.adapters.state import StateAdapter

# --- Constants and Configuration ---
CDE_ROOT = Path(".cde")
WORKFLOW_FILE = CDE_ROOT / "workflow.yml"
STATE_FILE = CDE_ROOT / "state.json"
PROMPT_RECIPES_DIR = CDE_ROOT / "prompts"
RECIPES_DIR = CDE_ROOT / "recipes"
SPECS_DIR = Path("specs")


# --- Core Service Initialization ---
logger = logging.getLogger("cde_orchestrator.server")
logging.basicConfig(level=os.environ.get("CDE_LOG_LEVEL", "INFO"))

app = FastMCP("CDE Orchestrator MCP")

state_manager = StateAdapter(STATE_FILE)
prompt_manager = PromptAdapter(PROMPT_RECIPES_DIR)


def _serialize_error(tool_name: str, exc: BaseException) -> str:
    """Normalize tool errors into a consistent JSON payload."""
    logger.exception("Tool %s failed: %s", tool_name, exc)
    return json.dumps(
        {
            "error": "tool_execution_failed",
            "tool": tool_name,
            "message": str(exc),
        },
        indent=2,
    )


def tool_handler(func):
    """Decorator that adds logging and error normalization for MCP tools."""

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - want full logging
                return _serialize_error(func.__name__, exc)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - want full logging
            return _serialize_error(func.__name__, exc)

    return sync_wrapper

@app.tool()
@tool_handler
async def cde_onboardingProject(ctx: Context[ServerSession, None]) -> str: # Made async, added Context
    """
    Analyzes project structure and performs onboarding setup.
    Automatically detects if onboarding is needed and creates Spec-Kit compatible structure.
    Now includes AI assistant configuration following 2025 industry best practices.
    This is typically called when first connecting the MCP server to a new or existing project.

    Args:
        ctx: FastMCP Context for progress reporting and logging

    Returns:
        A contextualized prompt for the AI agent to execute onboarding,
        or a message if onboarding is not needed
    """
    # START: Progress tracking 🚀
    await ctx.info("🚀 CDE Onboarding Analysis Started")
    await ctx.report_progress(0.0, 1.0, "Initializing onboarding analysis")

    project_root = Path.cwd()
    await ctx.debug(f"Project root: {project_root}")

    git_adapter = GitAdapter(project_root) # Instantiate GitAdapter
    analyzer = OnboardingUseCase(project_root, git_adapter) # Pass GitAdapter

    # Checkpoint 1: Structure scan (20%)
    await ctx.info("📁 Scanning project structure...")
    await ctx.report_progress(0.2, 1.0, "Scanning directory structure")

    # Check if onboarding is needed
    analysis = await analyzer.needs_onboarding() # Await needs_onboarding

    # Checkpoint 2: Analysis complete (40%)
    git_info = analysis.get("project_info", {}).get("git", {})
    commit_count = git_info.get("commit_count", 0)
    missing_count = len(analysis.get("missing_structure", []))

    await ctx.info(f"📊 Analysis: {commit_count} commits, {missing_count} missing items")
    await ctx.report_progress(0.4, 1.0, f"Structure analysis complete")

    if not analysis["needs_onboarding"]:
        await ctx.info("✅ Project already configured!")
        await ctx.report_progress(1.0, 1.0, "Analysis complete - no onboarding needed")
        return json.dumps(
            {
                "status": "already_configured",
                "message": "Project already has Spec-Kit compatible structure.",
                "existing_structure": analysis["existing_structure"],
            },
            indent=2,
        )

    # Checkpoint 3: Generate plan (60%)
    await ctx.info("📝 Generating onboarding plan...")
    await ctx.report_progress(0.6, 1.0, "Generating comprehensive plan")

    # Generate onboarding plan
    plan = await analyzer.generate_onboarding_plan() # Await generate_onboarding_plan

    await ctx.debug(f"Plan generated: {len(plan.get('docs_to_generate', []))} docs, {len(plan.get('structure_to_create', []))} directories")

    # Checkpoint 4: AI Assistant detection (75%)
    await ctx.info("🤖 Detecting AI assistants...")
    await ctx.report_progress(0.75, 1.0, "Detecting AI agents")

    # Detect AI assistants available on the system
    from .cde_orchestrator.application.ai_config import AIConfigUseCase

    ai_configurator = AIConfigUseCase(project_root)
    detected_agents = ai_configurator.detect_installed_agents()
    ai_summary = ai_configurator.get_configuration_summary()

    if detected_agents:
        await ctx.info(f"✨ Detected: {', '.join(detected_agents)}")
    else:
        await ctx.debug("No AI assistants detected")

    logger.info(
        f"Detected AI assistants: {', '.join(detected_agents) if detected_agents else 'none'}"
    )

    # Prepare context for POML prompt
    # repo_digest will be populated by GitAdapter in future tasks
    repo_digest = {
        "summary": "Repository digest will be generated by GitAdapter.",
        "tree": [],
        "top_files": [],
    }

    plan_context = plan.get("context", {})
    context = {
        "PROJECT_ANALYSIS": json.dumps(analysis, indent=2),
        "GIT_INSIGHTS": json.dumps(analysis["project_info"]["git"], indent=2),
        "MISSING_STRUCTURE": json.dumps(analysis["missing_structure"], indent=2),
        "TECH_STACK": json.dumps(analyzer._detect_tech_stack(), indent=2),
        "REPO_DIGEST": json.dumps(
            {
                "summary": repo_digest.get("summary"),
                "top_files": [
                    {"path": f["path"], "snippet": f["snippet"][:1000]}
                    for f in repo_digest.get("top_files", [])[:10]
                ],
            },
            indent=2,
        ),
        "REPO_SYNTHESIS": json.dumps(
            plan_context.get("repository_synthesis", {}), indent=2
        ),
        "CLEANUP_RECOMMENDATIONS": json.dumps(plan.get("cleanup_plan", {}), indent=2),
        "AI_ASSISTANTS": json.dumps(
            {
                "detected": detected_agents,
                "summary": ai_summary,
                "recommendation": "Configure AI assistant instruction files (AGENTS.md, GEMINI.md, .github/copilot-instructions.md) following 2025 industry standards.",
            },
            indent=2,
        ),
        "MANAGEMENT_PRINCIPLES": (
            "Specification-as-Code, Single Source of Truth (Git + Issues), Progressive Scalability, "
            "Automation-friendly structure for AI assistants. "
            "AI-First Documentation: AGENTS.md (OpenAI standard), GEMINI.md (Google AI Studio), "
            ".github/copilot-instructions.md (GitHub Copilot)."
        ),
    }

    # Checkpoint 5: Prepare prompt (90%)
    await ctx.info("📄 Preparing onboarding prompt...")
    await ctx.report_progress(0.9, 1.0, "Loading prompt template")

    # Load and prepare onboarding prompt
    onboarding_prompt_path = PROMPT_RECIPES_DIR / "00_onboarding.poml"
    if not onboarding_prompt_path.exists():
        await ctx.error(f"❌ Prompt template not found: {onboarding_prompt_path}")
        return json.dumps(
            {
                "error": "Onboarding prompt not found",
                "expected_path": str(onboarding_prompt_path),
            },
            indent=2,
        )

    try:
        final_prompt = prompt_manager.load_and_prepare(onboarding_prompt_path, context)

        # Save plan and prompt to state for reference and require human approval before writing files
        state = state_manager.load_state()
        if "onboarding" not in state:
            state["onboarding"] = {}
        state["onboarding"]["plan"] = plan
        state["onboarding"]["analysis"] = analysis
        state["onboarding"]["cleanup_plan"] = plan.get("cleanup_plan", {})
        state["onboarding"]["repository_synthesis"] = plan_context.get(
            "repository_synthesis", {}
        )
        state["onboarding"]["ai_assistants"] = {
            "detected": detected_agents,
            "summary": ai_summary,
        }
        # store the generated prompt as a draft (not yet applied)
        state["onboarding"]["draft_prompt"] = final_prompt
        state["onboarding"]["repo_digest"] = repo_digest
        state["onboarding"]["awaiting_approval"] = True
        state_manager.save_state(state)

        # Checkpoint 6: Complete! (100%)
        await ctx.info("✅ Onboarding draft ready!")
        await ctx.report_progress(1.0, 1.0, "Complete - awaiting document generation")

        await ctx.info("📋 Next: Use LLM to generate documents, then call cde_publishOnboarding")

        # Return the prompt to the client so it can generate draft documents with an LLM.
        # The user must call the `cde_publishOnboarding` tool with the generated documents
        # to persist them into the repository (this enforces human validation).
        return json.dumps(
            {
                "status": "draft_ready",
                "message": "Onboarding draft prompt prepared. Use an LLM to generate documents, then call cde_publishOnboarding to apply after human approval.",
                "draft_preview": final_prompt[:2000],
                "detected_agents": detected_agents,
                "missing_count": missing_count,
                "commit_count": commit_count,
            },
            indent=2,
        )
    except Exception as exc:
        logger.exception("Error generating onboarding prompt")
        await ctx.error(f"❌ Failed to generate prompt: {str(exc)}")
        return json.dumps(
            {"error": "onboarding_prompt_failed", "message": str(exc)}, indent=2
        )


@app.tool()
@tool_handler
def cde_publishOnboarding(documents: Dict[str, str], approve: bool = True) -> str:
    """Apply onboarding documents generated by an LLM into the repo.

    Args:
        documents: mapping file_path -> content (relative to project root)
        approve: boolean that confirms the user approves writing these files

    Returns:
        status message
    """
    project_root = Path.cwd()
    state = state_manager.load_state()
    onboarding = state.get("onboarding", {})

    if not onboarding.get("awaiting_approval"):
        return json.dumps(
            {
                "error": "no_onboarding_pending",
                "message": "Run cde_onboardingProject first.",
            },
            indent=2,
        )

    if not approve:
        # mark as declined
        onboarding["awaiting_approval"] = False
        onboarding["approved"] = False
        state_manager.save_state(state)
        return json.dumps(
            {"status": "declined", "message": "Onboarding draft declined by user."},
            indent=2,
        )

    # Apply documents: write files under project_root, but do not commit (user workflow can commit)
    created = []
    failed = []
    for path, content in (documents or {}).items():
        try:
            dest = project_root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            created.append(str(dest.relative_to(project_root)))
        except Exception as e:
            failed.append({"path": path, "error": str(e)})

    onboarding["awaiting_approval"] = False
    onboarding["approved"] = True
    onboarding["created_files"] = created
    onboarding["failed_writes"] = failed
    state_manager.save_state(state)

    return json.dumps(
        {"status": "applied", "created": created, "failed": failed}, indent=2
    )


# ============================================================================
# DOCUMENTATION MANAGEMENT TOOLS (NEW)
# ============================================================================


@app.tool()
@tool_handler
def cde_scanDocumentation(project_path: str = ".") -> str:
    """
    Scan and analyze documentation structure in a project.

    **USE THIS TOOL TO:**
    - Audit documentation organization
    - Find missing metadata (YAML frontmatter)
    - Identify orphaned documents
    - Get recommendations for improvement

    Args:
        project_path: Path to project root (default: current directory)

    Returns:
        JSON with:
            - total_docs: Total markdown files found
            - by_location: Documents grouped by directory
            - missing_metadata: Files without YAML frontmatter
            - orphaned_docs: Files not in standard directories
            - large_files: Documents exceeding 1000 lines
            - recommendations: Actionable improvement suggestions

    Examples:
        >>> cde_scanDocumentation(".")
        {
          "total_docs": 45,
          "missing_metadata": ["docs/old-guide.md", "README-backup.md"],
          "recommendations": [
            "🔴 12 documents missing YAML frontmatter metadata",
            "⚠️ 3 orphaned documents in root directory"
          ]
        }

        >>> cde_scanDocumentation("E:\\my-project")
        # Scan specific project

    **Common Use Cases:**
    1. Initial project audit: `cde_scanDocumentation(".")`
    2. Before migration: Check what needs fixing
    3. After cleanup: Verify improvements
    """
    use_case = ScanDocumentationUseCase()

    # Resolve project path
    if project_path == ".":
        project_path = os.getcwd()

    result = use_case.execute(project_path)
    return json.dumps(result, indent=2)


@app.tool()
@tool_handler
def cde_analyzeDocumentation(project_path: str = ".") -> str:
    """
    Deep analysis of documentation quality and structure.

    **USE THIS TOOL TO:**
    - Check link integrity (find broken links)
    - Analyze metadata consistency
    - Get quality score (0-100)
    - Identify specific issues
    - Get actionable suggestions

    Args:
        project_path: Path to project root (default: current directory)

    Returns:
        JSON with:
            - quality_score: Overall quality rating (0-100)
            - link_analysis: Broken/valid links
            - metadata_analysis: Consistency checks
            - quality_indicators: Content quality metrics
            - issues: List of problems found
            - suggestions: Actionable improvements

    Examples:
        >>> cde_analyzeDocumentation(".")
        {
          "quality_score": 72.5,
          "link_analysis": {
            "total_links": 156,
            "valid_links": 142,
            "broken_links": 14
          },
          "issues": [
            "🔴 14 broken internal links detected",
            "⚠️ 8 files missing required metadata fields"
          ],
          "suggestions": [
            "✅ Documentation quality is good. Minor improvements recommended.",
            "→ Fix broken links to improve navigation",
            "→ Add YAML frontmatter to all documents"
          ]
        }

    **Quality Score Breakdown:**
    - 90-100: Excellent (well-organized, complete metadata, no broken links)
    - 70-89: Good (minor issues, mostly organized)
    - 50-69: Needs work (missing metadata, broken links)
    - <50: Poor (major issues, needs comprehensive audit)

    **Common Use Cases:**
    1. Health check: `cde_analyzeDocumentation(".")`
    2. Pre-migration assessment: See what needs fixing
    3. Post-cleanup validation: Verify improvements
    """
    use_case = AnalyzeDocumentationUseCase()

    # Resolve project path
    if project_path == ".":
        project_path = os.getcwd()

    result = use_case.execute(project_path)
    return json.dumps(result, indent=2)


# ========================================
# WORKFLOW ORCHESTRATION TOOLS (NEW)
# ========================================

@app.tool()
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


@app.tool()
@tool_handler
async def cde_sourceSkill(
    skill_query: str,
    source: str = "awesome-claude-skills",
    destination: str = "base"
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
    use_case = SkillSourcingUseCase()
    result = await use_case.execute(
        skill_query=skill_query,
        source=source,
        destination=destination
    )
    return json.dumps(result, indent=2)


@app.tool()
@tool_handler
async def cde_updateSkill(
    skill_name: str,
    topics: List[str],
    max_sources: int = 10
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
    use_case = WebResearchUseCase()

    # Convert skill_name to file path
    skill_file = Path(f".copilot/skills/base/{skill_name}.md")

    result = await use_case.execute(
        skill_name=skill_name,
        topics=topics,
        max_sources=max_sources,
        skill_file_path=skill_file if skill_file.exists() else None
    )
    return json.dumps(result, indent=2)


@app.tool()
@tool_handler
async def cde_delegateToJules(
    user_prompt: str,
    project_path: str = ".",
    branch: str = "main",
    require_plan_approval: bool = False,
    timeout: int = 1800,
    detached: bool = False
) -> str:
    """
    🤖 **Jules AI Agent Integration** - Delegate complex coding tasks to Jules.

    Use this tool to execute long-running, complex development tasks using Jules,
    Google's async AI coding agent with full repository context.

    **When to Use:**
    - Complex feature development (4-8 hours estimated)
    - Large-scale refactoring across multiple files
    - Tasks requiring full codebase context
    - Long-running tasks that need async execution

    **Advantages over CLI Agents:**
    - Full repository context (100,000+ lines)
    - Plan generation with approval workflow
    - Progress tracking via activities
    - Session persistence (resume later)
    - Web UI for monitoring

    **Requirements:**
    - JULES_API_KEY in .env file
    - Repository connected to Jules (https://jules.google/)
    - jules-agent-sdk installed

    **Args:**
        user_prompt: Natural language task description
            Example: "Refactor authentication module to use OAuth2 with comprehensive error handling"

        project_path: Path to project (default: current directory)

        branch: Starting Git branch (default: "main")

        require_plan_approval: Wait for human approval of execution plan (default: False)
            Set to True for critical/complex tasks

        timeout: Maximum wait time in seconds (default: 1800 = 30 minutes)
            Set to 3600 for very complex tasks

        detached: Don't wait for completion, return immediately (default: False)
            Use for very long tasks, check status separately

    **Returns:**
        JSON with:
        - success: bool
        - session_id: Jules session ID
        - state: COMPLETED | FAILED | IN_PROGRESS
        - modified_files: List of changed files
        - activities_count: Number of actions taken
        - log: Human-readable activity log
        - metadata: Session URL, prompt, etc.

    **Example 1: Simple Feature**
        >>> result = cde_delegateToJules(
        ...     user_prompt="Add comprehensive logging to all API endpoints",
        ...     branch="develop"
        ... )
        >>> # Returns: Session completed with 12 files modified

    **Example 2: Complex Refactor with Plan Approval**
        >>> result = cde_delegateToJules(
        ...     user_prompt="Migrate database layer from SQLAlchemy to SQLModel with type safety",
        ...     require_plan_approval=True,
        ...     timeout=3600
        ... )
        >>> # Jules generates plan → you approve → execution proceeds

    **Example 3: Detached Execution (Long-Running)**
        >>> result = cde_delegateToJules(
        ...     user_prompt="Complete system-wide security audit and apply fixes",
        ...     detached=True
        ... )
        >>> # Returns immediately with session_id
        >>> # Check progress at Jules web UI

    **Workflow:**
    1. Jules resolves project to source (cached after first time)
    2. Creates session with your prompt
    3. Generates execution plan (if approval required, waits)
    4. Executes code changes
    5. Returns results with activity log

    **Error Handling:**
    - If project not connected to Jules → Error with setup instructions
    - If API key invalid → Authentication error
    - If session fails → Error with failure details

    **See Also:**
    - cde_selectWorkflow() - Analyze task and recommend agent
    - cde_listAvailableAgents() - Check which agents are available
    """
    import os
    from pathlib import Path
    from cde_orchestrator.adapters.agents import JulesAsyncAdapter

    try:
        # Get API key from environment
        api_key = os.getenv("JULES_API_KEY")
        if not api_key:
            return json.dumps({
                "error": "JULES_API_KEY not found in environment",
                "message": "Add JULES_API_KEY to your .env file. Get key from https://jules.google/",
                "setup_instructions": [
                    "1. Go to https://jules.google/",
                    "2. Sign in with Google",
                    "3. Go to Settings → API Keys",
                    "4. Create new API key",
                    "5. Add to .env: JULES_API_KEY=your-key-here"
                ]
            }, indent=2)

        # Initialize Jules adapter
        adapter = JulesAsyncAdapter(
            api_key=api_key,
            default_timeout=timeout,
            require_plan_approval=require_plan_approval
        )

        # Execute prompt
        result_json = await adapter.execute_prompt(
            project_path=Path(project_path),
            prompt=user_prompt,
            context={
                "branch": branch,
                "timeout": timeout,
                "detached": detached,
                "require_plan_approval": require_plan_approval
            }
        )

        # Close adapter
        await adapter.close()

        return result_json

    except Exception as e:
        return json.dumps({
            "error": "jules_execution_failed",
            "message": str(e),
            "type": type(e).__name__
        }, indent=2)


@app.tool()
@tool_handler
async def cde_listAvailableAgents() -> str:
    """
    📋 **List Available AI Coding Agents** - Check which agents are ready to use.

    Returns information about all configured AI coding agents and their availability.

    **Agents Supported:**
    - **Jules**: Async AI agent with full repo context (requires API key)
    - **Copilot CLI**: GitHub Copilot suggestions (requires gh copilot extension)
    - **Gemini CLI**: Google Gemini code generation (requires gemini CLI)
    - **Qwen CLI**: Alibaba Qwen agent (requires qwen CLI)

    **Returns:**
        JSON with:
        - available_agents: List of ready-to-use agents
        - unavailable_agents: List of agents with setup required
        - recommendations: Which agent to use for current task

    **Example:**
        >>> result = cde_listAvailableAgents()
        >>> {
        ...   "available_agents": [
        ...     {
        ...       "name": "Jules",
        ...       "type": "async_api",
        ...       "status": "available",
        ...       "capabilities": ["full_context", "plan_approval", "long_running"],
        ...       "best_for": ["refactoring", "complex_features"]
        ...     },
        ...     {
        ...       "name": "Copilot CLI",
        ...       "type": "sync_cli",
        ...       "status": "available",
        ...       "capabilities": ["quick_suggestions", "code_generation"],
        ...       "best_for": ["quick_fixes", "code_completion"]
        ...     }
        ...   ],
        ...   "unavailable_agents": [
        ...     {
        ...       "name": "Gemini CLI",
        ...       "status": "not_installed",
        ...       "install_command": "pip install gemini-cli"
        ...     }
        ...   ]
        ... }
    """
    import os
    import shutil

    agents_status = []

    # Check Jules
    jules_available = bool(os.getenv("JULES_API_KEY"))
    try:
        import jules_agent_sdk
        jules_sdk_installed = True
    except ImportError:
        jules_sdk_installed = False

    agents_status.append({
        "name": "Jules",
        "type": "async_api",
        "status": "available" if (jules_available and jules_sdk_installed) else "unavailable",
        "api_key_configured": jules_available,
        "sdk_installed": jules_sdk_installed,
        "capabilities": ["full_context", "plan_approval", "long_running", "async"],
        "best_for": ["refactoring", "complex_features", "large_scale_changes"],
        "setup_required": [] if (jules_available and jules_sdk_installed) else [
            "Install SDK: pip install jules-agent-sdk" if not jules_sdk_installed else None,
            "Add JULES_API_KEY to .env" if not jules_available else None
        ]
    })

    # Check Copilot CLI
    copilot_available = shutil.which("gh") is not None
    agents_status.append({
        "name": "Copilot CLI",
        "type": "sync_cli",
        "status": "available" if copilot_available else "unavailable",
        "cli_installed": copilot_available,
        "capabilities": ["quick_suggestions", "code_generation"],
        "best_for": ["quick_fixes", "code_completion", "suggestions"],
        "setup_required": [] if copilot_available else [
            "Install GitHub CLI: https://cli.github.com/",
            "Install extension: gh extension install github/gh-copilot"
        ]
    })

    # Check Gemini CLI
    gemini_available = shutil.which("gemini") is not None
    agents_status.append({
        "name": "Gemini CLI",
        "type": "sync_cli",
        "status": "available" if gemini_available else "unavailable",
        "cli_installed": gemini_available,
        "capabilities": ["code_understanding", "documentation", "analysis"],
        "best_for": ["documentation", "code_analysis", "quick_tasks"],
        "setup_required": [] if gemini_available else [
            "Install Gemini CLI: https://ai.google.dev/gemini-api/docs/cli"
        ]
    })

    # Check Qwen CLI
    qwen_available = shutil.which("qwen") is not None
    agents_status.append({
        "name": "Qwen CLI",
        "type": "sync_cli",
        "status": "available" if qwen_available else "unavailable",
        "cli_installed": qwen_available,
        "capabilities": ["code_generation", "fallback"],
        "best_for": ["backup_option"],
        "setup_required": [] if qwen_available else [
            "Install Qwen CLI: pip install qwen-cli"
        ]
    })

    available = [a for a in agents_status if a["status"] == "available"]
    unavailable = [a for a in agents_status if a["status"] == "unavailable"]

    return json.dumps({
        "summary": f"{len(available)}/{len(agents_status)} agents available",
        "available_agents": available,
        "unavailable_agents": unavailable,
        "recommendations": {
            "complex_tasks": "Jules (async, full context)" if any(a["name"] == "Jules" for a in available) else "None available",
            "quick_fixes": "Copilot CLI" if any(a["name"] == "Copilot CLI" for a in available) else "Gemini CLI",
            "documentation": "Gemini CLI" if any(a["name"] == "Gemini CLI" for a in available) else "Copilot CLI"
        }
    }, indent=2)


if __name__ == "__main__":
    # This allows running the server directly for testing
    app.run()
