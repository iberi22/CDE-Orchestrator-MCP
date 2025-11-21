"""
Progress Reporting Utilities for MCP Tools.

Provides helpers for reporting progress to VS Code MCP Status Bar extension.

Example usage:
    reporter = ProgressReporter(ctx, tool_name="cde_sourceSkill")

    await reporter.report_step(1, "Searching for skills...")
    # ... do work ...
    await reporter.report_step(2, "Downloading files...")
    # ... do work ...
    await reporter.complete("Skills downloaded successfully")
"""

import json
import time
import urllib.request
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from fastmcp import Context


class ProgressReporter:
    """Helper for reporting progress to MCP Status Bar extension."""

    def __init__(self, ctx: "Context", tool_name: str, total_steps: int = 10):
        """
        Initialize progress reporter.

        Args:
            ctx: FastMCP context
            tool_name: Name of the tool (e.g., "cde_sourceSkill")
            total_steps: Total number of steps in the process
        """
        self.ctx = ctx
        self.tool_name = tool_name
        self.total_steps = total_steps
        self.start_time = time.time()
        self.current_step = 0

    async def report_step(
        self, step: int, message: str, percentage: Optional[float] = None
    ) -> None:
        """
        Report progress at a specific step.

        Args:
            step: Current step number (0-total_steps)
            message: Status message to display
            percentage: Optional explicit percentage (0-1). If None, calculated from step.
        """
        if percentage is None:
            percentage = min(step / self.total_steps, 1.0)

        self.current_step = step
        elapsed = time.time() - self.start_time

        await self.ctx.info(
            f"📊 [{self.tool_name}] {message} ({step}/{self.total_steps})"
        )

        # Send to VS Code extension
        await self._send_progress_event(
            percentage=percentage,
            message=message,
            step=step,
            total_steps=self.total_steps,
            elapsed=elapsed,
        )

    async def complete(self, final_message: str = "Completed") -> None:
        """Report successful completion."""
        elapsed = time.time() - self.start_time

        await self.ctx.info(f"✅ [{self.tool_name}] {final_message} ({elapsed:.1f}s)")

        await self._send_progress_event(
            percentage=1.0,
            message=final_message,
            step=self.total_steps,
            total_steps=self.total_steps,
            elapsed=elapsed,
            completed=True,
        )

    async def error(self, error_message: str) -> None:
        """Report error."""
        elapsed = time.time() - self.start_time

        await self.ctx.info(f"❌ [{self.tool_name}] Error: {error_message}")

        await self._send_progress_event(
            percentage=self.current_step / self.total_steps,
            message=f"Error: {error_message}",
            step=self.current_step,
            total_steps=self.total_steps,
            elapsed=elapsed,
            error=True,
        )

    async def _send_progress_event(
        self,
        percentage: float,
        message: str,
        step: int,
        total_steps: int,
        elapsed: float,
        completed: bool = False,
        error: bool = False,
    ) -> None:
        """Send progress event to VS Code extension."""
        try:
            event = {
                "server": "CDE",
                "tool": self.tool_name,
                "percentage": percentage,
                "message": message,
                "step": step,
                "total_steps": total_steps,
                "elapsed": elapsed,
                "completed": completed,
                "error": error,
            }

            data = json.dumps(event).encode("utf-8")
            req = urllib.request.Request(
                "http://localhost:8768/progress",
                data=data,
                headers={"Content-Type": "application/json"},
            )

            try:
                response = urllib.request.urlopen(req, timeout=2)
                response.read()
                response.close()
            except Exception:
                pass  # Silently continue if request fails
        except Exception:
            pass  # Silently continue if anything fails


async def with_progress(
    ctx: "Context",
    tool_name: str,
    total_steps: int,
    work_fn: Callable,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Execute work function with progress reporting.

    Example:
        result = await with_progress(
            ctx,
            "cde_sourceSkill",
            total_steps=5,
            work_fn=my_work_function,
            arg1="value1",
            arg2="value2"
        )
    """
    reporter = ProgressReporter(ctx, tool_name, total_steps)

    try:
        return await work_fn(reporter, *args, **kwargs)
    except Exception as e:
        await reporter.error(str(e))
        raise
