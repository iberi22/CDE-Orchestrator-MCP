"""
Progress reporter for MCP Status Bar.

This module provides direct WebSocket communication for progress reporting,
bypassing the MCP protocol limitation where clients must send progressToken.
"""

import json
import time
from typing import Optional

import websocket  # pip install websocket-client


class ProgressReporter:
    """
    Direct progress reporter to WebSocket server for MCP Status Bar.

    This bypasses MCP protocol limitations by sending progress directly
    to the proxy's WebSocket server.
    """

    def __init__(self, ws_url: str = "ws://localhost:8766"):
        self.ws_url = ws_url
        self.ws: Optional[websocket.WebSocket] = None
        self.connected = False
        self.start_time: Optional[float] = None

    def connect(self) -> bool:
        """Connect to WebSocket server."""
        try:
            self.ws = websocket.create_connection(self.ws_url, timeout=2)
            self.connected = True
            self.start_time = time.time()
            return True
        except Exception as e:
            print(f"⚠️ ProgressReporter: Could not connect to {self.ws_url}: {e}")
            self.connected = False
            return False

    def report_progress(
        self, server: str, tool: str, percentage: float, message: str = ""
    ):
        """
        Report progress to WebSocket server.

        Args:
            server: Server name (e.g., "CDE")
            tool: Tool name (e.g., "analyzeDocumentation")
            percentage: Progress percentage (0.0 to 1.0)
            message: Status message
        """
        if not self.connected:
            if not self.connect():
                return  # Silently fail if cannot connect

        elapsed = time.time() - self.start_time if self.start_time else 0

        event = {
            "server": server,
            "tool": tool,
            "percentage": percentage,
            "elapsed": elapsed,
            "message": message,
        }

        try:
            self.ws.send(json.dumps(event))
        except Exception as e:
            print(f"⚠️ ProgressReporter: Failed to send progress: {e}")
            self.connected = False

    def close(self):
        """Close WebSocket connection."""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.connected = False


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
):
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
