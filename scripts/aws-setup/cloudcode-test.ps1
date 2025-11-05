#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test CloudCode CLI con AWS Bedrock
#>

param([string]$Prompt = "Hello, write a simple Python function")

Write-Host "Testing CloudCode CLI with Bedrock..." -ForegroundColor Cyan
Write-Host "Provider: bedrock" -ForegroundColor Yellow
Write-Host "Model: anthropic.claude-sonnet-4-5-20250929-v1:0" -ForegroundColor Yellow
Write-Host "Prompt: $Prompt" -ForegroundColor Yellow
Write-Host ""

# Ejecutar CloudCode
claude-code run --provider bedrock --model anthropic.claude-sonnet-4-5-20250929-v1:0 --prompt "$Prompt"
