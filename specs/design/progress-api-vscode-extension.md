---
title: "Progress Tracking API + VS Code Extension - Technical Specification"
description: "Complete architecture for real-time MCP progress tracking via FastAPI/WebSockets and VS Code Extension"
type: design
status: active
created: "2025-11-06"
updated: "2025-11-06"
author: "CDE Team"
tags:
  - api
  - websockets
  - vscode-extension
  - progress-tracking
  - real-time
llm_summary: |
  Professional architecture for real-time MCP progress tracking using FastAPI/WebSockets backend
  and VS Code Extension frontend. MCP server sends progress events to API, API broadcasts via WebSocket,
  Extension renders in VS Code status bar with animated icons, percentage, and elapsed time.
---

# Progress Tracking API + VS Code Extension

> **Architecture**: FastAPI Service (WebSocket + REST) + VS Code Extension (TypeScript)
> **Goal**: Real-time progress feedback in VS Code status bar for all MCP operations
> **Latency Target**: < 100ms from MCP event to VS Code UI update

---

## 🎯 Executive Summary

### Problem Statement

**Current State**:
- ✅ MCP server sends `ctx.report_progress()` correctly
- ✅ Logs show progress in server console
- ❌ VS Code Copilot Chat **does not display progress** in real-time
- ❌ Users see no feedback for 15-30s operations
- ❌ No visibility into what MCP is doing

**Why This Happens**:
VS Code's MCP client implementation doesn't render progress notifications in the Chat UI. This is a limitation of the current VS Code Copilot integration, not our MCP server.

### Proposed Solution

**3-Tier Architecture**:

```
┌─────────────────────┐
│  MCP Server         │
│  (Python)           │
│                     │
│  - cde_onboarding   │
│  - cde_scanDocs     │
│  - cde_analyze      │
│  - etc.             │
└──────────┬──────────┘
           │ HTTP POST
           │ (progress events)
           ▼
┌─────────────────────┐
│  Progress API       │
│  (FastAPI)          │
│                     │
│  - REST endpoints   │
│  - WebSocket server │
│  - In-memory state  │
└──────────┬──────────┘
           │ WebSocket
           │ (real-time stream)
           ▼
┌─────────────────────┐
│  VS Code Extension  │
│  (TypeScript)       │
│                     │
│  - WebSocket client │
│  - Status bar UI    │
│  - TreeView history │
└─────────────────────┘
```

**Benefits**:
- ✅ **Real-time updates** in VS Code status bar (< 100ms latency)
- ✅ **Native VS Code UI** - professional look & feel
- ✅ **Persistent history** - see all operations in TreeView
- ✅ **Configurable** - users can enable/disable via settings
- ✅ **Works everywhere** - local, remote, WSL, Codespaces
- ✅ **Scalable** - API can serve multiple clients

---

## 📐 Architecture Overview

### Component 1: MCP Server (Existing)

**Location**: `src/server.py`, `src/mcp_tools/*.py`

**Responsibilities**:
- Execute MCP tools (onboarding, scanning, etc.)
- Send progress events to Progress API
- Handle errors and report to API

**Changes Required**:
- Add `ProgressReporter` middleware
- POST progress events to `http://localhost:8765/api/progress`
- No breaking changes to existing tools

### Component 2: Progress Tracking API (New)

**Location**: `src/cde_orchestrator/api/progress_service.py`

**Technology**: FastAPI + Uvicorn + WebSockets

**Responsibilities**:
- Receive progress events from MCP server (REST)
- Store state in-memory (Redis optional for production)
- Broadcast updates via WebSocket to all connected clients
- Serve historical data via REST API

**Endpoints**:

```python
POST   /api/progress/start      # Start new task
POST   /api/progress/update     # Update task progress
POST   /api/progress/complete   # Mark task complete
POST   /api/progress/error      # Report task error
GET    /api/progress/{task_id}  # Get task status
GET    /api/progress/active     # Get all active tasks
WebSocket /ws/progress          # Real-time stream
```

**Data Model**:

```python
class ProgressEvent:
    task_id: str              # Unique task ID (UUID)
    tool_name: str            # e.g., "cde_onboardingProject"
    project_path: str         # Project being operated on
    status: str               # "started", "progress", "completed", "error"
    percentage: float         # 0.0 to 1.0
    message: str              # Human-readable status
    elapsed: float            # Seconds since start
    timestamp: datetime       # Event timestamp
```

### Component 3: VS Code Extension (New)

**Location**: `cde-progress-extension/` (separate project)

**Technology**: TypeScript + VS Code Extension API

**Responsibilities**:
- Connect to Progress API via WebSocket
- Display active tasks in status bar
- Show progress percentage and elapsed time
- Animate icon during operations
- Provide TreeView with operation history
- Handle reconnection if API restarts

**UI Components**:

1. **Status Bar Item** (always visible)
   - Animated icon: `$(sync~spin)` during operations
   - Text: `"Onboarding 47% (12.3s)"`
   - Tooltip: Detailed progress message
   - Click to open TreeView

2. **TreeView** (sidebar)
   - Active operations (collapsible)
   - Recent history (last 20 operations)
   - Operation details (expand to see logs)

3. **Configuration**:
   - `cde.progress.enabled`: Enable/disable extension
   - `cde.progress.apiUrl`: API endpoint (default: `http://localhost:8765`)
   - `cde.progress.statusBar.show`: Show status bar item
   - `cde.progress.notifications`: Show completion notifications

---

## 🔧 Implementation Details

### Part 1: Progress Tracking API

#### File Structure

```
src/cde_orchestrator/api/
├── __init__.py
├── progress_service.py      # FastAPI app
├── models.py                # Pydantic models
├── state_manager.py         # In-memory state
└── websocket_manager.py     # WebSocket connection manager
```

#### progress_service.py

```python
"""
Progress Tracking API Service.

FastAPI service that receives progress events from MCP server
and broadcasts them to connected VS Code Extension clients via WebSocket.

Usage:
    # Start service (separate terminal)
    python -m cde_orchestrator.api.progress_service

    # Or via uvicorn
    uvicorn cde_orchestrator.api.progress_service:app --port 8765 --reload
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Dict, List
from datetime import datetime
import uuid

from .models import ProgressEvent, ProgressStartRequest, ProgressUpdateRequest
from .websocket_manager import WebSocketManager
from .state_manager import StateManager

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
ws_manager = WebSocketManager()
state_manager = StateManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    logger.info("🚀 Progress Tracking API starting...")
    yield
    logger.info("🛑 Progress Tracking API shutting down...")


# FastAPI app
app = FastAPI(
    title="CDE Progress Tracking API",
    description="Real-time progress tracking for MCP operations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# REST Endpoints

@app.post("/api/progress/start")
async def start_task(request: ProgressStartRequest) -> dict:
    """
    Start a new task.

    Called by MCP server when tool execution begins.
    """
    task_id = str(uuid.uuid4())

    event = ProgressEvent(
        task_id=task_id,
        tool_name=request.tool_name,
        project_path=request.project_path,
        status="started",
        percentage=0.0,
        message=request.initial_message,
        elapsed=0.0,
        timestamp=datetime.now()
    )

    # Store in state
    state_manager.add_task(event)

    # Broadcast to all connected clients
    await ws_manager.broadcast(event.dict())

    logger.info(f"✅ Task started: {task_id} - {request.tool_name}")

    return {"task_id": task_id, "status": "started"}


@app.post("/api/progress/update")
async def update_task(request: ProgressUpdateRequest) -> dict:
    """
    Update task progress.

    Called by MCP server during tool execution.
    """
    task = state_manager.get_task(request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task
    task.status = "progress"
    task.percentage = request.percentage
    task.message = request.message
    task.elapsed = request.elapsed
    task.timestamp = datetime.now()

    state_manager.update_task(task)

    # Broadcast
    await ws_manager.broadcast(task.dict())

    logger.debug(f"📊 Task updated: {request.task_id} - {request.percentage*100:.0f}%")

    return {"status": "updated"}


@app.post("/api/progress/complete")
async def complete_task(task_id: str, duration: float) -> dict:
    """
    Mark task as completed.

    Called by MCP server when tool execution finishes successfully.
    """
    task = state_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Mark complete
    task.status = "completed"
    task.percentage = 1.0
    task.elapsed = duration
    task.timestamp = datetime.now()

    state_manager.update_task(task)

    # Broadcast
    await ws_manager.broadcast(task.dict())

    logger.info(f"✅ Task completed: {task_id} - {duration:.1f}s")

    # Archive after 5 seconds
    asyncio.create_task(_archive_task(task_id))

    return {"status": "completed"}


@app.post("/api/progress/error")
async def error_task(task_id: str, error: str) -> dict:
    """
    Report task error.

    Called by MCP server when tool execution fails.
    """
    task = state_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Mark error
    task.status = "error"
    task.message = f"Error: {error}"
    task.timestamp = datetime.now()

    state_manager.update_task(task)

    # Broadcast
    await ws_manager.broadcast(task.dict())

    logger.error(f"❌ Task error: {task_id} - {error}")

    # Archive after 10 seconds
    asyncio.create_task(_archive_task(task_id, delay=10))

    return {"status": "error"}


@app.get("/api/progress/{task_id}")
async def get_task(task_id: str) -> ProgressEvent:
    """Get current status of a task"""
    task = state_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/api/progress/active")
async def get_active_tasks() -> List[ProgressEvent]:
    """Get all active tasks"""
    return state_manager.get_active_tasks()


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_tasks": len(state_manager.get_active_tasks()),
        "connected_clients": len(ws_manager.connections)
    }


# WebSocket Endpoint

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time progress updates.

    VS Code Extension connects here to receive live updates.
    """
    await ws_manager.connect(websocket)

    try:
        # Send current active tasks on connect
        active_tasks = state_manager.get_active_tasks()
        for task in active_tasks:
            await websocket.send_json(task.dict())

        # Keep connection alive
        while True:
            # Wait for messages (ping/pong for keep-alive)
            data = await websocket.receive_text()

            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket")


# Helper functions

async def _archive_task(task_id: str, delay: int = 5):
    """Archive task after delay"""
    await asyncio.sleep(delay)
    state_manager.archive_task(task_id)


# CLI entry point
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Progress Tracking API on http://localhost:8765")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8765,
        log_level="info"
    )
```

#### models.py

```python
"""
Data models for Progress Tracking API.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProgressStartRequest(BaseModel):
    """Request to start a new task"""
    tool_name: str = Field(..., description="Name of MCP tool (e.g., cde_onboardingProject)")
    project_path: str = Field(..., description="Path to project being operated on")
    initial_message: str = Field(default="Starting...", description="Initial status message")


class ProgressUpdateRequest(BaseModel):
    """Request to update task progress"""
    task_id: str = Field(..., description="Task UUID")
    percentage: float = Field(..., ge=0.0, le=1.0, description="Progress percentage (0.0-1.0)")
    message: str = Field(..., description="Progress message")
    elapsed: float = Field(..., description="Elapsed time in seconds")


class ProgressEvent(BaseModel):
    """Progress event data"""
    task_id: str
    tool_name: str
    project_path: str
    status: str  # "started", "progress", "completed", "error"
    percentage: float  # 0.0 to 1.0
    message: str
    elapsed: float  # seconds
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

#### state_manager.py

```python
"""
In-memory state management for progress tracking.

For production, consider using Redis for persistence and multi-instance support.
"""

from typing import Dict, List, Optional
from .models import ProgressEvent
import threading


class StateManager:
    """Thread-safe in-memory state manager"""

    def __init__(self):
        self.tasks: Dict[str, ProgressEvent] = {}
        self.archived: List[ProgressEvent] = []
        self.lock = threading.Lock()
        self.max_archived = 100  # Keep last 100 completed tasks

    def add_task(self, task: ProgressEvent):
        """Add new task"""
        with self.lock:
            self.tasks[task.task_id] = task

    def update_task(self, task: ProgressEvent):
        """Update existing task"""
        with self.lock:
            self.tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Optional[ProgressEvent]:
        """Get task by ID"""
        with self.lock:
            return self.tasks.get(task_id)

    def get_active_tasks(self) -> List[ProgressEvent]:
        """Get all active tasks"""
        with self.lock:
            return [
                task for task in self.tasks.values()
                if task.status in ["started", "progress"]
            ]

    def archive_task(self, task_id: str):
        """Move task to archive"""
        with self.lock:
            task = self.tasks.pop(task_id, None)
            if task:
                self.archived.append(task)
                # Keep only last N archived tasks
                if len(self.archived) > self.max_archived:
                    self.archived = self.archived[-self.max_archived:]

    def get_archived_tasks(self, limit: int = 20) -> List[ProgressEvent]:
        """Get recent archived tasks"""
        with self.lock:
            return self.archived[-limit:]
```

#### websocket_manager.py

```python
"""
WebSocket connection manager for broadcasting progress events.
"""

from fastapi import WebSocket
from typing import List
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections and broadcasting"""

    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.connections.append(websocket)
        logger.info(f"✅ Client connected. Total connections: {len(self.connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.connections:
            self.connections.remove(websocket)
            logger.info(f"❌ Client disconnected. Total connections: {len(self.connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []

        for connection in self.connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up dead connections
        for connection in disconnected:
            self.disconnect(connection)
```

### Part 2: MCP Server Integration

#### progress_reporter.py

```python
"""
Progress Reporter for MCP Server.

Sends progress events to Progress Tracking API.
"""

import os
import aiohttp
import logging
from typing import Optional
from contextlib import asynccontextmanager
import time

logger = logging.getLogger(__name__)


class ProgressReporter:
    """Report MCP progress to tracking API"""

    def __init__(self, api_url: str = "http://localhost:8765"):
        self.enabled = os.getenv("CDE_PROGRESS_API", "true").lower() == "true"
        self.api_url = api_url
        self.task_id: Optional[str] = None
        self.start_time: float = 0
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self, tool_name: str, project_path: str, initial_message: str = "Starting..."):
        """Start tracking a new task"""
        if not self.enabled:
            return

        self.start_time = time.time()

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.post(
                f"{self.api_url}/api/progress/start",
                json={
                    "tool_name": tool_name,
                    "project_path": project_path,
                    "initial_message": initial_message
                },
                timeout=aiohttp.ClientTimeout(total=2)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.task_id = data["task_id"]
                    logger.debug(f"✅ Progress tracking started: {self.task_id}")
                else:
                    logger.warning(f"Failed to start progress tracking: {response.status}")

        except Exception as e:
            logger.debug(f"Progress API not available: {e}")
            self.enabled = False  # Disable for this session

    async def update(self, percentage: float, message: str):
        """Update progress"""
        if not self.enabled or not self.task_id:
            return

        elapsed = time.time() - self.start_time

        try:
            async with self.session.post(
                f"{self.api_url}/api/progress/update",
                json={
                    "task_id": self.task_id,
                    "percentage": percentage,
                    "message": message,
                    "elapsed": elapsed
                },
                timeout=aiohttp.ClientTimeout(total=1)
            ) as response:
                if response.status != 200:
                    logger.warning(f"Failed to update progress: {response.status}")

        except Exception as e:
            logger.debug(f"Failed to update progress: {e}")

    async def complete(self):
        """Mark task as completed"""
        if not self.enabled or not self.task_id:
            return

        duration = time.time() - self.start_time

        try:
            async with self.session.post(
                f"{self.api_url}/api/progress/complete",
                params={"task_id": self.task_id, "duration": duration},
                timeout=aiohttp.ClientTimeout(total=1)
            ) as response:
                if response.status == 200:
                    logger.debug(f"✅ Progress tracking completed: {self.task_id}")

        except Exception as e:
            logger.debug(f"Failed to complete progress: {e}")

        finally:
            if self.session:
                await self.session.close()
                self.session = None

    async def error(self, error_message: str):
        """Report error"""
        if not self.enabled or not self.task_id:
            return

        try:
            async with self.session.post(
                f"{self.api_url}/api/progress/error",
                params={"task_id": self.task_id, "error": error_message},
                timeout=aiohttp.ClientTimeout(total=1)
            ) as response:
                if response.status == 200:
                    logger.debug(f"❌ Progress tracking error reported: {self.task_id}")

        except Exception as e:
            logger.debug(f"Failed to report error: {e}")

        finally:
            if self.session:
                await self.session.close()
                self.session = None

    @asynccontextmanager
    async def track(self, tool_name: str, project_path: str = ".", initial_message: str = "Starting..."):
        """Context manager for automatic progress lifecycle"""
        await self.start(tool_name, project_path, initial_message)
        try:
            yield self
        except Exception as e:
            await self.error(str(e))
            raise
        else:
            await self.complete()
```

#### Usage in MCP Tools

```python
# src/mcp_tools/onboarding.py
from cde_orchestrator.api.progress_reporter import ProgressReporter

async def cde_onboardingProject(ctx: Context, project_path: str = ".") -> str:
    """Onboarding with API progress tracking"""

    reporter = ProgressReporter()

    async with reporter.track("cde_onboardingProject", project_path, "CDE Onboarding Started"):
        # Checkpoint 1 (20%)
        await ctx.info("📁 Scanning structure...")
        await reporter.update(0.2, "Scanning project structure...")

        # ... implementation ...

        # Checkpoint 6 (100%)
        await ctx.info("✅ Complete!")
        await reporter.update(1.0, "Complete!")

    return result
```

### Part 3: VS Code Extension

#### Extension Structure

```
cde-progress-extension/
├── package.json               # Extension manifest
├── tsconfig.json              # TypeScript config
├── webpack.config.js          # Bundler config
├── .vscodeignore             # Files to exclude from package
├── README.md                  # Extension documentation
├── CHANGELOG.md              # Version history
├── src/
│   ├── extension.ts          # Main entry point
│   ├── websocket/
│   │   ├── WebSocketClient.ts       # WebSocket connection
│   │   └── ReconnectionManager.ts  # Auto-reconnect logic
│   ├── ui/
│   │   ├── StatusBarController.ts  # Status bar item
│   │   ├── ProgressTreeView.ts     # TreeView provider
│   │   └── NotificationManager.ts  # Completion notifications
│   ├── models/
│   │   └── ProgressEvent.ts        # TypeScript interfaces
│   └── config/
│       └── Configuration.ts         # Settings management
├── resources/
│   └── icons/
│       ├── progress.svg            # Extension icon
│       ├── sync-spin.svg           # Animated icon
│       └── ...
└── test/
    └── suite/
        └── extension.test.ts       # Extension tests
```

#### package.json

```json
{
  "name": "cde-progress-tracker",
  "displayName": "CDE MCP Progress Tracker",
  "description": "Real-time progress tracking for CDE Orchestrator MCP operations",
  "version": "1.0.0",
  "publisher": "cde-team",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["Other"],
  "keywords": ["mcp", "progress", "cde", "orchestrator"],
  "activationEvents": [
    "onStartupFinished"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "configuration": {
      "title": "CDE Progress Tracker",
      "properties": {
        "cde.progress.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable CDE MCP progress tracking"
        },
        "cde.progress.apiUrl": {
          "type": "string",
          "default": "http://localhost:8765",
          "description": "Progress API base URL"
        },
        "cde.progress.statusBar.show": {
          "type": "boolean",
          "default": true,
          "description": "Show progress in status bar"
        },
        "cde.progress.statusBar.position": {
          "type": "string",
          "enum": ["left", "right"],
          "default": "right",
          "description": "Status bar position"
        },
        "cde.progress.notifications.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Show completion notifications"
        },
        "cde.progress.notifications.onlyErrors": {
          "type": "boolean",
          "default": false,
          "description": "Only show notifications for errors"
        }
      }
    },
    "viewsContainers": {
      "activitybar": [
        {
          "id": "cde-progress",
          "title": "CDE Progress",
          "icon": "resources/icons/progress.svg"
        }
      ]
    },
    "views": {
      "cde-progress": [
        {
          "id": "cdeProgressView",
          "name": "Operations"
        }
      ]
    },
    "commands": [
      {
        "command": "cde.progress.refresh",
        "title": "Refresh Progress",
        "icon": "$(refresh)"
      },
      {
        "command": "cde.progress.clearHistory",
        "title": "Clear History",
        "icon": "$(clear-all)"
      }
    ]
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "pretest": "npm run compile && npm run lint",
    "lint": "eslint src --ext ts",
    "test": "node ./out/test/runTest.js",
    "package": "vsce package"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "@types/node": "^20.x",
    "@types/ws": "^8.5.10",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.50.0",
    "typescript": "^5.2.0",
    "@vscode/test-electron": "^2.3.5",
    "@vscode/vsce": "^2.21.0"
  },
  "dependencies": {
    "ws": "^8.14.2"
  }
}
```

#### src/extension.ts

```typescript
import * as vscode from 'vscode';
import { WebSocketClient } from './websocket/WebSocketClient';
import { StatusBarController } from './ui/StatusBarController';
import { ProgressTreeViewProvider } from './ui/ProgressTreeView';
import { Configuration } from './config/Configuration';

let wsClient: WebSocketClient;
let statusBar: StatusBarController;
let treeView: ProgressTreeViewProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('CDE Progress Tracker extension activating...');

    const config = new Configuration();

    if (!config.isEnabled()) {
        console.log('CDE Progress Tracker is disabled');
        return;
    }

    // Initialize components
    statusBar = new StatusBarController(context);
    treeView = new ProgressTreeViewProvider();
    wsClient = new WebSocketClient(config.getApiUrl(), statusBar, treeView);

    // Register TreeView
    vscode.window.registerTreeDataProvider('cdeProgressView', treeView);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('cde.progress.refresh', () => {
            treeView.refresh();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('cde.progress.clearHistory', () => {
            treeView.clearHistory();
        })
    );

    // Connect to API
    wsClient.connect();

    // Watch for configuration changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('cde.progress')) {
                // Reconnect with new settings
                wsClient.disconnect();
                wsClient = new WebSocketClient(config.getApiUrl(), statusBar, treeView);
                wsClient.connect();
            }
        })
    );

    console.log('✅ CDE Progress Tracker extension activated');
}

export function deactivate() {
    if (wsClient) {
        wsClient.disconnect();
    }
    if (statusBar) {
        statusBar.dispose();
    }
    console.log('CDE Progress Tracker extension deactivated');
}
```

#### src/websocket/WebSocketClient.ts

```typescript
import WebSocket from 'ws';
import { ProgressEvent } from '../models/ProgressEvent';
import { StatusBarController } from '../ui/StatusBarController';
import { ProgressTreeViewProvider } from '../ui/ProgressTreeView';

export class WebSocketClient {
    private ws: WebSocket | null = null;
    private reconnectTimer: NodeJS.Timeout | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 10;
    private reconnectDelay = 3000; // 3 seconds

    constructor(
        private apiUrl: string,
        private statusBar: StatusBarController,
        private treeView: ProgressTreeViewProvider
    ) {}

    public connect() {
        const wsUrl = this.apiUrl.replace('http:', 'ws:').replace('https:', 'wss:') + '/ws/progress';

        console.log(`Connecting to Progress API: ${wsUrl}`);

        this.ws = new WebSocket(wsUrl);

        this.ws.on('open', () => {
            console.log('✅ Connected to Progress API');
            this.reconnectAttempts = 0;

            // Start ping interval
            this.startPingInterval();
        });

        this.ws.on('message', (data: WebSocket.Data) => {
            try {
                const event: ProgressEvent = JSON.parse(data.toString());
                this.handleProgressEvent(event);
            } catch (error) {
                console.error('Error parsing progress event:', error);
            }
        });

        this.ws.on('close', () => {
            console.log('❌ Disconnected from Progress API');
            this.scheduleReconnect();
        });

        this.ws.on('error', (error) => {
            console.error('WebSocket error:', error);
        });
    }

    public disconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    private handleProgressEvent(event: ProgressEvent) {
        console.log(`Progress event: ${event.tool_name} - ${event.percentage * 100}%`);

        // Update UI components
        this.statusBar.updateProgress(event);
        this.treeView.updateProgress(event);

        // Show completion notification if configured
        if (event.status === 'completed') {
            this.statusBar.showCompletionNotification(event);
        } else if (event.status === 'error') {
            this.statusBar.showErrorNotification(event);
        }
    }

    private startPingInterval() {
        setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send('ping');
            }
        }, 30000); // Ping every 30 seconds
    }

    private scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached. Giving up.');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.min(this.reconnectAttempts, 5);

        console.log(`Reconnecting in ${delay / 1000}s (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, delay);
    }
}
```

#### src/ui/StatusBarController.ts

```typescript
import * as vscode from 'vscode';
import { ProgressEvent } from '../models/ProgressEvent';

export class StatusBarController {
    private statusBarItem: vscode.StatusBarItem;
    private currentEvent: ProgressEvent | null = null;

    constructor(context: vscode.ExtensionContext) {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );

        this.statusBarItem.command = 'cde.progress.refresh';

        context.subscriptions.push(this.statusBarItem);
    }

    public updateProgress(event: ProgressEvent) {
        this.currentEvent = event;

        const percentage = Math.round(event.percentage * 100);
        const elapsed = event.elapsed.toFixed(1);

        // Icon based on status
        let icon = '$(sync~spin)'; // Spinning icon during progress
        if (event.status === 'completed') {
            icon = '$(check)';
        } else if (event.status === 'error') {
            icon = '$(error)';
        }

        // Status bar text
        this.statusBarItem.text = `${icon} ${event.tool_name.replace('cde_', '')} ${percentage}% (${elapsed}s)`;

        // Tooltip with details
        this.statusBarItem.tooltip = new vscode.MarkdownString(
            `**${event.tool_name}**\n\n` +
            `Status: ${event.status}\n\n` +
            `Progress: ${percentage}%\n\n` +
            `Message: ${event.message}\n\n` +
            `Elapsed: ${elapsed}s\n\n` +
            `Project: ${event.project_path}`
        );

        this.statusBarItem.show();

        // Auto-hide after completion
        if (event.status === 'completed' || event.status === 'error') {
            setTimeout(() => {
                this.statusBarItem.hide();
            }, 5000); // Hide after 5 seconds
        }
    }

    public showCompletionNotification(event: ProgressEvent) {
        const config = vscode.workspace.getConfiguration('cde.progress.notifications');

        if (!config.get('enabled', true) || config.get('onlyErrors', false)) {
            return;
        }

        vscode.window.showInformationMessage(
            `✅ ${event.tool_name}: Completed in ${event.elapsed.toFixed(1)}s`
        );
    }

    public showErrorNotification(event: ProgressEvent) {
        const config = vscode.workspace.getConfiguration('cde.progress.notifications');

        if (!config.get('enabled', true)) {
            return;
        }

        vscode.window.showErrorMessage(
            `❌ ${event.tool_name}: ${event.message}`
        );
    }

    public dispose() {
        this.statusBarItem.dispose();
    }
}
```

#### src/ui/ProgressTreeView.ts

```typescript
import * as vscode from 'vscode';
import { ProgressEvent } from '../models/ProgressEvent';

class ProgressTreeItem extends vscode.TreeItem {
    constructor(
        public readonly event: ProgressEvent,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(event.tool_name, collapsibleState);

        this.tooltip = event.message;
        this.description = `${Math.round(event.percentage * 100)}% - ${event.elapsed.toFixed(1)}s`;

        // Icon based on status
        if (event.status === 'completed') {
            this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('charts.green'));
        } else if (event.status === 'error') {
            this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('charts.red'));
        } else {
            this.iconPath = new vscode.ThemeIcon('sync~spin', new vscode.ThemeColor('charts.blue'));
        }
    }
}

export class ProgressTreeViewProvider implements vscode.TreeDataProvider<ProgressTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ProgressTreeItem | undefined | null | void> =
        new vscode.EventEmitter<ProgressTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ProgressTreeItem | undefined | null | void> =
        this._onDidChangeTreeData.event;

    private activeOperations: Map<string, ProgressEvent> = new Map();
    private history: ProgressEvent[] = [];
    private maxHistory = 20;

    public updateProgress(event: ProgressEvent) {
        if (event.status === 'started' || event.status === 'progress') {
            this.activeOperations.set(event.task_id, event);
        } else {
            // Move to history
            this.activeOperations.delete(event.task_id);
            this.history.unshift(event);
            if (this.history.length > this.maxHistory) {
                this.history.pop();
            }
        }

        this.refresh();
    }

    public refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    public clearHistory(): void {
        this.history = [];
        this.refresh();
    }

    getTreeItem(element: ProgressTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ProgressTreeItem): Thenable<ProgressTreeItem[]> {
        if (!element) {
            // Root level - show categories
            const items: ProgressTreeItem[] = [];

            // Active operations
            if (this.activeOperations.size > 0) {
                const activeEvents = Array.from(this.activeOperations.values());
                items.push(...activeEvents.map(e => new ProgressTreeItem(e, vscode.TreeItemCollapsibleState.None)));
            }

            // History
            if (this.history.length > 0) {
                items.push(...this.history.map(e => new ProgressTreeItem(e, vscode.TreeItemCollapsibleState.None)));
            }

            return Promise.resolve(items);
        }

        return Promise.resolve([]);
    }
}
```

#### src/models/ProgressEvent.ts

```typescript
export interface ProgressEvent {
    task_id: string;
    tool_name: string;
    project_path: string;
    status: 'started' | 'progress' | 'completed' | 'error';
    percentage: number;
    message: string;
    elapsed: number;
    timestamp: string;
}
```

---

## 📊 Deployment & Configuration

### Step 1: Start Progress API

```bash
# Terminal 1: Start Progress API
cd "E:\scripts-python\CDE Orchestrator MCP"
.\.venv\Scripts\activate
python -m cde_orchestrator.api.progress_service
# Server starts on http://localhost:8765
```

### Step 2: Update MCP Server Configuration

Update `.vscode/mcp.json`:

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": ["src/server.py"],
      "env": {
        "PYTHONPATH": "src",
        "CDE_AUTO_DISCOVER": "true",
        "CDE_LOG_LEVEL": "INFO",
        "CDE_PROGRESS_API": "true",  // ✨ Enable Progress API integration
        "PROGRESS_API_URL": "http://localhost:8765"
      }
    }
  }
}
```

### Step 3: Install VS Code Extension

```bash
# Build extension
cd cde-progress-extension
npm install
npm run compile
npm run package  # Creates .vsix file

# Install in VS Code
code --install-extension cde-progress-tracker-1.0.0.vsix
```

### Step 4: Configure Extension

VS Code Settings (`settings.json`):

```json
{
  "cde.progress.enabled": true,
  "cde.progress.apiUrl": "http://localhost:8765",
  "cde.progress.statusBar.show": true,
  "cde.progress.statusBar.position": "right",
  "cde.progress.notifications.enabled": true,
  "cde.progress.notifications.onlyErrors": false
}
```

---

## 🎯 Success Metrics

### Performance Targets

- ✅ **Latency**: < 100ms from MCP event to VS Code UI update
- ✅ **CPU Usage**: < 5% during idle, < 15% during active operations
- ✅ **Memory**: < 50MB for API service, < 20MB for extension
- ✅ **Reliability**: 99.9% uptime, auto-reconnect on failures

### User Experience

- ✅ **Visibility**: Progress visible within 100ms of operation start
- ✅ **Clarity**: Status, percentage, and elapsed time always shown
- ✅ **Non-intrusive**: Notifications optional, auto-hide after completion
- ✅ **History**: Last 20 operations accessible in TreeView

---

## 📚 Testing Strategy

### Unit Tests

```bash
# API tests
pytest src/cde_orchestrator/api/tests/

# Extension tests
cd cde-progress-extension
npm test
```

### Integration Tests

```bash
# Test full flow: MCP → API → Extension
python tests/integration/test_progress_flow.py
```

### Manual Testing

1. Start Progress API
2. Start MCP server
3. Install VS Code extension
4. Run MCP tool (e.g., `cde_onboardingProject`)
5. Verify status bar updates in real-time
6. Check TreeView shows operation
7. Verify completion notification

---

## 🚀 Next Steps

1. **Phase 1** (This Week): Implement Progress API
2. **Phase 2** (Week 2): Integrate with MCP Server
3. **Phase 3** (Week 3-4): Build VS Code Extension
4. **Phase 4** (Week 5): Testing & deployment
5. **Phase 5** (Week 6): Publish to VS Code Marketplace

---

**Status**: ✅ Ready for Implementation
**Owner**: CDE Team
**Timeline**: 4-6 weeks for complete implementation
