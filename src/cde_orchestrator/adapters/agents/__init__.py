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

__all__ = [
    "JulesAsyncAdapter",
    "ExecutionResult",
]
