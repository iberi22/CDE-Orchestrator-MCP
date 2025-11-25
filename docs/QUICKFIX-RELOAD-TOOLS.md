---
title: Quick Fix - Tool Not Found (cde_generateSpec)
description: 30-second fix for "tool not found" errors
type: quickfix
status: active
created: '2025-11-24'
updated: '2025-11-24'
author: Nexus AI Team
tags:
  - quickfix
  - reload
  - troubleshooting
llm_summary: "30-second fix for tool discovery issues - just reload VS Code"
---

# Quick Fix - Tool Not Found

> **Problem**: "cde_generateSpec no existe" or "tool not found"
> **Solution Time**: 30 seconds
> **Success Rate**: 95%

---

## 🚀 The Fix (30 seconds)

### Step 1: Reload VS Code (15 seconds)

1. Press `Ctrl + Shift + P`
2. Type: **"Developer: Reload Window"**
3. Press `Enter`
4. Wait 10-15 seconds

### Step 2: Verify (15 seconds)

Open GitHub Copilot Chat and type:

```text
@workspace Use cde_healthCheck
```

**Expected result**:

```json
{
  "status": "healthy",
  "tools_registered": 26
}
```

✅ **If you see 26 tools**: Fixed! Try using `cde_generateSpec` now.

❌ **If you see 22 or less tools**: Continue to advanced fix below.

---

## 🔧 Advanced Fix (If reload didn't work)

### Check 1: Verify you're in the right project

The tool works in **CDE Orchestrator project**, but your external project needs proper configuration.

**For external projects**, ensure `.vscode/mcp.json` exists:

```powershell
# Check if mcp.json exists
Test-Path ".vscode\mcp.json"
```

If it returns `False`, create it:

```powershell
mkdir .vscode -Force
New-Item -ItemType File -Path ".vscode\mcp.json" -Force
```

Then add this content:

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": [
        "E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py",
        "--scan-paths",
        "E:\\your-project"
      ],
      "env": {
        "PYTHONPATH": "E:\\scripts-python\\CDE Orchestrator MCP\\src",
        "CDE_AUTO_DISCOVER": "true",
        "CDE_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important**: Replace `E:\\your-project` with your actual project path.

Then **reload VS Code again** (Ctrl+Shift+P → Reload Window).

---

### Check 2: Verify server is running

If still not working, test the server manually:

```powershell
cd "E:\scripts-python\CDE Orchestrator MCP"
$env:PYTHONPATH = "src"
python src/server.py
```

Press `Ctrl+C` after 5 seconds.

**Look for**:

```text
✅ Generated 26 MCP tool files
```

If you see **22** instead of **26**, the tool isn't registered. Run:

```powershell
git pull origin main
```

Then reload VS Code.

---

## 📊 Diagnostic Commands

Run these to check your configuration:

```powershell
# Check tool is registered
Select-String -Path "E:\scripts-python\CDE Orchestrator MCP\src\server.py" -Pattern "cde_generateSpec"

# Check tool is exported
Select-String -Path "E:\scripts-python\CDE Orchestrator MCP\src\mcp_tools\__init__.py" -Pattern "cde_generateSpec"

# Check implementation exists
Test-Path "E:\scripts-python\CDE Orchestrator MCP\src\mcp_tools\spec_generator.py"
```

All should return positive results.

---

## ✅ Success Checklist

- [ ] Reloaded VS Code (Ctrl+Shift+P → Reload Window)
- [ ] `cde_healthCheck` shows 26 tools registered
- [ ] `.vscode/mcp.json` exists in your project (for external projects)
- [ ] Absolute paths used in mcp.json configuration

---

## 📖 More Help

- **Full Troubleshooting**: [troubleshooting-cde-generatespec.md](troubleshooting-cde-generatespec.md)
- **Configuration Guide**: [configuration-guide.md](configuration-guide.md)
- **Tool Documentation**: [tool-cde-generatespec.md](tool-cde-generatespec.md)

---

**TL;DR**: Press `Ctrl+Shift+P`, type "Reload Window", wait 15 seconds. Done. ✅
