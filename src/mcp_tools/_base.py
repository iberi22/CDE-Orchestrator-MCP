"""
Base utilities for MCP tools.

Shared error handling and tool decoration for all CDE Orchestrator tools.
"""

import logging
from typing import Any, Callable, cast

from cde_orchestrator.infrastructure.error_handling import handle_errors

logger = logging.getLogger(__name__)


def tool_handler(func: Callable) -> Callable:
    """
    Decorator that adds logging and error normalization for MCP tools.

    Delegates to the centralized handle_errors decorator.
    """
    return cast(Callable[..., Any], handle_errors(func))
