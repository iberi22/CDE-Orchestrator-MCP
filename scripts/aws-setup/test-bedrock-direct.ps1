#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test AWS Bedrock connectivity directly via AWS CLI
.DESCRIPTION
    Invokes Claude Sonnet 4.5 on Bedrock using AWS CLI to verify full connectivity
#>

param(
    [string]$Prompt = "Say 'Hello from AWS Bedrock' in a creative way (max 10 words)",
    [string]$ModelId = "anthropic.claude-sonnet-4-5-20250929-v1:0",
    [string]$Region = "us-east-1",
    [string]$Profile = "bedrock"
)

# Color functions
function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Error-Custom { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warning-Custom { param($Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }

Write-Host "`n═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Testing AWS Bedrock Connectivity" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════`n" -ForegroundColor Cyan

# Test 1: AWS credentials
Write-Info "Test 1: Verificando credenciales AWS..."
try {
    $identity = aws sts get-caller-identity --profile $Profile 2>&1 | ConvertFrom-Json
    if ($LASTEXITCODE -eq 0) {
        Write-Success "AWS User: $($identity.Arn)"
        Write-Success "Account: $($identity.Account)"
    } else {
        Write-Error-Custom "AWS credentials failed"
        exit 1
    }
} catch {
    Write-Error-Custom "Error verificando credenciales: $_"
    exit 1
}

# Test 2: Bedrock access
Write-Info "`nTest 2: Verificando acceso a Bedrock..."
try {
    $models = aws bedrock list-foundation-models --region $Region --profile $Profile 2>&1 | ConvertFrom-Json
    $claudeModels = $models.modelSummaries | Where-Object { $_.modelId -like "anthropic.claude*" }
    Write-Success "Claude models disponibles: $($claudeModels.Count)"

    # Verificar que nuestro modelo específico está disponible
    $ourModel = $claudeModels | Where-Object { $_.modelId -eq $ModelId }
    if ($ourModel) {
        Write-Success "Modelo objetivo encontrado: $($ourModel.modelName)"
    } else {
        Write-Warning-Custom "Modelo $ModelId no encontrado en la lista"
    }
} catch {
    Write-Error-Custom "Error verificando Bedrock: $_"
    exit 1
}

# Test 3: Invoke Bedrock Model
Write-Info "`nTest 3: Invocando modelo Bedrock..."
Write-Info "Prompt: `"$Prompt`""

# Create payload for Bedrock
$payload = @{
    anthropic_version = "bedrock-2023-05-31"
    max_tokens = 150
    messages = @(
        @{
            role = "user"
            content = $Prompt
        }
    )
} | ConvertTo-Json -Depth 10 -Compress

# Save to temp file (required for AWS CLI)
$tempFile = [System.IO.Path]::GetTempFileName()
$responseFile = [System.IO.Path]::GetTempFileName()

try {
    $payload | Out-File -FilePath $tempFile -Encoding utf8 -NoNewline

    $response = aws bedrock-runtime invoke-model `
        --model-id $ModelId `
        --body "file://$tempFile" `
        --region $Region `
        --profile $Profile `
        --cli-binary-format raw-in-base64-out `
        $responseFile 2>&1

    if ($LASTEXITCODE -eq 0) {
        $result = Get-Content $responseFile | ConvertFrom-Json
        $message = $result.content[0].text

        Write-Host "`n┌─────────────────────────────────────────┐" -ForegroundColor Cyan
        Write-Host "│  Bedrock Response                       │" -ForegroundColor Cyan
        Write-Host "└─────────────────────────────────────────┘" -ForegroundColor Cyan
        Write-Host "$message" -ForegroundColor White
        Write-Host ""

        Write-Success "Bedrock invocation successful!"
        Write-Info "Tokens used: Input=$($result.usage.input_tokens), Output=$($result.usage.output_tokens)"
    } else {
        Write-Error-Custom "Bedrock invocation failed"
        Write-Host "Error: $response" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Error-Custom "Error invocando Bedrock: $_"
    exit 1
} finally {
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    Remove-Item $responseFile -ErrorAction SilentlyContinue
}

Write-Host "`n═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  All Tests Passed!" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════`n" -ForegroundColor Cyan

Write-Info "Your Bedrock environment is ready to use:"
Write-Info "  • AWS Profile: $Profile"
Write-Info "  • Region: $Region"
Write-Info "  • Model: $ModelId"
Write-Info "  • Claude CLI: $(claude --version)"
