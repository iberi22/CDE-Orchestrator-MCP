#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Lanzar terminal con entorno Bedrock configurado
.DESCRIPTION
    Abre PowerShell con Oh My Posh, AWS profile cargado y CloudCode CLI listo
#>

# Cargar variables
$env:AWS_PROFILE = "bedrock"
$env:AWS_REGION = "us-east-1"
$env:CLOUDCODE_PROVIDER = "bedrock"
$env:CLOUDCODE_MODEL = "anthropic.claude-sonnet-4-5-20250929-v1:0"

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Bedrock Development Environment     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "AWS Profile: $env:AWS_PROFILE" -ForegroundColor Yellow
Write-Host "AWS Region:  $env:AWS_REGION" -ForegroundColor Yellow
Write-Host "Model:       $env:CLOUDCODE_MODEL" -ForegroundColor Yellow
Write-Host ""
Write-Host "Comandos disponibles:"
Write-Host "  cloudcode-test      - Test Bedrock connectivity"
Write-Host "  cloudcode-run       - Run CloudCode with Bedrock"
Write-Host "  bedrock-models      - List available models"
Write-Host ""

# Cargar perfil Oh My Posh si existe
if (Test-Path $PROFILE.CurrentUserAllHosts) {
    . $PROFILE.CurrentUserAllHosts
}
