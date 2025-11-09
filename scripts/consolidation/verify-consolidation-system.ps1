#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick verification script for folder-separated consolidation system

.DESCRIPTION
    Checks current state of consolidation system:
    - Lists files in execution/ and sessions/
    - Verifies W45 consolidation structure
    - Shows what needs to be done

.EXAMPLE
    .\verify-consolidation-system.ps1
#>

Write-Host "🔍 Folder-Separated Consolidation System - Verification" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check execution/ folder
Write-Host "📁 Checking agent-docs/execution/..." -ForegroundColor Yellow
$execFiles = Get-ChildItem -Path "agent-docs/execution" -Filter "*.md" -File | Sort-Object Name

Write-Host "   Total files: $($execFiles.Count)" -ForegroundColor White

$weeklyExec = $execFiles | Where-Object { $_.Name -like "WEEKLY-CONSOLIDATION-EXECUTION-*.md" }
$weeklyMixed = $execFiles | Where-Object { $_.Name -eq "WEEKLY-CONSOLIDATION-2025-W45.md" }
$regularExec = $execFiles | Where-Object {
    $_.Name -notlike "WEEKLY-*" -and
    $_.Name -notlike "FINAL-*" -and
    $_.Name -notlike "INTEGRATION-*" -and
    $_.Name -notlike "CONSOLIDATION_*" -and
    $_.Name -notlike "RESUMEN-*" -and
    $_.Name -notlike "EXECUTIONS-*"
}

if ($weeklyExec.Count -gt 0) {
    Write-Host "   ✅ Found EXECUTION consolidations: $($weeklyExec.Count)" -ForegroundColor Green
    foreach ($file in $weeklyExec) {
        Write-Host "      - $($file.Name) ($([math]::Round($file.Length/1KB, 2)) KB)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️  No EXECUTION consolidations found" -ForegroundColor Yellow
}

if ($weeklyMixed) {
    Write-Host "   ❌ Found MIXED consolidation: $($weeklyMixed.Name)" -ForegroundColor Red
    Write-Host "      Size: $([math]::Round($weeklyMixed.Length/1KB, 2)) KB" -ForegroundColor Gray
    Write-Host "      ACTION REQUIRED: Split this file into EXECUTION + SESSIONS" -ForegroundColor Red
}

if ($regularExec.Count -gt 0) {
    Write-Host "   📝 Regular execution files: $($regularExec.Count)" -ForegroundColor White
    Write-Host "      (Files to be consolidated in next run)" -ForegroundColor Gray
}

Write-Host ""

# Check sessions/ folder
Write-Host "📁 Checking agent-docs/sessions/..." -ForegroundColor Yellow
$sessFiles = Get-ChildItem -Path "agent-docs/sessions" -Filter "*.md" -File -ErrorAction SilentlyContinue | Sort-Object Name

if ($null -eq $sessFiles -or $sessFiles.Count -eq 0) {
    Write-Host "   ⚠️  Folder is EMPTY" -ForegroundColor Yellow
    Write-Host "      No session consolidation files found" -ForegroundColor Gray
    Write-Host "      Expected: WEEKLY-CONSOLIDATION-SESSIONS-*.md" -ForegroundColor Gray
} else {
    Write-Host "   Total files: $($sessFiles.Count)" -ForegroundColor White

    $weeklySess = $sessFiles | Where-Object { $_.Name -like "WEEKLY-CONSOLIDATION-SESSIONS-*.md" }
    $regularSess = $sessFiles | Where-Object { $_.Name -notlike "WEEKLY-*" }

    if ($weeklySess.Count -gt 0) {
        Write-Host "   ✅ Found SESSIONS consolidations: $($weeklySess.Count)" -ForegroundColor Green
        foreach ($file in $weeklySess) {
            Write-Host "      - $($file.Name) ($([math]::Round($file.Length/1KB, 2)) KB)" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ⚠️  No SESSIONS consolidations found" -ForegroundColor Yellow
    }

    if ($regularSess.Count -gt 0) {
        Write-Host "   📝 Regular session files: $($regularSess.Count)" -ForegroundColor White
        Write-Host "      (Files to be consolidated in next run)" -ForegroundColor Gray
    }
}

Write-Host ""

# Check scripts
Write-Host "🔧 Checking consolidation scripts..." -ForegroundColor Yellow
$scripts = @(
    "scripts/consolidation/consolidate-execution-with-jules.py",
    "scripts/consolidation/consolidate-sessions-with-jules.py",
    "scripts/consolidation/cleanup-after-consolidation.py"
)

$allScriptsExist = $true
foreach ($script in $scripts) {
    if (Test-Path $script) {
        $size = (Get-Item $script).Length
        Write-Host "   ✅ $script ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Missing: $script" -ForegroundColor Red
        $allScriptsExist = $false
    }
}

Write-Host ""

# Check workflow
Write-Host "⚙️  Checking GitHub Actions workflow..." -ForegroundColor Yellow
$workflow = ".github/workflows/weekly-consolidation-jules-separated.yml"
if (Test-Path $workflow) {
    $size = (Get-Item $workflow).Length
    Write-Host "   ✅ $workflow ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Missing: $workflow" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan

# Summary and recommendations
Write-Host ""
Write-Host "📊 SUMMARY & RECOMMENDATIONS" -ForegroundColor Cyan
Write-Host ""

if ($weeklyMixed) {
    Write-Host "❌ CRITICAL ACTION REQUIRED:" -ForegroundColor Red
    Write-Host "   1. Split W45 mixed consolidation into separate files:" -ForegroundColor White
    Write-Host "      - execution/WEEKLY-CONSOLIDATION-EXECUTION-2025-W45.md" -ForegroundColor Gray
    Write-Host "      - sessions/WEEKLY-CONSOLIDATION-SESSIONS-2025-W45.md" -ForegroundColor Gray
    Write-Host "   2. Update YAML frontmatter (type, file_count, source_files)" -ForegroundColor White
    Write-Host "   3. Delete: $($weeklyMixed.Name)" -ForegroundColor White
    Write-Host ""
}

if ($weeklySess.Count -eq 0) {
    Write-Host "⚠️  WARNING:" -ForegroundColor Yellow
    Write-Host "   sessions/ folder has no consolidation file" -ForegroundColor White
    Write-Host "   This will be fixed once W45 is split" -ForegroundColor Gray
    Write-Host ""
}

if ($allScriptsExist -and (Test-Path $workflow)) {
    Write-Host "✅ SYSTEM STATUS: Ready for testing" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Next steps:" -ForegroundColor White
    Write-Host "   1. Fix W45 consolidation (split into 2 files)" -ForegroundColor Gray
    Write-Host "   2. Test scripts locally:" -ForegroundColor Gray
    Write-Host "      python scripts/consolidation/consolidate-execution-with-jules.py" -ForegroundColor DarkGray
    Write-Host "   3. Run workflow manually:" -ForegroundColor Gray
    Write-Host "      gh workflow run weekly-consolidation-jules-separated.yml -f skip_cleanup=true" -ForegroundColor DarkGray
} else {
    Write-Host "❌ SYSTEM STATUS: Incomplete setup" -ForegroundColor Red
    Write-Host "   Some scripts or workflow files are missing" -ForegroundColor White
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
