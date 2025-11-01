# AI Research Integration for CDE Orchestrator

> **Module**: Research automation functions
> **Purpose**: Background AI research during development
> **Usage**: Import in PowerShell profile or use directly

## PowerShell Profile Integration

Add to `$PROFILE` (run `notepad $PROFILE` to edit):

```powershell
# CDE Orchestrator: AI Research Helpers
# Location: E:\scripts-python\CDE Orchestrator MCP\.copilot\scripts\research-helpers.ps1

function cde-research {
    <#
    .SYNOPSIS
    Launch background research with Gemini CLI

    .EXAMPLE
    cde-research "async Python patterns" -Save research/async.txt

    .EXAMPLE
    cde-research "FastAPI best practices" -Name "FastAPI"
    #>
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [string]$Query,

        [string]$Name = "Research-$(Get-Date -Format 'HHmmss')",
        [string]$Model = "gemini-2.5-flash",
        [string]$Save
    )

    if ($Save) {
        Start-Job -ScriptBlock {
            param($q, $m, $file)
            $result = gemini --model=$m --yolo $q
            $result | Out-File -FilePath $file -Encoding UTF8
        } -ArgumentList $Query, $Model, $Save -Name $Name
    }
    else {
        Start-Job -ScriptBlock {
            param($q, $m)
            gemini --model=$m --yolo $q
        } -ArgumentList $Query, $Model -Name $Name
    }

    Write-Host "✓ Research '$Name' started" -ForegroundColor Green
    Write-Host "  Check status: cde-status" -ForegroundColor Gray
    Write-Host "  Get results:  cde-results $Name" -ForegroundColor Gray
}

function cde-status {
    <#
    .SYNOPSIS
    Show status of all background research jobs
    #>

    $jobs = Get-Job

    if ($jobs.Count -eq 0) {
        Write-Host "No active research jobs" -ForegroundColor Yellow
        return
    }

    Write-Host "`n=== CDE Research Status ===" -ForegroundColor Cyan
    Write-Host ""

    $stats = @{
        Running = ($jobs | Where-Object State -eq "Running").Count
        Completed = ($jobs | Where-Object State -eq "Completed").Count
        Failed = ($jobs | Where-Object State -eq "Failed").Count
    }

    Write-Host "Running:   " -NoNewline
    Write-Host $stats.Running -ForegroundColor Yellow
    Write-Host "Completed: " -NoNewline
    Write-Host $stats.Completed -ForegroundColor Green
    Write-Host "Failed:    " -NoNewline
    Write-Host $stats.Failed -ForegroundColor Red
    Write-Host ""

    $jobs | Select-Object Name, State,
        @{N='Started';E={$_.PSBeginTime.ToString('HH:mm:ss')}},
        @{N='Duration';E={
            if ($_.State -eq 'Completed') {
                ($_.PSEndTime - $_.PSBeginTime).TotalSeconds.ToString('F1') + 's'
            } else {
                ((Get-Date) - $_.PSBeginTime).TotalSeconds.ToString('F1') + 's'
            }
        }} | Format-Table -AutoSize
}

function cde-results {
    <#
    .SYNOPSIS
    Get results from a research job

    .EXAMPLE
    cde-results AsyncPatterns

    .EXAMPLE
    cde-results -All  # Get all completed jobs
    #>
    param(
        [Parameter(Position=0)]
        [string]$Name,

        [switch]$All,
        [switch]$Save
    )

    if ($All) {
        $jobs = Get-Job -State Completed
    }
    elseif ($Name) {
        $jobs = @(Get-Job -Name $Name -ErrorAction SilentlyContinue)
    }
    else {
        Write-Host "Usage: cde-results <Name> or cde-results -All" -ForegroundColor Yellow
        return
    }

    if ($jobs.Count -eq 0) {
        Write-Host "No completed jobs found" -ForegroundColor Yellow
        return
    }

    foreach ($job in $jobs) {
        Write-Host "`n=== Results: $($job.Name) ===" -ForegroundColor Cyan
        Write-Host "Status: $($job.State)" -ForegroundColor Green
        Write-Host "Duration: $(($job.PSEndTime - $job.PSBeginTime).TotalSeconds)s" -ForegroundColor Gray
        Write-Host ""

        $result = Receive-Job -Job $job -Keep
        Write-Host $result

        if ($Save) {
            $filename = "research-$($job.Name)-$(Get-Date -Format 'yyyy-MM-dd-HHmmss').txt"
            $result | Out-File $filename
            Write-Host "`nSaved to: $filename" -ForegroundColor Green
        }
    }
}

function cde-cleanup {
    <#
    .SYNOPSIS
    Remove completed research jobs
    #>
    param(
        [switch]$All
    )

    if ($All) {
        $count = (Get-Job).Count
        Get-Job | Remove-Job -Force
        Write-Host "✓ Removed $count jobs" -ForegroundColor Green
    }
    else {
        $completed = Get-Job -State Completed
        $count = $completed.Count
        $completed | Remove-Job
        Write-Host "✓ Removed $count completed jobs" -ForegroundColor Green
    }
}

function cde-research-feature {
    <#
    .SYNOPSIS
    Launch comprehensive research for a feature

    .EXAMPLE
    cde-research-feature "async repository analyzer"
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$FeatureName
    )

    $dir = ".cde/research/$(Get-Date -Format 'yyyy-MM-dd')/$FeatureName"
    New-Item -ItemType Directory -Path $dir -Force | Out-Null

    $queries = @{
        "architecture" = "Technical architecture and design patterns for: $FeatureName. Include class structure, interfaces, and key components."
        "implementation" = "Implementation best practices for: $FeatureName. Include code examples, common pitfalls, and optimization techniques."
        "testing" = "Testing strategies for: $FeatureName. Include unit tests, integration tests, and test patterns."
        "security" = "Security considerations for: $FeatureName. Include common vulnerabilities and mitigation strategies."
    }

    Write-Host "`n=== Launching Feature Research ===" -ForegroundColor Cyan
    Write-Host "Feature: $FeatureName" -ForegroundColor White
    Write-Host "Output:  $dir" -ForegroundColor Gray
    Write-Host ""

    foreach ($aspect in $queries.Keys) {
        $jobName = "$FeatureName-$aspect"
        $outFile = "$dir/$aspect.txt"

        Start-Job -ScriptBlock {
            param($q, $file)
            $result = gemini --model=gemini-2.5-flash --yolo $q
            $result | Out-File -FilePath $file -Encoding UTF8
        } -ArgumentList $queries[$aspect], $outFile -Name $jobName

        Write-Host "✓ Started: $aspect" -ForegroundColor Green
    }

    Write-Host "`nMonitor with: cde-status" -ForegroundColor Yellow
    Write-Host "Results in: $dir" -ForegroundColor Yellow
}

function cde-research-parallel {
    <#
    .SYNOPSIS
    Launch multiple research queries in parallel

    .EXAMPLE
    cde-research-parallel @("query1", "query2", "query3")
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$Queries,

        [string]$OutputDir = "research-$(Get-Date -Format 'yyyy-MM-dd-HHmmss')"
    )

    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

    Write-Host "`n=== Parallel Research ===" -ForegroundColor Cyan
    Write-Host "Queries: $($Queries.Count)" -ForegroundColor White
    Write-Host "Output:  $OutputDir" -ForegroundColor Gray
    Write-Host ""

    $i = 0
    foreach ($query in $Queries) {
        $jobName = "Research-$i"
        $outFile = "$OutputDir/research-$i.txt"

        Start-Job -ScriptBlock {
            param($q, $file)
            $result = gemini --model=gemini-2.5-flash --yolo $q
            @{
                timestamp = (Get-Date).ToString('o')
                query = $q
                result = $result
            } | ConvertTo-Json -Depth 10 | Out-File $file -Encoding UTF8
        } -ArgumentList $query, $outFile -Name $jobName

        Write-Host "✓ [$i] $(($query.Length -gt 50) ? $query.Substring(0,50) + '...' : $query)" -ForegroundColor Green
        $i++
    }

    Write-Host "`nMonitor with: cde-status" -ForegroundColor Yellow
}

# Aliases for convenience
Set-Alias -Name research -Value cde-research
Set-Alias -Name rstatus -Value cde-status
Set-Alias -Name rresults -Value cde-results
Set-Alias -Name rclean -Value cde-cleanup

Write-Host "✓ CDE Research helpers loaded" -ForegroundColor Green
Write-Host "  Commands: cde-research, cde-status, cde-results, cde-cleanup" -ForegroundColor Gray
Write-Host "  Aliases:  research, rstatus, rresults, rclean" -ForegroundColor Gray
```

## Quick Usage Guide

```powershell
# 1. Simple research
cde-research "async Python patterns"

# 2. Named research with output
cde-research "FastAPI authentication" -Name "Auth" -Save auth-research.txt

# 3. Check status
cde-status

# 4. Get results
cde-results Auth

# 5. Feature research (launches 4 parallel jobs)
cde-research-feature "async repository analyzer"

# 6. Parallel research
cde-research-parallel @(
    "Python async best practices",
    "Token estimation for LLMs",
    "Repository caching strategies"
)

# 7. Cleanup
cde-cleanup  # Remove completed
cde-cleanup -All  # Remove all
```

## Installation

### Option 1: Add to PowerShell Profile

```powershell
# 1. Open profile
notepad $PROFILE

# 2. Add this line at the end
. "E:\scripts-python\CDE Orchestrator MCP\.copilot\scripts\research-helpers.ps1"

# 3. Reload profile
. $PROFILE
```

### Option 2: Manual Import

```powershell
# Import when needed
. ".\.copilot\scripts\research-helpers.ps1"
```

## Advanced Examples

### Example 1: Onboarding System Research

```powershell
$queries = @(
    "Async repository analysis: GitIngest patterns, performance, scalability",
    "Token estimation: tiktoken usage, chunking, context optimization",
    "Project validation: health checks, quality metrics, scoring algorithms",
    "Constitution templates: tech-specific standards, team adaptation",
    "Caching strategies: SQLite vs Redis vs file-based, invalidation"
)

cde-research-parallel $queries -OutputDir "research/onboarding-system"
```

### Example 2: Watch and Auto-Save

```powershell
# Launch research
cde-research "Python async patterns" -Name "AsyncTest"

# Auto-save when complete
while ((Get-Job -Name "AsyncTest").State -eq "Running") {
    Start-Sleep -Seconds 5
}

cde-results AsyncTest -Save
```

### Example 3: Pipeline Integration

```powershell
# In your build script
& {
    Write-Host "Starting feature research..." -ForegroundColor Cyan
    cde-research-feature "user-authentication-system"

    Write-Host "Waiting for research to complete..." -ForegroundColor Yellow
    Get-Job | Wait-Job

    Write-Host "Research complete! Generating summary..." -ForegroundColor Green
    cde-results -All -Save
}
```

---

**Installation Status**: Ready to use
**Dependencies**: Gemini CLI, PowerShell 5.1+
**Full Docs**: `.copilot/skills/parallel-ai-research.md`
