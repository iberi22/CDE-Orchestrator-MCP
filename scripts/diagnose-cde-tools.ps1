# diagnose-cde-tools.ps1
# Quick diagnostic for CDE Orchestrator tool discovery issues
# Usage: .\diagnose-cde-tools.ps1

param(
    [string]$CdePath = "E:\scripts-python\CDE Orchestrator MCP",
    [switch]$Verbose
)

Write-Host "`n🔍 CDE Tool Discovery Diagnostic" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$issues = @()
$checks = 0
$passed = 0

# Check 1: CDE Orchestrator exists
Write-Host "[1/7] Checking CDE Orchestrator path..." -NoNewline
$checks++
if (!(Test-Path $CdePath)) {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      Path not found: $CdePath" -ForegroundColor Red
    $issues += "CDE Orchestrator not found at $CdePath"
} else {
    Write-Host " ✅ OK" -ForegroundColor Green
    $passed++
    if ($Verbose) { Write-Host "      Path: $CdePath" -ForegroundColor Gray }
}

# Check 2: server.py exists
Write-Host "[2/7] Checking server.py..." -NoNewline
$checks++
$serverPath = Join-Path $CdePath "src\server.py"
if (!(Test-Path $serverPath)) {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      File not found: $serverPath" -ForegroundColor Red
    $issues += "server.py not found"
} else {
    Write-Host " ✅ OK" -ForegroundColor Green
    $passed++
}

# Check 3: cde_generateSpec in server.py
Write-Host "[3/7] Checking cde_generateSpec registration..." -NoNewline
$checks++
if (Test-Path $serverPath) {
    $serverContent = Get-Content $serverPath -Raw
    if ($serverContent -match "cde_generateSpec") {
        Write-Host " ✅ OK" -ForegroundColor Green
        $passed++
        if ($Verbose) {
            $matches = Select-String -Path $serverPath -Pattern "cde_generateSpec"
            Write-Host "      Found in $($matches.Count) locations" -ForegroundColor Gray
        }
    } else {
        Write-Host " ❌ FAILED" -ForegroundColor Red
        Write-Host "      cde_generateSpec not found in server.py" -ForegroundColor Red
        $issues += "cde_generateSpec not registered in server"
    }
} else {
    Write-Host " ⏭️  SKIPPED" -ForegroundColor Yellow
}

# Check 4: spec_generator.py exists
Write-Host "[4/7] Checking spec_generator.py..." -NoNewline
$checks++
$specGenPath = Join-Path $CdePath "src\mcp_tools\spec_generator.py"
if (!(Test-Path $specGenPath)) {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      File not found: $specGenPath" -ForegroundColor Red
    $issues += "spec_generator.py implementation missing"
} else {
    Write-Host " ✅ OK" -ForegroundColor Green
    $passed++
    if ($Verbose) {
        $lines = (Get-Content $specGenPath).Count
        Write-Host "      Implementation: $lines lines" -ForegroundColor Gray
    }
}

# Check 5: .vscode/mcp.json in current directory
Write-Host "[5/7] Checking .vscode/mcp.json..." -NoNewline
$checks++
$mcpPath = ".vscode\mcp.json"
if (!(Test-Path $mcpPath)) {
    Write-Host " ⚠️  WARNING" -ForegroundColor Yellow
    Write-Host "      File not found: $mcpPath" -ForegroundColor Yellow
    Write-Host "      This is OK if you're in CDE Orchestrator project" -ForegroundColor Gray
    $issues += "No mcp.json in current directory (may be intentional)"
} else {
    Write-Host " ✅ OK" -ForegroundColor Green
    $passed++

    # Validate JSON
    try {
        $config = Get-Content $mcpPath | ConvertFrom-Json
        if ($config.servers.CDE_Orchestrator) {
            if ($Verbose) {
                Write-Host "      CDE_Orchestrator server configured" -ForegroundColor Gray
            }
        } else {
            Write-Host "      ⚠️  CDE_Orchestrator server not found in config" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "      ⚠️  Invalid JSON syntax" -ForegroundColor Yellow
        $issues += "mcp.json has invalid JSON syntax"
    }
}

# Check 6: Python availability
Write-Host "[6/7] Checking Python..." -NoNewline
$checks++
try {
    $pythonVersion = python --version 2>&1
    Write-Host " ✅ OK" -ForegroundColor Green
    $passed++
    if ($Verbose) { Write-Host "      $pythonVersion" -ForegroundColor Gray }
} catch {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      Python not found in PATH" -ForegroundColor Red
    $issues += "Python not available"
}

# Check 7: Test server startup (quick test)
Write-Host "[7/7] Testing server startup..." -NoNewline
$checks++
Push-Location $CdePath
$env:PYTHONPATH = "src"
try {
    $output = python src/server.py 2>&1 | Select-Object -First 15
    $outputText = $output -join "`n"

    if ($outputText -match "Generated (\d+) MCP tool files") {
        $toolCount = $matches[1]
        if ([int]$toolCount -ge 26) {
            Write-Host " ✅ OK" -ForegroundColor Green
            $passed++
            if ($Verbose) { Write-Host "      $toolCount tools registered" -ForegroundColor Gray }
        } elseif ([int]$toolCount -ge 22) {
            Write-Host " ⚠️  WARNING" -ForegroundColor Yellow
            Write-Host "      Only $toolCount tools registered (expected 26)" -ForegroundColor Yellow
            $issues += "Some tools not registered ($toolCount/26)"
        } else {
            Write-Host " ❌ FAILED" -ForegroundColor Red
            Write-Host "      Only $toolCount tools registered (expected 26)" -ForegroundColor Red
            $issues += "Too few tools registered ($toolCount/26)"
        }
    } else {
        Write-Host " ⚠️  WARNING" -ForegroundColor Yellow
        Write-Host "      Could not parse tool count" -ForegroundColor Yellow
        $issues += "Could not verify tool count"
    }
} catch {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      $($_.Exception.Message)" -ForegroundColor Red
    $issues += "Server failed to start: $($_.Exception.Message)"
} finally {
    Pop-Location
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`nChecks: $passed/$checks passed" -ForegroundColor $(if ($passed -eq $checks) { "Green" } elseif ($passed -ge ($checks * 0.7)) { "Yellow" } else { "Red" })

if ($issues.Count -eq 0) {
    Write-Host "`n✅ All checks passed!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Reload VS Code (Ctrl+Shift+P → Reload Window)" -ForegroundColor Gray
    Write-Host "  2. Test: @workspace Use cde_healthCheck" -ForegroundColor Gray
    Write-Host "  3. Use: @workspace Use cde_generateSpec to create specs" -ForegroundColor Gray
} else {
    Write-Host "`n⚠️  Issues found ($($issues.Count)):" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "  • $issue" -ForegroundColor Yellow
    }

    Write-Host "`nRecommended actions:" -ForegroundColor Cyan
    if ($issues -match "not registered") {
        Write-Host "  1. Run: git pull origin main" -ForegroundColor Gray
        Write-Host "  2. Reload VS Code (Ctrl+Shift+P → Reload Window)" -ForegroundColor Gray
    }
    if ($issues -match "mcp.json") {
        Write-Host "  1. See: docs/configuration-guide.md" -ForegroundColor Gray
        Write-Host "  2. Create .vscode/mcp.json with proper configuration" -ForegroundColor Gray
    }
    if ($issues -match "Python") {
        Write-Host "  1. Install Python 3.11+ from python.org" -ForegroundColor Gray
        Write-Host "  2. Add Python to PATH" -ForegroundColor Gray
    }
}

Write-Host "`n📖 Documentation:" -ForegroundColor Cyan
Write-Host "  • Quick Fix: docs/QUICKFIX-RELOAD-TOOLS.md" -ForegroundColor Gray
Write-Host "  • Full Guide: docs/configuration-guide.md" -ForegroundColor Gray
Write-Host "  • Troubleshooting: docs/troubleshooting.md" -ForegroundColor Gray

Write-Host "`n" + ("=" * 60) + "`n" -ForegroundColor Cyan

exit $(if ($passed -eq $checks) { 0 } else { 1 })
