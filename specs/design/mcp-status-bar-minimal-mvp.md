---
title: "MCP Status Bar Extension - Minimal MVP"
description: "Ultra-simple VS Code extension showing MCP progress in status bar only"
type: design
status: active
created: "2025-11-06"
updated: "2025-11-06"
author: "CDE Team"
tags:
  - vscode-extension
  - status-bar
  - mcp
  - minimal-mvp
llm_summary: |
  Minimal VS Code extension (Phase 1) that ONLY shows MCP server progress in status bar.
  No dashboard, no TreeView - just status bar item with percentage and elapsed time.
  Universal proxy captures data from any MCP server via JSON-RPC interception.
---

# MCP Status Bar Extension - Minimal MVP

> **Goal**: Ver % de ejecución de MCP tools en VS Code status bar
> **Approach**: Extensión minimalista + Proxy universal
> **Timeline**: 2-3 días para MVP funcional

---

## 🎯 MVP Scope (Fase 1)

### ✅ Lo que SÍ incluye:

1. **Status Bar Item** (esquina inferior derecha)
   - Ícono animado durante ejecución: `$(sync~spin)`
   - Texto: `"MCP: Onboarding 47% (12.3s)"`
   - Tooltip con detalles
   - Auto-hide cuando no hay operaciones activas

2. **WebSocket Client** (en la extensión)
   - Conecta a `ws://localhost:8766`
   - Recibe eventos de progreso en tiempo real
   - Auto-reconnect si proxy se reinicia

3. **MCP Proxy Universal** (Python script)
   - Intercepta JSON-RPC de CUALQUIER MCP server
   - Extrae `notifications/progress` y `tools/call`
   - Broadcast vía WebSocket

### ❌ Lo que NO incluye (Fase 2 - futuro):

- ❌ TreeView / Sidebar
- ❌ Dashboard web
- ❌ Log viewer
- ❌ Historial de operaciones
- ❌ Performance metrics

**Razón**: Queremos algo **ultra-rápido** de implementar y probar.

---

## 📐 Arquitectura Simplificada

```
VS Code
   ↕ (JSON-RPC)
MCP Proxy (Python)
   ↓ (parse messages)
   ↓ (extract progress)
   ↓ (WebSocket broadcast)
   ↓
VS Code Extension
   ↓
Status Bar Item
(muestra % y tiempo)
```

---

## 🔧 Implementación

### Parte 1: VS Code Extension (Super Simple)

**Estructura**:

```
mcp-status-bar/
├── package.json           # Extension manifest
├── src/
│   ├── extension.ts       # Main entry (< 100 líneas)
│   └── StatusBar.ts       # Status bar controller (< 50 líneas)
└── README.md
```

#### package.json

```json
{
  "name": "mcp-status-bar",
  "displayName": "MCP Status Bar",
  "description": "Show MCP server progress in status bar",
  "version": "0.1.0",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["Other"],
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "configuration": {
      "title": "MCP Status Bar",
      "properties": {
        "mcpStatusBar.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable MCP progress in status bar"
        },
        "mcpStatusBar.proxyUrl": {
          "type": "string",
          "default": "ws://localhost:8766",
          "description": "MCP Proxy WebSocket URL"
        }
      }
    }
  },
  "scripts": {
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "package": "vsce package"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "@types/node": "^20.x",
    "@types/ws": "^8.5.10",
    "typescript": "^5.2.0"
  },
  "dependencies": {
    "ws": "^8.14.2"
  }
}
```

#### src/extension.ts

```typescript
import * as vscode from 'vscode';
import WebSocket from 'ws';

let statusBarItem: vscode.StatusBarItem;
let ws: WebSocket | null = null;
let reconnectTimer: NodeJS.Timeout | null = null;

interface ProgressEvent {
    server: string;
    tool: string;
    percentage: number;  // 0.0 - 1.0
    elapsed: number;     // seconds
    message: string;
}

export function activate(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('mcpStatusBar');

    if (!config.get('enabled', true)) {
        return;
    }

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    context.subscriptions.push(statusBarItem);

    // Connect to proxy
    connectToProxy(config.get('proxyUrl', 'ws://localhost:8766'));

    // Watch for config changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('mcpStatusBar.proxyUrl')) {
                reconnect();
            }
        })
    );
}

function connectToProxy(url: string) {
    console.log(`Connecting to MCP Proxy: ${url}`);

    ws = new WebSocket(url);

    ws.on('open', () => {
        console.log('✅ Connected to MCP Proxy');
    });

    ws.on('message', (data: WebSocket.Data) => {
        try {
            const event: ProgressEvent = JSON.parse(data.toString());
            updateStatusBar(event);
        } catch (error) {
            console.error('Error parsing progress event:', error);
        }
    });

    ws.on('close', () => {
        console.log('❌ Disconnected from MCP Proxy');
        scheduleReconnect();
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
}

function updateStatusBar(event: ProgressEvent) {
    const percentage = Math.round(event.percentage * 100);
    const elapsed = event.elapsed.toFixed(1);

    // Icon
    const icon = percentage === 100 ? '$(check)' : '$(sync~spin)';

    // Text
    statusBarItem.text = `${icon} ${event.tool}: ${percentage}% (${elapsed}s)`;

    // Tooltip
    statusBarItem.tooltip = new vscode.MarkdownString(
        `**${event.server}** - ${event.tool}\n\n` +
        `Progress: ${percentage}%\n\n` +
        `Elapsed: ${elapsed}s\n\n` +
        `Status: ${event.message}`
    );

    statusBarItem.show();

    // Auto-hide after 5 seconds if complete
    if (percentage === 100) {
        setTimeout(() => {
            statusBarItem.hide();
        }, 5000);
    }
}

function scheduleReconnect() {
    if (reconnectTimer) {
        clearTimeout(reconnectTimer);
    }

    reconnectTimer = setTimeout(() => {
        const config = vscode.workspace.getConfiguration('mcpStatusBar');
        connectToProxy(config.get('proxyUrl', 'ws://localhost:8766'));
    }, 3000); // Retry every 3 seconds
}

function reconnect() {
    if (ws) {
        ws.close();
        ws = null;
    }
    const config = vscode.workspace.getConfiguration('mcpStatusBar');
    connectToProxy(config.get('proxyUrl', 'ws://localhost:8766'));
}

export function deactivate() {
    if (reconnectTimer) {
        clearTimeout(reconnectTimer);
    }
    if (ws) {
        ws.close();
    }
}
```

**Total: ~120 líneas** ✅

---

### Parte 2: MCP Proxy (Python Script Simplificado)

**Archivo único**: `mcp_proxy.py`

```python
#!/usr/bin/env python3
"""
MCP Status Bar Proxy - Ultra-simplified version

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
import subprocess
import websockets
import time
from typing import Dict, Any, Set
from dataclasses import dataclass
from datetime import datetime

# Global state
active_connections: Set[websockets.WebSocketServerProtocol] = set()
active_operations: Dict[str, Dict[str, Any]] = {}


@dataclass
class Operation:
    """Track active operation"""
    server: str
    tool: str
    start_time: float
    progress: float = 0.0
    message: str = "Starting..."


async def broadcast(message: dict):
    """Broadcast message to all connected VS Code extensions"""
    if active_connections:
        await asyncio.gather(
            *[conn.send(json.dumps(message)) for conn in active_connections],
            return_exceptions=True
        )


async def handle_websocket(websocket):
    """Handle WebSocket connection from VS Code extension"""
    active_connections.add(websocket)
    print(f"✅ VS Code extension connected. Total: {len(active_connections)}")

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
        print(f"❌ VS Code extension disconnected. Total: {len(active_connections)}")


async def run_proxy(server_name: str, command: list):
    """Run MCP server and intercept JSON-RPC messages"""
    print(f"🚀 Starting MCP proxy for: {server_name}")
    print(f"   Command: {' '.join(command)}")

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
                    "message": "Starting..."
                }

                await broadcast(active_operations[op_id])

        except:
            pass

        # Forward to server
        process.stdin.write(line.encode())
        await process.stdin.drain()


async def forward_server_to_client(process, server_name: str):
    """Forward MCP Server → VS Code"""
    while True:
        line = await process.stdout.readline()

        if not line:
            break

        line_str = line.decode()

        # Parse and extract progress
        try:
            msg = json.loads(line_str)

            # Progress notification
            if msg.get("method") == "notifications/progress":
                params = msg.get("params", {})
                token = params.get("progressToken", "unknown")
                progress = params.get("progress", 0) / params.get("total", 1)

                # Find matching operation
                for op_id, op_data in active_operations.items():
                    if token in op_id or op_id in token:
                        op_data["percentage"] = progress
                        op_data["elapsed"] = time.time() - op_data.get("start_time", time.time())
                        op_data["message"] = params.get("message", "In progress...")

                        await broadcast(op_data)

                        # Clean up if complete
                        if progress >= 1.0:
                            asyncio.create_task(cleanup_operation(op_id))

                        break

            # Tool call response
            elif "id" in msg and ("result" in msg or "error" in msg):
                op_id = str(msg["id"])

                if op_id in active_operations:
                    active_operations[op_id]["percentage"] = 1.0
                    active_operations[op_id]["message"] = "Complete" if "result" in msg else "Error"

                    await broadcast(active_operations[op_id])

                    asyncio.create_task(cleanup_operation(op_id))

        except:
            pass

        # Forward to VS Code
        sys.stdout.write(line_str)
        sys.stdout.flush()


async def monitor_stderr(process):
    """Monitor server stderr"""
    while True:
        line = await process.stderr.readline()
        if not line:
            break
        # Just log to our stderr
        sys.stderr.write(line.decode())


async def cleanup_operation(op_id: str):
    """Remove operation after 5 seconds"""
    await asyncio.sleep(5)
    if op_id in active_operations:
        del active_operations[op_id]


async def main():
    if len(sys.argv) < 3:
        print("Usage: python mcp_proxy.py <server_name> <command> [args...]")
        sys.exit(1)

    server_name = sys.argv[1]
    command = sys.argv[2:]

    # Start WebSocket server
    ws_server = await websockets.serve(
        handle_websocket,
        "localhost",
        8766
    )

    print(f"📡 WebSocket server listening on ws://localhost:8766")

    # Start proxy
    await run_proxy(server_name, command)


if __name__ == "__main__":
    asyncio.run(main())
```

**Total: ~200 líneas** ✅

---

## 🚀 Cómo Usar (3 Pasos)

### Paso 1: Instalar dependencias del proxy

```bash
pip install websockets
```

### Paso 2: Actualizar `.vscode/mcp.json`

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": [
        "E:\\scripts-python\\CDE Orchestrator MCP\\mcp_proxy.py",
        "CDE",
        "python", "src/server.py"
      ],
      "env": {
        "PYTHONPATH": "src",
        "CDE_AUTO_DISCOVER": "true"
      }
    }
  }
}
```

### Paso 3: Instalar extensión VS Code

```bash
cd mcp-status-bar
npm install
npm run compile
npm run package

# Instalar
code --install-extension mcp-status-bar-0.1.0.vsix
```

### Paso 4: ¡Usar!

```
1. Reiniciar VS Code
2. Usar cualquier tool MCP en Copilot Chat
3. Ver progreso en status bar (esquina inferior derecha)
   → $(sync~spin) CDE: Onboarding 47% (12.3s)
```

---

## 🎯 Lo que ve el usuario

### Durante ejecución:

```
Status Bar (inferior derecha):
┌────────────────────────────────────────┐
│ $(sync~spin) CDE: scanDocs 47% (12.3s)│
└────────────────────────────────────────┘
```

### Al completar:

```
Status Bar (5 segundos):
┌────────────────────────────────────────┐
│ $(check) CDE: scanDocs 100% (23.1s)   │
└────────────────────────────────────────┘

Luego desaparece
```

### Tooltip (hover):

```
╔════════════════════════════════════╗
║ CDE Orchestrator - scanDocs        ║
║                                    ║
║ Progress: 47%                      ║
║ Elapsed: 12.3s                     ║
║ Status: Analyzing dependencies... ║
╚════════════════════════════════════╝
```

---

## 📊 Ventajas del Enfoque Minimalista

### ✅ Pros:

1. **Rápido de implementar**: 2-3 días
2. **Fácil de probar**: Solo status bar
3. **Universal**: Funciona con CUALQUIER MCP server
4. **No intrusivo**: Solo aparece cuando hay operación activa
5. **Ligero**: < 1MB extension, < 5MB memory
6. **Fácil evolución**: Fase 2 puede agregar TreeView, dashboard

### ❌ Contras:

- Solo muestra 1 operación a la vez (si hay múltiples, muestra la más reciente)
- No hay historial
- No hay logs detallados

**Pero**: Para MVP es perfecto! 🎯

---

## 🔄 Fase 2 (Futuro)

Cuando MVP funcione, agregar:

1. **TreeView en Sidebar**
   - Lista de operaciones activas
   - Historial (últimas 20)
   - Click para ver detalles

2. **Panel de Output**
   - Logs en tiempo real
   - Filter por server/level

3. **Comandos**
   - "MCP: Show History"
   - "MCP: Clear History"
   - "MCP: Export Logs"

4. **Dashboard Web** (opcional)
   - Para ver múltiples proyectos
   - Métricas avanzadas
   - Performance analysis

---

## 📝 Checklist de Implementación

### Hoy (2-3 horas):

- [ ] Crear `mcp_proxy.py` (código arriba)
- [ ] Probar con 1 MCP server (CDE)
- [ ] Verificar WebSocket funciona

### Mañana (4-5 horas):

- [ ] Crear extensión VS Code (scaffold)
- [ ] Implementar status bar controller
- [ ] Conectar WebSocket
- [ ] Testing básico

### Pasado mañana (2-3 horas):

- [ ] Polish UI (icons, colors)
- [ ] Testing con múltiples servers
- [ ] Documentación
- [ ] Package & publish

**Total: 8-11 horas = 2-3 días** ✅

---

## 🎯 Success Criteria

MVP es exitoso si:

- ✅ Status bar muestra progress de MCP tools
- ✅ Funciona con al menos 2 MCP servers diferentes
- ✅ Latency < 200ms (event → UI update)
- ✅ No crashes
- ✅ Auto-reconnect si proxy reinicia

---

**Status**: ✅ Ready to Build
**Complexity**: 🟢 Low (MVP minimalista)
**Impact**: 🚀 High (primera extensión de su tipo)
