<#
.SYNOPSIS
    Professional AWS Bedrock + Claude Sonnet 4.5 Connectivity Test
.DESCRIPTION
    Tests complete Bedrock integration following Anthropic's official best practices
    Based on: https://docs.anthropic.com/en/api/claude-on-amazon-bedrock
.PARAMETER Prompt
    Test prompt to send to Claude
.PARAMETER ModelId
    Claude model ID (default: Sonnet 4.5)
.PARAMETER Region
    AWS region (default: us-east-1)
.PARAMETER Profile
    AWS CLI profile (default: bedrock)
#>

param(
    [string]$Prompt = "Say 'Hello from AWS Bedrock' in a creative way (max 10 words)",
    [string]$ModelId = "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    [string]$Region = "us-east-1",
    [string]$Profile = "bedrock"
)

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   AWS Bedrock + Claude Connectivity Test" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Test 1: AWS Credentials
Write-Host "[1/4] Verificando credenciales AWS..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity --profile $Profile 2>&1 | ConvertFrom-Json
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Usuario AWS: $($identity.Arn)" -ForegroundColor Green
        Write-Host "[OK] Cuenta: $($identity.Account)" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Credenciales AWS fallaron" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Error verificando credenciales: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Bedrock Access
Write-Host "`n[2/4] Verificando acceso a Bedrock..." -ForegroundColor Yellow
try {
    $models = aws bedrock list-foundation-models --region $Region --profile $Profile 2>&1 | ConvertFrom-Json
    $claudeModels = $models.modelSummaries | Where-Object { $_.modelId -like "anthropic.claude*" }
    Write-Host "[OK] Claude models disponibles: $($claudeModels.Count)" -ForegroundColor Green

    $ourModel = $claudeModels | Where-Object { $_.modelId -eq $ModelId }
    if ($ourModel) {
        Write-Host "[OK] Modelo objetivo encontrado: $($ourModel.modelName)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Modelo $ModelId no encontrado en la lista" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Error verificando Bedrock: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Claude CLI
Write-Host "`n[3/4] Verificando Claude CLI..." -ForegroundColor Yellow
try {
    $version = claude --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Claude CLI version: $version" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Claude CLI no encontrado (opcional)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARN] Claude CLI no instalado (opcional para este test)" -ForegroundColor Yellow
}

# Test 4: Invoke Bedrock Model (Official Anthropic Method)
Write-Host "`n[4/4] Invocando modelo Bedrock..." -ForegroundColor Yellow
Write-Host "[INFO] Usando Messages API (Anthropic best practice)" -ForegroundColor Cyan
Write-Host "[INFO] Prompt: `"$Prompt`"" -ForegroundColor Cyan

# Create payload using Anthropic Messages API format
# Reference: https://docs.anthropic.com/en/api/claude-on-amazon-bedrock#making-requests
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

$tempFile = [System.IO.Path]::GetTempFileName()
$responseFile = [System.IO.Path]::GetTempFileName()

try {
    $payload | Out-File -FilePath $tempFile -Encoding utf8 -NoNewline

    # Invoke using AWS CLI (official method)
    $invokeResult = aws bedrock-runtime invoke-model `
        --model-id $ModelId `
        --body "file://$tempFile" `
        --region $Region `
        --profile $Profile `
        --cli-binary-format raw-in-base64-out `
        $responseFile 2>&1

    if ($LASTEXITCODE -eq 0) {
        $result = Get-Content $responseFile | ConvertFrom-Json
        $message = $result.content[0].text

        Write-Host "`n+------------------------------------------+" -ForegroundColor Cyan
        Write-Host "|  Bedrock Response                        |" -ForegroundColor Cyan
        Write-Host "+------------------------------------------+" -ForegroundColor Cyan
        Write-Host "$message" -ForegroundColor White
        Write-Host ""

        Write-Host "[OK] Bedrock invocation successful!" -ForegroundColor Green
        Write-Host "[INFO] Tokens: Input=$($result.usage.input_tokens), Output=$($result.usage.output_tokens)" -ForegroundColor Cyan
    } else {
        Write-Host "[ERROR] Bedrock invocation failed" -ForegroundColor Red
        Write-Host "Error: $invokeResult" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Error invocando Bedrock: $_" -ForegroundColor Red
    exit 1
} finally {
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    Remove-Item $responseFile -ErrorAction SilentlyContinue
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   All Tests Passed!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Su entorno Bedrock está listo:" -ForegroundColor Cyan
Write-Host "  * AWS Profile: $Profile" -ForegroundColor White
Write-Host "  * Region: $Region" -ForegroundColor White
Write-Host "  * Model: $ModelId" -ForegroundColor White
Write-Host "  * Documentation: https://docs.anthropic.com/en/api/claude-on-amazon-bedrock`n" -ForegroundColor White
