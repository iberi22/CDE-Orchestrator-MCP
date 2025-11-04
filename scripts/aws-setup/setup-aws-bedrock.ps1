#!/usr/bin/env pwsh
<#
.SYNOPSIS
    AWS CLI Bedrock Profile Configuration Script
.DESCRIPTION
    Configures AWS CLI with a 'bedrock' profile for Claude Bedrock access.
    Supports both IAM user credentials and interactive setup.
.PARAMETER AccessKeyId
    AWS Access Key ID (optional - prompted if not provided)
.PARAMETER SecretAccessKey
    AWS Secret Access Key (optional - prompted if not provided)
.PARAMETER Region
    AWS Region (default: us-east-1)
.PARAMETER ProfileName
    AWS Profile name (default: bedrock)
.EXAMPLE
    .\setup-aws-bedrock.ps1 -Region us-east-1 -ProfileName bedrock
    .\setup-aws-bedrock.ps1 -AccessKeyId AKIA... -SecretAccessKey wJalr...
#>

param(
    [string]$AccessKeyId,
    [string]$SecretAccessKey,
    [string]$Region = "us-east-1",
    [string]$ProfileName = "bedrock"
)

# Colors for output
$colors = @{
    Success = [System.ConsoleColor]::Green
    Error   = [System.ConsoleColor]::Red
    Warning = [System.ConsoleColor]::Yellow
    Info    = [System.ConsoleColor]::Cyan
}

function Write-ColorOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $true)]
        [System.ConsoleColor]$Color
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-AwsCliInstalled {
    Write-ColorOutput "🔍 Checking AWS CLI installation..." $colors.Info

    $awsCmd = Get-Command aws -ErrorAction SilentlyContinue
    if ($null -eq $awsCmd) {
        Write-ColorOutput "❌ AWS CLI is not installed or not in PATH" $colors.Error
        Write-Host ""
        Write-Host "Install AWS CLI v2:"
        Write-Host "  Option 1 (recommended): Download from https://aws.amazon.com/cli/"
        Write-Host "  Option 2 (winget): winget install Amazon.AWSCLI"
        Write-Host "  Option 3 (chocolatey): choco install awscli"
        return $false
    }

    $version = & aws --version 2>&1
    Write-ColorOutput "✓ AWS CLI found: $version" $colors.Success
    return $true
}

function Get-Credentials {
    Write-ColorOutput "`n📋 AWS Credentials Setup" $colors.Info

    if ([string]::IsNullOrEmpty($AccessKeyId)) {
        $AccessKeyId = Read-Host "Enter AWS Access Key ID"
        if ([string]::IsNullOrEmpty($AccessKeyId)) {
            Write-ColorOutput "❌ Access Key ID cannot be empty" $colors.Error
            return $null
        }
    }

    if ([string]::IsNullOrEmpty($SecretAccessKey)) {
        $prompt = Read-Host "Enter AWS Secret Access Key" -AsSecureString
        $SecretAccessKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($prompt)
        )
        if ([string]::IsNullOrEmpty($SecretAccessKey)) {
            Write-ColorOutput "❌ Secret Access Key cannot be empty" $colors.Error
            return $null
        }
    }

    return @{
        AccessKeyId     = $AccessKeyId
        SecretAccessKey = $SecretAccessKey
    }
}

function Configure-AwsProfile {
    param(
        [hashtable]$Credentials,
        [string]$ProfileName,
        [string]$Region
    )

    Write-ColorOutput "`n⚙️  Configuring AWS profile '$ProfileName'..." $colors.Info

    try {
        # Set credentials
        & aws configure set aws_access_key_id $Credentials.AccessKeyId --profile $ProfileName
        & aws configure set aws_secret_access_key $Credentials.SecretAccessKey --profile $ProfileName
        & aws configure set region $Region --profile $ProfileName
        & aws configure set output json --profile $ProfileName

        Write-ColorOutput "✓ Profile '$ProfileName' configured successfully" $colors.Success
        return $true
    }
    catch {
        Write-ColorOutput "❌ Failed to configure profile: $_" $colors.Error
        return $false
    }
}

function Test-BedrockAccess {
    param(
        [string]$ProfileName,
        [string]$Region
    )

    Write-ColorOutput "`n🧪 Testing Bedrock access..." $colors.Info

    try {
        $modelsList = & aws bedrock list-foundation-models --region $Region --profile $ProfileName 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Successfully connected to Bedrock service" $colors.Success

            # Try to find Claude Sonnet model
            if ($modelsList -match "anthropic.claude-3-sonnet") {
                Write-ColorOutput "✓ Claude Sonnet 3 model is available" $colors.Success
            }
            elseif ($modelsList -match "anthropic.claude") {
                Write-ColorOutput "⚠ Claude model available (may need to request access)" $colors.Warning
            }
            else {
                Write-ColorOutput "⚠ No Claude models found (request access from AWS console)" $colors.Warning
            }

            return $true
        }
        else {
            Write-ColorOutput "❌ Failed to access Bedrock: $modelsList" $colors.Error
            return $false
        }
    }
    catch {
        Write-ColorOutput "❌ Error testing Bedrock access: $_" $colors.Error
        return $false
    }
}

function Show-Configuration {
    param(
        [string]$ProfileName,
        [string]$Region
    )

    Write-ColorOutput "`n📋 Configuration Summary" $colors.Info
    Write-Host ""
    Write-Host "Profile Name:        $ProfileName"
    Write-Host "Region:              $Region"
    Write-Host "Credentials file:    $env:USERPROFILE\.aws\credentials"
    Write-Host "Config file:         $env:USERPROFILE\.aws\config"
    Write-Host ""
    Write-ColorOutput "Environment variables:" $colors.Info
    Write-Host "  Export the profile as default:"
    Write-Host "    `$env:AWS_PROFILE = '$ProfileName'"
    Write-Host "    `$env:AWS_REGION = '$Region'"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  aws bedrock list-foundation-models --profile $ProfileName"
    Write-Host ""
}

function Save-Configuration {
    param(
        [string]$ProfileName,
        [string]$Region
    )

    Write-ColorOutput "`n💾 Saving configuration to PowerShell profile..." $colors.Info

    $profilePath = $PROFILE.CurrentUserAllHosts
    $profileDir = Split-Path $profilePath

    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }

    $configScript = @"
# AWS Bedrock Configuration
`$env:AWS_PROFILE = '$ProfileName'
`$env:AWS_REGION = '$Region'

# Bedrock CLI function
function bedrock-test {
    Write-Host "Testing Bedrock with profile: `$env:AWS_PROFILE" -ForegroundColor Cyan
    aws bedrock list-foundation-models --profile `$env:AWS_PROFILE --region `$env:AWS_REGION
}

function bedrock-invoke {
    param([string]`$Prompt, [string]`$Model = "anthropic.claude-3-sonnet-20240229-v1:0")

    `$payload = @{
        prompt = `$Prompt
        max_tokens = 2048
    } | ConvertTo-Json

    Write-Host "Invoking `$Model..." -ForegroundColor Cyan
    aws bedrock-runtime invoke-model `
        --model-id `$Model `
        --body `$payload `
        --profile `$env:AWS_PROFILE `
        --region `$env:AWS_REGION `
        /dev/stdout | jq .
}

# Alias
Set-Alias -Name bedrock = bedrock-test -Force
"@

    if (-not (Test-Path $profilePath)) {
        New-Item -ItemType File -Path $profilePath -Force | Out-Null
    }

    # Append to profile if not already present
    $profileContent = Get-Content $profilePath -ErrorAction SilentlyContinue
    if ($profileContent -notmatch "AWS Bedrock Configuration") {
        Add-Content -Path $profilePath -Value "`n$configScript"
        Write-ColorOutput "✓ PowerShell profile updated" $colors.Success
    }
    else {
        Write-ColorOutput "⚠ PowerShell profile already contains AWS Bedrock configuration" $colors.Warning
    }
}

# Main execution
Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   AWS CLI Bedrock Profile Setup       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check AWS CLI
if (-not (Test-AwsCliInstalled)) {
    exit 1
}

# Step 2: Get credentials
$credentials = Get-Credentials
if ($null -eq $credentials) {
    exit 1
}

# Step 3: Configure profile
if (-not (Configure-AwsProfile -Credentials $credentials -ProfileName $ProfileName -Region $Region)) {
    exit 1
}

# Step 4: Test access
Test-BedrockAccess -ProfileName $ProfileName -Region $Region | Out-Null

# Step 5: Show configuration
Show-Configuration -ProfileName $ProfileName -Region $Region

# Step 6: Save to PowerShell profile
Save-Configuration -ProfileName $ProfileName -Region $Region

Write-ColorOutput "`n✅ AWS Bedrock profile setup complete!" $colors.Success
Write-ColorOutput "Next steps:" $colors.Info
Write-Host "  1. Close and reopen PowerShell to load the new configuration"
Write-Host "  2. Run: bedrock-test"
Write-Host "  3. Request access to Claude model if needed from AWS Console"
