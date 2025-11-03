"""
AI Agents MCP Tools.

Tools for delegating tasks to AI coding agents and checking availability.
"""

import json
import os
import shutil
from pathlib import Path

from cde_orchestrator.adapters.agents import JulesAsyncAdapter

from ._base import tool_handler


@tool_handler
async def cde_delegateToJules(
    user_prompt: str,
    project_path: str = ".",
    branch: str = "main",
    require_plan_approval: bool = False,
    timeout: int = 1800,
    detached: bool = False,
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
    try:
        # Get API key from environment
        api_key = os.getenv("JULES_API_KEY")
        if not api_key:
            return json.dumps(
                {
                    "error": "JULES_API_KEY not found in environment",
                    "message": "Add JULES_API_KEY to your .env file. Get key from https://jules.google/",
                    "setup_instructions": [
                        "1. Go to https://jules.google/",
                        "2. Sign in with Google",
                        "3. Go to Settings → API Keys",
                        "4. Create new API key",
                        "5. Add to .env: JULES_API_KEY=your-key-here",
                    ],
                },
                indent=2,
            )

        # Initialize Jules adapter
        adapter = JulesAsyncAdapter(
            api_key=api_key,
            default_timeout=timeout,
            require_plan_approval=require_plan_approval,
        )

        # Execute prompt
        result_json = await adapter.execute_prompt(
            project_path=Path(project_path),
            prompt=user_prompt,
            context={
                "branch": branch,
                "timeout": timeout,
                "detached": detached,
                "require_plan_approval": require_plan_approval,
            },
        )

        # Close adapter
        await adapter.close()

        return result_json

    except Exception as e:
        return json.dumps(
            {
                "error": "jules_execution_failed",
                "message": str(e),
                "type": type(e).__name__,
            },
            indent=2,
        )


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
    agents_status = []

    # Check Jules
    jules_available = bool(os.getenv("JULES_API_KEY"))
    try:
        import importlib.util

        jules_sdk_installed = importlib.util.find_spec("jules_agent_sdk") is not None
    except ImportError:
        jules_sdk_installed = False

    agents_status.append(
        {
            "name": "Jules",
            "type": "async_api",
            "status": (
                "available"
                if (jules_available and jules_sdk_installed)
                else "unavailable"
            ),
            "api_key_configured": jules_available,
            "sdk_installed": jules_sdk_installed,
            "capabilities": ["full_context", "plan_approval", "long_running", "async"],
            "best_for": ["refactoring", "complex_features", "large_scale_changes"],
            "setup_required": (
                []
                if (jules_available and jules_sdk_installed)
                else [
                    (
                        "Install SDK: pip install jules-agent-sdk"
                        if not jules_sdk_installed
                        else None
                    ),
                    "Add JULES_API_KEY to .env" if not jules_available else None,
                ]
            ),
        }
    )

    # Check Copilot CLI
    copilot_available = shutil.which("gh") is not None
    agents_status.append(
        {
            "name": "Copilot CLI",
            "type": "sync_cli",
            "status": "available" if copilot_available else "unavailable",
            "cli_installed": copilot_available,
            "capabilities": ["quick_suggestions", "code_generation"],
            "best_for": ["quick_fixes", "code_completion", "suggestions"],
            "setup_required": (
                []
                if copilot_available
                else [
                    "Install GitHub CLI: https://cli.github.com/",
                    "Install extension: gh extension install github/gh-copilot",
                ]
            ),
        }
    )

    # Check Gemini CLI
    gemini_available = shutil.which("gemini") is not None
    agents_status.append(
        {
            "name": "Gemini CLI",
            "type": "sync_cli",
            "status": "available" if gemini_available else "unavailable",
            "cli_installed": gemini_available,
            "capabilities": ["code_understanding", "documentation", "analysis"],
            "best_for": ["documentation", "code_analysis", "quick_tasks"],
            "setup_required": (
                []
                if gemini_available
                else ["Install Gemini CLI: https://ai.google.dev/gemini-api/docs/cli"]
            ),
        }
    )

    # Check Qwen CLI
    qwen_available = shutil.which("qwen") is not None
    agents_status.append(
        {
            "name": "Qwen CLI",
            "type": "sync_cli",
            "status": "available" if qwen_available else "unavailable",
            "cli_installed": qwen_available,
            "capabilities": ["code_generation", "fallback"],
            "best_for": ["backup_option"],
            "setup_required": (
                [] if qwen_available else ["Install Qwen CLI: pip install qwen-cli"]
            ),
        }
    )

    available = [a for a in agents_status if a["status"] == "available"]
    unavailable = [a for a in agents_status if a["status"] == "unavailable"]

    return json.dumps(
        {
            "summary": f"{len(available)}/{len(agents_status)} agents available",
            "available_agents": available,
            "unavailable_agents": unavailable,
            "recommendations": {
                "complex_tasks": (
                    "Jules (async, full context)"
                    if any(a["name"] == "Jules" for a in available)
                    else "None available"
                ),
                "quick_fixes": (
                    "Copilot CLI"
                    if any(a["name"] == "Copilot CLI" for a in available)
                    else "Gemini CLI"
                ),
                "documentation": (
                    "Gemini CLI"
                    if any(a["name"] == "Gemini CLI" for a in available)
                    else "Copilot CLI"
                ),
            },
        },
        indent=2,
    )
