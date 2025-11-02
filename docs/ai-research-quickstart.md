---
title: 'Quick Start: AI Research Automation'
description: '```powershell $dir = "research-$(Get-Date -Format ''yyyy-MM-dd-HHmmss'')"'
type: guide
status: draft
created: '2025-11-02'
updated: '2025-11-02'
author: Auto-Generated
tags:
- ai
- api
- architecture
- authentication
- documentation
- performance
llm_summary: "User guide for Quick Start: AI Research Automation.\n  > **For**: CDE\
  \ Orchestrator Team > **Purpose**: Execute parallel research while continuing development\
  \ > **Last Updated**: 2025-10-31 Add these to your PowerShell profile (`$PROFILE`):\
  \ **Skill Location**: `.copilot/skills/parallel-ai-research.md`\n  Reference when\
  \ working with guide documentation."
---

# Quick Start: AI Research Automation

> **For**: CDE Orchestrator Team
> **Purpose**: Execute parallel research while continuing development
> **Last Updated**: 2025-10-31

---

## ⚡ Quick Commands

### Single Background Research

```powershell
# Start research
Start-Job -ScriptBlock {
    gemini --model=gemini-2.5-flash --yolo "your research query"
} -Name "MyResearch"

# Check status
Get-Job

# Get results (when State = Completed)
Receive-Job -Name "MyResearch"

# Cleanup
Remove-Job -Name "MyResearch"
```

### Multiple Parallel Investigations

```powershell
# Launch 3 research tasks simultaneously
$queries = @(
    "Best practices for async Python repository scanning",
    "Token estimation strategies for LLM context windows",
    "Caching patterns for expensive computations"
)

$i = 0
foreach ($q in $queries) {
    Start-Job -ScriptBlock {
        gemini --model=gemini-2.5-flash --yolo $args[0]
    } -ArgumentList $q -Name "Research$i"
    $i++
}

# Monitor progress
Get-Job | Format-Table

# Wait for all
Get-Job | Wait-Job

# Collect all results
Get-Job | Receive-Job -Keep

# Cleanup
Get-Job | Remove-Job
```

### Save Results to Files

```powershell
# Research with output capture
Start-Job -ScriptBlock {
    $result = gemini --model=gemini-2.5-flash --yolo $args[0]
    $result | Out-File -FilePath $args[1]
} -ArgumentList "research query", "output.txt" -Name "SavedResearch"
```

---

## 🎯 Real Example: Onboarding System Research

```powershell
# Create research directory
$dir = "research-$(Get-Date -Format 'yyyy-MM-dd-HHmmss')"
New-Item -ItemType Directory -Path $dir -Force

# Launch parallel research
$research = @{
    "architecture" = "Analyze async repository analysis architectures: GitIngest patterns, performance optimization, scalability"
    "caching" = "Best caching strategies for repository analysis: SQLite, Redis, file-based, invalidation patterns"
    "validation" = "Project onboarding validation approaches: health checks, metrics, quality gates"
    "templates" = "Project constitution templates: tech-specific standards, team size adaptation, quality requirements"
}

foreach ($topic in $research.Keys) {
    Start-Job -ScriptBlock {
        param($query, $outPath)
        $result = gemini --model=gemini-2.5-flash --yolo $query
        @{
            timestamp = (Get-Date).ToString('o')
            topic = $using:topic
            query = $query
            result = $result
        } | ConvertTo-Json -Depth 10 | Out-File $outPath
    } -ArgumentList $research[$topic], "$dir/$topic.json" -Name "Research-$topic"
}

Write-Host "Research launched! Monitor with: Get-Job"
Write-Host "Results will be saved to: $dir"
```

---

## 📊 Monitoring Dashboard

```powershell
# Create monitoring function
function Show-ResearchStatus {
    while ((Get-Job -State Running).Count -gt 0) {
        Clear-Host
        Write-Host "=== Research Progress ===" -ForegroundColor Cyan
        Write-Host ""

        $stats = @{
            Running = (Get-Job -State Running).Count
            Completed = (Get-Job -State Completed).Count
            Failed = (Get-Job -State Failed).Count
            Total = (Get-Job).Count
        }

        Write-Host "Running:   $($stats.Running)" -ForegroundColor Yellow
        Write-Host "Completed: $($stats.Completed)" -ForegroundColor Green
        Write-Host "Failed:    $($stats.Failed)" -ForegroundColor Red
        Write-Host "Total:     $($stats.Total)" -ForegroundColor White
        Write-Host ""

        Get-Job | Format-Table -Property Name, State, PSBeginTime -AutoSize

        Start-Sleep -Seconds 5
    }

    Write-Host "All research complete!" -ForegroundColor Green
}

# Usage: Launch jobs, then monitor
Show-ResearchStatus
```

---

## 🔧 Helper Functions

Add these to your PowerShell profile (`$PROFILE`):

```powershell
# Quick research launcher
function Research {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Query,

        [string]$Name = "Research",
        [string]$Model = "gemini-2.5-flash"
    )

    Start-Job -ScriptBlock {
        param($q, $m)
        gemini --model=$m --yolo $q
    } -ArgumentList $Query, $Model -Name $Name

    Write-Host "Research '$Name' started" -ForegroundColor Green
}

# Quick status check
function Research-Status {
    Get-Job | Format-Table -Property Name, State, PSBeginTime, PSEndTime -AutoSize
}

# Quick results retrieval
function Research-Results {
    param([string]$Name)

    if ($Name) {
        Receive-Job -Name $Name -Keep
    } else {
        Get-Job | Receive-Job -Keep
    }
}

# Quick cleanup
function Research-Cleanup {
    Get-Job | Remove-Job -Force
    Write-Host "All jobs removed" -ForegroundColor Yellow
}
```

### Usage Examples

```powershell
# Launch research
Research -Query "Analyze FastAPI authentication patterns" -Name "AuthResearch"

# Check status
Research-Status

# Get results
Research-Results -Name "AuthResearch"

# Cleanup
Research-Cleanup
```

---

## 💡 Pro Tips

### 1. Batch Processing

```powershell
# Process multiple topics from a file
Get-Content "research-topics.txt" | ForEach-Object {
    $topic = $_
    Start-Job -ScriptBlock {
        gemini --model=gemini-2.5-flash --yolo $args[0] |
        Out-File "research-$(($args[0] -replace '[^a-zA-Z0-9]', '-')).txt"
    } -ArgumentList $topic -Name "Topic-$($topic.GetHashCode())"
}
```

### 2. Pipeline Integration

```powershell
# Integrate with CDE workflow
function Start-FeatureResearch {
    param([string]$FeatureName)

    $queries = @(
        "Technical architecture for: $FeatureName",
        "Security considerations for: $FeatureName",
        "Testing strategy for: $FeatureName",
        "Performance optimization for: $FeatureName"
    )

    $dir = ".cde/research/$FeatureName"
    New-Item -ItemType Directory -Path $dir -Force | Out-Null

    $i = 0
    foreach ($q in $queries) {
        Start-Job -ScriptBlock {
            gemini --model=gemini-2.5-flash --yolo $args[0] |
            Out-File $args[1]
        } -ArgumentList $q, "$dir/research-$i.txt" -Name "FR-$FeatureName-$i"
        $i++
    }
}

# Usage
Start-FeatureResearch -FeatureName "async-repository-analyzer"
```

### 3. Error Handling

```powershell
# Robust research with error handling
function Safe-Research {
    param([string]$Query, [string]$OutputFile)

    Start-Job -ScriptBlock {
        param($q, $out)
        try {
            $result = gemini --model=gemini-2.5-flash --yolo $q
            @{
                success = $true
                query = $q
                result = $result
                timestamp = (Get-Date).ToString('o')
            } | ConvertTo-Json | Out-File $out
        }
        catch {
            @{
                success = $false
                query = $q
                error = $_.Exception.Message
                timestamp = (Get-Date).ToString('o')
            } | ConvertTo-Json | Out-File $out
        }
    } -ArgumentList $Query, $OutputFile -Name "SafeResearch"
}
```

---

## 🚀 Current Research Session

```powershell
# Example: Active research for onboarding system
Write-Host "Launching onboarding system research..." -ForegroundColor Cyan

$topics = @{
    "AsyncPatterns" = "Research async repository analysis patterns in Python"
    "TokenEstimation" = "Research token estimation techniques for LLM context"
    "CachingStrategies" = "Research caching patterns for repository analysis"
    "ValidationApproaches" = "Research project validation and health scoring"
}

foreach ($name in $topics.Keys) {
    Start-Job -ScriptBlock {
        gemini --model=gemini-2.5-flash --yolo $args[0]
    } -ArgumentList $topics[$name] -Name $name
}

Write-Host "4 research jobs launched!" -ForegroundColor Green
Write-Host "Monitor with: Get-Job" -ForegroundColor Yellow
```

---

## 📝 Best Practices

1. **Use descriptive job names** for easy identification
2. **Limit concurrent jobs** to 3-5 to avoid resource exhaustion
3. **Save important results** to files immediately
4. **Clean up completed jobs** regularly to free memory
5. **Use `gemini-2.5-flash`** for fast research (unless you need deep analysis)
6. **Monitor job state** before trying to retrieve results
7. **Handle errors gracefully** with try-catch in job scripts

---

**Skill Location**: `.copilot/skills/parallel-ai-research.md`
**Full Documentation**: See above file for complete API reference
**Status**: ✅ ACTIVE AND READY
