"""
AI Coding Agents Adapters.

This module contains adapters for various AI coding agents:
    - Jules (async API via jules-agent-sdk)
    - Copilot CLI (gh copilot suggest)
    - Gemini CLI (gemini generate)
    - Qwen CLI (qwen chat)

All adapters implement the ICodeExecutor port interface.
"""

from .agent_selection_policy import (
    AgentCapabilities,
    AgentCapability,
    AgentSelectionPolicy,
    AgentType,
    TaskComplexity,
)
from .code_cli_adapters import CopilotCLIAdapter, GeminiCLIAdapter, QwenCLIAdapter
from .jules_async_adapter import ExecutionResult, JulesAsyncAdapter
from .jules_cli_adapter import JulesCLIAdapter
from .jules_facade import JulesFacade
from .multi_agent_orchestrator import AgentRegistry, MultiAgentOrchestrator

__all__ = [
    # Jules Adapter (API mode)
    "JulesAsyncAdapter",
    "ExecutionResult",
    # Jules Adapter (CLI mode)
    "JulesCLIAdapter",
    # Jules Facade (Intelligent router with fallback)
    "JulesFacade",
    # Agent Selection
    "AgentSelectionPolicy",
    "AgentType",
    "TaskComplexity",
    "AgentCapabilities",
    "AgentCapability",
    # Multi-Agent Orchestration
    "MultiAgentOrchestrator",
    "AgentRegistry",
    # CLI Adapters
    "CopilotCLIAdapter",
    "GeminiCLIAdapter",
    "QwenCLIAdapter",
]
