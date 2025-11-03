#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Execute CDE Onboarding using Gemini CLI with MCP integration

.DESCRIPTION
    This script starts the MCP server and then runs the onboarding process
    using Gemini CLI. It includes progress tracking and detailed logging.

.EXAMPLE
    .\test-gemini-mcp-onboarding.ps1
#>

$ErrorActionPreference = "Stop"

# Colors for output - using System.ConsoleColor enum
$colors = @{
    "Success" = [System.ConsoleColor]::Green
    "Info"    = [System.ConsoleColor]::Cyan
    "Warning" = [System.ConsoleColor]::Yellow
    "Error"   = [System.ConsoleColor]::Red
}

function Write-Colored {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    $colorValue = switch($Color) {
        "Success" { "Green" }
        "Info"    { "Cyan" }
        "Warning" { "Yellow" }
        "Error"   { "Red" }
        default   { "White" }
    }
    Write-Host $Message -ForegroundColor $colorValue
}

Write-Colored "`n╔════════════════════════════════════════════════════╗" "Cyan"
Write-Colored "║  🚀 CDE Orchestrator MCP - Gemini CLI Integration  ║" "Cyan"
Write-Colored "╚════════════════════════════════════════════════════╝" "Cyan"

# Step 1: Verify Gemini CLI
Write-Colored "`n[1/5] Verifying Gemini CLI installation..." "Info"
try {
    $geminiVersion = (gemini --version 2>&1)
    Write-Colored "✓ Gemini CLI version: $geminiVersion" "Success"
} catch {
    Write-Colored "✗ Gemini CLI not found. Please install it:" "Error"
    Write-Colored "  npm install -g @google/gemini-cli" "Warning"
    exit 1
}

# Step 2: Verify MCP Server can start
Write-Colored "`n[2/5] Verifying MCP server (src/server.py)..." "Info"
$serverPath = "src/server.py"
if (-Not (Test-Path $serverPath)) {
    Write-Colored "✗ Server file not found: $serverPath" "Error"
    exit 1
}
Write-Colored "✓ MCP server file found" "Success"

# Step 3: Check .gemini/settings.json configuration
Write-Colored "`n[3/5] Checking Gemini configuration..." "Info"
$settingsPath = ".gemini/settings.json"
if (-Not (Test-Path $settingsPath)) {
    Write-Colored "✗ Settings not found: $settingsPath" "Error"
    exit 1
}
Write-Colored "✓ Gemini settings configured at: $settingsPath" "Success"

# Display config
$settings = Get-Content $settingsPath | ConvertFrom-Json
$serverName = $settings.mcpServers.PSObject.Properties.Name[0]
Write-Colored "  - MCP Server: $serverName" "Info"
Write-Colored "  - Model: $($settings.model)" "Info"
Write-Colored "  - Timeout: $($settings.timeout)ms" "Info"

# Step 4: Create the onboarding prompt
Write-Colored "`n[4/5] Creating onboarding prompt for Gemini CLI..." "Info"
$prompt = @"
You are analyzing the CDE Orchestrator MCP project for onboarding.

TASK: Use the cde_onboardingProject MCP tool to analyze this project and generate comprehensive onboarding documentation.

STEPS:
1. Call the cde_onboardingProject tool to analyze the current project structure
2. Review the output including:
   - Project analysis (commits, tech stack, structure)
   - Missing Spec-Kit elements
   - AI assistants detected
   - Onboarding plan

3. Generate a summary with:
   - Current state assessment
   - Key findings
   - Onboarding recommendations
   - Next steps for the project owner

Use the tool output to provide a detailed, actionable onboarding report.
"@

Write-Colored "✓ Prompt created successfully" "Success"

# Step 5: Execute Gemini CLI with MCP
Write-Colored "`n[5/5] Launching Gemini CLI with MCP tools..." "Info"
Write-Colored "━" -ForegroundColor Cyan
Write-Colored "`nGemini CLI will now:
  1. Connect to the CDE Orchestrator MCP server
  2. Discover available tools (cde_onboardingProject, etc.)
  3. Execute the onboarding analysis
  4. Generate a comprehensive report

Press Enter to continue or Ctrl+C to cancel...`n" "Info"
Read-Host

# Execute gemini with the prompt
# Using -o, --output-format stream-json for real-time streaming
Write-Colored "`n🔗 Starting Gemini CLI with MCP integration...\n" "Cyan"

try {
    # Change to project root directory
    $projectRoot = Get-Location
    Write-Colored "Working directory: $projectRoot" "Info"

    # Run gemini with non-interactive mode and streaming output
    gemini -p "$prompt" --output-format stream-json

    Write-Colored "`n━" -ForegroundColor Cyan
    Write-Colored "`n✅ Gemini CLI execution completed successfully!" "Success"
} catch {
    Write-Colored "`n✗ Error executing Gemini CLI:" "Error"
    Write-Colored $_.Exception.Message "Error"
    exit 1
}

# Step 6: Summary
Write-Colored "`n╔════════════════════════════════════════════════════╗" "Cyan"
Write-Colored "║  ✅ Onboarding Process Complete!                   ║" "Cyan"
Write-Colored "╚════════════════════════════════════════════════════╝" "Cyan"

Write-Colored "`nWhat was accomplished:
  ✓ Gemini CLI connected to MCP server
  ✓ Discovered CDE tools (cde_onboardingProject, etc.)
  ✓ Analyzed project structure
  ✓ Generated onboarding recommendations
  ✓ Provided detailed feedback and next steps

Next steps:
  1. Review the Gemini output above for recommendations
  2. Implement suggested improvements
  3. Run again if you make structural changes

For more details, see:
  - Documentation: .gemini/settings.json (Gemini CLI config)
  - Results: agent-docs/feedback/ (Generated feedback)
  - Logs: Check stdout above for detailed analysis

Thank you for using CDE Orchestrator MCP! 🚀
" "Success"
