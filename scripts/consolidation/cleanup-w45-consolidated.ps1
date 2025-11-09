#!/usr/bin/env pwsh
# Script: Remove consolidated files from W45
# Purpose: Delete ONLY files that were consolidated by Jules in WEEKLY-CONSOLIDATION-2025-W45.md
# Date: 2025-11-08
# Author: Consolidation Agent

param(
    [switch]$Force = $false
)

Write-Host "🧹 CLEANUP: Removing consolidated files from W45" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Define the 70 files that were consolidated in W45
$W45_ConsolidatedFiles = @(
    # Core Execution Reports (27 files)
    "agent-docs/execution/execution-phase4-commit-summary-2025-11-06.md",
    "agent-docs/execution/execution-phase4-unified-store-optimization-2025-11-06.md",
    "agent-docs/execution/execution-phase5-testing-validation-2025-11-06.md",
    "agent-docs/execution/execution-phase2ab-complete-2025-11-06.md",
    "agent-docs/execution/audit-complete-cde-mcp-2025-11-07.md",
    "agent-docs/execution/EXECUTIVE_SUMMARY_AUDIT_2025-11-07.md",
    "agent-docs/execution/decision-matrix-implementation-2025-11-07.md",
    "agent-docs/execution/optimization-roadmap-2025-11-07.md",
    "agent-docs/execution/execution-week1-cleanup-2025-11-07.md",
    "agent-docs/execution/execution-semana2-three-agent-remediation-2025-11-07.md",
    "agent-docs/execution/delegation-semana2-to-jules-2025-11-07.md",
    "agent-docs/execution/bedrock-setup-complete-2025-11-05.md",
    "agent-docs/execution/change-log-2025-11-05.md",
    "agent-docs/execution/enterprise-services-analysis-2025-11-05.md",
    "agent-docs/execution/execution-implementation-plan-2025-11-05.md",
    "agent-docs/execution/fair-source-implementation-2025-11-05.md",
    "agent-docs/execution/license-features-implementation-2025-11-05.md",
    "agent-docs/execution/meta-orchestration-complete-2025-11-05.md",
    "agent-docs/execution/meta-orchestration-summary-2025-11-05.md",
    "agent-docs/execution/execution-harcos-deployment-complete-2025-11-05.md",
    "agent-docs/execution/execution-dsms-phase1-2025-11-04.md",
    "agent-docs/execution/execution-phase3c-deployment-2025-11-04.md",
    "agent-docs/execution/execution-phase3c-summary-2025-11-04.md",
    "agent-docs/execution/execution-phase3c-verification-2025-11-04.md",
    "agent-docs/execution/execution-repository-ready-2025-11-04.md",
    "agent-docs/execution/resumen-mision-completada-2025-11-04.md",
    "agent-docs/execution/session-phase3c-complete-2025-11-04.md",

    # Feature & Phase Launches (12 files)
    "agent-docs/execution/execution-phase2c-launch-summary-2025-11.md",
    "agent-docs/execution/phase2c-enhanced-ui-jules-tasks.md",
    "agent-docs/execution/phase2c-jules-sessions.md",
    "agent-docs/execution/workflow-orchestration-testing-implementation-2025-11.md",
    "agent-docs/execution/intelligent-agent-system-implementation-2025-11.md",
    "agent-docs/execution/python-314-code-audit-2025-11.md",
    "agent-docs/execution/python-314-migration-report.md",
    "agent-docs/execution/execution-ready-2025-11.md",
    "agent-docs/execution/execution-onboarding-2025-01.md",
    "agent-docs/execution/validation-report-2025-01.md",
    "agent-docs/execution/phase-3b-testing-completion.md",
    "agent-docs/execution/workflow-selector-completion-2025-11-02.md",

    # Testing, Documentation & Deployment (15 files)
    "agent-docs/execution/mcp-progress-tracking-implementation-2025-11-02.md",
    "agent-docs/execution/harcos_deployment_next_steps.md",
    "agent-docs/execution/harcos_deployment_package_index.md",
    "agent-docs/execution/harcos_quick_start.md",
    "agent-docs/execution/phase5-manual-testing-checklist-2025-11-06.md",
    "agent-docs/execution/test-progress-tracking-2025-11-06.json",
    "agent-docs/execution/EXECUTIONS-julius-activation-guide-2025-11-08-0012.md",
    "agent-docs/execution/EXECUTIONS-julius-implementation-summary-2025-11-08-0012.md",
    "agent-docs/execution/EXECUTIONS-julius-quick-start-2025-11-08-0012.md",
    "agent-docs/execution/README-AUDIT-2025-11-07.md",
    "agent-docs/execution/rapid-donation-strategy-2025-11-06.md",
    "agent-docs/execution/SEMANA2-JULES-DELEGATION-SUMMARY-2025-11-07.md",
    "agent-docs/execution/ai-assistant-config-implementation-complete.md",
    "agent-docs/execution/documentation-architecture-phase-1-2-complete.md",
    "agent-docs/execution/commit_summary_2025-11-06.md",

    # Session Files (16 files)
    "agent-docs/sessions/session-agent-governance-implementation-2025-11.md",
    "agent-docs/sessions/session-ai-assistant-instructions-2025-11.md",
    "agent-docs/sessions/session-documentation-reorganization-2025-11.md",
    "agent-docs/sessions/session-enterprise-model-evaluation-2025-11-05.md",
    "agent-docs/sessions/session-features-license-implementation-2025-11-05.md",
    "agent-docs/sessions/session-implementation-finalization-2025-11.md",
    "agent-docs/sessions/session-jules-amazon-q-context-2025-11.md",
    "agent-docs/sessions/session-meta-orchestration-implementation-2025-11-05.md",
    "agent-docs/sessions/session-phase5-complete-2025-11-06.md",
    "agent-docs/sessions/session-workflow-selector-completion-2025-11-02.md",
    "agent-docs/sessions/session-mcp-tools-testing-feedback-2025-11-02.md",
    "agent-docs/sessions/session-final-complete-2025-11-04.md",
    "agent-docs/sessions/readme-session-2025-11-02.md",
    "agent-docs/sessions/resumen-final-2025-11-05.md",
    "agent-docs/sessions/session-onboarding-research-2025-10.md",
    "agent-docs/sessions/session-onboarding-review-2025-01.md"
)

# Files to PRESERVE (consolidations and verification documents)
$PreserveFiles = @(
    "agent-docs/execution/WEEKLY-CONSOLIDATION-2025-W44.md",
    "agent-docs/execution/WEEKLY-CONSOLIDATION-2025-W45.md",
    "agent-docs/execution/FINAL-VERIFICATION-JULES-W44-2025-11-08.md",
    "agent-docs/execution/FINAL-VERIFICATION-JULES-W45-2025-11-08.md",
    "agent-docs/execution/INTEGRATION-jules-w44-completion-2025-11-08.md",
    "agent-docs/execution/consolidation-prompt-enhancement-analysis-2025-11-08.md",
    "agent-docs/execution/jules-w44-review-complete-2025-11-08.md",
    "agent-docs/execution/REVIEW-jules-w44-session-7178-2025-11-08.md",
    "agent-docs/execution/execution-w45-consolidation-realtime-2025-11-08.md",
    "agent-docs/execution/review-jules-w44-prompt-enhancement-2025-11-08.md"
)

Write-Host "📊 Summary:" -ForegroundColor Yellow
Write-Host "  - Files to delete: $($W45_ConsolidatedFiles.Count)" -ForegroundColor White
Write-Host "  - Files to preserve: $($PreserveFiles.Count)" -ForegroundColor White
Write-Host ""

# Safety check: Verify all files exist before deleting
Write-Host "🔍 Verifying files exist..." -ForegroundColor Yellow
$ExistingFiles = @()
$MissingFiles = @()

foreach ($file in $W45_ConsolidatedFiles) {
    if (Test-Path $file) {
        $ExistingFiles += $file
    } else {
        $MissingFiles += $file
    }
}

Write-Host "  ✅ Found: $($ExistingFiles.Count) files" -ForegroundColor Green
if ($MissingFiles.Count -gt 0) {
    Write-Host "  ⚠️  Missing: $($MissingFiles.Count) files (already deleted or never existed)" -ForegroundColor Yellow
}
Write-Host ""

# Safety check: Verify preserve files are NOT in deletion list
$Conflicts = $W45_ConsolidatedFiles | Where-Object { $PreserveFiles -contains $_ }
if ($Conflicts.Count -gt 0) {
    Write-Host "❌ ERROR: Conflict detected!" -ForegroundColor Red
    Write-Host "  The following files are marked for BOTH deletion and preservation:" -ForegroundColor Red
    $Conflicts | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
    exit 1
}

# Ask for confirmation
if (-not $Force) {
    Write-Host "⚠️  WARNING: This will DELETE $($ExistingFiles.Count) files permanently!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Files to preserve (will NOT be deleted):" -ForegroundColor Cyan
    $PreserveFiles | ForEach-Object { Write-Host "  ✓ $_" -ForegroundColor Green }
    Write-Host ""

    $confirmation = Read-Host "Type 'DELETE' to proceed with deletion"

    if ($confirmation -ne "DELETE") {
        Write-Host "❌ Deletion cancelled. No files were deleted." -ForegroundColor Red
        exit 0
    }
} else {
    Write-Host "⚠️  FORCE MODE: Deleting $($ExistingFiles.Count) files without confirmation..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🗑️  Deleting consolidated files..." -ForegroundColor Red

$DeletedCount = 0
$FailedCount = 0

foreach ($file in $ExistingFiles) {
    try {
        Remove-Item -Path $file -Force
        $DeletedCount++
        Write-Host "  ✅ Deleted: $file" -ForegroundColor Gray
    } catch {
        $FailedCount++
        Write-Host "  ❌ Failed: $file - $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 CLEANUP RESULTS:" -ForegroundColor Cyan
Write-Host "  - Deleted: $DeletedCount files" -ForegroundColor Green
Write-Host "  - Failed: $FailedCount files" -ForegroundColor $(if ($FailedCount -gt 0) { "Red" } else { "Gray" })
Write-Host "  - Preserved: $($PreserveFiles.Count) consolidation documents" -ForegroundColor Yellow
Write-Host ""

if ($DeletedCount -gt 0) {
    Write-Host "✅ Cleanup complete! Now run:" -ForegroundColor Green
    Write-Host "   git status" -ForegroundColor White
    Write-Host "   git add agent-docs/" -ForegroundColor White
    Write-Host "   git commit -m 'chore(cleanup): remove W45 consolidated files - 70 files archived'" -ForegroundColor White
}
