# Jules Integration - Quick Install Script
# Run this to set up Jules in < 1 minute

Write-Host "🚀 Jules Integration - Quick Install" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is active
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not active!" -ForegroundColor Yellow
    Write-Host "   Run: .\.venv\Scripts\activate" -ForegroundColor White
    Write-Host ""
    $activate = Read-Host "Activate now? (y/n)"
    if ($activate -eq "y") {
        & .\.venv\Scripts\Activate.ps1
    } else {
        Write-Host "❌ Aborted. Please activate venv first." -ForegroundColor Red
        exit 1
    }
}

# Step 1: Install Jules SDK
Write-Host "📦 Step 1: Installing jules-agent-sdk..." -ForegroundColor Green
pip install jules-agent-sdk --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ jules-agent-sdk installed" -ForegroundColor Green
} else {
    Write-Host "   ❌ Installation failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Check for API key
Write-Host "🔑 Step 2: Checking for Jules API key..." -ForegroundColor Green
$envFile = ".env"
$apiKeyPattern = "JULES_API_KEY="

if (Test-Path $envFile) {
    $content = Get-Content $envFile -Raw
    if ($content -match $apiKeyPattern) {
        Write-Host "   ✅ JULES_API_KEY found in .env" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  JULES_API_KEY not found in .env" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   To get your API key:" -ForegroundColor White
        Write-Host "   1. Go to https://jules.google/" -ForegroundColor White
        Write-Host "   2. Sign in with Google" -ForegroundColor White
        Write-Host "   3. Navigate to Settings → API Keys" -ForegroundColor White
        Write-Host "   4. Create new API key" -ForegroundColor White
        Write-Host ""
        $addKey = Read-Host "Do you have your API key? (y/n)"
        if ($addKey -eq "y") {
            $apiKey = Read-Host "Paste your API key"
            Add-Content -Path $envFile -Value "`nJULES_API_KEY=$apiKey"
            Write-Host "   ✅ API key added to .env" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Skipping for now. Add manually later." -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   ℹ️  .env file not found, creating..." -ForegroundColor Blue
    $apiKey = Read-Host "Paste your Jules API key (or press Enter to skip)"
    if ($apiKey) {
        "JULES_API_KEY=$apiKey" | Out-File -FilePath $envFile -Encoding UTF8
        Write-Host "   ✅ .env created with API key" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Skipped. Add JULES_API_KEY to .env manually." -ForegroundColor Yellow
    }
}
Write-Host ""

# Step 3: Verify installation
Write-Host "✨ Step 3: Verifying installation..." -ForegroundColor Green
$verifyScript = @"
import sys
try:
    import jules_agent_sdk
    print('✅ jules-agent-sdk imported successfully')
    sys.exit(0)
except ImportError:
    print('❌ jules-agent-sdk import failed')
    sys.exit(1)
"@

$verifyScript | python -
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Jules SDK verified" -ForegroundColor Green
} else {
    Write-Host "   ❌ Verification failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Create .jules directory
Write-Host "📁 Step 4: Setting up .jules directory..." -ForegroundColor Green
if (-not (Test-Path ".jules")) {
    New-Item -ItemType Directory -Path ".jules" | Out-Null
    Write-Host "   ✅ .jules directory created" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  .jules directory already exists" -ForegroundColor Blue
}
Write-Host ""

# Step 5: Summary
Write-Host "🎉 Installation Complete!" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Jules SDK installed" -ForegroundColor Green
Write-Host "✅ Configuration ready" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Connect your repository: https://jules.google/" -ForegroundColor White
Write-Host "   2. Read quick start: docs/jules-quick-start.md" -ForegroundColor White
Write-Host "   3. Try first task:" -ForegroundColor White
Write-Host "      cde_delegateToJules('Add logging to API')" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tip: Use 'cde_listAvailableAgents()' to check Jules status" -ForegroundColor Yellow
Write-Host ""
