#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Diagnose and test MCP server connection with Gemini CLI
#>

$ErrorActionPreference = "Continue"

Write-Host "`n═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  MCP Server Diagnostic Tool" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════`n" -ForegroundColor Cyan

# Test 1: MCP Server can start independently
Write-Host "[Test 1/4] Testing MCP server startup..." -ForegroundColor Yellow
try {
    $serverProcess = Start-Process -FilePath "python" -ArgumentList "src/server.py" -NoNewWindow -PassThru -RedirectStandardOutput "mcp-server-test.log" -RedirectStandardError "mcp-server-error.log"
    Start-Sleep -Seconds 3

    if (-not $serverProcess.HasExited) {
        Write-Host "✓ MCP server started (PID: $($serverProcess.Id))" -ForegroundColor Green
        $serverProcess.Kill()
        Write-Host "✓ Server stopped cleanly" -ForegroundColor Green
    } else {
        Write-Host "✗ Server exited immediately" -ForegroundColor Red
        Write-Host "Check mcp-server-error.log for details" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Failed to start server: $_" -ForegroundColor Red
}

# Test 2: Check configuration
Write-Host "`n[Test 2/4] Checking Gemini configuration..." -ForegroundColor Yellow
$configPath = ".gemini/settings.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath | ConvertFrom-Json
    Write-Host "✓ Configuration found" -ForegroundColor Green
    Write-Host "  Server command: $($config.mcpServers.'cde-orchestrator'.command)" -ForegroundColor Cyan
    Write-Host "  Server args: $($config.mcpServers.'cde-orchestrator'.args -join ' ')" -ForegroundColor Cyan
    Write-Host "  Timeout: $($config.mcpServers.'cde-orchestrator'.timeout)ms" -ForegroundColor Cyan
    Write-Host "  Trust: $($config.mcpServers.'cde-orchestrator'.trust)" -ForegroundColor Cyan
} else {
    Write-Host "✗ Configuration not found: $configPath" -ForegroundColor Red
}

# Test 3: Test Gemini CLI can see MCP
Write-Host "`n[Test 3/4] Testing Gemini CLI MCP discovery..." -ForegroundColor Yellow
Write-Host "Running: gemini /mcp (timeout: 10s)" -ForegroundColor Cyan

$job = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    gemini "/mcp"
}

Wait-Job $job -Timeout 10 | Out-Null
$output = Receive-Job $job
Stop-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -ErrorAction SilentlyContinue

if ($output -match "cde-orchestrator") {
    Write-Host "✓ MCP server discovered by Gemini CLI" -ForegroundColor Green
    Write-Host $output -ForegroundColor Gray
} else {
    Write-Host "✗ MCP server not discovered" -ForegroundColor Red
    Write-Host "Output:" -ForegroundColor Yellow
    Write-Host $output -ForegroundColor Gray
}

# Test 4: Try simple non-interactive command
Write-Host "`n[Test 4/4] Testing simple Gemini CLI command..." -ForegroundColor Yellow
Write-Host "Running: gemini -p 'List available MCP tools' (timeout: 15s)" -ForegroundColor Cyan

$job = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    gemini -p "List available MCP tools"
}

Wait-Job $job -Timeout 15 | Out-Null
$output = Receive-Job $job
Stop-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -ErrorAction SilentlyContinue

if ($output) {
    Write-Host "✓ Gemini CLI responded" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    Write-Host $output -ForegroundColor Gray
} else {
    Write-Host "✗ No response from Gemini CLI" -ForegroundColor Red
}

# Summary
Write-Host "`n═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Diagnostic Complete" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "Recommendations:" -ForegroundColor Yellow
Write-Host "1. Check mcp-server-test.log and mcp-server-error.log" -ForegroundColor White
Write-Host "2. If server fails, check Python dependencies" -ForegroundColor White
Write-Host "3. If discovery fails, try: gemini mcp list" -ForegroundColor White
Write-Host "4. For detailed logs: gemini --debug" -ForegroundColor White
Write-Host "`nDone! Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
