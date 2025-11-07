#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SEMANA 2 - Three-Agent Parallel Orchestration Script

.DESCRIPTION
    Launches Gemini, Codex, and Qwen agents in parallel headless mode
    to complete 3 independent governance remediation tasks.

.NOTES
    Location: .cde/launch-three-agents.ps1
    Author: CDE-Orchestrator-MCP
    Date: 2025-11-07
#>

param(
    [string]$ProjectRoot = "E:\scripts-python\CDE Orchestrator MCP",
    [int]$TimeoutSeconds = 1800  # 30 minutes
)

# Set working directory
Set-Location $ProjectRoot

# Define agent configurations
$agents = @{
    "GEMINI" = @{
        "TaskFile" = ".cde/agent-instructions/gemini-semana2-task1-metadata-yaml.md"
        "Priority" = "HIGH"
        "Prompt" = "You are GEMINI-AGENT-1. Your task is to fix YAML frontmatter and status enum violations in 35 documentation files. Read the instructions in the attached file and execute all 4 parts. Output: ✅ GEMINI TASK 1 COMPLETE after finishing all fixes. Then commit with: git commit -m 'fix(governance): Gemini YAML & enum fixes - 35 files' --no-verify"
    }
    "CODEX" = @{
        "TaskFile" = ".cde/agent-instructions/codex-semana2-task2-filenames-dates.md"
        "Priority" = "HIGH"
        "Prompt" = "You are CODEX-AGENT-2. Your task is to normalize filenames and add missing date fields to 54+ documentation files. Read the instructions in the attached file and execute both parts. Use 'git mv' for renames to preserve history. Output: ✅ CODEX TASK 2 COMPLETE after finishing. Then commit with: git commit -m 'fix(governance): Codex filename normalization & date fields - 54 files' --no-verify"
    }
    "QWEN" = @{
        "TaskFile" = ".cde/agent-instructions/qwen-semana2-task3-directories.md"
        "Priority" = "HIGH"
        "Prompt" = "You are QWEN-AGENT-3. Your task is to reorganize directory structure and move orphaned files in the documentation. Read the instructions in the attached file and execute all 4 parts. Use 'git mv' and 'git rm' commands. Output: ✅ QWEN TASK 3 COMPLETE after finishing. Then commit with: git commit -m 'fix(governance): Qwen reorganize directory structure & move orphaned files' --no-verify"
    }
}

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "🚀 SEMANA 2 - THREE-AGENT PARALLEL ORCHESTRATION" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "`nProject: $ProjectRoot"
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "Mode: Headless CLI (Parallel Execution)"
Write-Host "`n"

# Create results directory
$resultsDir = ".cde/agent-results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null
}

# Dictionary to track job IDs
$jobIds = @{}
$sessionFiles = @{}

# ============================================================
# PHASE 1: Launch all 3 agents in parallel
# ============================================================

Write-Host "📡 PHASE 1: Launching 3 agents in parallel..." -ForegroundColor Yellow
Write-Host "   Waiting 2 seconds between launches for stability`n"

$launchTime = Get-Date

foreach ($agentName in ("GEMINI", "CODEX", "QWEN")) {
    $taskFile = $agents[$agentName]["TaskFile"]
    $prompt = $agents[$agentName]["Prompt"]

    # Read task file content
    if (-not (Test-Path $taskFile)) {
        Write-Host "❌ Task file not found: $taskFile" -ForegroundColor Red
        continue
    }

    $taskContent = Get-Content $taskFile -Raw

    # Create combined prompt with task file
    $fullPrompt = $prompt + "`n`n--- TASK INSTRUCTIONS (from file) ---`n`n" + $taskContent

    # Session file for tracking
    $sessionFile = "$resultsDir/$($agentName.ToLower())-session-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
    $sessionFiles[$agentName] = $sessionFile

    Write-Host "🔧 $agentName Agent:" -ForegroundColor Cyan
    Write-Host "   Task: SEMANA2-$agentName"
    Write-Host "   Priority: $($agents[$agentName]['Priority'])"
    Write-Host "   Session: $sessionFile"
    Write-Host "   Status: LAUNCHING..."

    # Launch gemini CLI in background
    # Note: Using Gemini CLI with prompt
    $jobParams = @{
        ScriptBlock = {
            param($agent, $fullPrompt, $sessionFile)

            try {
                # Call gemini CLI with the full prompt
                $output = gemini "$fullPrompt" 2>&1

                # Save output to session file
                $output | Out-File $sessionFile -Encoding UTF8 -Append

                Write-Host "✅ $agent completed"
                return @{ Agent = $agent; Status = "COMPLETED"; Output = $output }
            } catch {
                $error = $_.Exception.Message
                $error | Out-File $sessionFile -Encoding UTF8 -Append
                Write-Host "❌ $agent failed: $error"
                return @{ Agent = $agent; Status = "FAILED"; Error = $error }
            }
        }
        ArgumentList = ($agentName, $fullPrompt, $sessionFile)
    }

    # Start job
    $job = Start-Job @jobParams
    $jobIds[$agentName] = $job.Id

    Write-Host "   Job ID: $($job.Id)"
    Write-Host "   Status: QUEUED`n"

    # Small delay between launches
    Start-Sleep -Seconds 2
}

# ============================================================
# PHASE 2: Monitor job progress
# ============================================================

Write-Host "⏱️  PHASE 2: Monitoring 3 jobs..." -ForegroundColor Yellow
Write-Host "   Timeout: $TimeoutSeconds seconds (30 minutes)`n"

$allJobs = $jobIds.Values | ForEach-Object { Get-Job -Id $_ }
$completedCount = 0
$monitorStart = Get-Date

while ($completedCount -lt 3) {
    # Check each job
    foreach ($agentName in ("GEMINI", "CODEX", "QWEN")) {
        $jobId = $jobIds[$agentName]
        $job = Get-Job -Id $jobId

        if ($job.State -eq "Completed") {
            if ($job.HasMoreData) {
                $result = Receive-Job -Job $job
                Write-Host "✅ $agentName (Job $jobId): COMPLETED" -ForegroundColor Green
                $completedCount++
            }
        } elseif ($job.State -eq "Failed") {
            Write-Host "❌ $agentName (Job $jobId): FAILED" -ForegroundColor Red
            $completedCount++
        }
    }

    # Check timeout
    $elapsed = (Get-Date) - $monitorStart
    if ($elapsed.TotalSeconds -gt $TimeoutSeconds) {
        Write-Host "`n⚠️  TIMEOUT reached after $($elapsed.TotalSeconds) seconds" -ForegroundColor Yellow
        break
    }

    # Wait before next check
    Start-Sleep -Seconds 5
}

# ============================================================
# PHASE 3: Collect results
# ============================================================

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "📊 RESULTS SUMMARY" -ForegroundColor Green
Write-Host "========================================================`n"

$successCount = 0
$failureCount = 0

foreach ($agentName in ("GEMINI", "CODEX", "QWEN")) {
    $jobId = $jobIds[$agentName]
    $job = Get-Job -Id $jobId
    $sessionFile = $sessionFiles[$agentName]

    $status = $job.State
    $icon = if ($status -eq "Completed") { "✅" } elseif ($status -eq "Failed") { "❌" } else { "⏸️ " }

    Write-Host "$icon $agentName        | Status: $status | Job: $jobId"

    if ($status -eq "Completed") {
        $successCount++
    } else {
        $failureCount++
    }

    if (Test-Path $sessionFile) {
        Write-Host "    Session: $sessionFile"
    }
}

Write-Host "`n📈 Total: $successCount completed, $failureCount pending/failed"
Write-Host "`n⏱️  Execution time: $(((Get-Date) - $launchTime).TotalSeconds) seconds"

# ============================================================
# PHASE 4: Post-execution validation
# ============================================================

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "🔍 PHASE 4: Post-Execution Validation" -ForegroundColor Cyan
Write-Host "========================================================`n"

Write-Host "Running governance validation..." -ForegroundColor Yellow
$validationOutput = python scripts/validation/validate-docs.py --all 2>&1 | Select-Object -Last 5
$validationOutput | ForEach-Object { Write-Host $_ }

# ============================================================
# Cleanup
# ============================================================

Write-Host "`n========================================================" -ForegroundColor Yellow
Write-Host "🧹 Cleanup" -ForegroundColor Yellow
Write-Host "========================================================`n"

# Remove background jobs
Remove-Job -Id $jobIds.Values -Force -ErrorAction SilentlyContinue

Write-Host "✅ Jobs cleaned up"
Write-Host "`n📄 Full results saved to: $resultsDir"
Write-Host "`n🎯 Next steps:"
Write-Host "   1. Review session files for any errors"
Write-Host "   2. Run: python .cde/integrate-agent-results.py"
Write-Host "   3. Verify final compliance: python scripts/validation/validate-docs.py --all"

Write-Host "`n========================================================`n"
