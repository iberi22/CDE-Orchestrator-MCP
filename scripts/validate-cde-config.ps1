# validate-cde-config.ps1
# Validates CDE Orchestrator MCP configuration
# Usage: .\validate-cde-config.ps1 [-ProjectPath "path/to/project"]

param(
    [string]$ProjectPath = "."
)

Write-Host "`n🔍 CDE Configuration Validator" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Push-Location $ProjectPath

# Check 1: mcp.json exists
Write-Host "[1/6] Checking mcp.json..." -NoNewline
$mcpPath = ".vscode\mcp.json"
if (!(Test-Path $mcpPath)) {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      File not found: $mcpPath"
    Write-Host "`n💡 Solution: Create .vscode\mcp.json in your project root"
    Pop-Location
    exit 1
}
Write-Host " ✅ OK" -ForegroundColor Green

# Check 2: Valid JSON
Write-Host "[2/6] Validating JSON syntax..." -NoNewline
try {
    $config = Get-Content $mcpPath | ConvertFrom-Json
    Write-Host " ✅ OK" -ForegroundColor Green
} catch {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      Invalid JSON: $($_.Exception.Message)"
    Pop-Location
    exit 1
}

# Check 3: CDE_Orchestrator server configured
Write-Host "[3/6] Checking server configuration..." -NoNewline
if (!$config.servers.CDE_Orchestrator) {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      CDE_Orchestrator server not found"
    Write-Host "`n💡 Solution: Add CDE_Orchestrator to servers section"
    Pop-Location
    exit 1
}
Write-Host " ✅ OK" -ForegroundColor Green

# Check 4: Required fields present
Write-Host "[4/6] Checking required fields..." -NoNewline
$server = $config.servers.CDE_Orchestrator
if (!$server.command -or !$server.args -or !$server.env) {
    Write-Host " ❌ FAILED" -ForegroundColor Red
    Write-Host "      Missing required fields (command, args, or env)"
    Pop-Location
    exit 1
}
Write-Host " ✅ OK" -ForegroundColor Green

# Check 5: PYTHONPATH set
Write-Host "[5/6] Checking PYTHONPATH..." -NoNewline
if (!$server.env.PYTHONPATH) {
    Write-Host " ⚠️  WARNING" -ForegroundColor Yellow
    Write-Host "      PYTHONPATH not set"
} else {
    Write-Host " ✅ OK" -ForegroundColor Green

    # Verify PYTHONPATH exists
    $pythonPath = $server.env.PYTHONPATH
    if (!(Test-Path $pythonPath)) {
        Write-Host "      ⚠️  Warning: PYTHONPATH directory not found: $pythonPath" -ForegroundColor Yellow
    }
}

# Check 6: Server executable exists
Write-Host "[6/6] Checking server executable..." -NoNewline
if ($server.args -and $server.args.Count -gt 0) {
    $serverPath = $server.args[0]
    if (!(Test-Path $serverPath)) {
        Write-Host " ⚠️  WARNING" -ForegroundColor Yellow
        Write-Host "      Server path not found: $serverPath"
    } else {
        Write-Host " ✅ OK" -ForegroundColor Green
    }
} else {
    Write-Host " ⚠️  SKIPPED" -ForegroundColor Yellow
}

Pop-Location

Write-Host ""
Write-Host "✅ Configuration validation complete!" -ForegroundColor Green
Write-Host "   Next steps:" -ForegroundColor Cyan
Write-Host "   1. Reload VS Code: Ctrl+Shift+P → Developer: Reload Window"
Write-Host "   2. Test tools: @workspace cde_healthCheck"
Write-Host ""

exit 0
