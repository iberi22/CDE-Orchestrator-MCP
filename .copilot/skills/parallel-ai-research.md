# Skill: Parallel AI Research Execution

> **Capability**: Execute Gemini CLI and GitHub Copilot CLI in background for research
> **Use Case**: Run AI-powered investigations while continuing other work
> **Status**: ✅ ACTIVE
> **Last Updated**: 2025-10-31

---

## Overview

Este skill permite ejecutar comandos de investigación con Gemini CLI y GitHub Copilot CLI en segundo plano mientras continúas trabajando en otras tareas.

## Prerequisites

- **Gemini CLI**: Instalado y configurado con credenciales
- **GitHub Copilot CLI**: Instalado vía `gh extension install github/gh-copilot`
- **PowerShell**: Para ejecución en segundo plano

## Usage Patterns

### 1. Gemini CLI Research (Background)

```powershell
# Basic background research
Start-Job -ScriptBlock {
    gemini --model=gemini-2.5-flash --yolo "investiga [tu consulta aquí]"
} -Name "GeminiResearch"

# With output redirection
Start-Job -ScriptBlock {
    $result = gemini --model=gemini-2.5-flash --yolo "investiga [consulta]"
    $result | Out-File -FilePath "research-output.txt"
} -Name "GeminiResearch"

# Check job status
Get-Job -Name "GeminiResearch"

# Get results when complete
Receive-Job -Name "GeminiResearch" -Keep

# Clean up completed job
Remove-Job -Name "GeminiResearch"
```

### 2. GitHub Copilot CLI (Background Code Suggestions)

```powershell
# Background code explanation
Start-Job -ScriptBlock {
    gh copilot explain "tu código o pregunta aquí"
} -Name "CopilotExplain"

# Background code suggestion
Start-Job -ScriptBlock {
    gh copilot suggest "what you want to do"
} -Name "CopilotSuggest"

# Check results
Receive-Job -Name "CopilotExplain"
```

### 3. Multiple Parallel Investigations

```powershell
# Launch multiple research tasks in parallel
$tasks = @(
    @{Name="Research1"; Query="Compare GitIngest vs Spec-Kit architectures"},
    @{Name="Research2"; Query="Best practices for repository onboarding"},
    @{Name="Research3"; Query="Token estimation strategies for LLMs"}
)

foreach ($task in $tasks) {
    Start-Job -ScriptBlock {
        param($q)
        gemini --model=gemini-2.5-flash --yolo $q
    } -ArgumentList $task.Query -Name $task.Name
}

# Wait for all jobs to complete
Get-Job | Wait-Job

# Collect all results
$results = Get-Job | Receive-Job -Keep
$results | Out-File -FilePath "combined-research.txt"

# Cleanup
Get-Job | Remove-Job
```

### 4. Structured Research Pipeline

```powershell
# Create research directory
$researchDir = "research-$(Get-Date -Format 'yyyy-MM-dd-HHmmss')"
New-Item -ItemType Directory -Path $researchDir -Force

# Launch research with structured output
Start-Job -ScriptBlock {
    param($query, $outputPath)
    $result = gemini --model=gemini-2.5-flash --yolo $query
    @{
        timestamp = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        query = $query
        result = $result
    } | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputPath
} -ArgumentList @(
    "Analyze onboarding patterns in open-source projects",
    "$researchDir/onboarding-analysis.json"
) -Name "StructuredResearch"
```

## Gemini CLI Options

### Models Available
- `gemini-2.5-flash` (fastest, recommended for research)
- `gemini-2.5-pro` (more capable, slower)
- `gemini-1.5-pro`
- `gemini-1.5-flash`

### Key Flags
- `--yolo` / `-y`: Auto-approve all actions (no interactive prompts)
- `--model` / `-m`: Specify model
- `--prompt` / `-p`: Direct prompt (deprecated, use positional)
- `--output-format` / `-o`: Output format (text/json/stream-json)
- `--sandbox` / `-s`: Run in sandbox mode
- `--debug` / `-d`: Debug mode

### Advanced Usage

```powershell
# JSON output for parsing
Start-Job -ScriptBlock {
    gemini --model=gemini-2.5-flash --yolo --output-format json "research query" |
    ConvertFrom-Json |
    ConvertTo-Json -Depth 10 |
    Out-File "structured-output.json"
} -Name "JsonResearch"

# With MCP server filtering
Start-Job -ScriptBlock {
    gemini --model=gemini-2.5-flash --yolo `
           --allowed-mcp-server-names "github","filesystem" `
           "research query using specific MCPs"
} -Name "MCPResearch"

# With extensions
Start-Job -ScriptBlock {
    gemini --model=gemini-2.5-flash --yolo `
           --extensions "web-search","code-analysis" `
           "research query"
} -Name "ExtensionResearch"
```

## GitHub Copilot CLI Options

```powershell
# Explain code
gh copilot explain "complex code snippet or concept"

# Suggest commands
gh copilot suggest "what you want to do"

# Background suggestion with output capture
Start-Job -ScriptBlock {
    gh copilot suggest "create a FastAPI endpoint for user authentication" |
    Out-File "copilot-suggestion.txt"
} -Name "CopilotSuggestion"
```

## Best Practices

### 1. Resource Management

```powershell
# Limit concurrent jobs to prevent resource exhaustion
$maxJobs = 3
while ((Get-Job -State Running).Count -ge $maxJobs) {
    Start-Sleep -Seconds 2
}
Start-Job -ScriptBlock { gemini --yolo "query" } -Name "NewResearch"
```

### 2. Error Handling

```powershell
Start-Job -ScriptBlock {
    try {
        $result = gemini --model=gemini-2.5-flash --yolo $args[0]
        @{success=$true; result=$result}
    } catch {
        @{success=$false; error=$_.Exception.Message}
    } | ConvertTo-Json
} -ArgumentList "research query" -Name "SafeResearch"
```

### 3. Progress Monitoring

```powershell
# Monitor all background jobs
while ((Get-Job -State Running).Count -gt 0) {
    $running = (Get-Job -State Running).Count
    $completed = (Get-Job -State Completed).Count
    $failed = (Get-Job -State Failed).Count

    Write-Host "Jobs: Running=$running | Completed=$completed | Failed=$failed"
    Start-Sleep -Seconds 5
}
```

### 4. Result Aggregation

```powershell
# Collect and aggregate results
$allResults = Get-Job | ForEach-Object {
    $job = $_
    $result = Receive-Job -Job $job -Keep

    [PSCustomObject]@{
        JobName = $job.Name
        State = $job.State
        Started = $job.PSBeginTime
        Ended = $job.PSEndTime
        Duration = ($job.PSEndTime - $job.PSBeginTime).TotalSeconds
        Output = $result
    }
}

$allResults | Export-Csv -Path "research-results.csv" -NoTypeInformation
```

## Real-World Examples

### Example 1: Comprehensive Onboarding Research

```powershell
# Launch parallel research on onboarding systems
$queries = @(
    "Analyze GitIngest architecture and key innovations",
    "Spec-Kit methodology and workflow patterns",
    "Token estimation strategies for large codebases",
    "Best practices for project constitution documents",
    "Async repository analysis patterns in Python"
)

$i = 0
foreach ($query in $queries) {
    Start-Job -ScriptBlock {
        param($q, $idx, $dir)
        $result = gemini --model=gemini-2.5-flash --yolo $q
        $result | Out-File "$dir/research-$idx.txt"
    } -ArgumentList $query, $i, $researchDir -Name "Research$i"
    $i++
}

# Wait and collect
Get-Job | Wait-Job
Write-Host "Research complete! Results in $researchDir"
Get-Job | Remove-Job
```

### Example 2: Code Review with Copilot

```powershell
# Background code review for multiple files
$files = Get-ChildItem -Path "src/cde_orchestrator/onboarding" -Filter "*.py"

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    Start-Job -ScriptBlock {
        param($code, $filename)
        gh copilot explain $code | Out-File "review-$filename.txt"
    } -ArgumentList $content, $file.Name -Name "Review-$($file.BaseName)"
}
```

### Example 3: Research + Summarization Pipeline

```powershell
# Phase 1: Parallel research
Start-Job -Name "Phase1" -ScriptBlock {
    gemini --model=gemini-2.5-flash --yolo `
        "Research async repository analysis patterns" |
    Out-File "phase1-raw.txt"
}

# Wait for Phase 1
Wait-Job -Name "Phase1"

# Phase 2: Summarize findings
Start-Job -Name "Phase2" -ScriptBlock {
    $rawData = Get-Content "phase1-raw.txt" -Raw
    gemini --model=gemini-2.5-flash --yolo `
        "Summarize the following research in 3 key points: $rawData" |
    Out-File "phase2-summary.txt"
}

# Final collection
Wait-Job -Name "Phase2"
Get-Content "phase2-summary.txt"
```

## Integration with CDE Orchestrator

### Automated Research for Onboarding

```powershell
# Trigger research when starting feature development
function Start-CDEResearch {
    param(
        [string]$FeaturePrompt,
        [string]$OutputDir = ".cde/research"
    )

    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

    # Research architecture patterns
    Start-Job -ScriptBlock {
        param($prompt, $outDir)
        gemini --model=gemini-2.5-flash --yolo `
            "Analyze technical approaches for: $prompt" |
        Out-File "$outDir/architecture.txt"
    } -ArgumentList $FeaturePrompt, $OutputDir -Name "ArchResearch"

    # Research best practices
    Start-Job -ScriptBlock {
        param($prompt, $outDir)
        gemini --model=gemini-2.5-flash --yolo `
            "Best practices and pitfalls for: $prompt" |
        Out-File "$outDir/best-practices.txt"
    } -ArgumentList $FeaturePrompt, $OutputDir -Name "BestPractices"

    # Research similar implementations
    Start-Job -ScriptBlock {
        param($prompt, $outDir)
        gemini --model=gemini-2.5-flash --yolo `
            "Find open-source implementations similar to: $prompt" |
        Out-File "$outDir/references.txt"
    } -ArgumentList $FeaturePrompt, $OutputDir -Name "References"

    Write-Host "Research started. Use Get-Job to monitor progress."
}

# Usage
Start-CDEResearch -FeaturePrompt "async repository analyzer with caching"
```

## Troubleshooting

### Job Stuck or Hanging

```powershell
# Force stop hung jobs
Get-Job | Where-Object {$_.State -eq "Running"} | Stop-Job
Get-Job | Remove-Job -Force
```

### Large Output Issues

```powershell
# Stream output to file instead of keeping in memory
Start-Job -ScriptBlock {
    gemini --model=gemini-2.5-flash --yolo $args[0] |
    Tee-Object -FilePath "output.txt"
} -ArgumentList "large query"
```

### Credential Issues

```powershell
# Re-authenticate Gemini CLI
gemini mcp # Opens MCP configuration UI

# Check Copilot authentication
gh auth status
gh auth login
```

## Performance Tips

1. **Use `gemini-2.5-flash`** for fast research (vs slower pro models)
2. **Limit concurrent jobs** to 3-5 to prevent resource exhaustion
3. **Stream to files** for large outputs to avoid memory issues
4. **Use `--output-format json`** for structured, parseable results
5. **Cleanup jobs regularly** with `Get-Job | Remove-Job`

---

## Quick Reference Card

```powershell
# Quick start: Background research
Start-Job -ScriptBlock { gemini --yolo "query" } -Name "Research"
Get-Job -Name "Research"           # Check status
Receive-Job -Name "Research" -Keep  # Get results
Remove-Job -Name "Research"         # Cleanup

# Multiple parallel tasks
@("query1","query2","query3") | ForEach-Object {
    Start-Job -ScriptBlock { gemini --yolo $args[0] } -ArgumentList $_ -Name "Job$_"
}

# Wait for all and collect
Get-Job | Wait-Job
Get-Job | Receive-Job -Keep
Get-Job | Remove-Job
```

---

**Skill Status**: ✅ READY FOR USE
**Dependencies**: Gemini CLI, GitHub Copilot CLI (via `gh`)
**Compatibility**: Windows PowerShell 5.1+, PowerShell Core 7+
