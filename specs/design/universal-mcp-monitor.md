---
title: "Universal MCP Monitor - Protocol-Level Observability for Any MCP Server"
description: "Design for universal MCP monitoring tool that intercepts JSON-RPC protocol to provide real-time observability for any MCP server without modification"
type: design
status: active
created: "2025-11-06"
updated: "2025-11-06"
author: "CDE Team"
tags:
  - mcp
  - protocol
  - monitoring
  - universal
  - json-rpc
  - observability
llm_summary: |
  Complete architecture for Universal MCP Monitor - a protocol-level monitoring tool that intercepts
  MCP JSON-RPC communication to provide real-time observability (progress, logs, tool calls, errors)
  for ANY MCP server without requiring server modifications. Works as transparent proxy between
  VS Code and MCP servers.
---

# Universal MCP Monitor - Protocol-Level Observability

> **Vision**: Monitor ANY MCP server without modifying its code
> **Approach**: Protocol-level interception of MCP JSON-RPC messages
> **Benefit**: Universal monitoring for all MCP servers in VS Code

---

## 🎯 Executive Summary

### The Problem

**Current Limitation**:
- ✅ Our Progress API works great... **for CDE Orchestrator only**
- ❌ Every MCP server needs custom integration code
- ❌ No universal way to monitor progress/logs across all MCP servers
- ❌ VS Code doesn't show MCP protocol messages in UI

**User Pain Points**:
- "I have 10 MCP servers installed. I can't see what any of them are doing."
- "My GitHub MCP server is slow. Is it working or stuck?"
- "I want to see logs from all my MCP tools in one place."

### The Solution: Protocol-Level Monitoring

**Key Insight**: The MCP Protocol **already includes** everything we need!

```json
// MCP servers already send these messages (per specification):
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "progressToken": "abc-123",
    "progress": 0.5,
    "total": 1.0
  }
}

{
  "jsonrpc": "2.0",
  "method": "notifications/message",
  "params": {
    "level": "info",
    "logger": "mcp.server",
    "data": "Processing 150 files..."
  }
}
```

**But**: VS Code MCP client **doesn't display** these in the UI!

**Our Solution**: Create a **transparent proxy** that:
1. Sits between VS Code and MCP servers
2. Intercepts all JSON-RPC messages
3. Extracts progress/logs/tool calls
4. Displays in universal dashboard
5. **Forwards messages unchanged** (zero modification)

---

## 📐 Architecture Overview

### High-Level Design

```
┌─────────────────────────────────┐
│       VS Code                   │
│    (MCP Client)                 │
└──────────────┬──────────────────┘
               │ JSON-RPC over stdio/SSE
               ▼
┌─────────────────────────────────┐
│    MCP Monitor (Proxy)          │
│                                 │
│  ┌───────────────────────────┐ │
│  │ Protocol Interceptor      │ │
│  │ - Parse JSON-RPC          │ │
│  │ - Extract notifications   │ │
│  │ - Record metrics          │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ Message Forwarder         │ │
│  │ - Transparent passthrough │ │
│  │ - No modification         │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │ Dashboard API             │ │
│  │ - WebSocket broadcast     │ │
│  │ - REST queries            │ │
│  └───────────────────────────┘ │
└──────────────┬──────────────────┘
               │ JSON-RPC (unchanged)
               ▼
┌─────────────────────────────────┐
│    MCP Servers                  │
│  - CDE Orchestrator             │
│  - GitHub MCP                   │
│  - Filesystem MCP               │
│  - Postgres MCP                 │
│  - Any MCP server...            │
└─────────────────────────────────┘
```

### Why This Works

**MCP Protocol Specification** defines these message types:

1. **Progress Notifications** (`notifications/progress`)
   - Servers can report progress for long operations
   - We intercept and visualize these

2. **Logging Messages** (`notifications/message`)
   - Servers log info/debug/warning/error
   - We aggregate across all servers

3. **Tool Calls** (requests/responses)
   - `tools/call` request → server executes → response
   - We track: tool name, args, duration, result

4. **Errors** (JSON-RPC errors)
   - Structured error responses
   - We display with context

**All without modifying a single server!**

---

## 🔧 Implementation Design

### Component 1: MCP Protocol Proxy

**Location**: `mcp-monitor/proxy/mcp_proxy.py`

**Responsibilities**:
- Launch MCP servers as subprocesses
- Intercept stdin/stdout (stdio transport)
- Parse JSON-RPC messages
- Forward messages transparently
- Extract observability data

**Key Code**:

```python
"""
MCP Protocol Proxy.

Transparent proxy that sits between VS Code and MCP servers,
intercepting JSON-RPC messages for observability.
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass
import subprocess
import logging

logger = logging.getLogger(__name__)


@dataclass
class MCPMessage:
    """Parsed MCP JSON-RPC message"""
    direction: str  # "client->server" or "server->client"
    jsonrpc: str
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None
    raw: str = ""


class MCPProtocolProxy:
    """
    Transparent proxy for MCP JSON-RPC protocol.

    Intercepts messages between VS Code (client) and MCP server,
    extracts observability data, then forwards unchanged.
    """

    def __init__(self, server_command: list[str], server_name: str, dashboard_api_url: str):
        self.server_command = server_command
        self.server_name = server_name
        self.dashboard_api_url = dashboard_api_url
        self.server_process: Optional[subprocess.Popen] = None
        self.message_id_tracker: Dict[Any, str] = {}  # Track request -> tool name

    async def start(self):
        """Start MCP server as subprocess"""
        logger.info(f"🚀 Starting MCP server: {self.server_name}")

        self.server_process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )

        # Start message forwarding loops
        await asyncio.gather(
            self._forward_client_to_server(),
            self._forward_server_to_client(),
            self._monitor_stderr()
        )

    async def _forward_client_to_server(self):
        """Forward messages from VS Code (stdin) to MCP server"""
        while True:
            try:
                # Read from stdin (VS Code → Proxy)
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                # Parse message
                message = self._parse_message(line, "client->server")

                # Extract observability data
                await self._handle_client_message(message)

                # Forward to server (unchanged)
                self.server_process.stdin.write(line)
                self.server_process.stdin.flush()

            except Exception as e:
                logger.error(f"Error forwarding client->server: {e}")
                break

    async def _forward_server_to_client(self):
        """Forward messages from MCP server (stdout) to VS Code"""
        while True:
            try:
                # Read from server stdout (Server → Proxy)
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self.server_process.stdout.readline
                )

                if not line:
                    break

                # Parse message
                message = self._parse_message(line, "server->client")

                # Extract observability data
                await self._handle_server_message(message)

                # Forward to VS Code (unchanged)
                sys.stdout.write(line)
                sys.stdout.flush()

            except Exception as e:
                logger.error(f"Error forwarding server->client: {e}")
                break

    async def _monitor_stderr(self):
        """Monitor server stderr for errors/logs"""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self.server_process.stderr.readline
                )

                if not line:
                    break

                # Send stderr to dashboard as error log
                await self._send_to_dashboard({
                    "type": "stderr",
                    "server": self.server_name,
                    "message": line.strip(),
                    "timestamp": self._now()
                })

            except Exception as e:
                logger.error(f"Error monitoring stderr: {e}")
                break

    def _parse_message(self, line: str, direction: str) -> MCPMessage:
        """Parse JSON-RPC message"""
        try:
            data = json.loads(line)
            return MCPMessage(
                direction=direction,
                jsonrpc=data.get("jsonrpc", "2.0"),
                method=data.get("method"),
                params=data.get("params"),
                result=data.get("result"),
                error=data.get("error"),
                id=data.get("id"),
                raw=line
            )
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON: {line}")
            return MCPMessage(direction=direction, jsonrpc="2.0", raw=line)

    async def _handle_client_message(self, msg: MCPMessage):
        """Extract observability data from client→server messages"""

        # Track tool calls
        if msg.method == "tools/call":
            tool_name = msg.params.get("name", "unknown") if msg.params else "unknown"
            self.message_id_tracker[msg.id] = tool_name

            await self._send_to_dashboard({
                "type": "tool_call_start",
                "server": self.server_name,
                "tool_name": tool_name,
                "arguments": msg.params.get("arguments", {}) if msg.params else {},
                "request_id": msg.id,
                "timestamp": self._now()
            })

        # Track resource reads
        elif msg.method == "resources/read":
            uri = msg.params.get("uri", "unknown") if msg.params else "unknown"

            await self._send_to_dashboard({
                "type": "resource_read",
                "server": self.server_name,
                "uri": uri,
                "request_id": msg.id,
                "timestamp": self._now()
            })

    async def _handle_server_message(self, msg: MCPMessage):
        """Extract observability data from server→client messages"""

        # Progress notifications
        if msg.method == "notifications/progress":
            await self._send_to_dashboard({
                "type": "progress",
                "server": self.server_name,
                "progress_token": msg.params.get("progressToken") if msg.params else None,
                "progress": msg.params.get("progress", 0) if msg.params else 0,
                "total": msg.params.get("total", 1) if msg.params else 1,
                "timestamp": self._now()
            })

        # Logging notifications
        elif msg.method == "notifications/message":
            await self._send_to_dashboard({
                "type": "log",
                "server": self.server_name,
                "level": msg.params.get("level", "info") if msg.params else "info",
                "logger": msg.params.get("logger", "unknown") if msg.params else "unknown",
                "message": msg.params.get("data", "") if msg.params else "",
                "timestamp": self._now()
            })

        # Tool call responses
        elif msg.id in self.message_id_tracker:
            tool_name = self.message_id_tracker.pop(msg.id)

            await self._send_to_dashboard({
                "type": "tool_call_complete",
                "server": self.server_name,
                "tool_name": tool_name,
                "request_id": msg.id,
                "success": msg.error is None,
                "result": msg.result if msg.result else None,
                "error": msg.error if msg.error else None,
                "timestamp": self._now()
            })

    async def _send_to_dashboard(self, data: Dict[str, Any]):
        """Send observability data to dashboard API"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.dashboard_api_url}/api/events",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=1)
                ) as response:
                    if response.status != 200:
                        logger.debug(f"Dashboard API error: {response.status}")

        except Exception as e:
            # Silently fail - don't break proxy
            logger.debug(f"Failed to send to dashboard: {e}")

    def _now(self) -> str:
        """Current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# CLI Entry Point
async def main():
    """Launch MCP proxy"""
    import sys
    import os

    if len(sys.argv) < 3:
        print("Usage: python mcp_proxy.py <server_name> <command> [args...]")
        sys.exit(1)

    server_name = sys.argv[1]
    server_command = sys.argv[2:]
    dashboard_url = os.getenv("MCP_MONITOR_URL", "http://localhost:8766")

    proxy = MCPProtocolProxy(server_command, server_name, dashboard_url)
    await proxy.start()


if __name__ == "__main__":
    asyncio.run(main())
```

### Component 2: Universal Dashboard API

**Location**: `mcp-monitor/api/dashboard_service.py`

**Responsibilities**:
- Receive events from all MCP proxies
- Store in-memory (or Redis for production)
- Broadcast to web dashboard via WebSocket
- Provide REST API for queries

**Key Code**:

```python
"""
Universal MCP Monitor Dashboard API.

Receives observability events from MCP proxies and
broadcasts to web dashboard in real-time.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

app = FastAPI(title="MCP Monitor Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Data Models

class MCPEvent(BaseModel):
    """Universal MCP event"""
    type: str  # "tool_call_start", "progress", "log", etc.
    server: str  # Server name
    timestamp: str
    data: Dict[str, Any]


class ServerStatus(BaseModel):
    """Server connection status"""
    name: str
    status: str  # "connected", "disconnected"
    last_seen: str
    total_events: int


# State Management

class StateManager:
    def __init__(self):
        self.events: List[MCPEvent] = []
        self.servers: Dict[str, ServerStatus] = {}
        self.max_events = 1000  # Keep last 1000 events

    def add_event(self, event: MCPEvent):
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

        # Update server status
        if event.server not in self.servers:
            self.servers[event.server] = ServerStatus(
                name=event.server,
                status="connected",
                last_seen=event.timestamp,
                total_events=0
            )

        self.servers[event.server].last_seen = event.timestamp
        self.servers[event.server].total_events += 1

    def get_recent_events(self, limit: int = 100) -> List[MCPEvent]:
        return self.events[-limit:]

    def get_server_events(self, server: str, limit: int = 100) -> List[MCPEvent]:
        return [e for e in self.events if e.server == server][-limit:]


state = StateManager()


# WebSocket Management

class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)


ws_manager = WebSocketManager()


# REST Endpoints

@app.post("/api/events")
async def receive_event(event_data: Dict[str, Any]):
    """Receive event from MCP proxy"""

    event = MCPEvent(
        type=event_data.get("type", "unknown"),
        server=event_data.get("server", "unknown"),
        timestamp=event_data.get("timestamp", datetime.now().isoformat()),
        data=event_data
    )

    state.add_event(event)

    # Broadcast to dashboard
    await ws_manager.broadcast(event.dict())

    return {"status": "ok"}


@app.get("/api/events")
async def get_events(limit: int = 100) -> List[MCPEvent]:
    """Get recent events"""
    return state.get_recent_events(limit)


@app.get("/api/servers")
async def get_servers() -> List[ServerStatus]:
    """Get all server statuses"""
    return list(state.servers.values())


@app.get("/api/servers/{server_name}/events")
async def get_server_events(server_name: str, limit: int = 100) -> List[MCPEvent]:
    """Get events for specific server"""
    return state.get_server_events(server_name, limit)


@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time events"""
    await ws_manager.connect(websocket)

    try:
        # Send current state on connect
        for event in state.get_recent_events(50):
            await websocket.send_json(event.dict())

        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# Serve static dashboard
app.mount("/", StaticFiles(directory="dashboard/dist", html=True), name="dashboard")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8766)
```

### Component 3: VS Code Configuration

**How to Use**: Modify `.vscode/mcp.json` to use proxy wrapper

**Option A: Manual Wrapper** (Each server)

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": [
        "mcp-monitor/proxy/mcp_proxy.py",
        "CDE_Orchestrator",
        "python", "src/server.py"
      ],
      "env": {
        "PYTHONPATH": "src",
        "MCP_MONITOR_URL": "http://localhost:8766"
      }
    },

    "GitHub_MCP": {
      "command": "python",
      "args": [
        "mcp-monitor/proxy/mcp_proxy.py",
        "GitHub_MCP",
        "npx", "-y", "@modelcontextprotocol/server-github"
      ],
      "env": {
        "MCP_MONITOR_URL": "http://localhost:8766",
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
      }
    },

    "Filesystem_MCP": {
      "command": "python",
      "args": [
        "mcp-monitor/proxy/mcp_proxy.py",
        "Filesystem_MCP",
        "npx", "-y", "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/files"
      ],
      "env": {
        "MCP_MONITOR_URL": "http://localhost:8766"
      }
    }
  }
}
```

**Option B: Auto-Wrapper CLI** (Better UX)

```bash
# Install MCP Monitor CLI
npm install -g mcp-monitor

# Auto-wrap all servers in mcp.json
mcp-monitor wrap .vscode/mcp.json

# Start dashboard
mcp-monitor dashboard --port 8766
```

### Component 4: Web Dashboard

**Location**: `mcp-monitor/dashboard/` (React/Vue/Svelte)

**Features**:

1. **Server Overview**
   - List all connected MCP servers
   - Status: connected/disconnected/error
   - Last activity timestamp
   - Total events count

2. **Real-Time Event Stream**
   - Live feed of all events across all servers
   - Filter by server, event type, severity
   - Search/filter logs

3. **Tool Call Monitor**
   - See all tool calls in real-time
   - Tool name, arguments, duration, result
   - Success/failure rates
   - Performance metrics

4. **Progress Tracking**
   - Active operations across all servers
   - Progress bars with percentage
   - Elapsed time
   - Cancel operation (future)

5. **Log Viewer**
   - Aggregated logs from all servers
   - Color-coded by level (info/warning/error)
   - Structured log display
   - Export to file

6. **Performance Metrics**
   - Tool call latency (p50, p95, p99)
   - Request/response sizes
   - Error rates
   - Throughput

**UI Mockup**:

```
┌─────────────────────────────────────────────────────────────┐
│ MCP Monitor Dashboard                        [Settings] [⚙] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Servers (3 connected)                                        │
│ ┌────────────────┬──────────┬────────────┬─────────────┐   │
│ │ CDE Orchestrator│ ●Connected│ 2s ago    │ 145 events │   │
│ │ GitHub MCP      │ ●Connected│ 5s ago    │ 89 events  │   │
│ │ Filesystem MCP  │ ●Connected│ 1s ago    │ 234 events │   │
│ └────────────────┴──────────┴────────────┴─────────────┘   │
│                                                              │
│ Active Operations (2)                                        │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ [CDE] cde_onboardingProject                  47% 12.3s│ │
│ │ ███████████████████░░░░░░░░░░░░░░░░░░░░░              │ │
│ │                                                        │ │
│ │ [GitHub] github.searchRepositories           80% 5.1s │ │
│ │ ████████████████████████████████░░░░░░░░              │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ Recent Tool Calls                            [Filter ▼]     │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ 14:23:45 [CDE] cde_scanDocumentation  ✓ 2.3s         │ │
│ │ 14:23:42 [GitHub] github.getIssue     ✓ 0.8s         │ │
│ │ 14:23:40 [Filesystem] fs.readFile     ✓ 0.1s         │ │
│ │ 14:23:38 [CDE] cde_setupProject       ✗ Error        │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ Logs                                         [Filter ▼]     │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ [INFO ] [CDE] 📁 Scanning project structure...        │ │
│ │ [DEBUG] [GitHub] Rate limit: 4999/5000 remaining      │ │
│ │ [WARN ] [Filesystem] Slow file access: 2.3s          │ │
│ │ [ERROR] [CDE] ❌ Git repository not found             │ │
│ └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Proxy (Week 1)

**Deliverables**:
- ✅ `mcp_proxy.py` - Protocol interceptor
- ✅ Basic message parsing (JSON-RPC)
- ✅ Transparent forwarding (stdin/stdout)
- ✅ Extract progress/logs/tool calls
- ✅ Send to dashboard API

**Testing**:
```bash
# Test with CDE Orchestrator
python mcp_proxy.py CDE_Orchestrator python src/server.py

# Verify messages forwarded correctly
# Check dashboard receives events
```

### Phase 2: Dashboard API (Week 1-2)

**Deliverables**:
- ✅ FastAPI service on port 8766
- ✅ `/api/events` endpoint (receive from proxies)
- ✅ `/ws/events` WebSocket (broadcast to dashboard)
- ✅ In-memory state management
- ✅ Server status tracking

**Testing**:
```bash
# Start dashboard API
python dashboard_service.py

# Send test events
curl -X POST http://localhost:8766/api/events \
  -H "Content-Type: application/json" \
  -d '{"type":"log","server":"test","message":"Hello"}'

# Check WebSocket receives events
wscat -c ws://localhost:8766/ws/events
```

### Phase 3: Web Dashboard (Week 2-3)

**Deliverables**:
- ✅ React/Vue dashboard SPA
- ✅ Server list with status
- ✅ Real-time event stream
- ✅ Progress bars for active operations
- ✅ Log viewer with filtering
- ✅ Tool call history

**Testing**:
```bash
# Start dashboard
cd mcp-monitor/dashboard
npm install
npm run dev

# Open http://localhost:3000
# Verify real-time updates
```

### Phase 4: VS Code Integration (Week 3-4)

**Deliverables**:
- ✅ CLI tool for auto-wrapping mcp.json
- ✅ VS Code extension (optional)
- ✅ Documentation for setup
- ✅ Example configurations

**Testing**:
```bash
# Wrap all servers
mcp-monitor wrap .vscode/mcp.json

# Restart VS Code
# Verify all servers still work
# Check dashboard shows all servers
```

### Phase 5: Advanced Features (Week 4+)

**Deliverables**:
- ✅ Performance metrics (latency, throughput)
- ✅ Export logs to file
- ✅ Historical data (Redis backend)
- ✅ Alerts/notifications
- ✅ Dark/light theme
- ✅ Mobile-responsive dashboard

---

## 📊 Benefits of Universal Approach

### For Users

**Before** (Per-Server Custom Integration):
- ❌ Each MCP server needs custom code
- ❌ Only works for servers you control
- ❌ Inconsistent UX across servers
- ❌ No way to monitor 3rd-party MCP servers

**After** (Universal Protocol-Level Monitoring):
- ✅ **Works with ANY MCP server** (no modification needed)
- ✅ **Consistent UX** for all servers
- ✅ **Monitor 3rd-party servers** (GitHub MCP, etc.)
- ✅ **Aggregate view** of all MCP activity
- ✅ **Zero code changes** to existing servers

### For the MCP Ecosystem

- ✅ **First universal MCP monitoring tool**
- ✅ **Reference implementation** of protocol interception
- ✅ **Debugging aid** for MCP server developers
- ✅ **Promotes MCP adoption** (better observability)

---

## 🎯 Market Potential

### Target Audience

1. **Individual Developers**
   - Install 5-10 MCP servers
   - Want to see what they're doing
   - Need debugging tool

2. **Enterprise Teams**
   - Manage 50+ MCP servers
   - Need centralized monitoring
   - Compliance/audit requirements

3. **MCP Server Developers**
   - Test their own servers
   - Debug protocol issues
   - Performance profiling

### Monetization Options

**Open Source Core + Premium Features**:

**Free Tier**:
- ✅ Protocol proxy (open source)
- ✅ Basic dashboard
- ✅ Monitor up to 5 servers
- ✅ 1 hour data retention

**Pro Tier** ($9/month):
- ✅ Unlimited servers
- ✅ 30 days data retention
- ✅ Performance analytics
- ✅ Export/import
- ✅ Custom alerts

**Enterprise** ($99/month):
- ✅ Redis backend (multi-instance)
- ✅ SSO/RBAC
- ✅ Audit logs
- ✅ SLA support
- ✅ On-premise deployment

---

## 🔧 Technical Considerations

### Challenge 1: SSE Transport

**Problem**: Some MCP servers use SSE (Server-Sent Events) instead of stdio

**Solution**: Implement SSE proxy in addition to stdio proxy

```python
class SSEProxy:
    """Proxy for MCP servers using SSE transport"""

    async def proxy_sse_stream(self, request):
        # Forward HTTP request to server
        # Intercept SSE events
        # Extract observability data
        # Forward events to client
        pass
```

### Challenge 2: Binary Data

**Problem**: Some tool results may include binary data (images, etc.)

**Solution**:
- Detect binary content (base64 encoded)
- Store hash/size instead of full content
- Optionally store in object storage (S3)

### Challenge 3: High Volume

**Problem**: Popular servers may generate 1000s events/sec

**Solution**:
- Sampling (log 1 in N events)
- Aggregation (batch events before sending)
- Redis queue for buffering
- Compression (gzip JSON)

### Challenge 4: Privacy/Security

**Problem**: Tool arguments may contain sensitive data (tokens, passwords)

**Solution**:
- Redaction rules (regex patterns for secrets)
- User-configurable filters
- Local-only mode (no external transmission)
- End-to-end encryption (future)

---

## 📝 Getting Started (Prototype)

### Step 1: Install Dependencies

```bash
cd mcp-monitor
pip install -r requirements.txt
# fastapi, uvicorn, aiohttp, websockets
```

### Step 2: Start Dashboard API

```bash
python api/dashboard_service.py
# Dashboard API on http://localhost:8766
```

### Step 3: Wrap One MCP Server

```json
// .vscode/mcp.json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": [
        "mcp-monitor/proxy/mcp_proxy.py",
        "CDE_Orchestrator",
        "python", "src/server.py"
      ]
    }
  }
}
```

### Step 4: Test

```bash
# Restart VS Code
# Use CDE tool in Copilot Chat
# Open http://localhost:8766
# See events in real-time!
```

---

## 🎯 Success Metrics

### MVP Success Criteria

- ✅ Proxy works with at least 3 MCP servers (CDE, GitHub, Filesystem)
- ✅ Dashboard shows real-time events (< 200ms latency)
- ✅ Zero breaking changes to existing servers
- ✅ Installation takes < 5 minutes

### Production Success Criteria

- ✅ Works with 100% of spec-compliant MCP servers
- ✅ 10,000+ events/sec throughput
- ✅ < 50MB memory overhead per proxy
- ✅ 99.9% uptime (proxy doesn't crash servers)

---

## 🚀 Next Steps

**Immediate Actions** (Today):

1. ✅ Create `mcp-monitor/` directory
2. ✅ Implement basic `mcp_proxy.py` (stdio only)
3. ✅ Test with CDE Orchestrator
4. ✅ Verify messages forwarded correctly
5. ✅ Parse JSON-RPC messages

**This Week**:

1. Implement dashboard API (FastAPI)
2. Create basic web dashboard (HTML + JS)
3. Test with 2-3 different MCP servers
4. Document setup process

**Next Month**:

1. Polish dashboard UI
2. Add SSE transport support
3. Implement CLI wrapper tool
4. Open source on GitHub
5. Write blog post announcing tool

---

## 📚 References

- **MCP Specification**: https://spec.modelcontextprotocol.io/specification/
- **JSON-RPC 2.0**: https://www.jsonrpc.org/specification
- **Progress Notifications**: https://spec.modelcontextprotocol.io/specification/server/utilities/progress/
- **Logging**: https://spec.modelcontextprotocol.io/specification/server/utilities/logging/

---

**Status**: ✅ Ready to Build
**Impact**: 🚀 **Game Changer** for MCP Ecosystem
**Timeline**: 3-4 weeks for MVP

---

## 💡 Key Insight

> "The MCP protocol already has everything we need for observability.
> We just need to make it visible."

By intercepting at the protocol level, we create a **universal monitoring solution** that works with **any MCP server, anywhere, without modification**.

This is the **right way** to solve this problem! 🎯
