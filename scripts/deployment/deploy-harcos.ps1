#Requires -Version 7.0
<#
.SYNOPSIS
    HARCOS-AI Organization Deployment Script - Optimized for Fast Donations

.DESCRIPTION
    Modern deployment script following 2025 industry best practices:
    - Automated GitHub organization setup
    - GitHub Sponsors with optimized conversion tiers
    - Landing page with clear CTAs
    - Fair Source licensing
    - Multi-platform fundraising (GitHub + Open Collective)

.PARAMETER SkipOrgCreation
    Skip organization creation if already exists

.PARAMETER OrgName
    Organization name (default: HARCOS-AI)

.PARAMETER DryRun
    Show what would be done without making changes

.EXAMPLE
    .\deploy-harcos.ps1
    Full deployment

.EXAMPLE
    .\deploy-harcos.ps1 -DryRun
    Preview deployment steps

.NOTES
    Author: CDE Orchestrator MCP
    Version: 1.0.0
    Date: 2025-11-06
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$SkipOrgCreation,

    [Parameter()]
    [string]$OrgName = "HARCOS-AI",

    [Parameter()]
    [switch]$DryRun
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Config = @{
    OrgName = $OrgName
    OrgDescription = "Human-AI Research Community Open Source"
    OrgWebsite = "https://harcos.ai"
    OrgTagline = "Open tools for symbiotic intelligence"

    # Repositories to create
    Repositories = @(
        @{
            Name = "CDE-Orchestrator-MCP"
            Description = "Context-Driven Engineering orchestrator for AI-powered development workflows"
            IsTransfer = $true
            Topics = @("ai", "mcp", "orchestration", "context-driven-engineering", "copilot")
        }
        @{
            Name = "Agent-Framework"
            Description = "Unified framework for building multi-agent AI systems with task decomposition"
            IsTransfer = $false
            Topics = @("ai-agents", "multi-agent", "task-decomposition", "framework")
        }
        @{
            Name = "LLM-Eval-Toolkit"
            Description = "Comprehensive toolkit for evaluating LLM performance across various benchmarks"
            IsTransfer = $false
            Topics = @("llm", "evaluation", "benchmarks", "testing")
        }
        @{
            Name = "docs"
            Description = "Landing page and documentation for HARCOS-AI projects"
            IsTransfer = $false
            Topics = @("documentation", "website", "landing-page")
        }
        @{
            Name = "enterprise"
            Description = "Enterprise services configuration and documentation"
            IsTransfer = $false
            Topics = @("enterprise", "services", "consulting")
        }
    )

    # GitHub Sponsors tiers (optimized for conversion)
    SponsorTiers = @(
        @{
            Name = "Community Supporter"
            Amount = 5
            Description = "Show your support for open-source AI tools"
            Benefits = @("Supporter badge on profile", "Name in SUPPORTERS.md")
        }
        @{
            Name = "Professional Developer"
            Amount = 25
            Description = "Priority support and early access to features"
            Benefits = @("All Community benefits", "Priority issue responses (48h)", "Early access to new features", "Name on website")
        }
        @{
            Name = "Team License"
            Amount = 100
            Description = "For teams using HARCOS tools in production"
            Benefits = @("All Professional benefits", "Team mention on website", "Monthly office hours access", "Private Slack channel")
        }
        @{
            Name = "Enterprise Partner"
            Amount = 500
            Description = "White-glove support for enterprise deployments"
            Benefits = @("All Team benefits", "24/7 priority support", "Dedicated onboarding", "Custom integrations support", "Quarterly strategy calls")
            IsCustom = $true
        }
    )
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> " -NoNewline -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor White
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ " -NoNewline -ForegroundColor Green
    Write-Host $Message -ForegroundColor Gray
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ " -NoNewline -ForegroundColor Yellow
    Write-Host $Message -ForegroundColor Gray
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ " -NoNewline -ForegroundColor Red
    Write-Host $Message -ForegroundColor Gray
}

function Test-GitHubCLI {
    try {
        $version = gh --version 2>&1 | Select-Object -First 1
        if ($version -match "gh version") {
            Write-Success "GitHub CLI installed: $version"
            return $true
        }
    }
    catch {
        Write-Error "GitHub CLI not found. Install from: https://cli.github.com"
        return $false
    }
}

function Test-GitHubAuth {
    try {
        $auth = gh auth status 2>&1
        if ($auth -match "Logged in") {
            Write-Success "GitHub authentication verified"
            return $true
        }
    }
    catch {
        Write-Error "Not authenticated with GitHub. Run: gh auth login"
        return $false
    }
}

function Get-CurrentRepo {
    try {
        $repo = gh repo view --json owner,name | ConvertFrom-Json
        return @{
            Owner = $repo.owner.login
            Name = $repo.name
            FullName = "$($repo.owner.login)/$($repo.name)"
        }
    }
    catch {
        Write-Error "Failed to get current repository info"
        return $null
    }
}

# ============================================================================
# DEPLOYMENT FUNCTIONS
# ============================================================================

function New-HARCOSOrganization {
    param([string]$OrgName)

    Write-Step "Creating GitHub Organization: $OrgName"

    if ($DryRun) {
        Write-Warning "DRY RUN: Would create organization $OrgName"
        return $true
    }

    # Check if organization already exists
    try {
        $existing = gh org view $OrgName 2>&1
        if ($existing -notmatch "Could not resolve") {
            Write-Warning "Organization $OrgName already exists"
            return $true
        }
    }
    catch {
        # Organization doesn't exist, continue
    }

    # GitHub CLI doesn't support org creation yet
    Write-Warning "GitHub CLI doesn't support organization creation"
    Write-Host "Please create the organization manually:"
    Write-Host "  1. Visit: https://github.com/organizations/new" -ForegroundColor Yellow
    Write-Host "  2. Organization name: $OrgName" -ForegroundColor Yellow
    Write-Host "  3. Billing email: Your email" -ForegroundColor Yellow
    Write-Host "  4. Description: $($Config.OrgDescription)" -ForegroundColor Yellow
    Write-Host "  5. Website: $($Config.OrgWebsite)" -ForegroundColor Yellow
    Write-Host ""

    $confirm = Read-Host "Have you created the organization? (y/N)"
    if ($confirm -ne 'y') {
        Write-Error "Organization creation cancelled"
        return $false
    }

    # Verify organization exists
    try {
        gh org view $OrgName | Out-Null
        Write-Success "Organization $OrgName verified"
        return $true
    }
    catch {
        Write-Error "Could not verify organization $OrgName"
        return $false
    }
}

function Move-RepositoryToOrg {
    param(
        [string]$OrgName,
        [hashtable]$CurrentRepo
    )

    Write-Step "Transferring $($CurrentRepo.FullName) to $OrgName"

    if ($DryRun) {
        Write-Warning "DRY RUN: Would transfer $($CurrentRepo.FullName) to $OrgName"
        return $true
    }

    Write-Warning "GitHub CLI doesn't support repository transfer"
    Write-Host "Please transfer the repository manually:"
    Write-Host "  1. Visit: https://github.com/$($CurrentRepo.FullName)/settings" -ForegroundColor Yellow
    Write-Host "  2. Scroll to 'Danger Zone' > 'Transfer ownership'" -ForegroundColor Yellow
    Write-Host "  3. New owner: $OrgName" -ForegroundColor Yellow
    Write-Host "  4. Confirm transfer" -ForegroundColor Yellow
    Write-Host ""

    $confirm = Read-Host "Have you transferred the repository? (y/N)"
    if ($confirm -ne 'y') {
        Write-Warning "Repository transfer skipped"
        return $false
    }

    Write-Success "Repository transferred to $OrgName/$($CurrentRepo.Name)"
    return $true
}

function New-HARCOSRepository {
    param(
        [string]$OrgName,
        [hashtable]$RepoConfig
    )

    $repoFullName = "$OrgName/$($RepoConfig.Name)"

    Write-Step "Creating repository: $repoFullName"

    if ($DryRun) {
        Write-Warning "DRY RUN: Would create repository $repoFullName"
        return $true
    }

    # Check if repository already exists
    try {
        gh repo view $repoFullName 2>&1 | Out-Null
        Write-Warning "Repository $repoFullName already exists"
        return $true
    }
    catch {
        # Repository doesn't exist, create it
    }

    # Create repository
    $topics = $RepoConfig.Topics -join ","

    try {
        gh repo create $repoFullName `
            --public `
            --description $RepoConfig.Description `
            --homepage $Config.OrgWebsite `
            --disable-issues=false `
            --disable-wiki=true

        Write-Success "Created repository $repoFullName"

        # Add topics
        gh repo edit $repoFullName --add-topic $topics
        Write-Success "Added topics: $topics"

        return $true
    }
    catch {
        Write-Error "Failed to create repository $repoFullName"
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $false
    }
}

function Enable-GitHubSponsors {
    param([string]$OrgName)

    Write-Step "Setting up GitHub Sponsors for $OrgName"

    if ($DryRun) {
        Write-Warning "DRY RUN: Would enable GitHub Sponsors"
        return $true
    }

    Write-Warning "GitHub Sponsors must be configured manually"
    Write-Host "Follow these steps:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://github.com/organizations/$OrgName/settings/sponsorship" -ForegroundColor Yellow
    Write-Host "  2. Click 'Set up GitHub Sponsors'" -ForegroundColor Yellow
    Write-Host "  3. Complete the onboarding form" -ForegroundColor Yellow
    Write-Host "  4. Configure sponsor tiers (see HARCOS_ORGANIZATION_SETUP.md)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Recommended tiers:" -ForegroundColor Cyan

    foreach ($tier in $Config.SponsorTiers) {
        Write-Host "  - $$($tier.Amount)/mo: $($tier.Name)" -ForegroundColor Gray
        Write-Host "    $($tier.Description)" -ForegroundColor DarkGray
    }

    Write-Host ""
    $confirm = Read-Host "Have you enabled GitHub Sponsors? (y/N)"
    if ($confirm -ne 'y') {
        Write-Warning "GitHub Sponsors configuration skipped"
        return $false
    }

    Write-Success "GitHub Sponsors enabled for $OrgName"
    return $true
}

function New-FUNDINGFile {
    param([string]$OrgName)

    Write-Step "Creating .github/FUNDING.yml"

    $fundingContent = @"
# GitHub Sponsors configuration for HARCOS-AI
github: $OrgName
open_collective: harcos-ai
custom: ["https://harcos.ai/sponsor", "https://harcos.ai/enterprise"]
"@

    if ($DryRun) {
        Write-Warning "DRY RUN: Would create FUNDING.yml with content:"
        Write-Host $fundingContent -ForegroundColor Gray
        return $true
    }

    $fundingPath = ".github/FUNDING.yml"

    try {
        New-Item -Path ".github" -ItemType Directory -Force | Out-Null
        Set-Content -Path $fundingPath -Value $fundingContent -Force
        Write-Success "Created $fundingPath"
        return $true
    }
    catch {
        Write-Error "Failed to create $fundingPath"
        return $false
    }
}

function Invoke-PreflightChecks {
    Write-Step "Running preflight checks"

    $checks = @(
        @{ Name = "GitHub CLI installed"; Test = { Test-GitHubCLI } }
        @{ Name = "GitHub authentication"; Test = { Test-GitHubAuth } }
        @{ Name = "Current repository info"; Test = { $null -ne (Get-CurrentRepo) } }
    )

    $allPassed = $true

    foreach ($check in $checks) {
        try {
            $result = & $check.Test
            if ($result) {
                Write-Success $check.Name
            }
            else {
                Write-Error $check.Name
                $allPassed = $false
            }
        }
        catch {
            Write-Error "$($check.Name) - $($_.Exception.Message)"
            $allPassed = $false
        }
    }

    return $allPassed
}

# ============================================================================
# MAIN DEPLOYMENT WORKFLOW
# ============================================================================

function Start-HARCOSDeployment {
    Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   HARCOS-AI Organization Deployment                         ║
║   Open tools for symbiotic intelligence                     ║
║                                                              ║
║   Version: 1.0.0                                            ║
║   Target: $($Config.OrgName.PadRight(46)) ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

    if ($DryRun) {
        Write-Warning "DRY RUN MODE - No changes will be made"
        Write-Host ""
    }

    # Phase 1: Preflight checks
    if (-not (Invoke-PreflightChecks)) {
        Write-Error "Preflight checks failed. Aborting deployment."
        return $false
    }

    # Get current repository info
    $currentRepo = Get-CurrentRepo
    if (-not $currentRepo) {
        Write-Error "Could not get current repository info"
        return $false
    }

    Write-Host ""
    Write-Host "Current Repository: $($currentRepo.FullName)" -ForegroundColor Gray
    Write-Host "Target Organization: $($Config.OrgName)" -ForegroundColor Gray
    Write-Host ""

    if (-not $DryRun) {
        $confirm = Read-Host "Continue with deployment? (y/N)"
        if ($confirm -ne 'y') {
            Write-Warning "Deployment cancelled by user"
            return $false
        }
    }

    # Phase 2: Create organization
    if (-not $SkipOrgCreation) {
        if (-not (New-HARCOSOrganization -OrgName $Config.OrgName)) {
            Write-Error "Organization creation failed"
            return $false
        }
    }
    else {
        Write-Warning "Skipping organization creation (--SkipOrgCreation)"
    }

    # Phase 3: Transfer current repository
    $transferRepo = $Config.Repositories | Where-Object { $_.IsTransfer -eq $true } | Select-Object -First 1
    if ($transferRepo) {
        Move-RepositoryToOrg -OrgName $Config.OrgName -CurrentRepo $currentRepo
    }

    # Phase 4: Create additional repositories
    $newRepos = $Config.Repositories | Where-Object { $_.IsTransfer -eq $false }
    foreach ($repo in $newRepos) {
        New-HARCOSRepository -OrgName $Config.OrgName -RepoConfig $repo
        Start-Sleep -Seconds 2  # Rate limiting
    }

    # Phase 5: Enable GitHub Sponsors
    Enable-GitHubSponsors -OrgName $Config.OrgName

    # Phase 6: Create FUNDING.yml
    New-FUNDINGFile -OrgName $Config.OrgName

    # Phase 7: Summary
    Write-Step "Deployment Summary"
    Write-Host ""
    Write-Host "Organization: https://github.com/$($Config.OrgName)" -ForegroundColor Green
    Write-Host "Landing Page: https://$($Config.OrgName.ToLower()).github.io/docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Deploy landing page (see .github/HARCOS_LANDING_PAGE_DEPLOYMENT.md)" -ForegroundColor Gray
    Write-Host "  2. Configure GitHub Sponsors tiers" -ForegroundColor Gray
    Write-Host "  3. Create Open Collective account" -ForegroundColor Gray
    Write-Host "  4. Update README.md with sponsorship badges" -ForegroundColor Gray
    Write-Host "  5. Launch announcement (Reddit, HN, Dev.to)" -ForegroundColor Gray
    Write-Host ""

    return $true
}

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

try {
    $success = Start-HARCOSDeployment

    if ($success) {
        Write-Host ""
        Write-Host "✓ Deployment completed successfully!" -ForegroundColor Green
        exit 0
    }
    else {
        Write-Host ""
        Write-Host "✗ Deployment failed or was cancelled" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "✗ Deployment error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkRed
    exit 1
}
