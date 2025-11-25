---
title: Troubleshooting cde_generateSpec Tool Discovery
description: How to fix "tool not found" issues for cde_generateSpec
type: troubleshooting
status: active
created: '2025-11-24'
updated: '2025-11-24'
author: Nexus AI Team
tags:
  - troubleshooting
  - cde_generateSpec
  - mcp
  - tool-discovery
llm_summary: "Complete troubleshooting guide for cde_generateSpec tool discovery issues in external projects."
---

# Troubleshooting cde_generateSpec Tool Discovery

> **Problem**: Agent says "cde_generateSpec not found" or "tool not available"
> **Last Updated**: 2025-11-24
> **Applies to**: CDE Orchestrator MCP v1.0+

---

## 🚨 Quick Fix (90% of cases)

### Step 1: Reload VS Code

The most common issue is that VS Code hasn't reloaded the MCP server after the tool was added.

**Solution**:
```
1. Press Ctrl+Shift+P
2. Type "Developer: Reload Window"
3. Press Enter
4. Wait 10-15 seconds for MCP server to restart
```

### Step 2: Verify Server Restart

Open GitHub Copilot Chat and ask:
```
@workspace Use cde_healthCheck to verify server status
```

Expected output should include:
```json
{
  "status": "healthy",
  "tools_registered": 26
}
```

If `tools_registered` is **less than 26**, continue to Step 3.

---

## 🔍 Detailed Diagnosis

### Check 1: Verify Tool is Registered in Server

<function_calls>
<invoke name="run_in_terminal">
<parameter name="command">cd "e:\scripts-python\CDE Orchestrator MCP"; Select-String -Path "src\server.py" -Pattern "cde_generateSpec"
