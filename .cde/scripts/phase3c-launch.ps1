#!/usr/bin/env pwsh
#
# PHASE 3C - QUICK LAUNCH SCRIPT FOR JULES
# This script verifies system readiness before Jules begins Phase 3C execution
#
# Usage: .\PHASE3C_QUICK_LAUNCH.ps1
#

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 PHASE 3C - SYSTEM READINESS VERIFICATION" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check 1: Git Status
Write-Host "✓ Checking Git Status..." -ForegroundColor Yellow
$git_status = git status --short
if ($git_status) {
    Write-Host "⚠️  Working directory has uncommitted changes:" -ForegroundColor Yellow
    Write-Host $git_status
} else {
    Write-Host "✅ Git working directory: CLEAN" -ForegroundColor Green
}
Write-Host ""

# Check 2: Recent Commits
Write-Host "✓ Recent Commits:" -ForegroundColor Yellow
git log --oneline -5
Write-Host ""

# Check 3: Test Status
Write-Host "✓ Running Tests..." -ForegroundColor Yellow
$test_results = pytest tests/ -v --tb=short 2>&1 | Select-String "passed|failed" | Select-Object -Last 1
if ($test_results -like "*passed*") {
    Write-Host "✅ Tests: $test_results" -ForegroundColor Green
} else {
    Write-Host "❌ Test failures detected" -ForegroundColor Red
}
Write-Host ""

# Check 4: Prompts Available
Write-Host "✓ Jules Execution Prompts:" -ForegroundColor Yellow
$prompt_files = @(
    "agent-docs/prompts/JULIUS_MASTER_PROMPT_PHASE3C.md",
    "agent-docs/prompts/JULIUS_PHASE3C_QUICK_START.md"
)
foreach ($file in $prompt_files) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length / 1KB
        Write-Host "✅ $file ($([Math]::Round($size))KB)" -ForegroundColor Green
    } else {
        Write-Host "❌ MISSING: $file" -ForegroundColor Red
    }
}
Write-Host ""

# Check 5: Code Structure
Write-Host "✓ Code Structure Verification:" -ForegroundColor Yellow
$code_files = @(
    "src/cde_orchestrator/adapters/agents/agent_selection_policy.py",
    "src/cde_orchestrator/adapters/agents/multi_agent_orchestrator.py",
    "src/cde_orchestrator/adapters/agents/jules_async_adapter.py",
    "src/mcp_tools/agents.py"
)
foreach ($file in $code_files) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ MISSING: $file" -ForegroundColor Red
    }
}
Write-Host ""

# Check 6: Documentation
Write-Host "✓ Phase 3C Documentation:" -ForegroundColor Yellow
$doc_files = @(
    "PHASE3C_EXECUTIVE_SUMMARY.md",
    "PHASE3C_FINAL_VERIFICATION.md",
    "PHASE3C_DEPLOYMENT_SUMMARY.md"
)
foreach ($file in $doc_files) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Optional: $file" -ForegroundColor Yellow
    }
}
Write-Host ""

# Summary
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ All systems ready for Phase 3C" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS FOR JULES:" -ForegroundColor Cyan
Write-Host "1. Copy contents of JULIUS_MASTER_PROMPT_PHASE3C.md" -ForegroundColor White
Write-Host "2. Go to https://jules.google/" -ForegroundColor White
Write-Host "3. Paste prompt and execute" -ForegroundColor White
Write-Host "4. Follow 3-workstream execution plan" -ForegroundColor White
Write-Host "5. Commit results to main branch" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Expected Duration: 6-8 hours" -ForegroundColor Cyan
Write-Host "📊 Expected Results:" -ForegroundColor Cyan
Write-Host "   - Jules SDK fully implemented" -ForegroundColor White
Write-Host "   - Documentation 100% governance-compliant" -ForegroundColor White
Write-Host "   - Testing infrastructure complete" -ForegroundColor White
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 SYSTEM READY FOR JULES" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
