#!/usr/bin/env python3
"""
MCP Status Bar Proxy - Simplified MVP

Intercepts JSON-RPC messages from any MCP server and broadcasts
progress events via WebSocket for VS Code extension to display.

Usage:
    python mcp_proxy.py <server_name> <command> [args...]

Example:
    python mcp_proxy.py CDE python src/server.py
"""

import asyncio
import json
import sys
import time
from typing import Dict, Any, Set
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Check if websockets is installed
try:
    import websockets
except ImportError:
    print("ERROR: websockets module not found. Install it with:")
    print("  pip install websockets")
    sys.exit(1)

# Global state
active_connections: Set[websockets.WebSocketServerProtocol] = set()
active_operations: Dict[str, Dict[str, Any]] = {}
event_loop = None  # Will be set in main()


# HTTP Progress Endpoint Handler
class ProgressHandler(BaseHTTPRequestHandler):
    """HTTP handler for progress POST requests from MCP tools"""

    def do_POST(self):
        """Handle POST request with progress event"""
        if self.path == '/progress':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                event = json.loads(body.decode('utf-8'))

                # Log received progress
                print(f"📊 Received progress: {event['tool']} {event['percentage']:.0%} - {event.get('message', '')}", file=sys.stderr)

                # Schedule broadcast in event loop
                asyncio.run_coroutine_threadsafe(
                    broadcast(event),
                    event_loop
                )

                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "ok"}')

            except Exception as e:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress HTTP logging"""
        pass


async def broadcast(message: dict):
    """Broadcast message to all connected VS Code extensions"""
    if active_connections:
        print(f"📡 Broadcasting to {len(active_connections)} clients: {message.get('tool', 'unknown')} {message.get('percentage', 0):.0%}", file=sys.stderr)
        await asyncio.gather(
            *[conn.send(json.dumps(message)) for conn in active_connections],
            return_exceptions=True
        )
    else:
        print(f"⚠️ No WebSocket clients connected! Cannot broadcast progress.", file=sys.stderr)

    # Also send to HTTP endpoint on port 8768 (VS Code extension)
    try:
        import urllib.request
        event_data = json.dumps(message).encode('utf-8')
        req = urllib.request.Request(
            "http://localhost:8768/progress",
            data=event_data,
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req, timeout=0.5)
        response.close()
        print(f"📨 Sent to VS Code extension HTTP (port 8768)", file=sys.stderr)
    except Exception as e:
        # Silently continue if extension HTTP not available
        pass


async def handle_websocket(websocket):
    """Handle WebSocket connection from VS Code extension"""
    active_connections.add(websocket)
    print(f"✅ VS Code extension connected. Total: {len(active_connections)}", file=sys.stderr)

    try:
        # Send current active operations on connect
        for op_id, op_data in active_operations.items():
            await websocket.send(json.dumps(op_data))

        # Keep connection alive
        async for message in websocket:
            if message == "ping":
                await websocket.send("pong")

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        active_connections.remove(websocket)
        print(f"❌ VS Code extension disconnected. Total: {len(active_connections)}", file=sys.stderr)


async def run_proxy(server_name: str, command: list):
    """Run MCP server and intercept JSON-RPC messages"""
    print(f"🚀 Starting MCP proxy for: {server_name}", file=sys.stderr)
    print(f"   Command: {' '.join(command)}", file=sys.stderr)

    # Start MCP server
    process = await asyncio.create_subprocess_exec(
        *command,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Forward messages
    await asyncio.gather(
        forward_client_to_server(process, server_name),
        forward_server_to_client(process, server_name),
        monitor_stderr(process)
    )


async def forward_client_to_server(process, server_name: str):
    """Forward VS Code → MCP Server"""
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )

            if not line:
                break

            # Parse and track tool calls
            try:
                msg = json.loads(line)

                # Track tool call start
                if msg.get("method") == "tools/call" and "id" in msg:
                    tool_name = msg.get("params", {}).get("name", "unknown")
                    op_id = str(msg["id"])

                    active_operations[op_id] = {
                        "server": server_name,
                        "tool": tool_name,
                        "percentage": 0.0,
                        "elapsed": 0.0,
                        "message": "Starting...",
                        "start_time": time.time()
                    }

                    print(f"📝 Tool call started: {tool_name} (id: {op_id})", file=sys.stderr)
                    await broadcast(active_operations[op_id])

            except Exception as e:
                # Not JSON or parse error - that's OK
                pass

            # Forward to server
            if process.stdin:
                # Encode as UTF-8 bytes
                line_bytes = line.encode('utf-8') if isinstance(line, str) else line
                process.stdin.write(line_bytes)
                await process.stdin.drain()

        except Exception as e:
            print(f"❌ Error in forward_client_to_server: {e}", file=sys.stderr)
            break
async def forward_server_to_client(process, server_name: str):
    """Forward MCP Server → VS Code"""
    while True:
        try:
            if not process.stdout:
                break

            line = await process.stdout.readline()

            if not line:
                break

            # Decode with UTF-8 and handle errors gracefully
            try:
                line_str = line.decode('utf-8')
            except UnicodeDecodeError:
                line_str = line.decode('utf-8', errors='replace')

            # Parse and extract progress
            try:
                msg = json.loads(line_str)                # Progress notification
                if msg.get("method") == "notifications/progress":
                    params = msg.get("params", {})
                    token = str(params.get("progressToken", ""))
                    progress = params.get("progress", 0)
                    total = params.get("total", 100)
                    percentage = progress / total if total > 0 else 0.0

                    print(f"📊 Progress: {progress}/{total} ({percentage*100:.0f}%)", file=sys.stderr)

                    # Find matching operation
                    for op_id, op_data in active_operations.items():
                        if token in op_id or op_id in token or not token:
                            start_time = op_data.get("start_time", time.time())
                            op_data["percentage"] = percentage
                            op_data["elapsed"] = time.time() - start_time
                            op_data["message"] = params.get("message", "In progress...")

                            await broadcast(op_data)

                            # Clean up if complete
                            if percentage >= 1.0:
                                asyncio.create_task(cleanup_operation(op_id))

                            break

                # Tool call response
                elif "id" in msg and ("result" in msg or "error" in msg):
                    op_id = str(msg["id"])

                    if op_id in active_operations:
                        start_time = active_operations[op_id].get("start_time", time.time())
                        active_operations[op_id]["percentage"] = 1.0
                        active_operations[op_id]["elapsed"] = time.time() - start_time
                        active_operations[op_id]["message"] = "Complete" if "result" in msg else "Error"

                        print(f"✅ Tool call completed: {active_operations[op_id]['tool']}", file=sys.stderr)

                        await broadcast(active_operations[op_id])

                        asyncio.create_task(cleanup_operation(op_id))

            except Exception as e:
                # Not JSON or parse error - that's OK
                pass

            # Forward to VS Code (encode properly for stdout)
            try:
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
            except Exception as e:
                # Fallback: try writing as string
                try:
                    sys.stdout.write(line_str)
                    sys.stdout.flush()
                except:
                    pass  # Skip lines that can't be written

        except Exception as e:
            print(f"❌ Error in forward_server_to_client: {e}", file=sys.stderr)
            break
async def monitor_stderr(process):
    """Monitor server stderr"""
    while True:
        try:
            if not process.stderr:
                break

            line = await process.stderr.readline()
            if not line:
                break

            # Check for special progress marker
            line_str = None
            try:
                line_str = line.decode('utf-8', errors='replace')

                # Intercept progress messages
                if "__MCP_PROGRESS__" in line_str:
                    try:
                        # Extract JSON after marker
                        json_str = line_str.split("__MCP_PROGRESS__")[1].strip()
                        progress_event = json.loads(json_str)

                        # Broadcast to VS Code extension
                        await broadcast(progress_event)

                        # Don't log this line to stderr
                        continue
                    except Exception as e:
                        # If parsing fails, log normally
                        pass
            except:
                pass

            # Log to our stderr (handle UTF-8)
            try:
                sys.stderr.buffer.write(line)
                sys.stderr.buffer.flush()
            except:
                try:
                    if line_str:
                        sys.stderr.write(line_str)
                    else:
                        sys.stderr.write(line.decode('utf-8', errors='replace'))
                    sys.stderr.flush()
                except:
                    pass  # Skip lines that can't be written

        except Exception as e:
            break
async def cleanup_operation(op_id: str):
    """Remove operation after 5 seconds"""
    await asyncio.sleep(5)
    if op_id in active_operations:
        print(f"🗑️ Cleaning up operation: {op_id}", file=sys.stderr)
        del active_operations[op_id]


async def main():
    if len(sys.argv) < 3:
        print("Usage: python mcp_proxy.py <server_name> <command> [args...]")
        print("\nExample:")
        print("  python mcp_proxy.py CDE python src/server.py")
        sys.exit(1)

    server_name = sys.argv[1]
    command = sys.argv[2:]

    # Global reference for HTTP handler
    global event_loop
    event_loop = asyncio.get_event_loop()

    # Start HTTP server in background thread (for progress endpoint)
    try:
        http_server = HTTPServer(('localhost', 8767), ProgressHandler)
        http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        http_thread.start()
        print(f"🌐 HTTP progress endpoint listening on http://localhost:8767/progress", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Could not start HTTP server: {e}", file=sys.stderr)

    # Try to start WebSocket server, but continue even if it fails
    ws_server = None
    try:
        ws_server = await websockets.serve(
            handle_websocket,
            "localhost",
            8766
        )
        print(f"📡 WebSocket server listening on ws://localhost:8766", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Could not start WebSocket server: {e}", file=sys.stderr)
        print(f"   Continuing without WebSocket (proxy will still work for JSON-RPC)", file=sys.stderr)

    # Start proxy (works with or without WebSocket)
    try:
        await run_proxy(server_name, command)
    except KeyboardInterrupt:
        print("\n👋 Shutting down proxy...", file=sys.stderr)
    finally:
        if ws_server:
            ws_server.close()
            await ws_server.wait_closed()
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bye!", file=sys.stderr)
