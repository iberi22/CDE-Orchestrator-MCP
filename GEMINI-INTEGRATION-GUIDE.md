---
title: "Gemini CLI + MCP Integration Setup Guide"
description: "Complete setup and testing guide for CDE Orchestrator MCP with Gemini CLI"
type: guide
status: active
created: "2025-11-02"
updated: "2025-11-02"
author: "AI Agent"
tags:
  - gemini-cli
  - mcp
  - integration
  - setup
  - onboarding
llm_summary: |
  Complete guide to integrate CDE Orchestrator MCP server with Gemini CLI.
  Includes configuration setup, tool discovery, and onboarding process execution.
---

# Gemini CLI + MCP Integration Setup & Testing

**Date**: 2025-11-02
**Status**: ✅ Ready for Testing
**Gemini CLI Version**: 0.11.3+

---

## 🎯 Overview

This guide explains how to integrate the **CDE Orchestrator MCP server** with **Gemini CLI** to enable AI-powered onboarding analysis using native MCP tool support.

### What is Gemini CLI?

Gemini CLI is an open-source AI agent that brings Google's Gemini model directly to the terminal. It supports:
- **Native MCP integration** - Connect custom MCP servers for extended functionality
- **Streaming responses** - Real-time output with progress tracking
- **Tool discovery** - Automatic detection and execution of MCP tools
- **Multi-model support** - Gemini 2.5 Pro with 1M token context window
- **Free tier** - 60 requests/min, 1,000 requests/day with Google account

---

## 📋 Prerequisites

### Required Software

- ✅ **Gemini CLI** v0.11.3+ (`npm install -g @google/gemini-cli`)
- ✅ **Python** 3.8+ (for MCP server)
- ✅ **Git** (for repository analysis)
- ✅ **Node.js** 20+ (for Gemini CLI)

### Required Configuration

- ✅ **Google Account** (for OAuth login or API key)
- ✅ **Gemini API Key** (or use OAuth login)

### Verify Installation

```bash
# Check Gemini CLI
gemini --version  # Should show v0.11.3 or higher

# Check Python
python --version  # Should show Python 3.8+

# Check Node.js
node --version    # Should show v20+
```

---

## 🔧 Configuration Setup

### Step 1: Create `.gemini/settings.json`

**Location**: `e:\scripts-python\CDE Orchestrator MCP\.gemini\settings.json`

**Configuration**:

```json
{
  "model": "gemini-2.5-pro",
  "temperature": 0.7,
  "timeout": 600000,
  "mcpServers": {
    "cde-orchestrator": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": ".",
      "env": {
        "CDE_LOG_LEVEL": "INFO"
      },
      "timeout": 30000,
      "trust": false,
      "includeTools": [
        "cde_onboardingProject",
        "cde_scanDocumentation",
        "cde_analyzeDocumentation",
        "cde_selectWorkflow"
      ]
    }
  },
  "mcp": {
    "allowed": ["cde-orchestrator"]
  }
}
```

### Configuration Options Explained

| Property | Value | Purpose |
|----------|-------|---------|
| `model` | `gemini-2.5-pro` | Use latest Gemini model |
| `temperature` | `0.7` | Balance creativity and precision |
| `timeout` | `600000` | 10 minute timeout for long operations |
| `command` | `python` | MCP server executable |
| `args` | `["src/server.py"]` | Server startup arguments |
| `cwd` | `.` | Working directory (project root) |
| `timeout` | `30000` | 30 second timeout per tool call |
| `trust` | `false` | Require user confirmation for tools |
| `includeTools` | `[...]` | Whitelist specific tools |

### Step 2: Authenticate with Gemini CLI

```bash
# Option 1: OAuth Login (Recommended)
gemini

# Option 2: API Key
export GEMINI_API_KEY="your-key-from-aistudio.google.com"
gemini
```

---

## 🚀 Discovery Process

### What Happens When Gemini CLI Starts

1. **Server Connection**
   - Gemini CLI reads `.gemini/settings.json`
   - Spawns MCP server process: `python src/server.py`
   - Establishes stdio connection

2. **Tool Discovery**
   - Queries MCP server for available tools
   - Receives tool definitions with schemas
   - Validates compatibility with Gemini API
   - Filters by `includeTools` list

3. **Tool Registration**
   - 4 tools become available to Gemini model:
     - `cde_onboardingProject` - Analyze and setup project
     - `cde_scanDocumentation` - Audit doc structure
     - `cde_analyzeDocumentation` - Check quality/links
     - `cde_selectWorkflow` - Route to optimal workflow

4. **Ready for Queries**
   - Model can now use tools in responses
   - User confirmations required before execution

### Verify Discovery

```bash
gemini

# Inside Gemini CLI, type:
/mcp

# Output shows:
# 📡 cde-orchestrator (CONNECTED)
#   Command: python src/server.py
#   Tools: cde_onboardingProject, cde_scanDocumentation, ...
```

---

## 🎬 Running Onboarding with Gemini CLI

### Method 1: Interactive Mode

```bash
cd "e:\scripts-python\CDE Orchestrator MCP"

# Start Gemini CLI
gemini

# Type your prompt:
> Please analyze this project structure using cde_onboardingProject and tell me what's missing

# Gemini will:
# 1. Read your request
# 2. Decide to use cde_onboardingProject tool
# 3. Ask for confirmation (tool=false)
# 4. Execute the tool
# 5. Show results and recommendations
```

### Method 2: Non-Interactive (Scripted)

```bash
gemini -p "Analyze this project using cde_onboardingProject and provide onboarding recommendations"
```

### Method 3: Streaming Output (Real-time)

```bash
gemini -p "Run the onboarding analysis" --output-format stream-json
```

---

## 📊 Expected Output Example

### Tool Execution Flow

```
You:
> Run the cde_onboardingProject tool to analyze this project

Gemini:
I'll analyze your project structure using the CDE Orchestrator's onboarding tool...

[Tool Call Confirmation]
✓ Allow this tool call? (cde_onboardingProject)
  [Y]es [N]o [A]lways [C]ancel: Y

[Executing Tool...]
🚀 CDE Onboarding Analysis Started
📁 Scanning project structure...
📊 Analysis: 342 commits, 5 missing items
📝 Generating onboarding plan...
🤖 Detecting AI assistants...
✨ Detected: Cursor, GitHub Copilot
📄 Preparing onboarding prompt...
✅ Onboarding draft ready!

[Tool Results]
{
  "status": "success",
  "project_name": "CDE Orchestrator MCP",
  "analysis": {
    "commits": 342,
    "branches": 1,
    "tech_stack": ["Python", "FastMCP", "MCP"],
    "missing_structure": [...]
  },
  "plan": {...},
  ...
}

Gemini Analysis:
Based on the onboarding analysis, here are my findings:

**Current State:**
- Mature project with 342 commits
- Using FastMCP framework for Model Context Protocol
- Missing 5 spec-kit compliance items

**Recommendations:**
1. Add GOVERNANCE.md to specs/governance/
2. Create issue templates in .github/
3. Document testing strategy in specs/
...
```

---

## 🔍 Tool Discovery Details

### Available Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `cde_onboardingProject` | Analyze project for setup | `{}` (empty) | Full project analysis + plan |
| `cde_scanDocumentation` | Audit doc structure | Project path | Missing metadata, orphaned files |
| `cde_analyzeDocumentation` | Check quality | Project path | Broken links, score, issues |
| `cde_selectWorkflow` | Route to workflow | Prompt string | Workflow type + recipe |

### Tool Parameters

**cde_onboardingProject**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```
(No parameters - uses current project directory)

**cde_selectWorkflow**
```json
{
  "type": "object",
  "properties": {
    "user_prompt": {
      "type": "string",
      "description": "Natural language description of the task"
    }
  },
  "required": ["user_prompt"]
}
```

---

## 🛠️ Testing Script

A PowerShell script is provided to automate the setup and execution:

**File**: `test-gemini-mcp-onboarding.ps1`

**Usage**:
```bash
.\test-gemini-mcp-onboarding.ps1
```

**What it does**:
1. ✓ Verifies Gemini CLI installation
2. ✓ Checks MCP server file exists
3. ✓ Validates Gemini configuration
4. ✓ Displays configuration summary
5. ✓ Prompts user to begin
6. ✓ Executes Gemini CLI with onboarding prompt
7. ✓ Shows results and next steps

---

## 🔐 Security Considerations

### Trust Settings

**`"trust": false`** (Default - Recommended)
- Requires user confirmation before each tool execution
- Safer for shared environments
- Slightly slower due to prompts

**`"trust": true`** (Use with caution!)
- Bypasses all confirmation dialogs
- Faster execution
- Only use for servers you completely control

### Environment Variables

```json
"env": {
  "CDE_LOG_LEVEL": "INFO",
  "API_KEY": "$MY_SECRET_KEY"
}
```

The `$` prefix allows referencing system environment variables:
```bash
export MY_SECRET_KEY="your-secret-key"
gemini  # Will use the secret
```

---

## 🐛 Troubleshooting

### Issue: "Server won't connect"

**Symptoms**: `cde-orchestrator (DISCONNECTED)`

**Solutions**:
1. Check MCP server file: `src/server.py` exists
2. Verify Python: `python --version` (3.8+)
3. Test manually: `python src/server.py` (should start without error)
4. Check logs: Look for error messages in Gemini CLI output
5. Verify CWD: Make sure you're in the project root

### Issue: "No tools discovered"

**Symptoms**: Server connects but shows no tools

**Solutions**:
1. Verify tool names in `includeTools` match actual tool names
2. Check server logs for tool registration errors
3. Run `gemini /mcp` to see discovery state
4. Test MCP server independently: `python test_progress_tracking.py`

### Issue: "Tool execution times out"

**Symptoms**: Tool starts but hangs for 30 seconds then fails

**Solutions**:
1. Increase timeout in settings: `"timeout": 60000` (60 seconds)
2. Check if Git analysis is slow (large repos)
3. Monitor server logs for performance issues
4. Try with smaller project first to isolate issue

### Issue: "Authentication failed"

**Symptoms**: OAuth redirect doesn't work or API key rejected

**Solutions**:
1. **OAuth**: Make sure browser can access `http://localhost:7777/oauth/callback`
2. **API Key**: Verify key from [aistudio.google.com](https://aistudio.google.com/apikey)
3. **Quota**: Check free tier limits (60 req/min, 1000 req/day)
4. **Permissions**: Ensure account has Gemini API access

---

## 📚 Advanced Configuration

### Multiple MCP Servers

```json
{
  "mcpServers": {
    "cde-orchestrator": {
      "command": "python",
      "args": ["src/server.py"],
      "timeout": 30000
    },
    "github-tools": {
      "url": "https://api.github.com/mcp",
      "timeout": 10000
    },
    "database-tools": {
      "command": "node",
      "args": ["db-mcp.js"],
      "env": {
        "DB_URL": "$DATABASE_URL"
      }
    }
  }
}
```

### Tool Filtering

```json
{
  "cde-orchestrator": {
    "command": "python",
    "args": ["src/server.py"],
    "includeTools": ["cde_onboardingProject"],
    "excludeTools": []
  }
}
```

### Custom Timeouts

```json
{
  "cde-orchestrator": {
    "command": "python",
    "args": ["src/server.py"],
    "timeout": 60000  // 60 seconds for long operations
  }
}
```

---

## 📖 Quick Reference

### Starting Gemini CLI

```bash
# Interactive mode
gemini

# Non-interactive
gemini -p "Your prompt here"

# With streaming output
gemini -p "Your prompt" --output-format stream-json

# Specify model
gemini -m gemini-2.5-flash
```

### Gemini CLI Commands

```bash
# Inside gemini prompt:
/mcp              # Show MCP server status
/mcp auth         # Manage OAuth tokens
/help             # Show all commands
/exit or /quit    # Exit Gemini CLI
```

### Debugging

```bash
# Enable debug logging
gemini --debug

# Check configuration
cat .gemini/settings.json

# List discovered tools
gemini
/mcp
```

---

## 🎓 Learning Resources

- **Gemini CLI Docs**: https://github.com/google-gemini/gemini-cli/blob/main/docs/
- **MCP Docs**: https://modelcontextprotocol.io/
- **Gemini API**: https://ai.google.dev/docs/gemini_api

---

## ✅ Verification Checklist

Before running onboarding:

- [ ] Gemini CLI installed (`gemini --version`)
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Google account created or API key obtained
- [ ] `.gemini/settings.json` configured
- [ ] `src/server.py` exists
- [ ] Project is a Git repository
- [ ] Network connectivity available

---

## 🚀 Next Steps

1. **Test Discovery**
   ```bash
   gemini
   /mcp  # Verify server connects
   /exit
   ```

2. **Run Onboarding**
   ```bash
   gemini -p "Analyze this project using cde_onboardingProject and provide recommendations"
   ```

3. **Review Output**
   - Check AI recommendations
   - Review analysis results
   - Note suggested improvements

4. **Implement Changes**
   - Follow recommendations
   - Create missing documentation
   - Update structure as needed

5. **Re-run if Needed**
   - After making changes
   - Gemini will confirm all is well

---

## 📞 Support

For issues or questions:

1. **Check troubleshooting section** above
2. **Review Gemini CLI docs**: https://github.com/google-gemini/gemini-cli
3. **Check MCP spec**: https://modelcontextprotocol.io/
4. **Open GitHub issue**: Create issue in CDE Orchestrator MCP repo

---

**Status**: ✅ **Ready to Use**
**Last Updated**: 2025-11-02
**Tested With**: Gemini CLI v0.11.3, Python 3.11, Git 2.45

**Created by**: AI Agent
**For**: CDE Orchestrator MCP Project
