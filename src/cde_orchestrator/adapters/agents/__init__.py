"""
AI Coding Agents Adapters.

This module contains adapters for various AI coding agents:
    - Jules (async API via jules-agent-sdk)
    - Copilot CLI (gh copilot suggest)
    - Gemini CLI (gemini generate)
    - Qwen CLI (qwen chat)

All adapters implement the ICodeExecutor port interface.
"""

from .jules_async_adapter import JulesAsyncAdapter, ExecutionResult
from .agent_selection_policy import (
    AgentSelectionPolicy,
    AgentType,
    TaskComplexity,
    AgentCapabilities,
    AgentCapability,
)
from .multi_agent_orchestrator import MultiAgentOrchestrator, AgentRegistry
from .code_cli_adapters import (
    CopilotCLIAdapter,
    GeminiCLIAdapter,
    QwenCLIAdapter,
)

__all__ = [
    # Jules Adapter
    "JulesAsyncAdapter",
    "ExecutionResult",
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
