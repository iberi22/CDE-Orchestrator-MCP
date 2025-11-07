# CDE Rust Core Setup Script
# Configures the Rust extension module for high-performance operations

Write-Host "Setting up CDE Rust Core..." -ForegroundColor Green

# Check if maturin is installed
if (!(Get-Command maturin -ErrorAction SilentlyContinue)) {
    Write-Host "Installing maturin..." -ForegroundColor Yellow
    pip install maturin
}

# Navigate to the Rust core directory
Set-Location "$PSScriptRoot\..\..\src\rust_core"

# Build the Rust extension in development mode
Write-Host "Building Rust extension..." -ForegroundColor Yellow
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
maturin develop --release

if ($LASTEXITCODE -eq 0) {
    Write-Host "Rust core setup complete!" -ForegroundColor Green
    Write-Host "The cde_rust_core module is now available for import." -ForegroundColor Cyan
} else {
    Write-Host "Failed to build Rust extension" -ForegroundColor Red
    exit 1
}
