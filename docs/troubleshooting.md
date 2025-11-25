---
title: Troubleshooting - CDE Orchestrator MCP
description: Common issues and solutions when using CDE Orchestrator in external projects
type: guide
status: active
created: '2025-11-24'
updated: '2025-11-24'
author: Nexus AI Team
tags:
  - troubleshooting
  - debugging
  - support
llm_summary: "Troubleshooting guide for CDE Orchestrator MCP configuration issues. Includes real examples and solutions for common problems."
---

# Troubleshooting Guide - CDE Orchestrator MCP

> **Quick Solutions for Common Problems**
> **Last Updated**: 2025-11-24

---

## 🔍 Quick Diagnostics

### Step 1: Verify Server is Running

```powershell
# In CDE Orchestrator directory
cd "E:\scripts-python\CDE Orchestrator MCP"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "$PWD\src"
python src/server.py
```

**Expected Output**:
```
✅ Generated 25 MCP tool files
📁 Filesystem structure: E:\scripts-python\CDE Orchestrator MCP
🚀 Server started on stdio
```

**If you see errors here**, the problem is with CDE installation, not configuration.

### Step 2: Check VS Code MCP Logs

1. Press `Ctrl+Shift+P`
2. Type: "MCP: Show Server Logs"
3. Select: "CDE_Orchestrator"

Look for:
- ✅ "Server started successfully"
- ✅ "25 tools registered"
- ❌ "Connection refused"
- ❌ "Module not found"

### Step 3: Test Tool Availability

In GitHub Copilot Chat:
```
@workspace Run cde_healthCheck
```

**Expected Response**:
```json
{
  "status": "healthy",
  "python_version": "3.14.0",
  "rust_module": "loaded",
  "tools_registered": 25
}
```

---

## 🚨 Common Problems & Solutions

### Problem 1: "Tool not found" or "cde_setupProject not available"

**Symptoms**:
- Copilot says: "I don't have access to that tool"
- Tool names don't appear in autocomplete
- `@workspace` commands return errors

**Root Cause**: MCP server not loaded in VS Code

**Solution A**: Verify mcp.json Location

```powershell
# In your project directory
dir .vscode\mcp.json
```

If file doesn't exist:
```powershell
mkdir .vscode
# Copy from docs/mcp.json.example and edit paths
```

**Solution B**: Check mcp.json Syntax

Common mistakes:
```json
// ❌ WRONG: Relative paths
{
  "command": "python",
  "args": ["src/server.py"]  // ← Won't work!
}

// ✅ RIGHT: Absolute paths
{
  "command": "python",
  "args": ["E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py"]
}
```

**Solution C**: Reload VS Code

After editing `mcp.json`:
1. Press `Ctrl+Shift+P`
2. Type: "Developer: Reload Window"
3. Wait 5-10 seconds
4. Test again

---

### Problem 2: "Python not found" or "Command failed"

**Symptoms**:
- MCP logs show: "python: command not found"
- Server won't start
- No output in logs

**Root Cause**: Python not in PATH or wrong Python version

**Solution A**: Use Full Python Path

Update `mcp.json`:
```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "E:\\scripts-python\\CDE Orchestrator MCP\\.venv\\Scripts\\python.exe",
      "args": ["E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py"],
      ...
    }
  }
}
```

**Solution B**: Verify Python Installation

```powershell
# Check Python version
python --version
# Should show: Python 3.11+ (e.g., 3.14.0)

# If not found, add to PATH or use full path
```

---

### Problem 3: "ModuleNotFoundError: No module named 'cde_orchestrator'"

**Symptoms**:
- Server starts but crashes immediately
- Logs show import errors
- Tools partially available

**Root Cause**: PYTHONPATH not set correctly

**Solution**:

Ensure `PYTHONPATH` points to CDE's `src` directory:

```json
{
  "env": {
    "PYTHONPATH": "E:\\scripts-python\\CDE Orchestrator MCP\\src"
  }
}
```

**Test PYTHONPATH**:
```powershell
$env:PYTHONPATH = "E:\scripts-python\CDE Orchestrator MCP\src"
python -c "import cde_orchestrator; print('OK')"
# Should print: OK
```

---

### Problem 4: "No module named 'cde_rust_core'"

**Symptoms**:
- Server starts but some tools fail
- Logs show Rust module import error
- Documentation scanning doesn't work

**Root Cause**: Rust module not compiled

**Solution**:

```powershell
cd "E:\scripts-python\CDE Orchestrator MCP\rust_core"
maturin develop --release
cd ..
```

**Verify**:
```powershell
python -c "import cde_rust_core; print(cde_rust_core.__version__)"
# Should print: 0.2.0 (or current version)
```

---

### Problem 5: Tools work in CDE project but not in other projects

**Symptoms**:
- `cde_setupProject` works when called from CDE directory
- Same command fails in external project
- Logs show "Project not found"

**Root Cause**: Project not in scan paths or auto-discovery disabled

**Solution A**: Add Project to Scan Paths

```json
{
  "args": [
    "E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py",
    "--scan-paths",
    "E:\\your-project",
    "E:\\another-project"
  ]
}
```

**Solution B**: Enable Auto-Discovery

```json
{
  "env": {
    "CDE_AUTO_DISCOVER": "true"
  }
}
```

**Test**:
```
@workspace Run cde_onboardingProject with project_path="E:\your-project"
```

---

### Problem 6: "Connection refused" or "Server crashed"

**Symptoms**:
- MCP logs show connection errors
- Server starts then stops immediately
- Tools available then disappear

**Root Cause**: Port conflict or server crash

**Solution A**: Check for Port Conflicts

```powershell
# Find processes using port 8000 (if using HTTP mode)
netstat -ano | findstr :8000
```

**Solution B**: Use stdio Mode (Default)

Don't specify `--port` in args (stdio is more reliable):

```json
{
  "args": [
    "E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py"
    // ❌ Don't add: "--port", "8000"
  ]
}
```

**Solution C**: Check Logs for Crash

Look for:
- Import errors
- Permission errors
- File not found errors

---

### Problem 7: "Slow startup" or "Tools take long to load"

**Symptoms**:
- VS Code hangs on startup
- First tool call takes 30+ seconds
- Subsequent calls are fast

**Root Cause**: Rust module compilation or large project scan

**Solution A**: Pre-compile Rust Module

```powershell
cd "E:\scripts-python\CDE Orchestrator MCP\rust_core"
maturin develop --release
```

**Solution B**: Limit Scan Paths

Only include projects you need:

```json
{
  "args": [
    "E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py",
    "--scan-paths",
    "E:\\your-project"
    // Don't add entire drives: "E:\\"
  ]
}
```

---

### Problem 8: "Tool returns empty result" or "No output"

**Symptoms**:
- Tool executes but returns empty JSON
- No errors in logs
- `cde_onboardingProject` returns `{}`

**Root Cause**: Project path doesn't exist or is inaccessible

**Solution**:

**Verify Path**:
```powershell
Test-Path "E:\your-project"
# Should return: True
```

**Use Absolute Paths**:
```
@workspace Run cde_onboardingProject with project_path="E:\your-project"
```

**Not**:
```
@workspace Run cde_onboardingProject
# This uses current directory, which might not be your project
```

---

## 🔧 Advanced Debugging

### Enable Debug Logging

```json
{
  "env": {
    "CDE_LOG_LEVEL": "DEBUG"
  }
}
```

### Run Server Manually

```powershell
cd "E:\scripts-python\CDE Orchestrator MCP"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "$PWD\src"
$env:CDE_LOG_LEVEL = "DEBUG"
python src/server.py
```

Watch for errors in console output.

### Test Tools Directly

```powershell
# In Python
python
>>> from mcp_tools import cde_setupProject
>>> import asyncio
>>> result = asyncio.run(cde_setupProject(None, "E:\\your-project", False))
>>> print(result)
```

---

## 📋 Configuration Checklist

Use this checklist to verify your setup:

- [ ] `.vscode/mcp.json` exists in project root
- [ ] All paths in `mcp.json` are **absolute** (not relative)
- [ ] `PYTHONPATH` points to CDE's `src` directory
- [ ] Python version is 3.11+ (`python --version`)
- [ ] Rust module compiled (`import cde_rust_core` works)
- [ ] CDE server starts manually (test in PowerShell)
- [ ] VS Code reloaded after editing `mcp.json`
- [ ] MCP logs show "Server started successfully"
- [ ] `cde_healthCheck` returns healthy status
- [ ] Project path in scan paths or auto-discovery enabled

---

## 🆘 Getting Help

If none of these solutions work:

1. **Collect Information**:
   - VS Code version
   - Python version (`python --version`)
   - Contents of `.vscode/mcp.json`
   - MCP server logs (last 50 lines)
   - Error message (full text)

2. **Check Documentation**:
   - [Configuration Guide](configuration-guide.md)
   - [Quick Start](../QUICKSTART_LOCAL.md)
   - [Main README](../README.md)

3. **GitHub Issues**:
   - Search existing issues: https://github.com/iberi22/CDE-Orchestrator-MCP/issues
   - Create new issue with information from step 1

4. **Email Support**:
   - Enterprise: enterprise@nexus-ai.dev
   - Include information from step 1

---

## 💡 Pro Tips

1. **Always Use Absolute Paths**: Never use relative paths in `mcp.json`
2. **Test in CDE First**: Verify tools work in CDE project before external use
3. **Check Logs Early**: Don't guess, check MCP logs immediately
4. **Reload Often**: Reload VS Code after any `mcp.json` change
5. **One Change at a Time**: If debugging, change one thing and test
6. **Enable Debug Logs**: When troubleshooting, always use `CDE_LOG_LEVEL=DEBUG`

---

## 📚 Related Documentation

- [Configuration Guide](configuration-guide.md) - Full setup instructions
- [MCP Tools Manual](../specs/api/mcp-tools.md) - Tool reference
- [QUICKSTART_LOCAL.md](../QUICKSTART_LOCAL.md) - Local installation
- [README.md](../README.md) - Project overview

---

**Last Updated**: 2025-11-24
**Version**: 1.0.0
**Maintainer**: Nexus AI Team
