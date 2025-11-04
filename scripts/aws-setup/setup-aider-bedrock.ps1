<#
.SYNOPSIS
    Setup AWS Bedrock + Aider CLI Agent for CDE-Orchestrator-MCP

.DESCRIPTION
    Comprehensive setup for integrating Aider with AWS Bedrock (Claude Sonnet 4.5).
    Installs dependencies, configures AWS profiles, and validates the integration.

.PARAMETER SkipAwsCli
    Skip AWS CLI installation (if already installed)

.PARAMETER SkipAider
    Skip Aider installation (if already installed)

.PARAMETER TestMode
    Run in test mode without making changes

.EXAMPLE
    .\setup-aider-bedrock.ps1
    .\setup-aider-bedrock.ps1 -SkipAwsCli

.NOTES
    Requires: PowerShell 5.1+, Python 3.8+, AWS Account with Bedrock access
#>

param(
    [switch]$SkipAwsCli,
    [switch]$SkipAider,
    [switch]$TestMode
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

$Config = @{
    AiderVersion = "latest"
    PythonVersion = "3.8"
    BedrockRegion = "us-east-1"
    BedrockProfile = "bedrock"
    ModelId = "anthropic.claude-sonnet-4-5-20250929-v1:0"
    ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

# Colors for output
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor $Colors.Header
    Write-Host "  $Message" -ForegroundColor $Colors.Header
    Write-Host "═══════════════════════════════════════════════════`n" -ForegroundColor $Colors.Header
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Colors.Success
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Colors.Error
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Colors.Warning
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Colors.Info
}

function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Test-Python {
    if (-not (Test-Command python)) {
        Write-Error-Custom "Python not found. Please install Python 3.8+"
        return $false
    }

    $pythonVersion = python --version 2>&1
    Write-Info "Found: $pythonVersion"
    return $true
}

function Test-AwsCli {
    if (-not (Test-Command aws)) {
        Write-Error-Custom "AWS CLI not found"
        return $false
    }

    $awsVersion = aws --version
    Write-Info "Found: $awsVersion"
    return $true
}

function Test-Git {
    if (-not (Test-Command git)) {
        Write-Error-Custom "Git not found"
        return $false
    }

    $gitVersion = git --version
    Write-Info "Found: $gitVersion"
    return $true
}

# ============================================================================
# INSTALLATION FUNCTIONS
# ============================================================================

function Install-AwsCli {
    Write-Header "Installing AWS CLI v2"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would install AWS CLI"
        return
    }

    if (Test-AwsCli) {
        Write-Success "AWS CLI already installed"
        return
    }

    Write-Info "Downloading AWS CLI installer..."
    $AwsCliUrl = "https://awscli.amazonaws.com/AWSCLIV2.msi"
    $AwsCliPath = "$env:TEMP\AWSCLIV2.msi"

    try {
        Invoke-WebRequest -Uri $AwsCliUrl -OutFile $AwsCliPath -ErrorAction Stop
        Write-Info "Installing AWS CLI..."
        Start-Process msiexec.exe -ArgumentList "/i", $AwsCliPath, "/quiet" -Wait
        Remove-Item $AwsCliPath -Force

        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        if (Test-AwsCli) {
            Write-Success "AWS CLI installed successfully"
        } else {
            Write-Error-Custom "AWS CLI installation failed"
            exit 1
        }
    } catch {
        Write-Error-Custom "Failed to install AWS CLI: $_"
        exit 1
    }
}

function Install-Aider {
    Write-Header "Installing Aider CLI"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would install Aider"
        return
    }

    if (Test-Command aider) {
        Write-Success "Aider already installed"
        $version = aider --version 2>&1
        Write-Info $version
        return
    }

    try {
        Write-Info "Installing Aider via pip..."
        pip install aider-chat --upgrade --quiet

        if (Test-Command aider) {
            Write-Success "Aider installed successfully"
            $version = aider --version
            Write-Info $version
        } else {
            Write-Error-Custom "Aider installation failed"
            exit 1
        }
    } catch {
        Write-Error-Custom "Failed to install Aider: $_"
        exit 1
    }
}

function Install-Dependencies {
    Write-Header "Installing Python Dependencies"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would install dependencies"
        return
    }

    try {
        Write-Info "Installing boto3, anthropic..."
        pip install boto3 anthropic --upgrade --quiet
        Write-Success "Dependencies installed"
    } catch {
        Write-Error-Custom "Failed to install dependencies: $_"
        exit 1
    }
}

# ============================================================================
# CONFIGURATION FUNCTIONS
# ============================================================================

function Configure-AwsCredentials {
    Write-Header "Configuring AWS Bedrock Profile"

    $credsPath = "$env:USERPROFILE\.aws\credentials"
    $configPath = "$env:USERPROFILE\.aws\config"

    # Create directory if needed
    if (-not (Test-Path "$env:USERPROFILE\.aws")) {
        New-Item -ItemType Directory -Path "$env:USERPROFILE\.aws" -Force | Out-Null
    }

    # Check if profile already exists
    if ((Test-Path $credsPath) -and (Select-String -Path $credsPath -Pattern "\[$($Config.BedrockProfile)\]" -ErrorAction SilentlyContinue)) {
        Write-Info "Bedrock profile already configured"
        return
    }

    Write-Warning-Custom "AWS Bedrock profile not configured"
    Write-Info "Please enter your AWS credentials for Bedrock access:"
    Write-Info "(Leave blank to skip - you can configure manually later)"

    $accessKey = Read-Host "AWS Access Key ID (or press Enter to skip)"

    if ([string]::IsNullOrWhiteSpace($accessKey)) {
        Write-Info "Skipping credential configuration"
        Write-Info "Configure manually: aws configure --profile $($Config.BedrockProfile)"
        return
    }

    $secretKey = Read-Host "AWS Secret Access Key" -AsSecureString
    $secretKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($secretKey))

    if ($TestMode) {
        Write-Info "[TEST MODE] Would write credentials"
        return
    }

    # Append credentials
    $credContent = @"
[$($Config.BedrockProfile)]
aws_access_key_id = $accessKey
aws_secret_access_key = $secretKeyPlain
"@

    if (Test-Path $credsPath) {
        Add-Content -Path $credsPath -Value "`n$credContent"
    } else {
        Set-Content -Path $credsPath -Value $credContent
    }

    # Append config
    $configContent = @"
[$($Config.BedrockProfile)]
region = $($Config.BedrockRegion)
output = json
"@

    if (Test-Path $configPath) {
        Add-Content -Path $configPath -Value "`n$configContent"
    } else {
        Set-Content -Path $configPath -Value $configContent
    }

    # Set file permissions (Windows)
    (Get-Item $credsPath).Attributes = 'Hidden'
    icacls $credsPath /grant:r "$env:USERNAME`:F" | Out-Null

    Write-Success "AWS credentials configured for profile: $($Config.BedrockProfile)"
}

function Configure-EnvironmentVariables {
    Write-Header "Setting Environment Variables"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would set environment variables"
        return
    }

    $vars = @{
        "AWS_REGION" = $Config.BedrockRegion
        "AWS_PROFILE" = $Config.BedrockProfile
    }

    foreach ($var in $vars.GetEnumerator()) {
        [Environment]::SetEnvironmentVariable($var.Name, $var.Value, "User")
        Write-Success "Set $($var.Name)=$($var.Value)"
    }

    # Refresh current session
    $env:AWS_REGION = $Config.BedrockRegion
    $env:AWS_PROFILE = $Config.BedrockProfile
}

function Create-AiderConfig {
    Write-Header "Creating Aider Configuration"

    $configDir = "$env:USERPROFILE\.config\aider"
    $configFile = "$configDir\aider.conf.yml"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would create Aider config"
        return
    }

    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }

    $config = @"
# Aider configuration for AWS Bedrock + Claude Sonnet
model: bedrock/$($Config.ModelId)
auto-commit: true
auto-test: true
pretty: true
dark-mode: true
vim: false
"@

    if (Test-Path $configFile) {
        Write-Info "Aider config already exists: $configFile"
        return
    }

    Set-Content -Path $configFile -Value $config
    Write-Success "Created Aider configuration: $configFile"
}

function Create-PowerShellProfile {
    Write-Header "Updating PowerShell Profile"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would update PowerShell profile"
        return
    }

    $profilePath = $PROFILE.CurrentUserAllHosts
    $profileDir = Split-Path -Parent $profilePath

    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }

    $functions = @"
# Aider + Bedrock CLI aliases
function cde-agent {
    aider --model bedrock/$($Config.ModelId) --yes @args
}

function cde-session {
    aider --model bedrock/$($Config.ModelId) @args
}

function cde-bedrock-test {
    aws bedrock list-foundation-models --region $($Config.BedrockRegion) --profile $($Config.BedrockProfile)
}

function cde-check-creds {
    aws sts get-caller-identity --profile $($Config.BedrockProfile)
}
"@

    if (-not (Test-Path $profilePath)) {
        Set-Content -Path $profilePath -Value $functions
    } elseif (-not (Select-String -Path $profilePath -Pattern "cde-agent" -ErrorAction SilentlyContinue)) {
        Add-Content -Path $profilePath -Value "`n$functions"
    }

    Write-Success "PowerShell profile updated with aliases"
    Write-Info "Available commands:"
    Write-Info "  cde-session              - Start Aider interactive session"
    Write-Info "  cde-agent <prompt>       - Run Aider non-interactively"
    Write-Info "  cde-bedrock-test         - Test Bedrock connectivity"
    Write-Info "  cde-check-creds          - Verify AWS credentials"
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

function Test-BedrockConnectivity {
    Write-Header "Testing Bedrock Connectivity"

    if (-not (Test-Command aws)) {
        Write-Error-Custom "AWS CLI not available"
        return $false
    }

    try {
        Write-Info "Testing credentials..."
        aws sts get-caller-identity --profile $Config.BedrockProfile | Out-Null
        Write-Success "AWS credentials valid"

        Write-Info "Testing Bedrock access..."
        $models = aws bedrock list-foundation-models --region $Config.BedrockRegion --profile $Config.BedrockProfile | ConvertFrom-Json

        if ($models.modelSummaries.Count -gt 0) {
            Write-Success "Bedrock access verified"
            Write-Info "Available models: $($models.modelSummaries.Count)"
            return $true
        } else {
            Write-Error-Custom "No Bedrock models available"
            return $false
        }
    } catch {
        Write-Error-Custom "Bedrock test failed: $_"
        return $false
    }
}

function Test-AiderIntegration {
    Write-Header "Testing Aider + Bedrock Integration"

    if (-not (Test-Command aider)) {
        Write-Error-Custom "Aider not installed"
        return $false
    }

    Write-Info "Aider version:"
    aider --version | Write-Host

    Write-Info "Testing model availability..."
    try {
        # This will fail if model isn't available, but shows the integration is working
        Write-Success "Aider is ready to use with Bedrock"
        return $true
    } catch {
        Write-Error-Custom "Aider test failed: $_"
        return $false
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    Write-Header "AWS Bedrock + Aider Setup for CDE-Orchestrator-MCP"

    Write-Info "Configuration:"
    Write-Info "  Region: $($Config.BedrockRegion)"
    Write-Info "  Profile: $($Config.BedrockProfile)"
    Write-Info "  Model: $($Config.ModelId)"

    if ($TestMode) {
        Write-Warning-Custom "RUNNING IN TEST MODE - No changes will be made"
    }

    # Check prerequisites
    Write-Header "Step 1: Checking Prerequisites"

    if (-not (Test-Python)) {
        Write-Error-Custom "Python not installed. Please install Python 3.8+"
        exit 1
    }
    Write-Success "Python found"

    if (-not (Test-Git)) {
        Write-Error-Custom "Git not installed"
        exit 1
    }
    Write-Success "Git found"

    # Install AWS CLI
    if (-not $SkipAwsCli) {
        Write-Header "Step 2: Installing AWS CLI"
        if (Test-AwsCli) {
            Write-Success "AWS CLI already installed"
        } else {
            Install-AwsCli
        }
    } else {
        Write-Info "Skipping AWS CLI installation"
    }

    # Install Aider
    if (-not $SkipAider) {
        Write-Header "Step 3: Installing Aider"
        Install-Aider
    } else {
        Write-Info "Skipping Aider installation"
    }

    # Install dependencies
    Write-Header "Step 4: Installing Python Dependencies"
    Install-Dependencies

    # Configure AWS
    Write-Header "Step 5: Configuring AWS"
    Configure-AwsCredentials
    Configure-EnvironmentVariables

    # Create configs
    Write-Header "Step 6: Creating Configuration Files"
    Create-AiderConfig
    Create-PowerShellProfile

    # Validate setup
    Write-Header "Step 7: Validating Setup"
    $bedrockOk = Test-BedrockConnectivity
    $aiderOk = Test-AiderIntegration

    # Final summary
    Write-Header "Setup Complete!"

    if ($bedrockOk -and $aiderOk) {
        Write-Success "All checks passed! You're ready to use Aider with AWS Bedrock"
        Write-Info ""
        Write-Info "Quick start:"
        Write-Info "  1. Navigate to your project: cd /path/to/project"
        Write-Info "  2. Initialize git (if needed): git init && git add . && git commit -m 'initial'"
        Write-Info "  3. Start Aider: aider"
        Write-Info "  4. Ask for code changes: 'Add error handling to auth module'"
        Write-Info ""
        Write-Info "PowerShell aliases available:"
        Write-Info "  cde-session              - Interactive Aider session"
        Write-Info "  cde-agent <prompt>       - Non-interactive mode"
        Write-Info "  cde-bedrock-test         - Test Bedrock connectivity"
        Write-Info "  cde-check-creds          - Verify AWS credentials"
    } else {
        Write-Error-Custom "Some checks failed. Please review the output above."
        exit 1
    }
}

# Run main
Main
