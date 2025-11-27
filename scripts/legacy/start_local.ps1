#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start Nexus AI MCP Server (Local Mode)

.DESCRIPTION
    Starts the Nexus AI MCP Server in local mode without Docker.
    Automatically activates virtual environment and sets up environment.

.PARAMETER Validate
    Run validation tests before starting the server

.PARAMETER Port
    Port to run the server on (default: 8000)

.EXAMPLE
    .\start_local.ps1
    Start server on default port 8000

.EXAMPLE
    .\start_local.ps1 -Validate
    Run validation tests, then start server

.EXAMPLE
    .\start_local.ps1 -Port 9000
    Start server on port 9000
#>

[CmdletBinding()]
param(
    [switch]$Validate,
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Failure { param($msg) Write-Host "[FAIL] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "NEXUS AI - LOCAL SERVER STARTUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
Write-Info "Checking Python installation..."
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Failure "Python not found. Please install Python 3.11+"
    exit 1
}
Write-Success "Python detected: $pythonVersion"

# 2. Check virtual environment
Write-Info "Checking virtual environment..."
if (-not (Test-Path ".venv")) {
    Write-Failure "Virtual environment not found at .venv"
    Write-Warning "Run: python -m venv .venv"
    exit 1
}
Write-Success "Virtual environment exists"

# 3. Activate virtual environment
Write-Info "Activating virtual environment..."
try {
    & .\.venv\Scripts\Activate.ps1
    Write-Success "Virtual environment activated"
} catch {
    Write-Failure "Failed to activate virtual environment: $_"
    exit 1
}

# 4. Set PYTHONPATH
Write-Info "Setting PYTHONPATH..."
$env:PYTHONPATH = "$PWD\src"
Write-Success "PYTHONPATH set to: $env:PYTHONPATH"

# 5. Check Rust module
Write-Info "Checking Rust module..."
$rustCheck = python -c "import cde_rust_core; print('OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Rust module not compiled. Compiling now..."
    Set-Location rust_core
    maturin develop --release
    Set-Location ..

    $rustCheck2 = python -c "import cde_rust_core; print('OK')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Rust module compilation failed"
        exit 1
    }
}
Write-Success "Rust module available"

# 6. Run validation (if requested)
if ($Validate) {
    Write-Info "Running validation tests..."
    python validate_local.py

    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Validation failed. Fix issues before starting server."
        exit 1
    }
    Write-Success "All validation tests passed"
    Write-Host ""
}

# 7. Check port availability
Write-Info "Checking port $Port..."
$portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Warning "Port $Port is already in use"
    Write-Info "Choose a different port with: .\start_local.ps1 -Port <number>"
    exit 1
}
Write-Success "Port $Port is available"

# 8. Start server
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "STARTING NEXUS AI MCP SERVER" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Info "Server will start on: http://localhost:$Port"
Write-Info "Press Ctrl+C to stop the server"
Write-Host ""

$env:PORT = $Port
python src/server.py
