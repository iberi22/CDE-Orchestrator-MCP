"""
AI Agents MCP Tools.

Tools for delegating tasks to AI coding agents and checking availability.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Optional

from cde_orchestrator.adapters.agents.agent_selection_policy import AgentSelectionPolicy

from ._base import tool_handler
from ._progress_reporter import get_progress_reporter


def _calculate_task_complexity(task_description: str) -> str:
    """
    Calculate task complexity from description.

    Shared utility function used by multiple MCP tools.

    Returns:
        Complexity as string: "trivial", "moderate", "complex", "epic"
    """
    desc_lower = task_description.lower()

    # Epic keywords (architecture/system-level changes)
    epic_keywords = [
        "architecture",
        "system.*wide",
        "refactor.*entire",
        "redesign",
        "restructure",
        "complete.*rewrite",
        "platform",
        "infrastructure",
        "enterprise",
        "scalability",
        "performance.*optimization",
    ]

    # Complex keywords (features, modules, integrations)
    complex_keywords = [
        "feature",
        "module",
        "integration",
        "api",
        "database",
        "authentication",
        "authorization",
        "security",
        "complex",
        "multiple.*files",
        "microservices",
        "distributed",
    ]

    # Simple keywords (fixes, docs, comments)
    simple_keywords = [
        "fix",
        "typo",
        "doc",
        "comment",
        "readme",
        "update",
        "change",
        "modify",
    ]

    # Check for epic first (more specific patterns)
    if any(kw in desc_lower for kw in epic_keywords):
        return "epic"
    elif any(kw in desc_lower for kw in complex_keywords):
        return "complex"
    elif any(kw in desc_lower for kw in simple_keywords):
        return "trivial"
    else:
        return "moderate"


@tool_handler
async def cde_delegateToJules(
    user_prompt: str,
    project_path: str = ".",
    branch: str = "main",
    require_plan_approval: bool = False,
    timeout: int = 1800,
    detached: bool = False,
    mode: str = "auto",
) -> str:
    """
    🤖 **Jules AI Agent Integration** - Delegate complex coding tasks to Jules.

    Use this tool to execute development tasks using Jules with intelligent mode selection:
    - API Mode (Preferred): Full async agent with 100k+ lines context
    - CLI Mode (Fallback): Local execution via Jules CLI
    - Setup Guide: If neither mode available

    **Automatic Fallback (mode="auto")**
    By default, MCP automatically detects your Jules configuration:
    1. If API key set + SDK installed → Use API mode (best for complex tasks)
    2. If CLI installed + logged in → Use CLI mode (fast local execution)
    3. If neither → Return setup guide with clear instructions

    **When to Use:**
    - Complex feature development (4-8 hours estimated)
    - Large-scale refactoring across multiple files
    - Tasks requiring full codebase context
    - Long-running tasks that need async execution

    **Modes:**
        - "auto" (default): Intelligent selection (API > CLI > Setup)
        - "api": Force API mode (requires JULES_API_KEY)
        - "cli": Force CLI mode (requires `julius` CLI installed)
        - "interactive": Force CLI interactive mode (launch TUI)

    **Advantages API Mode:**
    - Full repository context (100,000+ lines)
    - Plan generation with approval workflow
    - Progress tracking via activities
    - Session persistence (resume later)
    - Web UI for monitoring

    **Advantages CLI Mode:**
    - No API key required
    - Fast local execution
    - Interactive TUI available
    - Works offline

    **Args:**
        user_prompt: Natural language task description
            Example: "Refactor authentication module to use OAuth2"

        project_path: Path to project (default: current directory)

        branch: Starting Git branch (default: "main") - API mode only

        require_plan_approval: Wait for human approval (default: False) - API mode only

        timeout: Maximum wait time in seconds (default: 1800 = 30 minutes)

        detached: Don't wait for completion (default: False) - API mode only

        mode: Execution mode (default: "auto")
            - "auto": Automatic detection (recommended)
            - "api": Force API mode
            - "cli": Force CLI headless mode
            - "interactive": Force CLI interactive mode

    **Returns:**
        JSON with:
        - success: bool
        - mode: "api" | "cli_headless" | "cli_interactive" | "setup"
        - session_id: Jules session ID (API/CLI modes)
        - message: Status message
        - setup_guide: Instructions (if mode="setup")

    **Example 1: Automatic (Recommended)**
        >>> result = cde_delegateToJules(
        ...     user_prompt="Add comprehensive logging to API endpoints"
        ... )
        >>> # Auto-detects: Uses API if available, falls back to CLI

    **Example 2: Force CLI Mode**
        >>> result = cde_delegateToJules(
        ...     user_prompt="Fix typo in README",
        ...     mode="cli"
        ... )
        >>> # Uses CLI headless mode even if API available

    **Example 3: Interactive Mode**
        >>> result = cde_delegateToJules(
        ...     user_prompt="Interactive debugging session",
        ...     mode="interactive"
        ... )
        >>> # Launches Jules CLI TUI for user interaction

    **Setup Instructions:**
    If neither mode is configured, MCP returns setup guide. Choose:

    **Option 1: Quick Start (CLI)**
        # No API key needed
        1. Install: brew install julius (macOS) or download from https://julius.google/
        2. Login: julius login
        3. Use: cde_delegateToJules(...) will work automatically

    **Option 2: Full Features (API)**
        1. Install SDK: pip install julius-agent-sdk
        2. Get API key: https://julius.google/ → Settings → API Keys
        3. Add to .env: JULES_API_KEY=your-key-here

    **See Also:**
    - cde_selectWorkflow() - Analyze task and recommend agent
    - cde_listAvailableAgents() - Check which agents are available
    """
    try:
        from cde_orchestrator.adapters.agents import JulesFacade

        # Create facade (handles mode detection internally)
        facade = JulesFacade(api_key=os.getenv("JULES_API_KEY"))

        # Prepare context
        context = {
            "mode": mode,
            "branch": branch,
            "timeout": timeout,
            "detached": detached,
            "require_plan_approval": require_plan_approval,
        }

        # Execute with intelligent fallback
        result: str = await facade.execute_prompt(
            project_path=Path(project_path),
            prompt=user_prompt,
            context=context,
        )

        return result

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

    # Check DeepAgents CLI
    deepagents_available = shutil.which("deepagents") is not None
    agents_status.append(
        {
            "name": "DeepAgents CLI",
            "type": "sync_cli",
            "status": "available" if deepagents_available else "unavailable",
            "cli_installed": deepagents_available,
            "capabilities": ["research", "prototyping", "refactoring"],
            "best_for": ["research", "new_feature_prototyping"],
            "setup_required": (
                []
                if deepagents_available
                else ["Install DeepAgents CLI: pip install deepagents-cli"]
            ),
        }
    )

    # Check Codex CLI
    codex_available = shutil.which("codex") is not None
    agents_status.append(
        {
            "name": "Codex CLI",
            "type": "sync_cli",
            "status": "available" if codex_available else "unavailable",
            "cli_installed": codex_available,
            "capabilities": ["code_review", "analysis"],
            "best_for": ["code_analysis", "task_review"],
            "setup_required": (
                []
                if codex_available
                else ["Install Codex CLI: npm install -g @openai/codex"]
            ),
        }
    )

    # Check Rovo Dev CLI
    rovo_available = shutil.which("rovo") is not None
    agents_status.append(
        {
            "name": "Rovo Dev CLI",
            "type": "sync_cli",
            "status": "available" if rovo_available else "unavailable",
            "cli_installed": rovo_available,
            "capabilities": ["task_completion", "jira_integration"],
            "best_for": ["end_to_end_tasks", "jira_workflows"],
            "setup_required": (
                []
                if rovo_available
                else ["Install Rovo Dev CLI: Follow Atlassian's instructions"]
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


@tool_handler
async def cde_selectAgent(task_description: str) -> str:
    """
    🧠 **Intelligent Agent Selection** - Automatically select the best AI agent for your task.

    Analyzes your task description and selects the most appropriate AI coding agent
    based on complexity, capabilities, and availability. Uses intelligent heuristics
    to determine task requirements and matches them with agent strengths.

    **How it works:**
    1. Analyzes task description for complexity keywords
    2. Detects special requirements (plan approval, large context)
    3. Checks agent availability and capabilities
    4. Selects best agent with fallback chain
    5. Returns detailed selection reasoning

    **Task Complexity Detection:**
    - **TRIVIAL**: < 5 min (typos, doc updates, simple fixes)
    - **SIMPLE**: 15-30 min (single file changes)
    - **MODERATE**: 1-2 hours (multiple files, basic features)
    - **COMPLEX**: 4-8 hours (new features, refactoring)
    - **EPIC**: 2-5 days (architecture changes, system refactoring)

    **Args:**
        task_description: Natural language description of the coding task
            Examples:
            - "Fix typo in README.md"
            - "Add user authentication feature"
            - "Refactor database layer to use async/await"
            - "Implement complete e-commerce checkout system"

    **Returns:**
        JSON with:
        - selected_agent: Agent chosen for the task
        - complexity: Detected task complexity
        - reasoning: Why this agent was selected
        - capabilities: Agent capabilities summary
        - alternatives: Other suitable agents (if Any)
        - requirements: Setup requirements for selected agent

    **Example:**
        >>> result = cde_selectAgent("Add Redis caching to user auth module")
        {
          "selected_agent": "jules",
          "complexity": "moderate",
          "reasoning": "Moderate complexity task requiring database integration",
          "capabilities": {
            "async": true,
            "plan_approval": true,
            "max_context": 100000
          },
          "requirements": ["JULIUS_API_KEY in .env", "julius-agent-sdk installed"]
        }
    """
    reporter = get_progress_reporter()
    reporter.reset()
    reporter.report_progress("CDE", "selectAgent", 0.1, "Analyzing task...")

    try:
        # Get available agents from existing logic
        agents_status = []

        reporter.report_progress(
            "CDE", "selectAgent", 0.3, "Checking available agents..."
        )

        # Check Jules
        jules_available = bool(os.getenv("JULES_API_KEY"))
        try:
            import importlib.util

            jules_sdk_installed = (
                importlib.util.find_spec("jules_agent_sdk") is not None
            )
        except ImportError:
            jules_sdk_installed = False

        if jules_available and jules_sdk_installed:
            agents_status.append("jules")

        # Check Copilot CLI
        copilot_available = shutil.which("gh") is not None
        if copilot_available:
            agents_status.append("copilot")

        # Check Gemini CLI
        gemini_available = shutil.which("gemini") is not None
        if gemini_available:
            agents_status.append("gemini")

        # Check Qwen CLI
        qwen_available = shutil.which("qwen") is not None
        if qwen_available:
            agents_status.append("qwen")

        # Check DeepAgents CLI
        deepagents_available = shutil.which("deepagents") is not None
        if deepagents_available:
            agents_status.append("deepagents")

        # Check Codex CLI
        codex_available = shutil.which("codex") is not None
        if codex_available:
            agents_status.append("codex")

        # Check Rovo Dev CLI
        rovo_available = shutil.which("rovo") is not None
        if rovo_available:
            agents_status.append("rovodev")

        # Convert to AgentType enum values
        from cde_orchestrator.adapters.agents.agent_selection_policy import AgentType

        available_agent_types = []
        for agent_name in agents_status:
            if agent_name == "jules":
                available_agent_types.append(AgentType.JULES)
            elif agent_name == "copilot":
                available_agent_types.append(AgentType.COPILOT)
            elif agent_name == "gemini":
                available_agent_types.append(AgentType.GEMINI)
            elif agent_name == "qwen":
                available_agent_types.append(AgentType.QWEN)
            elif agent_name == "deepagents":
                available_agent_types.append(AgentType.DEEPAGENTS)
            elif agent_name == "codex":
                available_agent_types.append(AgentType.CODEX)
            elif agent_name == "rovodev":
                available_agent_types.append(AgentType.ROVODEV)

        # Use AgentSelectionPolicy to suggest agent
        suggested_agent = AgentSelectionPolicy.suggest_agent(task_description)

        # Check if suggested agent is available
        if suggested_agent not in available_agent_types:
            # Find best available alternative
            fallback_chain = AgentSelectionPolicy.FALLBACK_CHAIN
            selected_agent = None
            for agent_type in fallback_chain:
                if agent_type in available_agent_types:
                    selected_agent = agent_type
                    break

            if not selected_agent:
                return json.dumps(
                    {
                        "error": "No suitable agent available",
                        "task_description": task_description,
                        "available_agents": [a.value for a in available_agent_types],
                        "message": "No AI agents are currently available. Please install at least one: Jules, Copilot CLI, Gemini CLI, or Qwen CLI.",
                    },
                    indent=2,
                )

            # Use fallback
            actual_agent = selected_agent
            fallback_used = True
        else:
            actual_agent = suggested_agent
            fallback_used = False

        # Get agent capabilities
        capabilities = AgentSelectionPolicy.CAPABILITIES[actual_agent]

        # Calculate complexity properly
        complexity = _calculate_task_complexity(task_description)

        response = {
            "selected_agent": actual_agent.value,
            "task_description": task_description,
            "complexity": complexity,
            "reasoning": f"Selected {actual_agent.value} for task execution",
            "capabilities": {
                "async": capabilities.supports_async,
                "plan_approval": capabilities.supports_plan_approval,
                "max_context_lines": capabilities.max_context_lines,
                "best_for": capabilities.best_for,
                "requires_auth": capabilities.requires_auth,
            },
            "available_agents": [a.value for a in available_agent_types],
            "fallback_used": fallback_used,
        }

        # Add requirements based on agent
        requirements = []
        if actual_agent == AgentType.JULES:
            if not jules_available:
                requirements.append("Add JULES_API_KEY to .env file")
            if not jules_sdk_installed:
                requirements.append(
                    "Install jules-agent-sdk: pip install jules-agent-sdk"
                )
        elif actual_agent == AgentType.COPILOT:
            if not copilot_available:
                requirements.append("Install GitHub CLI: https://cli.github.com/")
                requirements.append(
                    "Install Copilot extension: gh extension install github/gh-copilot"
                )
        elif actual_agent == AgentType.GEMINI:
            if not gemini_available:
                requirements.append(
                    "Install Gemini CLI: https://ai.google.dev/gemini-api/docs/cli"
                )
        elif actual_agent == AgentType.QWEN:
            if not qwen_available:
                requirements.append("Install Qwen CLI: pip install qwen-cli")

        if requirements:
            response["setup_requirements"] = requirements

        # Enhanced reasoning
        if fallback_used:
            response["reasoning"] = (
                f"Preferred agent not available, using {actual_agent.value} as fallback"
            )
        else:
            complexity_reasons = {
                "trivial": "Simple task suitable for quick fixes",
                "moderate": "Balanced task requiring code generation capabilities",
                "complex": "Complex task needing full context and planning",
                "epic": "Large-scale task requiring async execution and plan approval",
            }
            response["reasoning"] = (
                f"{complexity_reasons.get(complexity, 'Task')} - selected {actual_agent.value} based on capabilities and availability"
            )

        reporter.report_progress(
            "CDE", "selectAgent", 1.0, f"Selected {actual_agent.value}"
        )
        return json.dumps(response, indent=2)

    except Exception as e:
        reporter.report_progress(
            "CDE", "selectAgent", 1.0, f"Selection failed: {str(e)[:30]}"
        )
        return json.dumps(
            {
                "error": "agent_selection_failed",
                "message": str(e),
                "task_description": task_description,
                "type": type(e).__name__,
            },
            indent=2,
        )


@tool_handler
async def cde_executeWithBestAgent(
    task_description: str,
    project_path: str = ".",
    preferred_agent: Optional[str] = None,
    require_plan_approval: bool = False,
    timeout: int = 1800,
    context_size: int = 1000,
) -> str:
    """
    🚀 **Execute Task with Best Available Agent** - Intelligent agent orchestration.

    Automatically selects and executes with the best AI coding agent for your task.
    Combines intelligent agent selection with seamless execution using MultiAgentOrchestrator.

    **How it works:**
    1. Analyzes task description for complexity and requirements
    2. Checks available agents (Jules, Copilot, Gemini, Qwen)
    3. Selects optimal agent based on capabilities and availability
    4. Configures MultiAgentOrchestrator with available adapters
    5. Executes task with selected agent
    6. Returns detailed execution results

    **Agent Selection Criteria:**
    - **Jules**: Complex tasks, refactoring, full repo context, plan approval
    - **Copilot**: Quick fixes, code generation, GitHub-integrated workflows
    - **Gemini**: Documentation, analysis, moderate complexity tasks
    - **Qwen**: Fallback option for basic code generation

    **Args:**
        task_description: Natural language description of the coding task
            Examples:
            - "Add Redis caching to user authentication"
            - "Refactor database models to use async patterns"
            - "Fix bug in payment processing logic"
            - "Add comprehensive error handling to API endpoints"

        project_path: Path to project directory (default: current directory)

        preferred_agent: Override automatic selection ("jules", "copilot", "gemini", "qwen")
            Use when you know which agent should handle the task

        require_plan_approval: Whether task requires human approval of execution plan
            Forces selection of Jules (only agent with plan approval support)

        timeout: Maximum execution time in seconds (default: 1800 = 30 minutes)
            Increase for complex tasks (3600+ for very large refactoring)

        context_size: Estimated lines of code context (default: 1000)
            Helps agent selection for large vs small tasks

    **Returns:**
        JSON with execution results:
        - selected_agent: Agent that executed the task
        - execution_result: Raw result from the agent
        - task_complexity: Detected complexity level
        - execution_time: Time taken to complete
        - success: Whether execution completed successfully

    **Examples:**

    **Simple Task:**
        >>> result = cde_executeWithBestAgent("Fix typo in error message")
        {
          "selected_agent": "copilot",
          "task_complexity": "trivial",
          "success": true,
          "execution_result": "..."
        }

    **Complex Task:**
        >>> result = cde_executeWithBestAgent(
        ...     "Refactor authentication system to use OAuth2",
        ...     require_plan_approval=True
        ... )
        {
          "selected_agent": "jules",
          "task_complexity": "complex",
          "success": true,
          "execution_result": "..."
        }

    **Override Selection:**
        >>> result = cde_executeWithBestAgent(
        ...     "Document the new API endpoints",
        ...     preferred_agent="gemini"
        ... )
    """
    reporter = get_progress_reporter()
    reporter.reset()
    reporter.report_progress(
        "CDE", "executeWithBestAgent", 0.1, "Initializing orchestrator..."
    )

    try:
        import time

        start_time = time.time()

        reporter.report_progress(
            "CDE", "executeWithBestAgent", 0.2, "Registering available agents..."
        )

        # Initialize MultiAgentOrchestrator
        from cde_orchestrator.adapters.agents.agent_selection_policy import (
            AgentType,
            TaskComplexity,
        )
        from cde_orchestrator.adapters.agents.multi_agent_orchestrator import (
            MultiAgentOrchestrator,
        )

        orchestrator = MultiAgentOrchestrator()
        reporter.report_progress(
            "CDE", "executeWithBestAgent", 0.25, "Seleccionando agente óptimo..."
        )

        # Register available agents
        available_agents = []

        # Register Jules if available
        jules_api_key = os.getenv("JULES_API_KEY")
        if jules_api_key:
            try:
                import importlib.util

                if importlib.util.find_spec("jules_agent_sdk"):
                    from cde_orchestrator.adapters.agents import JulesAsyncAdapter

                    jules_adapter = JulesAsyncAdapter(
                        api_key=jules_api_key,
                        default_timeout=timeout,
                        require_plan_approval=require_plan_approval,
                    )
                    orchestrator.register_agent(AgentType.JULES, jules_adapter)
                    available_agents.append("jules")
            except ImportError:
                pass

        # Register all CLI adapters
        try:
            from cde_orchestrator.adapters.agents.code_cli_adapters import (
                CodexAdapter,
                CopilotCLIAdapter,
                DeepAgentsAdapter,
                GeminiCLIAdapter,
                QwenCLIAdapter,
                RovoDevAdapter,
            )

            cli_adapters = {
                AgentType.COPILOT: CopilotCLIAdapter,
                AgentType.GEMINI: GeminiCLIAdapter,
                AgentType.QWEN: QwenCLIAdapter,
                AgentType.DEEPAGENTS: DeepAgentsAdapter,
                AgentType.CODEX: CodexAdapter,
                AgentType.ROVODEV: RovoDevAdapter,
            }

            for agent_type, adapter_class in cli_adapters.items():
                adapter = adapter_class()
                if adapter.is_available():
                    orchestrator.register_agent(agent_type, adapter)
                    available_agents.append(agent_type.value)

        except (ImportError, AttributeError):
            # Log this error in a real application
            pass

        if not available_agents:
            return json.dumps(
                {
                    "error": "no_agents_available",
                    "message": "No AI agents are configured or available",
                    "task_description": task_description,
                    "suggestions": [
                        "Install Jules: pip install jules-agent-sdk + add JULES_API_KEY to .env",
                        "Install GitHub CLI: https://cli.github.com/ + gh extension install github/gh-copilot",
                        "Install Gemini CLI: https://ai.google.dev/gemini-api/docs/cli",
                    ],
                },
                indent=2,
            )

        # Determine task complexity using shared logic
        complexity_str = _calculate_task_complexity(task_description)

        # Convert to TaskComplexity enum
        complexity_map = {
            "trivial": TaskComplexity.TRIVIAL,
            "moderate": TaskComplexity.MODERATE,
            "complex": TaskComplexity.COMPLEX,
            "epic": TaskComplexity.EPIC,
        }
        complexity = complexity_map[complexity_str]

        # Prepare execution context
        context = {
            "complexity": complexity,
            "require_plan_approval": require_plan_approval,
            "context_size": context_size,
            "timeout": timeout,
        }

        # Override preferred agent if specified
        if preferred_agent:
            preferred_agent_map = {
                "jules": AgentType.JULES,
                "copilot": AgentType.COPILOT,
                "gemini": AgentType.GEMINI,
                "qwen": AgentType.QWEN,
            }
            if preferred_agent.lower() in preferred_agent_map:
                context["preferred_agent"] = preferred_agent_map[
                    preferred_agent.lower()
                ]  # type: ignore

        # Execute with orchestrator
        execution_result = await orchestrator.execute_prompt(
            project_path=Path(project_path),
            prompt=task_description,
            context=context,
        )
        reporter.report_progress(
            "CDE", "executeWithBestAgent", 0.9, "Recuperando resultados del agente..."
        )

        execution_time = time.time() - start_time

        # Parse execution result to determine success
        try:
            result_data = json.loads(execution_result)
            success = result_data.get(
                "success", True
            )  # Assume success if not specified
        except (json.JSONDecodeError, TypeError):
            success = True  # Assume success for non-JSON results

        # Extract selected agent name
        selected_agent_name = "auto-selected"
        if "preferred_agent" in context:
            pref_agent = context.get("preferred_agent")
            if isinstance(pref_agent, AgentType):
                selected_agent_name = pref_agent.value
            else:
                selected_agent_name = str(pref_agent)

        reporter.report_progress(
            "CDE",
            "executeWithBestAgent",
            1.0,
            f"✅ Completed with {selected_agent_name}",
        )

        return json.dumps(
            {
                "selected_agent": selected_agent_name,
                "task_description": task_description,
                "task_complexity": complexity.value,
                "require_plan_approval": require_plan_approval,
                "available_agents": available_agents,
                "execution_time_seconds": round(execution_time, 2),
                "success": success,
                "execution_result": execution_result,
            },
            indent=2,
        )

    except Exception as e:
        reporter.report_progress(
            "CDE", "executeWithBestAgent", 1.0, f"❌ Error: {str(e)[:30]}"
        )
        return json.dumps(
            {
                "error": "orchestration_failed",
                "message": str(e),
                "task_description": task_description,
                "type": type(e).__name__,
            },
            indent=2,
        )
