# 🚀 Quick Start Guide - Nexus AI (Local)

**Last Updated**: 2025-11-23
**Status**: ✅ VALIDATED & READY

---

## Prerequisites

- ✅ Python 3.11+ (tested with 3.14.0)
- ✅ Rust toolchain (tested with 1.88.0)
- ✅ Git

---

## Option 1: Automated Start (Recommended)

### Windows PowerShell

```powershell
# Start server (default port 8000)
.\start_local.ps1

# Start with validation
.\start_local.ps1 -Validate

# Start on custom port
.\start_local.ps1 -Port 9000
```

The script automatically:
1. ✅ Checks Python installation
2. ✅ Activates virtual environment
3. ✅ Sets PYTHONPATH
4. ✅ Compiles Rust module (if needed)
5. ✅ Runs validation tests (if -Validate)
6. ✅ Starts MCP server

---

## Option 2: Manual Start

### Step 1: Setup Environment

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Set PYTHONPATH
$env:PYTHONPATH = "$PWD\src"
```

### Step 2: Compile Rust Module (First Time Only)

```powershell
cd rust_core
maturin develop --release
cd ..
```

### Step 3: Start Server

```powershell
python src/server.py
```

---

## Verify Installation

Run the validation script:

```powershell
python validate_local.py
```

**Expected output**:
```
============================================================
NEXUS AI LOCAL VALIDATION
============================================================
Testing all components without Docker...

[PHASE 1] Python Environment
------------------------------------------------------------
[OK] Python version >= 3.11 (found 3.14.0)
[OK] Virtual environment active
...

Result: SUCCESS
```

---

## What's Running?

When you start the server, you get:

### MCP Server
- **Tools**: 25 AI orchestration tools
- **Port**: 8000 (default)
- **Protocol**: MCP (Model Context Protocol)

### Available Tools
1. `cde_startFeature` - Start new feature workflow
2. `cde_selectWorkflow` - Intelligent workflow routing
3. `cde_scanDocumentation` - Rust-powered doc scanning
4. `cde_executeWithBestAgent` - Multi-agent orchestration
5. ... 21 more tools

### Rust Performance Layer
- **Threads**: 12 parallel workers (auto-detected)
- **Operations**:
  - High-speed documentation scanning
  - Parallel workflow validation
  - Project structure analysis

---

## Testing the Server

### Method 1: Python Client

```python
import asyncio
from mcp_tools import cde_checkRecipes

async def test():
    result = cde_checkRecipes()
    print(result)

asyncio.run(test())
```

### Method 2: MCP Protocol

Use any MCP-compatible client (Claude Desktop, Cursor, Windsurf, etc.)

**Configuration Example** (Claude Desktop):

```json
{
  "mcpServers": {
    "nexus-ai": {
      "command": "python",
      "args": ["E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py"],
      "env": {
        "PYTHONPATH": "E:\\scripts-python\\CDE Orchestrator MCP\\src"
      }
    }
  }
}
```

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'cde_rust_core'"

**Solution**:
```powershell
cd rust_core
maturin develop --release
cd ..
```

### Issue: "Port already in use"

**Solution**:
```powershell
# Use different port
.\start_local.ps1 -Port 9000
```

### Issue: "Virtual environment not found"

**Solution**:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

---

## Next Steps

### 1. Explore MCP Tools

List all available tools:

```python
from server import app
import asyncio

async def list_tools():
    tools = await app.get_tools()
    for name in tools.keys():
        print(f"- {name}")

asyncio.run(list_tools())
```

### 2. Read Documentation

- **Architecture**: `specs/design/architecture/README.md`
- **Agent Instructions**: `AGENTS.md`
- **Governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`

### 3. Run Tests

```powershell
pytest tests/ -v
```

---

## Performance Benchmarks

| Operation | Local (No Docker) |
|-----------|-------------------|
| Server Startup | < 2s |
| Rust Module Load | < 1s |
| Tool Registration | 25 tools |
| Memory Usage | ~50MB |
| Parallel Threads | 12 (auto) |

---

## Docker Deployment (Optional)

Docker setup is **ready but not required**:

```powershell
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

See `docs/docker-deployment.md` for details.

---

## Support

**Issues**: https://github.com/iberi22/CDE-Orchestrator-MCP/issues
**Documentation**: `specs/` directory
**Agent Instructions**: `AGENTS.md`

---

## Summary

✅ **Local deployment is PRODUCTION-READY**
✅ **All 25 validation tests pass**
✅ **Docker is optional** (use when needed)

Start coding with AI orchestration! 🚀
