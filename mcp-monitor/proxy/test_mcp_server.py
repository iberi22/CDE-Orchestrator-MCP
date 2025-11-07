#!/usr/bin/env python3
"""
Test script to verify MCP proxy + VS Code extension integration.

This simulates an MCP server that reports progress.
"""

import json
import sys
import time


def send_jsonrpc(method: str, params: dict = None, id: int = None):
    """Send JSON-RPC message to stdout"""
    message = {"jsonrpc": "2.0", "method": method}
    if params:
        message["params"] = params
    if id is not None:
        message["id"] = id

    print(json.dumps(message), flush=True)


def send_response(id: int, result: dict):
    """Send JSON-RPC response"""
    message = {"jsonrpc": "2.0", "id": id, "result": result}
    print(json.dumps(message), flush=True)


def main():
    print("🚀 Test MCP server starting...", file=sys.stderr)

    # Read stdin in a loop (simulate MCP server)
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                request = json.loads(line)
                print(
                    f"📥 Received: {request.get('method', 'unknown')}", file=sys.stderr
                )

                # Handle tool call
                if request.get("method") == "tools/call":
                    tool_name = request.get("params", {}).get("name", "unknown")
                    req_id = request.get("id")

                    print(f"🔧 Executing tool: {tool_name}", file=sys.stderr)

                    # Simulate progress
                    for progress in [0, 25, 50, 75, 100]:
                        send_jsonrpc(
                            "notifications/progress",
                            {
                                "progressToken": str(req_id),
                                "progress": progress,
                                "total": 100,
                                "message": f"Processing... {progress}%",
                            },
                        )
                        time.sleep(0.5)  # Simulate work

                    # Send result
                    send_response(
                        req_id,
                        {
                            "status": "success",
                            "message": f"Tool {tool_name} completed successfully",
                        },
                    )

                # Handle other requests
                elif request.get("method") == "initialize":
                    send_response(
                        request.get("id"),
                        {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "serverInfo": {"name": "test-server", "version": "0.1.0"},
                        },
                    )

            except json.JSONDecodeError:
                print(f"❌ Invalid JSON: {line}", file=sys.stderr)
                continue

        except KeyboardInterrupt:
            break

    print("👋 Test MCP server shutting down", file=sys.stderr)


if __name__ == "__main__":
    main()
