---
title: "MCP Status Bar Installation & Agent Integration"
description: "Quick start guide for installing MCP Status Bar extension and enabling agent-based installation"
type: "guide"
status: "active"
created: "2025-11-06"
updated: "2025-11-06"
author: "CDE Team"
---

# MCP Status Bar - Installation & Agent Integration

## ⚡ Quick Start

### What It Does
Displays real-time progress of MCP tool executions in VS Code status bar:
- Tool executing: `$(sync~spin) scanDocumentation: 45% (2.3s)`
- Tool complete: `$(check) scanDocumentation: 100% (10.2s)`
- Ready: `$(radio-tower) MCP: Ready`

### Manual Installation
```bash
cd mcp-status-bar
npm install
npm run compile
npx vsce package --allow-star-activation
code --install-extension mcp-status-bar-0.1.0.vsix --force
```

Then restart VS Code and run any MCP tool to see progress!

## 🤖 Agent-Based Installation (Proposed)

### New MCP Tool: `cde_installMcpExtension`

```python
async def cde_installMcpExtension(
    ctx: Context,
    extension_name: str = "mcp-status-bar",
    force: bool = False
) -> str:
    """Install MCP extension automatically."""
    import subprocess
    from pathlib import Path

    # Check if installed
    if not force:
        try:
            result = subprocess.run(
                ["code", "--list-extensions"],
                capture_output=True, text=True
            )
            if "mcp-status-bar" in result.stdout:
                return json.dumps({"status": "already_installed"})
        except: pass

    # Build
    ext_dir = Path(extension_name)
    subprocess.run(["npm", "run", "compile"], cwd=ext_dir, check=True)
    subprocess.run(
        ["npx", "vsce", "package", "--allow-star-activation"],
        cwd=ext_dir, check=True
    )

    # Install
    vsix = ext_dir / f"{extension_name}-0.1.0.vsix"
    subprocess.run(
        ["code", "--install-extension", str(vsix), "--force"],
        check=True
    )

    return json.dumps({"status": "success", "extension": extension_name})
```

### Workflow Integration

In agent workflows, use before any progress-tracking tools:

```python
# Phase 1: Setup
cde_installMcpExtension(extension_name="mcp-status-bar")

# Phase 2: Long-running tools now show progress
cde_scanDocumentation(project_path="/path/to/project")
# → User sees live progress in status bar!

cde_analyzeDocumentation(project_path="/path/to/project")
# → User sees live progress in status bar!
```

## 🏗️ How It Works (Architecture)

### Three-Layer Communication

```
┌──────────────────────────────────────────┐
│ MCP Tool (Python)                        │
│ urllib.request.urlopen()                 │
│ POST http://localhost:8767/progress      │
└──────────────┬───────────────────────────┘
               │ HTTP
               ▼
┌──────────────────────────────────────────┐
│ MCP Proxy (HTTP Server 8767)             │
│ • Receives progress events               │
│ • Broadcasts to WebSocket (8766)         │
│ • Forwards to Extension (8768)           │
└──────────────┬───────────────────────────┘
               │ HTTP
               ▼
┌──────────────────────────────────────────┐
│ VS Code Extension (HTTP Server 8768)     │
│ • Receives progress HTTP POST            │
│ • Updates status bar in real-time        │
│ • Auto-resets after 5 seconds            │
└──────────────────────────────────────────┘
```

## 📝 Adding Progress to Your Tools

Simple template for any MCP tool:

```python
import json
import time
import urllib.request

async def my_long_tool(ctx: Context, items: list):
    total = len(items)

    for i, item in enumerate(items):
        # Do work
        process_item(item)

        # Report progress
        event = {
            "server": "CDE",
            "tool": "my_long_tool",
            "percentage": i / total,
            "elapsed": time.time() - start_time,
            "message": f"Processing {i+1}/{total}"
        }

        try:
            data = json.dumps(event).encode('utf-8')
            req = urllib.request.Request(
                "http://localhost:8767/progress",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=1).close()
        except Exception:
            pass  # Fail gracefully
```

## ✅ Verification

Check endpoints are running:

```bash
python check_endpoints.py
```

Expected output:
```
📡 WebSocket (8766): ✅ LISTENING
🌐 HTTP (8767):      ✅ LISTENING
🧪 Testing HTTP endpoint... ✅ Responding
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "MCP: Ready" not in status bar | Restart VS Code after install |
| Progress not updating | Run `python check_endpoints.py` |
| Extension install fails | Update VS Code to v1.85.0+ |
| HTTP timeout errors | Normal - tools continue working |

## 📚 See Also

- Complete docs: `docs/mcp-status-bar-complete-implementation.md`
- Original design: `specs/design/mcp-status-bar-minimal-mvp.md`
- Source code: `mcp-status-bar/`, `mcp-monitor/proxy/mcp_proxy.py`

