#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Demo del sistema de onboarding con AI Assistant Configuration

.DESCRIPTION
    Script de demostración que muestra cómo funciona el onboarding
    de CDE Orchestrator MCP en nuestro propio proyecto.

.EXAMPLE
    .\demo_onboarding.ps1
#>

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Section {
    param([string]$Title)
    Write-Host "`n$('=' * 80)" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "$('=' * 80)`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "  • $Message" -ForegroundColor White
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  ⚠ $Message" -ForegroundColor Yellow
}

function Write-Error2 {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor Red
}

# Project root
$ProjectRoot = $PSScriptRoot
Write-Section "🚀 CDE Orchestrator MCP - Onboarding Demo"
Write-Info "Project Root: $ProjectRoot"

# Step 1: Check Project Structure
Write-Section "📊 Step 1: Analyzing Project Structure"

$RequiredDirs = @(
    "specs",
    "specs/features",
    "specs/api",
    "specs/design",
    "specs/reviews",
    "memory"
)

$RequiredFiles = @(
    "specs/README.md",
    "memory/constitution.md"
)

Write-Info "Checking Spec-Kit structure..."
$ExistingDirs = @()
$MissingDirs = @()

foreach ($dir in $RequiredDirs) {
    $path = Join-Path $ProjectRoot $dir
    if (Test-Path $path) {
        $ExistingDirs += $dir
        Write-Success "$dir/"
    } else {
        $MissingDirs += $dir
        Write-Error2 "$dir/ (missing)"
    }
}

Write-Info "`nChecking required files..."
$ExistingFiles = @()
$MissingFiles = @()

foreach ($file in $RequiredFiles) {
    $path = Join-Path $ProjectRoot $file
    if (Test-Path $path) {
        $ExistingFiles += $file
        Write-Success $file
    } else {
        $MissingFiles += $file
        Write-Error2 "$file (missing)"
    }
}

$NeedsOnboarding = ($MissingDirs.Count -gt 0) -or ($MissingFiles.Count -gt 0)

# Step 2: Analyze Git History
Write-Section "🔍 Step 2: Analyzing Git History"

if (Test-Path (Join-Path $ProjectRoot ".git")) {
    Write-Success "Git repository detected"

    try {
        # Get commit count
        $CommitCount = (git rev-list --count HEAD 2>$null)
        Write-Info "Total Commits: $CommitCount"

        # Get branch count
        $Branches = (git branch -a --format="%(refname:short)" 2>$null)
        $BranchCount = ($Branches | Measure-Object).Count
        Write-Info "Branches: $BranchCount"

        # Get project age
        $FirstCommitDate = (git log --reverse --pretty=%ad --date=short 2>$null | Select-Object -First 1)
        if ($FirstCommitDate) {
            $Age = (New-TimeSpan -Start $FirstCommitDate -End (Get-Date)).Days
            Write-Info "Project Age: $Age days (since $FirstCommitDate)"
        }

        # Get recent commits
        Write-Info "`nRecent Commits (last 3):"
        git log --pretty=format:"    • %h - %s%n      by %an on %ad" --date=short -n 3 2>$null

    } catch {
        Write-Warning "Could not analyze Git history: $_"
    }
} else {
    Write-Warning "Not a Git repository"
}

# Step 3: Detect AI Assistants
Write-Section "🤖 Step 3: Detecting AI Assistants"

$AIAssistants = @{
    "copilot" = @{
        Name = "GitHub Copilot"
        Folder = ".github/"
        CheckType = "folder"
        Files = @("copilot-instructions.md", "AGENTS.md")
    }
    "gemini" = @{
        Name = "Gemini CLI"
        Folder = ".gemini/"
        CheckType = "cli"
        CLI = "gemini"
        Files = @("GEMINI.md", "AGENTS.md")
    }
    "claude" = @{
        Name = "Claude Code"
        Folder = ".claude/"
        CheckType = "cli"
        CLI = "claude"
        Files = @("AGENTS.md")
    }
    "cursor" = @{
        Name = "Cursor"
        Folder = ".cursor/"
        CheckType = "folder"
        Files = @("AGENTS.md")
    }
    "windsurf" = @{
        Name = "Windsurf"
        Folder = ".windsurf/"
        CheckType = "folder"
        Files = @("AGENTS.md")
    }
    "amp" = @{
        Name = "Amp"
        Folder = ".agents/"
        CheckType = "cli"
        CLI = "amp"
        Files = @("AGENTS.md")
    }
}

$DetectedAgents = @()
$ConfiguredAgents = @()

Write-Info "Detecting installed AI tools..."

foreach ($key in $AIAssistants.Keys) {
    $agent = $AIAssistants[$key]
    $detected = $false
    $configured = $false

    # Check if CLI tool is available
    if ($agent.CheckType -eq "cli") {
        try {
            $null = Get-Command $agent.CLI -ErrorAction SilentlyContinue
            if ($?) {
                $detected = $true
                $DetectedAgents += $key
            }
        } catch {
            # CLI not found
        }
    }

    # Check if folder exists
    $folderPath = Join-Path $ProjectRoot $agent.Folder
    if (Test-Path $folderPath) {
        $detected = $true
        $configured = $true
        if ($key -notin $DetectedAgents) {
            $DetectedAgents += $key
        }
        $ConfiguredAgents += $key
    }

    # Check if root-level files exist
    foreach ($file in $agent.Files) {
        if ($file -in @("AGENTS.md", "GEMINI.md")) {
            $filePath = Join-Path $ProjectRoot $file
            if (Test-Path $filePath) {
                $configured = $true
                if ($key -notin $ConfiguredAgents) {
                    $ConfiguredAgents += $key
                }
            }
        }
    }

    if ($detected) {
        Write-Success "$($agent.Name) - 🔍 Detected"
    }
}

if ($DetectedAgents.Count -eq 0) {
    Write-Warning "No AI assistants detected via CLI"
    Write-Info "Will configure defaults: GitHub Copilot + AGENTS.md"
}

# Step 4: Check Existing AI Config Files
Write-Section "📂 Step 4: Checking AI Configuration Files"

$ConfigFiles = @(
    @{ Path = "AGENTS.md"; Type = "File" },
    @{ Path = "GEMINI.md"; Type = "File" },
    @{ Path = ".github/copilot-instructions.md"; Type = "File" },
    @{ Path = ".claude/"; Type = "Folder" },
    @{ Path = ".cursor/"; Type = "Folder" },
    @{ Path = ".windsurf/"; Type = "Folder" },
    @{ Path = ".gemini/"; Type = "Folder" }
)

Write-Info "AI Assistant Configuration Files:"

foreach ($item in $ConfigFiles) {
    $fullPath = Join-Path $ProjectRoot $item.Path
    $exists = Test-Path $fullPath

    if ($exists) {
        if ($item.Type -eq "File") {
            $size = (Get-Item $fullPath).Length
            Write-Success "📄 $($item.Path) ($([math]::Round($size/1KB, 1)) KB)"
        } else {
            Write-Success "📁 $($item.Path)"
        }
    } else {
        Write-Error2 "$($item.Path) (missing)"
    }
}

# Step 5: Summary
Write-Section "📋 Step 5: Configuration Summary"

Write-Info "AI Assistants Summary:"
Write-Info "  Total Supported: $($AIAssistants.Count)"
Write-Info "  Detected on System: $($DetectedAgents.Count)"
Write-Info "  Already Configured: $($ConfiguredAgents.Count)"

Write-Info "`nAvailable AI Assistants:"
foreach ($key in $AIAssistants.Keys) {
    $agent = $AIAssistants[$key]
    $status = if ($key -in $ConfiguredAgents) { "✓ Configured" } else { "○ Available" }
    $detectedMark = if ($key -in $DetectedAgents) { "🔍" } else { " " }
    Write-Host "  $detectedMark $status $($agent.Name)" -ForegroundColor $(if ($key -in $ConfiguredAgents) { "Green" } else { "Gray" })
}

# Step 6: Recommendations
Write-Section "🎯 Step 6: Onboarding Recommendations"

if ($NeedsOnboarding) {
    Write-Warning "Onboarding needed - Missing Spec-Kit structure"
    Write-Info "`nWould create:"
    foreach ($dir in $MissingDirs) {
        Write-Info "  📁 $dir/"
    }
    foreach ($file in $MissingFiles) {
        Write-Info "  📄 $file"
    }
} else {
    Write-Success "Project has complete Spec-Kit structure"
}

Write-Info "`nAI Assistant Configuration:"
if ($ConfiguredAgents.Count -eq 0) {
    Write-Warning "No AI assistant configuration files found"
    Write-Info "Would generate:"
    Write-Info "  📄 AGENTS.md (OpenAI standard, universal)"
    Write-Info "  📄 GEMINI.md (Google AI Studio optimized)"
    Write-Info "  📄 .github/copilot-instructions.md (GitHub Copilot)"
} else {
    Write-Success "Found $($ConfiguredAgents.Count) AI assistant configuration(s)"
}

# Final Summary
Write-Section "✨ Demo Complete!"

Write-Host "`nProject Status:" -ForegroundColor Cyan
Write-Info "Structure: $(if (-not $NeedsOnboarding) { '✓ Complete' } else { '⚠ Needs Setup' })"
Write-Info "Git Repo: $(if (Test-Path (Join-Path $ProjectRoot '.git')) { '✓ Initialized' } else { '✗ Not initialized' })"
Write-Info "AI Detected: $($DetectedAgents.Count)"
Write-Info "AI Configured: $($ConfiguredAgents.Count)"

Write-Host "`nThis demo showed:" -ForegroundColor Cyan
Write-Success "Project structure analysis"
Write-Success "Git history analysis"
Write-Success "AI assistant auto-detection"
Write-Success "Configuration file management"
Write-Success "Spec-Kit compatibility"

Write-Host "`nTo actually run onboarding:" -ForegroundColor Yellow
Write-Host "  Use the MCP tool: cde_onboardingProject()" -ForegroundColor White
Write-Host "`n"
