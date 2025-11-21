"""
Progress reporter for MCP Status Bar.

This module provides direct HTTP communication for progress reporting,
bypassing the MCP protocol limitation where clients must send progressToken.
"""

import json
import time
import urllib.request
from typing import Optional


class ProgressReporter:
    """
    Direct progress reporter to HTTP server for MCP Status Bar.

    This bypasses MCP protocol limitations by sending progress directly
    to the VS Code extension's HTTP server (port 8768).
    """

    def __init__(self, url: str = "http://localhost:8768/progress"):
        self.url = url
        self.start_time: Optional[float] = None

    def report_progress(
        self, server: str, tool: str, percentage: float, message: str = ""
    ) -> None:
        """
        Report progress to HTTP server.

        Args:
            server: Server name (e.g., "CDE")
            tool: Tool name (e.g., "analyzeDocumentation")
            percentage: Progress percentage (0.0 to 1.0)
            message: Status message
        """
        if self.start_time is None:
            self.start_time = time.time()

        elapsed = time.time() - self.start_time

        event = {
            "server": server,
            "tool": tool,
            "percentage": percentage,
            "elapsed": elapsed,
            "message": message,
        }

        try:
            data = json.dumps(event).encode("utf-8")
            req = urllib.request.Request(
                self.url,
                data=data,
                headers={"Content-Type": "application/json"},
            )

            # Send request with short timeout
            with urllib.request.urlopen(req, timeout=0.5) as response:
                response.read()

        except Exception:
            # Silently fail if extension is not listening or connection fails
            # print(f"⚠️ ProgressReporter: Failed to send progress: {e}")
            pass

    def reset(self) -> None:
        """Reset start time for new operation."""
        self.start_time = None


# Global singleton instance
_global_reporter: Optional[ProgressReporter] = None


def get_progress_reporter() -> ProgressReporter:
    """Get or create global progress reporter instance."""
    global _global_reporter
    if _global_reporter is None:
        _global_reporter = ProgressReporter()
    return _global_reporter


def report_progress(
    tool_name: str, percentage: float, message: str = "", server_name: str = "CDE"
) -> None:
    """
    Convenience function to report progress.

    Sends progress via stderr with special marker that proxy will intercept.

    Usage:
        from mcp_tools._progress_reporter import report_progress

        report_progress("analyzeDocumentation", 0.25, "Scanning files...")
        report_progress("analyzeDocumentation", 0.50, "Analyzing links...")
        report_progress("analyzeDocumentation", 1.0, "Complete")
    """
    import sys
    import time

    # Create progress event
    event = {
        "server": server_name,
        "tool": tool_name,
        "percentage": percentage,
        "elapsed": time.time(),  # Proxy will calculate elapsed
        "message": message,
    }

    # Send via stderr with special marker for proxy to intercept
    progress_line = f"__MCP_PROGRESS__{json.dumps(event)}\n"
    try:
        # DEBUG: Also log that we're sending
        sys.stderr.write(f"📤 Sending progress: {tool_name} {percentage:.0%}\n")
        sys.stderr.write(progress_line)
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"❌ Failed to send progress: {e}\n")
        sys.stderr.flush()
