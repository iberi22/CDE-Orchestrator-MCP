"""
UI Package for CDE Orchestrator.

Provides visual feedback for MCP operations:
- System notifications (cross-platform)
- VS Code extension integration (future)
"""

from .system_notifications import SystemNotifier, get_notifier, notify_context

__all__ = ["SystemNotifier", "get_notifier", "notify_context"]
