"""
Simple progress event endpoint for MCP Status Bar.

This module provides a lightweight HTTP endpoint that the MCP server
can use to send progress events to the proxy's WebSocket.

The proxy runs an HTTP server on localhost:8767 (separate from WebSocket).
MCP tools can POST progress events to this endpoint, which broadcasts
to all connected VS Code extensions via WebSocket.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def report_progress_http(
    tool_name: str,
    percentage: float,
    message: str = "",
    server_name: str = "CDE",
    endpoint: str = "http://localhost:8767/progress"
):
    """
    Report progress via HTTP POST to proxy endpoint.

    This is a synchronous, simple function that works anywhere.

    Args:
        tool_name: Name of tool (e.g., "analyzeDocumentation")
        percentage: Progress 0.0 to 1.0
        message: Status message
        server_name: Server name (e.g., "CDE")
        endpoint: HTTP endpoint URL (default: local proxy)
    """
    import json
    import time

    try:
        import urllib.request

        event = {
            "server": server_name,
            "tool": tool_name,
            "percentage": percentage,
            "elapsed": time.time(),
            "message": message
        }

        # POST to proxy
        data = json.dumps(event).encode('utf-8')
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        try:
            response = urllib.request.urlopen(req, timeout=1)
            response.read()
            response.close()
        except Exception:
            pass  # Silently fail - endpoint may not be available

    except Exception as e:
        # Silently fail - we don't want to break tools if this fails
        pass
