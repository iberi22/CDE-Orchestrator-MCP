#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SEMANA 2 - Launch 3 Agents in Parallel (Simple Direct Execution)

.DESCRIPTION
    Launches Gemini agent 3 times with different tasks (acting as 3 agents)
    in parallel using background jobs.
#>

$ProjectRoot = "E:\scripts-python\CDE Orchestrator MCP"
$ResultsDir = "$ProjectRoot\.cde\agent-results-semana2"

if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null
}

Write-Host "`n=================================================="  -ForegroundColor Cyan
Write-Host "🚀 SEMANA 2 - THREE-AGENT PARALLEL EXECUTION" -ForegroundColor Cyan
Write-Host "==================================================`n" -ForegroundColor Cyan

Write-Host "Project Root: $ProjectRoot"
Write-Host "Results Dir: $ResultsDir"
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"

# Define tasks for each "agent"
$tasks = @{
    "GEMINI-YAML" = @{
        "Agent" = "GEMINI (Agent 1)"
        "Task" = "Fix YAML frontmatter & status enums"
        "Files" = "35 files"
        "Instruction" = ".cde/agent-instructions/gemini-semana2-task1-metadata-yaml.md"
    }
    "CODEX-FILES" = @{
        "Agent" = "CODEX (Agent 2)"
        "Task" = "Normalize filenames & add dates"
        "Files" = "54 files"
        "Instruction" = ".cde/agent-instructions/codex-semana2-task2-filenames-dates.md"
    }
    "QWEN-DIRS" = @{
        "Agent" = "QWEN (Agent 3)"
        "Task" = "Fix directories & orphaned files"
        "Files" = "12+ files"
        "Instruction" = ".cde/agent-instructions/qwen-semana2-task3-directories.md"
    }
}

Write-Host "Tasks to Execute (Parallel):`n"
foreach ($key in $tasks.Keys) {
    $task = $tasks[$key]
    Write-Host "  $($task.Agent)"
    Write-Host "    - Task: $($task.Task)"
    Write-Host "    - Files: $($task.Files)`n"
}

# Create background jobs for each agent
$jobIds = @{}
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

foreach ($key in $tasks.Keys) {
    $task = $tasks[$key]
    $instructionFile = "$ProjectRoot\$($task.Instruction)"
    $outputFile = "$ResultsDir\$($key.ToLower())-output-$timestamp.txt"
    
    if (-not (Test-Path $instructionFile)) {
        Write-Host "❌ Instruction file not found: $instructionFile" -ForegroundColor Red
        continue
    }
    
    # Read instructions
    $instructions = Get-Content $instructionFile -Raw
    
# Create prompt for this agent
    $agentPrompt = "You are $($task.Agent). Your mission: $($task.Task) ($($task.Files)).`n`nDetailed instructions:`n`n$instructions`n`nAfter completing ALL tasks, commit with semantic message and output completion status."
    
    Write-Host "📡 Launching $($task.Agent)..." -ForegroundColor Yellow
    Write-Host "   Output: $outputFile"
    
    # Create background job
    $job = Start-Job -ScriptBlock {
        param($Agent, $Prompt, $OutputFile, $ProjectRoot)
        
        Push-Location $ProjectRoot
        
        try {
            # Call gemini CLI with prompt
            $output = & gemini "$Prompt" --approval-mode auto_edit 2>&1
            
            # Save output
            $output | Out-File $OutputFile -Encoding UTF8 -Append
            
            Write-Host "✅ $Agent completed - output saved"
            return @{ 
                Status = "COMPLETED"
                Agent = $Agent
                Output = $output
            }
        } catch {
            Write-Host "❌ $Agent failed: $_"
            $_ | Out-File $OutputFile -Encoding UTF8 -Append
            return @{
                Status = "FAILED"
                Agent = $Agent
                Error = $_.Exception.Message
            }
        } finally {
            Pop-Location
        }
    } -ArgumentList $task.Agent, $agentPrompt, $outputFile, $ProjectRoot
    
    $jobIds[$key] = @{ JobId = $job.Id; OutputFile = $outputFile; Agent = $task.Agent }
    
    Write-Host "   Job ID: $($job.Id)"
    Write-Host "   Status: QUEUED`n"
    
    Start-Sleep -Seconds 1
}

Write-Host "`n=================================================="  -ForegroundColor Yellow
Write-Host "⏳ Waiting for all agents to complete..." -ForegroundColor Yellow
Write-Host "   (This may take 30+ minutes depending on task complexity)"
Write-Host "==================================================`n"  -ForegroundColor Yellow

# Monitor jobs
$completed = 0
$failed = 0
$timeout = 3600  # 60 minutes

$startTime = Get-Date
$lastCheck = Get-Date

foreach ($key in $jobIds.Keys) {
    $jobInfo = $jobIds[$key]
    $job = Get-Job -Id $jobInfo.JobId
    
    Write-Host "📊 $($jobInfo.Agent):"
    Write-Host "   Job ID: $($jobInfo.JobId)"
    Write-Host "   Status: Waiting for completion..."
}

# Wait for all jobs with timeout
$allJobs = $jobIds.Values | ForEach-Object { Get-Job -Id $_.JobId }
$allCompleted = Wait-Job -Job $allJobs -Timeout $timeout

if ($allCompleted.Count -eq 3 -or $allCompleted.Count -eq 0) {
    foreach ($job in $allJobs) {
        if ($job.State -eq "Completed") {
            Write-Host "✅ Job $($job.Id): COMPLETED" -ForegroundColor Green
        } elseif ($job.State -eq "Failed") {
            Write-Host "❌ Job $($job.Id): FAILED" -ForegroundColor Red
        } else {
            Write-Host "⏳ Job $($job.Id): $($job.State)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "⚠️  Some jobs still running or timed out" -ForegroundColor Yellow
}

# Collect results
Write-Host "`n=================================================="  -ForegroundColor Green
Write-Host "📊 FINAL RESULTS" -ForegroundColor Green
Write-Host "==================================================`n" -ForegroundColor Green

foreach ($key in $jobIds.Keys) {
    $jobInfo = $jobIds[$key]
    $job = Get-Job -Id $jobInfo.JobId
    
    if ($job.State -eq "Completed") {
        $result = Receive-Job -Job $job
        Write-Host "✅ $($jobInfo.Agent): COMPLETED" -ForegroundColor Green
        $completed++
    } else {
        Write-Host "❌ $($jobInfo.Agent): $($job.State)" -ForegroundColor Red
        $failed++
    }
    
    Write-Host "   Output: $($jobInfo.OutputFile)`n"
}

Write-Host "📈 Summary:"
Write-Host "   Completed: $completed"
Write-Host "   Failed/Pending: $failed"
Write-Host "   Total: $($ {completed+failed})`n"

# Cleanup jobs
Remove-Job -Job $allJobs -Force

# Post-execution validation
Write-Host "=================================================="  -ForegroundColor Cyan
Write-Host "🔍 Running Governance Validation" -ForegroundColor Cyan
Write-Host "==================================================`n" -ForegroundColor Cyan

Push-Location $ProjectRoot
python scripts/validation/validate-docs.py --all 2>&1 | Select-Object -Last 15
Pop-Location

Write-Host "`n=================================================="  -ForegroundColor Yellow
Write-Host "🎯 NEXT STEPS" -ForegroundColor Yellow
Write-Host "==================================================`n" -ForegroundColor Yellow

Write-Host "1. Review output files:"
Write-Host "   ls $ResultsDir`n"
Write-Host "2. Check git status:"
Write-Host "   git status`n"
Write-Host "3. Review changes:"
Write-Host "   git diff --stat`n"
Write-Host "4. View commits:"
Write-Host "   git log --oneline -10`n"

Write-Host "=================================================="

