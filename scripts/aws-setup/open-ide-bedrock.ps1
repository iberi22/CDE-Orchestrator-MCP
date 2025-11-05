#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Open IDE (VS Code o Zed) con entorno Bedrock
#>

param(
    [ValidateSet("code", "zed")]
    [string]$IDE = "code",
    [string]$ProjectPath = "."
)

# Cargar variables de entorno
$env:AWS_PROFILE = "bedrock"
$env:AWS_REGION = "us-east-1"
$env:CLOUDCODE_PROVIDER = "bedrock"
$env:CLOUDCODE_MODEL = "anthropic.claude-sonnet-4-5-20250929-v1:0"

Write-Host "Opening $IDE with Bedrock environment..." -ForegroundColor Cyan

if ($IDE -eq "code") {
    code $ProjectPath
} elseif ($IDE -eq "zed") {
    zed $ProjectPath
}
