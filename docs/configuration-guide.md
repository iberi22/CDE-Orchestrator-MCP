---
title: Configuration Guide - Using CDE Orchestrator in Other Projects
description: Step-by-step guide to configure CDE Orchestrator MCP server in external projects
type: guide
status: active
created: '2025-11-24'
updated: '2025-11-24'
author: Nexus AI Team
tags:
  - configuration
  - setup
  - mcp
  - vscode
llm_summary: "Complete guide for configuring CDE Orchestrator MCP server in external projects. Includes .vscode/mcp.json setup, environment variables, and troubleshooting."
---

# Configuration Guide - Using CDE Orchestrator in Other Projects

> **Target Audience**: Developers wanting to use CDE Orchestrator tools in their projects
> **Last Updated**: 2025-11-24
> **Prerequisites**: VS Code with GitHub Copilot installed

---

## 🎯 Overview

This guide shows you how to configure the **CDE Orchestrator MCP server** in any project to access all 28 AI orchestration tools including:

- ✅ `cde_setupProject` - Generate project configuration files
- ✅ `cde_onboardingProject` - Comprehensive project analysis
- ✅ `cde_generateSpec` - Generate professional Spec-Kit specifications
- ✅ `cde_syncTemplates` - Sync templates with GitHub Spec-Kit (NEW)
- ✅ `cde_validateSpec` - Validate specs against Spec-Kit standard (NEW)
- ✅ `cde_startFeature` - Start new feature workflows
- ✅ `cde_selectWorkflow` - Intelligent workflow selection
- ✅ And 21+ more tools...

---

## 📋 Step-by-Step Configuration

### Step 1: Verify CDE Orchestrator Installation

First, ensure CDE Orchestrator is installed and working:

```powershell
# Navigate to CDE Orchestrator directory
cd "E:\scripts-python\CDE Orchestrator MCP"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify server starts
$env:PYTHONPATH = "$PWD\src"
python src/server.py
```

You should see:

```text
✅ Generated 28 MCP tool files
📁 Filesystem structure: E:\scripts-python\CDE Orchestrator MCP
🚀 Server started on stdio
```

Press `Ctrl+C` to stop the server.

> **Note**: If you see "Generated 26 tool files" instead of 28, pull the latest code (cde_syncTemplates and cde_validateSpec tools were added on 2025-11-24).

---

### Step 2: Create `.vscode/mcp.json` in Your Project

Navigate to your target project and create the configuration file:

```powershell
# Navigate to your project
cd "E:\your-project"

# Create .vscode directory if it doesn't exist
if (!(Test-Path ".vscode")) { mkdir .vscode }

# Create mcp.json
New-Item -ItemType File -Path ".vscode\mcp.json" -Force
```

---

### Step 3: Configure MCP Server

Open `.vscode/mcp.json` and add this configuration:

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

**Critical Configuration Details:**

✅ **Use Absolute Paths**: Both `args` and `PYTHONPATH` must use full absolute paths

- ❌ Wrong: `"src/server.py"` or `"src"`
- ✅ Correct: `"E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py"`

✅ **Double Backslashes in JSON**: Windows paths require escaping

- ❌ Wrong: `"E:\scripts-python"`
- ✅ Correct: `"E:\\scripts-python"`

✅ **Replace Project Path**: Update `--scan-paths` with your actual project

- Example: `"E:\\your-project"` → `"E:\\projects\\my-app"`

**Why Absolute Paths?**

MCP servers run from VS Code's working directory (not your project directory), so relative paths like `src/server.py` will fail with "file not found" errors. Always use complete paths starting from the drive letter.

---

### Step 4: Verify Configuration

Reload VS Code and check if tools are available:

1. **Reload VS Code**: Press `Ctrl+Shift+P` → "Developer: Reload Window"
2. **Open GitHub Copilot Chat**: Press `Ctrl+Shift+I`
3. **Test a tool**: Ask Copilot:

```
@workspace Use cde_setupProject to analyze this project
```

Or:

```
@workspace Run cde_onboardingProject to generate project documentation
```

---

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PYTHONPATH` | Path to CDE source code | - | ✅ Yes |
| `CDE_AUTO_DISCOVER` | Enable multi-project discovery | `false` | ❌ No |
| `CDE_LOG_LEVEL` | Logging verbosity | `INFO` | ❌ No |
| `CDE_SCAN_PATHS` | Additional directories to scan | - | ❌ No |

### Command Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--scan-paths` | Directories to scan for projects | `--scan-paths E:\projects F:\code` |
| `--port` | Server port (stdio by default) | `--port 8000` |

---

## ❌ Common Configuration Mistakes

### Error: "Python cannot find server.py"

**Problem**: Using relative paths in `args`

```json
❌ WRONG:
"args": [
  "src/server.py",  // Relative path fails!
  "--scan-paths",
  "E:\\scripts-python"
]
```

**Solution**: Use absolute paths

```json
✅ CORRECT:
"args": [
  "E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py",
  "--scan-paths",
  "E:\\scripts-python"
]
```

### Error: "ModuleNotFoundError: No module named 'cde_orchestrator'"

**Problem**: `PYTHONPATH` is relative or missing

```json
❌ WRONG:
"env": {
  "PYTHONPATH": "src"  // Relative path fails!
}
```

**Solution**: Use absolute path

```json
✅ CORRECT:
"env": {
  "PYTHONPATH": "E:\\scripts-python\\CDE Orchestrator MCP\\src"
}
```

### Error: "Invalid escape sequence in JSON"

**Problem**: Single backslashes in Windows paths

```json
❌ WRONG:
"args": ["E:\scripts-python\src\server.py"]
```

**Solution**: Escape backslashes with double `\\`

```json
✅ CORRECT:
"args": ["E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py"]
```

---

## 🔍 Troubleshooting Checklist

If tools don't appear in GitHub Copilot Chat:

- [ ] **Absolute paths**: All paths start with drive letter (e.g., `E:\...`)
- [ ] **Double backslashes**: Windows paths use `\\` in JSON
- [ ] **Server running**: Check terminal shows "🚀 Server started on stdio"
- [ ] **Reloaded VS Code**: Press `Ctrl+Shift+P` → "Developer: Reload Window"
- [ ] **Virtual environment active**: CDE's `.venv` must be activated when server starts

**Still having issues?** See [Troubleshooting Guide](troubleshooting.md).

---

### Command Arguments (continued)

| Argument | Description | Example |
|----------|-------------|---------|
| `--scan-paths` | Directories to scan for projects | `--scan-paths E:\projects F:\code` |
| `--port` | Server port (stdio by default) | `--port 8000` |

---

## 📂 Directory Structure

After configuration, your project should look like this:

```
E:\your-project\
├── .vscode\
│   └── mcp.json          # ← MCP server configuration
├── src\
├── tests\
└── README.md
```

When you run `cde_setupProject`, it will create:

```
E:\your-project\
├── .vscode\
│   └── mcp.json
├── .cde\                  # ← CDE workflow configuration
│   └── workflow.yml
├── .gitignore             # ← Enhanced .gitignore
├── AGENTS.md              # ← AI agent instructions
├── specs\                 # ← Feature specifications
│   └── templates\
└── README.md
```

---

## 🚨 Common Issues & Solutions

> For comprehensive troubleshooting, see [Troubleshooting Guide](troubleshooting.md)

### Issue 1: "Tool not found" or "cde_setupProject not available"

**Cause**: MCP server not loaded or configuration incorrect

**Solution**:
1. Check `.vscode/mcp.json` exists in your project
2. Verify paths are correct (use absolute paths)
3. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
4. Check output: `Ctrl+Shift+P` → "MCP: Show Server Logs"

📖 **More details**: [Troubleshooting Guide - Problem 1](troubleshooting.md#problem-1-tool-not-found-or-cde_setupproject-not-available)

### Issue 2: "Python not found" error

**Cause**: Wrong Python path or virtual environment not activated

**Solution**:
Update `command` in `mcp.json` to use full path to Python:

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

📖 **More details**: [Troubleshooting Guide - Problem 2](troubleshooting.md#problem-2-python-not-found-or-command-failed)

### Issue 3: "ModuleNotFoundError: No module named 'cde_orchestrator'"

**Cause**: PYTHONPATH not set correctly

**Solution**:
Ensure `PYTHONPATH` points to the `src` directory:

```json
{
  "env": {
    "PYTHONPATH": "E:\\scripts-python\\CDE Orchestrator MCP\\src"
  }
}
```

📖 **More details**: [Troubleshooting Guide - Problem 3](troubleshooting.md#problem-3-modulenotfounderror-no-module-named-cde_orchestrator)

### Issue 4: Tools work in CDE project but not in other projects

**Cause**: CDE_AUTO_DISCOVER not enabled or wrong scan paths

**Solution**:
1. Add your project to `--scan-paths`:
```json
{
  "args": [
    "E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py",
    "--scan-paths",
    "E:\\your-project",
    "E:\\scripts-python"
  ]
}
```

2. Enable auto-discovery:
```json
{
  "env": {
    "CDE_AUTO_DISCOVER": "true"
  }
}
```

📖 **More details**: [Troubleshooting Guide - Problem 5](troubleshooting.md#problem-5-tools-work-in-cde-project-but-not-in-other-projects)

---

## ✅ Configuration Validation

### Automated Validation Script

Use this PowerShell script to validate your configuration automatically:

```powershell
# validate-cde-config.ps1
# Validates CDE Orchestrator MCP configuration

Write-Host "🔍 CDE Configuration Validator" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check 1: mcp.json exists
Write-Host "[1/5] Checking mcp.json..." -NoNewline
$mcpPath = ".vscode\mcp.json"
if (!(Test-Path $mcpPath)) {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      File not found: $mcpPath"
    exit 1
}
Write-Host " ✅ OK" -ForegroundColor Green

# Check 2: Valid JSON
Write-Host "[2/5] Validating JSON syntax..." -NoNewline
try {
    $config = Get-Content $mcpPath | ConvertFrom-Json
    Write-Host " ✅ OK" -ForegroundColor Green
} catch {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      Invalid JSON: $($_.Exception.Message)"
    exit 1
}

# Check 3: CDE_Orchestrator server configured
Write-Host "[3/5] Checking server configuration..." -NoNewline
if (!$config.servers.CDE_Orchestrator) {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      CDE_Orchestrator server not found"
    exit 1
}
Write-Host " ✅ OK" -ForegroundColor Green

# Check 4: Required fields present
Write-Host "[4/5] Checking required fields..." -NoNewline
$server = $config.servers.CDE_Orchestrator
if (!$server.command -or !$server.args -or !$server.env) {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      Missing required fields (command, args, or env)"
    exit 1
}
Write-Host " ✅ OK" -ForegroundColor Green

# Check 5: PYTHONPATH set
Write-Host "[5/5] Checking PYTHONPATH..." -NoNewline
if (!$server.env.PYTHONPATH) {
    Write-Host " ⚠️  WARNING" -ForegroundColor Yellow
    Write-Host "      PYTHONPATH not set"
} else {
    Write-Host " ✅ OK" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Configuration validation complete!" -ForegroundColor Green
Write-Host "   Next: Reload VS Code and test tools"
```

**Usage**:
```powershell
# Save as validate-cde-config.ps1, then run:
.\validate-cde-config.ps1
```

### Configuration Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Configuration Flow                        │
└─────────────────────────────────────────────────────────────┘

    START
      │
      ▼
┌─────────────────┐
│ 1. Verify CDE   │  ← Test: python src/server.py
│    Installation │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Create       │  ← mkdir .vscode
│    mcp.json     │  ← New-Item mcp.json
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Configure    │  ← Edit mcp.json
│    Paths        │  ← Set PYTHONPATH
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Validate     │  ← Run validate-cde-config.ps1
│    Config       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Reload       │  ← Ctrl+Shift+P → Reload Window
│    VS Code      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. Test Tools   │  ← @workspace cde_healthCheck
└────────┬────────┘
         │
         ▼
      SUCCESS ✅
```

---

## 🧪 Testing Configuration

### Test 1: Basic Tool Availability

Ask Copilot:
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

Or ask:
```
@workspace List available CDE tools
```

Expected output should include:
- cde_setupProject
- cde_onboardingProject
- cde_generateSpec (NEW)
- cde_startFeature
- cde_selectWorkflow
- ... (21+ more tools)

### Test 2: Project Setup

Ask Copilot:
```
@workspace Use cde_setupProject to set up this project
```

This should create:
- `.cde/workflow.yml`
- Enhanced `.gitignore`
- `AGENTS.md`

### Test 3: Project Analysis

Ask Copilot:
```
@workspace Run cde_onboardingProject to analyze project structure
```

This should return JSON with:
- Project structure
- Git history (if available)
- Framework detection
- Architecture patterns

---

## 📖 Available Tools Reference

### Project Setup & Analysis
- `cde_setupProject` - Generate configuration files
- `cde_onboardingProject` - Comprehensive project analysis
- `cde_publishOnboarding` - Apply onboarding documents

### Specification Generation (NEW)
- `cde_generateSpec` - Generate professional Spec-Kit feature specifications

### Workflow Management
- `cde_selectWorkflow` - Intelligent workflow selection
- `cde_startFeature` - Start new feature workflow
- `cde_submitWork` - Submit phase work

### Documentation
- `cde_scanDocumentation` - Scan documentation structure
- `cde_analyzeDocumentation` - Analyze documentation quality

### Skills & Recipes
- `cde_sourceSkill` - Download external skills
- `cde_updateSkill` - Update skill with web research
- `cde_downloadRecipes` - Download workflow recipes
- `cde_checkRecipes` - Check recipe status

### Agent Orchestration
- `cde_listAvailableAgents` - List available AI agents
- `cde_selectAgent` - Select best agent for task
- `cde_executeWithBestAgent` - Execute with optimal agent
- `cde_delegateToJules` - Delegate to Jules AI

### Advanced
- `cde_executeFullImplementation` - Full workflow execution
- `cde_healthCheck` - Server health check
- `cde_searchTools` - Search available tools
- `cde_testProgressReporting` - Test progress reporting

---

## 🔍 Debugging

### Enable Debug Logging

Update `mcp.json`:

```json
{
  "env": {
    "CDE_LOG_LEVEL": "DEBUG"
  }
}
```

### View Server Logs

1. Open Command Palette: `Ctrl+Shift+P`
2. Search: "MCP: Show Server Logs"
3. Select: "CDE_Orchestrator"

### Check Server Status

Ask Copilot:
```
@workspace Run cde_healthCheck
```

Expected output:

```json
{
  "status": "healthy",
  "python_version": "3.14.0",
  "rust_module": "loaded",
  "tools_registered": 28
}
```

> **Important**: If you see `"tools_registered": 26` or less, you need to pull latest code and reload VS Code. The newest tools (cde_syncTemplates, cde_validateSpec) were added on 2025-11-24.

---

## 🔄 Using Template Sync Tools (NEW)

### cde_syncTemplates

Keep your Spec-Kit templates synchronized with GitHub:

```
@workspace Use cde_syncTemplates to update templates
```

**What it does**:
- Downloads latest templates from github/spec-kit
- Backs up existing templates
- Applies CDE customizations (llm_summary, MCP Tools, etc.)
- Validates conformity (target: 95%+)

**Parameters**:
- `project_path`: Path to project (default: current directory)
- `force`: Overwrite without backup (default: false)
- `source`: Source to sync from (default: "github")

### cde_validateSpec

Validate generated specifications against Spec-Kit standard:

```
@workspace Use cde_validateSpec with spec_directory="specs/my-feature"
```

**What it does**:
- Validates YAML frontmatter
- Checks section structure
- Validates task format
- Detects broken links
- Calculates conformity score (0-100)

**Parameters**:
- `spec_directory`: Directory with spec.md, plan.md, tasks.md
- `project_path`: Project root (default: current directory)
- `strict`: Fail if conformity < 95% (default: false)

**Example Workflow**:

```
1. Generate spec:
   @workspace Use cde_generateSpec with feature_description="Add caching"

2. Validate spec:
   @workspace Use cde_validateSpec with spec_directory="specs/add-caching"

3. If conformity < 95%, sync templates:
   @workspace Use cde_syncTemplates

4. Regenerate spec with updated templates
```

---

## 📚 Next Steps

1. **Read Tool Documentation**: See `specs/api/mcp-tools.md`
2. **Explore Examples**: Check `specs/ai-assistant-config/` for usage patterns
3. **Join Community**: Contribute or ask questions on GitHub

---

## 💡 Pro Tips

1. **Use Full Paths**: Always use absolute paths in `mcp.json` to avoid confusion
2. **Test in CDE First**: Verify tools work in CDE project before using elsewhere
3. **Check Logs**: When in doubt, check MCP server logs
4. **Reload Often**: Reload VS Code after configuration changes
5. **Auto-Discovery**: Enable `CDE_AUTO_DISCOVER` for multi-project workflows

---

## 📞 Support

- **Documentation**: [README.md](../README.md)
- **Quick Start**: [QUICKSTART_LOCAL.md](../QUICKSTART_LOCAL.md)
- **GitHub Issues**: https://github.com/iberi22/CDE-Orchestrator-MCP/issues
- **Email**: enterprise@nexus-ai.dev

---

**Last Updated**: 2025-11-24
**Version**: 1.0.0
**License**: Fair Source 1.0
