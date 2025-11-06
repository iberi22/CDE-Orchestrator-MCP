#!/usr/bin/env pwsh
<#
.SYNOPSIS
Check if HTTP and WebSocket endpoints are listening.

.EXAMPLE
./CHECK_ENDPOINTS.ps1
#>

Write-Host "🔍 Checking endpoints..." -ForegroundColor Cyan

# Check WebSocket endpoint
Write-Host "`n📡 WebSocket (8766):" -ForegroundColor Yellow
$ws_test = Get-NetTCPConnection -LocalPort 8766 -ErrorAction SilentlyContinue
if ($ws_test) {
    Write-Host "  ✅ LISTENING" -ForegroundColor Green
} else {
    Write-Host "  ❌ NOT LISTENING" -ForegroundColor Red
}

# Check HTTP endpoint
Write-Host "`n🌐 HTTP (8767):" -ForegroundColor Yellow
$http_test = Get-NetTCPConnection -LocalPort 8767 -ErrorAction SilentlyContinue
if ($http_test) {
    Write-Host "  ✅ LISTENING" -ForegroundColor Green
} else {
    Write-Host "  ❌ NOT LISTENING" -ForegroundColor Red
}

# Try to POST test progress event
Write-Host "`n🧪 Testing HTTP endpoint..." -ForegroundColor Yellow
try {
    $event = @{
        server = "CDE"
        tool = "test"
        percentage = 0.5
        elapsed = 0
        message = "Test"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8767/progress" `
        -Method POST `
        -ContentType "application/json" `
        -Body $event `
        -ErrorAction SilentlyContinue

    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ HTTP endpoint responding" -ForegroundColor Green
    } else {
        Write-Host "  ❌ HTTP endpoint responded with status $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ HTTP endpoint not responding: $_" -ForegroundColor Red
}

Write-Host "`n✅ Check complete" -ForegroundColor Cyan
