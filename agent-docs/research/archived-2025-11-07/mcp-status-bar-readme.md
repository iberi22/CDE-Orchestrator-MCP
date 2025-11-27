---
updated: "2025-11-07"
author: Jules AI Agent
status: draft
created: "2025-11-07"
type: guide
title: Readme
description: A summary of the document.
---
# MCP Status Bar

Shows MCP (Model Context Protocol) server progress in VS Code status bar.

## Features

- **Real-time progress tracking**: Shows percentage and elapsed time for MCP tool executions
- **Non-intrusive**: Status bar item only appears during active operations
- **Auto-hide**: Automatically disappears 5 seconds after completion
- **Universal**: Works with ANY MCP server via protocol-level proxy
- **Animated icon**: Spinning sync icon during execution, checkmark when complete

## Requirements

- VS Code 1.85.0 or higher
- MCP Proxy running on `ws://localhost:8766` (included in CDE Orchestrator MCP)

## Setup

### 1. Install the extension

```bash
cd mcp-status-bar
npm install
npm run compile
npm run package
code --install-extension mcp-status-bar-0.1.0.vsix
```

### 2. Start the MCP Proxy

The proxy intercepts JSON-RPC messages from your MCP servers and broadcasts progress events.

```bash
# Install Python dependencies
pip install websockets

# Start proxy with your MCP server
python mcp_proxy.py CDE python src/server.py
```

### 3. Configure VS Code

Update `.vscode/mcp.json` to use the proxy:

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": [
        "E:\\path\\to\\mcp_proxy.py",
        "CDE",
        "python",
        "src/server.py"
      ]
    }
  }
}
```

## Extension Settings

This extension contributes the following settings:

- `mcpStatusBar.enabled`: Enable/disable MCP progress in status bar (default: `true`)
- `mcpStatusBar.proxyUrl`: WebSocket URL of the MCP proxy (default: `ws://localhost:8766`)
- `mcpStatusBar.showPercentage`: Show percentage in status bar (default: `true`)
- `mcpStatusBar.showElapsedTime`: Show elapsed time in status bar (default: `true`)

## What You'll See

During execution:
```
$(sync~spin) scanDocs: 47% (12.3s)
```

After completion (5 seconds, then disappears):
```
$(check) scanDocs: 100% (23.1s)
```

Tooltip shows full details:
```
CDE Orchestrator - scanDocs

Progress: 47%
Elapsed: 12.3s
Status: Analyzing dependencies...
```

## Architecture

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
```

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode (auto-compile on save)
npm run watch

# Package as .vsix
npm run package

# Lint
npm run lint
```

## Known Issues

- Only shows one operation at a time (displays most recent if multiple are active)
- Proxy must be running before starting VS Code

## Future Enhancements

- TreeView sidebar with operation history
- Detailed log panel
- Performance metrics
- Dashboard for multiple projects

## License

See LICENSE file in the CDE Orchestrator MCP repository.
