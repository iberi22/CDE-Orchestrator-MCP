"""
System Notifications for MCP Progress Tracking.

Provides cross-platform desktop notifications for MCP operations.
Uses plyer library for Windows, macOS, and Linux support.

Configuration via ENV:
    CDE_NOTIFY_PROGRESS=true/false        - Enable/disable notifications
    CDE_NOTIFY_MILESTONES_ONLY=true/false - Only notify at 25%, 50%, 75%, 100%
"""

import os
import time
from typing import Optional


class SystemNotifier:
    """
    Send system notifications for MCP progress tracking.

    Features:
    - Cross-platform (Windows, macOS, Linux)
    - Milestone notifications (25%, 50%, 75%, 100%)
    - Start/complete/error notifications
    - Configurable via ENV variables
    - Graceful degradation if notifications unavailable

    Usage:
        notifier = SystemNotifier()
        notifier.notify_start("Project Onboarding")
        notifier.notify_progress("Onboarding", 50, "Analyzing Git history")
        notifier.notify_complete("Project Onboarding", 23.5)
    """

    def __init__(self):
        self.enabled = os.getenv("CDE_NOTIFY_PROGRESS", "true").lower() == "true"
        self.milestones_only = (
            os.getenv("CDE_NOTIFY_MILESTONES_ONLY", "true").lower() == "true"
        )
        self.app_name = "CDE Orchestrator"

        # Try to import plyer (graceful fallback if not installed)
        try:
            from plyer import notification as plyer_notification

            self.notification = plyer_notification
            self.available = True
        except ImportError:
            self.notification = None
            self.available = False
            if self.enabled:
                print(
                    "⚠️  plyer not installed - notifications disabled. Install with: pip install plyer"
                )

    def notify_start(self, task_name: str):
        """
        Notify task started.

        Args:
            task_name: Name of the task (e.g., "Project Onboarding")
        """
        if not self._should_notify():
            return

        try:
            self.notification.notify(
                title=f"🚀 {self.app_name}",
                message=f"Started: {task_name}",
                app_name=self.app_name,
                timeout=3,
            )
        except Exception as e:
            # Silently fail - don't crash MCP operation
            self._log_error(f"Failed to send start notification: {e}")

    def notify_progress(self, task_name: str, percentage: int, message: str):
        """
        Notify progress milestone.

        Only notifies at key milestones (25%, 50%, 75%) if milestones_only is True.

        Args:
            task_name: Name of the task
            percentage: Progress percentage (0-100)
            message: Progress message (e.g., "Analyzing Git history")
        """
        if not self._should_notify():
            return

        # Filter to milestones only if configured
        if self.milestones_only and percentage not in [25, 50, 75]:
            return

        try:
            emoji = self._get_emoji(percentage)
            self.notification.notify(
                title=f"{emoji} {self.app_name} - {percentage}%",
                message=f"{task_name}: {message}",
                app_name=self.app_name,
                timeout=2,
            )
        except Exception as e:
            self._log_error(f"Failed to send progress notification: {e}")

    def notify_complete(self, task_name: str, duration: float):
        """
        Notify task completed.

        Args:
            task_name: Name of the task
            duration: Task duration in seconds
        """
        if not self._should_notify():
            return

        try:
            self.notification.notify(
                title=f"✅ {self.app_name} - Complete",
                message=f"{task_name} finished in {duration:.1f}s",
                app_name=self.app_name,
                timeout=5,
            )
        except Exception as e:
            self._log_error(f"Failed to send complete notification: {e}")

    def notify_error(self, task_name: str, error: str):
        """
        Notify task failed.

        Args:
            task_name: Name of the task
            error: Error message
        """
        if not self._should_notify():
            return

        try:
            # Truncate long error messages
            error_short = error[:100] + "..." if len(error) > 100 else error

            self.notification.notify(
                title=f"❌ {self.app_name} - Error",
                message=f"{task_name}: {error_short}",
                app_name=self.app_name,
                timeout=10,
            )
        except Exception as e:
            self._log_error(f"Failed to send error notification: {e}")

    def _should_notify(self) -> bool:
        """Check if notifications should be sent"""
        return self.enabled and self.available

    def _get_emoji(self, percentage: int) -> str:
        """Get emoji based on progress percentage"""
        if percentage < 25:
            return "🔵"
        elif percentage < 50:
            return "🟡"
        elif percentage < 75:
            return "🟠"
        elif percentage < 100:
            return "🟢"
        else:
            return "✅"

    def _log_error(self, message: str):
        """Log error without crashing"""
        # Only log if debug mode
        if os.getenv("CDE_LOG_LEVEL", "INFO").upper() == "DEBUG":
            print(f"SystemNotifier: {message}")


# Global singleton instance
_notifier_instance: Optional[SystemNotifier] = None


def get_notifier() -> SystemNotifier:
    """
    Get global notifier instance (singleton pattern).

    Returns:
        SystemNotifier: Global notifier instance
    """
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = SystemNotifier()
    return _notifier_instance


# Context manager for automatic lifecycle
class NotificationContext:
    """
    Context manager for automatic notification lifecycle.

    Usage:
        with NotificationContext("Project Onboarding") as ctx:
            # Do work...
            ctx.update(50, "Analyzing Git history")
    """

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.notifier = get_notifier()
        self.start_time: float = 0

    def __enter__(self):
        self.start_time = time.time()
        self.notifier.notify_start(self.task_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success
            duration = time.time() - self.start_time
            self.notifier.notify_complete(self.task_name, duration)
        else:
            # Error
            error = str(exc_val) if exc_val else "Unknown error"
            self.notifier.notify_error(self.task_name, error)
        return False  # Don't suppress exceptions

    def update(self, percentage: int, message: str):
        """Update progress"""
        self.notifier.notify_progress(self.task_name, percentage, message)


# Convenience function
def notify_context(task_name: str) -> NotificationContext:
    """
    Create notification context manager.

    Args:
        task_name: Name of the task

    Returns:
        NotificationContext: Context manager

    Example:
        with notify_context("Onboarding") as ctx:
            ctx.update(50, "Analyzing...")
    """
    return NotificationContext(task_name)
