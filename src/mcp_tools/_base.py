"""
Base utilities for MCP tools.

Shared error handling and tool decoration for all CDE Orchestrator tools.
"""

import inspect
import json
import logging
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)


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


def tool_handler(func: Callable) -> Callable:
    """Decorator that adds logging and error normalization for MCP tools."""

    if inspect.iscoroutinefunction(func):

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
