#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup completo: CloudCode CLI + AWS Bedrock + Oh My Posh + IDE Integration

.DESCRIPTION
    Configura un entorno de desarrollo Windows con:
    - CloudCode CLI (via npm)
    - AWS Bedrock (Claude Sonnet 4.5)
    - Oh My Posh (terminal personalizada)
    - IDE Integration (VS Code/Zed)
    - Scripts de automatización para agentes

.EXAMPLE
    .\setup-cloudcode-bedrock.ps1
    .\setup-cloudcode-bedrock.ps1 -SkipOhMyPosh

.NOTES
    Requires: PowerShell 5.1+, Node.js 18+, AWS Account con Bedrock
#>

param(
    [switch]$SkipOhMyPosh,
    [switch]$SkipIDE,
    [switch]$TestMode
)

$ErrorActionPreference = "Stop"

# Configuración
$Config = @{
    BedrockRegion = "us-east-1"
    BedrockProfile = "bedrock"
    ModelId = "anthropic.claude-sonnet-4-5-20250929-v1:0"
    OhMyPoshTheme = "atomic"
}

# Colores
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

function Write-Header {
    param([string]$Message)
    Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor $Colors.Header
    Write-Host "  $Message" -ForegroundColor $Colors.Header
    Write-Host "═══════════════════════════════════════════════════`n" -ForegroundColor $Colors.Header
}

function Write-Success { param([string]$Message); Write-Host "✅ $Message" -ForegroundColor $Colors.Success }
function Write-Error-Custom { param([string]$Message); Write-Host "❌ $Message" -ForegroundColor $Colors.Error }
function Write-Warning-Custom { param([string]$Message); Write-Host "⚠️  $Message" -ForegroundColor $Colors.Warning }
function Write-Info { param([string]$Message); Write-Host "ℹ️  $Message" -ForegroundColor $Colors.Info }

function Test-Command { param([string]$Command); return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue) }

# ============================================================================
# PASO 1: Verificar Node.js y npm
# ============================================================================

function Test-NodeInstallation {
    Write-Header "Verificando Node.js"

    if (-not (Test-Command node)) {
        Write-Error-Custom "Node.js no está instalado"
        Write-Info "Descarga desde: https://nodejs.org/"
        return $false
    }

    $nodeVersion = node --version
    Write-Info "Node.js: $nodeVersion"

    if (-not (Test-Command npm)) {
        Write-Error-Custom "npm no está disponible"
        return $false
    }

    $npmVersion = npm --version
    Write-Info "npm: v$npmVersion"

    Write-Success "Node.js y npm instalados correctamente"
    return $true
}

# ============================================================================
# PASO 2: Instalar CloudCode CLI
# ============================================================================

function Install-CloudCodeCLI {
    Write-Header "Instalando CloudCode CLI"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would install @anthropic-ai/claude-code"
        return
    }

    # Verificar si ya está instalado
    if (Test-Command claude-code) {
        Write-Success "CloudCode CLI ya instalado"
        $version = claude-code --version 2>&1
        Write-Info $version
        return
    }

    Write-Info "Instalando @anthropic-ai/claude-code globalmente..."

    try {
        npm install -g @anthropic-ai/claude-code --silent

        # Refrescar PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        if (Test-Command claude-code) {
            Write-Success "CloudCode CLI instalado correctamente"
            $version = claude-code --version
            Write-Info $version
        } else {
            Write-Error-Custom "CloudCode CLI instalado pero no disponible en PATH"
            Write-Info "Reinicia PowerShell y vuelve a ejecutar el script"
        }
    } catch {
        Write-Error-Custom "Error instalando CloudCode CLI: $_"
        exit 1
    }
}

# ============================================================================
# PASO 3: Verificar AWS Bedrock
# ============================================================================

function Test-BedrockAccess {
    Write-Header "Verificando AWS Bedrock"

    if (-not (Test-Command aws)) {
        Write-Error-Custom "AWS CLI no instalado"
        Write-Info "Ejecuta primero: .\setup-aider-bedrock.ps1"
        return $false
    }

    Write-Info "Verificando credenciales..."
    try {
        $identity = & aws sts get-caller-identity --profile $Config.BedrockProfile 2>&1 | ConvertFrom-Json
        Write-Success "Credenciales válidas: $($identity.Arn)"
    } catch {
        Write-Error-Custom "Credenciales AWS inválidas"
        Write-Info "Configura con: aws configure --profile $($Config.BedrockProfile)"
        return $false
    }

    Write-Info "Verificando acceso a Bedrock..."
    try {
        $models = & aws bedrock list-foundation-models --region $Config.BedrockRegion --profile $Config.BedrockProfile 2>&1 | ConvertFrom-Json

        if ($models.modelSummaries) {
            Write-Success "Acceso a Bedrock verificado"
            $claudeModels = $models.modelSummaries | Where-Object { $_.modelId -like "*claude*" }
            Write-Info "Modelos Claude disponibles: $($claudeModels.Count)"
            return $true
        }
    } catch {
        Write-Error-Custom "No se puede acceder a Bedrock: $_"
        return $false
    }

    return $false
}

# ============================================================================
# PASO 4: Configurar Variables de Entorno
# ============================================================================

function Configure-EnvironmentVariables {
    Write-Header "Configurando Variables de Entorno"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would set environment variables"
        return
    }

    $vars = @{
        "AWS_PROFILE" = $Config.BedrockProfile
        "AWS_REGION" = $Config.BedrockRegion
        "CLOUDCODE_PROVIDER" = "bedrock"
        "CLOUDCODE_MODEL" = $Config.ModelId
    }

    foreach ($var in $vars.GetEnumerator()) {
        [Environment]::SetEnvironmentVariable($var.Name, $var.Value, "User")
        Set-Item -Path "env:$($var.Name)" -Value $var.Value
        Write-Success "Set $($var.Name)=$($var.Value)"
    }
}

# ============================================================================
# PASO 5: Instalar y Configurar Oh My Posh
# ============================================================================

function Install-OhMyPosh {
    Write-Header "Instalando Oh My Posh"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would install Oh My Posh"
        return
    }

    if (Test-Command oh-my-posh) {
        Write-Success "Oh My Posh ya instalado"
        return
    }

    Write-Info "Instalando Oh My Posh via winget..."
    try {
        winget install JanDeDobbeleer.OhMyPosh -s winget --silent

        # Refrescar PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        if (Test-Command oh-my-posh) {
            Write-Success "Oh My Posh instalado correctamente"
        }
    } catch {
        Write-Error-Custom "Error instalando Oh My Posh: $_"
    }
}

function Configure-OhMyPosh {
    Write-Header "Configurando Oh My Posh"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would configure Oh My Posh"
        return
    }

    $profilePath = $PROFILE.CurrentUserAllHosts
    $profileDir = Split-Path -Parent $profilePath

    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }

    # Configuración Oh My Posh con AWS + Git info
    $ohMyPoshConfig = @"

# Oh My Posh Configuration
`$env:POSH_GIT_ENABLED = `$true
oh-my-posh init pwsh --config "`$env:POSH_THEMES_PATH\$($Config.OhMyPoshTheme).omp.json" | Invoke-Expression

# Custom prompt con AWS info
function Get-AwsPrompt {
    `$profile = `$env:AWS_PROFILE
    `$region = `$env:AWS_REGION
    if (`$profile) {
        Write-Host " AWS:(`$profile@`$region)" -ForegroundColor Yellow -NoNewline
    }
}

# Override prompt para incluir AWS info
`$originalPrompt = `$function:prompt
function prompt {
    Get-AwsPrompt
    & `$originalPrompt
}
"@

    if (-not (Test-Path $profilePath)) {
        Set-Content -Path $profilePath -Value $ohMyPoshConfig
    } elseif (-not (Select-String -Path $profilePath -Pattern "oh-my-posh init" -Quiet)) {
        Add-Content -Path $profilePath -Value "`n$ohMyPoshConfig"
    }

    Write-Success "Oh My Posh configurado en: $profilePath"
}

# ============================================================================
# PASO 6: Crear Scripts de Automatización
# ============================================================================

function Create-AutomationScripts {
    Write-Header "Creando Scripts de Automatización"

    $scriptsDir = "$PSScriptRoot"

    # Script 1: launch-bedrock.ps1
    $launchBedrockScript = @"
#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Lanzar terminal con entorno Bedrock configurado
.DESCRIPTION
    Abre PowerShell con Oh My Posh, AWS profile cargado y CloudCode CLI listo
#>

# Cargar variables
`$env:AWS_PROFILE = "$($Config.BedrockProfile)"
`$env:AWS_REGION = "$($Config.BedrockRegion)"
`$env:CLOUDCODE_PROVIDER = "bedrock"
`$env:CLOUDCODE_MODEL = "$($Config.ModelId)"

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Bedrock Development Environment     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "AWS Profile: `$env:AWS_PROFILE" -ForegroundColor Yellow
Write-Host "AWS Region:  `$env:AWS_REGION" -ForegroundColor Yellow
Write-Host "Model:       `$env:CLOUDCODE_MODEL" -ForegroundColor Yellow
Write-Host ""
Write-Host "Comandos disponibles:"
Write-Host "  cloudcode-test      - Test Bedrock connectivity"
Write-Host "  cloudcode-run       - Run CloudCode with Bedrock"
Write-Host "  bedrock-models      - List available models"
Write-Host ""

# Cargar perfil Oh My Posh si existe
if (Test-Path `$PROFILE.CurrentUserAllHosts) {
    . `$PROFILE.CurrentUserAllHosts
}
"@

    $launchBedrockPath = "$scriptsDir\launch-bedrock.ps1"
    Set-Content -Path $launchBedrockPath -Value $launchBedrockScript
    Write-Success "Created: launch-bedrock.ps1"

    # Script 2: cloudcode-test.ps1
    $cloudcodeTestScript = @"
#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test CloudCode CLI con AWS Bedrock
#>

param([string]`$Prompt = "Hello, write a simple Python function")

Write-Host "Testing CloudCode CLI with Bedrock..." -ForegroundColor Cyan
Write-Host "Provider: bedrock" -ForegroundColor Yellow
Write-Host "Model: $($Config.ModelId)" -ForegroundColor Yellow
Write-Host "Prompt: `$Prompt" -ForegroundColor Yellow
Write-Host ""

# Ejecutar CloudCode
claude-code run --provider bedrock --model $($Config.ModelId) --prompt "`$Prompt"
"@

    $cloudcodeTestPath = "$scriptsDir\cloudcode-test.ps1"
    Set-Content -Path $cloudcodeTestPath -Value $cloudcodeTestScript
    Write-Success "Created: cloudcode-test.ps1"

    # Script 3: open-ide-bedrock.ps1
    $openIdeScript = @"
#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Open IDE (VS Code o Zed) con entorno Bedrock
#>

param(
    [ValidateSet("code", "zed")]
    [string]`$IDE = "code",
    [string]`$ProjectPath = "."
)

# Cargar variables de entorno
`$env:AWS_PROFILE = "$($Config.BedrockProfile)"
`$env:AWS_REGION = "$($Config.BedrockRegion)"
`$env:CLOUDCODE_PROVIDER = "bedrock"
`$env:CLOUDCODE_MODEL = "$($Config.ModelId)"

Write-Host "Opening `$IDE with Bedrock environment..." -ForegroundColor Cyan

if (`$IDE -eq "code") {
    code `$ProjectPath
} elseif (`$IDE -eq "zed") {
    zed `$ProjectPath
}
"@

    $openIdePath = "$scriptsDir\open-ide-bedrock.ps1"
    Set-Content -Path $openIdePath -Value $openIdeScript
    Write-Success "Created: open-ide-bedrock.ps1"

    # Añadir aliases al perfil PowerShell
    $aliases = @"

# CloudCode CLI Aliases
function cloudcode-test { & "$cloudcodeTestPath" @args }
function cloudcode-run { claude-code run --provider bedrock --model $($Config.ModelId) @args }
function bedrock-models { aws bedrock list-foundation-models --region $($Config.BedrockRegion) --profile $($Config.BedrockProfile) }
function launch-bedrock { & "$launchBedrockPath" }
function open-ide-bedrock { & "$openIdePath" @args }
"@

    $profilePath = $PROFILE.CurrentUserAllHosts
    if (Test-Path $profilePath) {
        if (-not (Select-String -Path $profilePath -Pattern "CloudCode CLI Aliases" -Quiet)) {
            Add-Content -Path $profilePath -Value "`n$aliases"
            Write-Success "Aliases añadidos al perfil PowerShell"
        }
    } else {
        Set-Content -Path $profilePath -Value $aliases
        Write-Success "Perfil PowerShell creado con aliases"
    }
}

# ============================================================================
# PASO 7: Configurar IDE Integration
# ============================================================================

function Configure-IDEIntegration {
    Write-Header "Configurando IDE Integration"

    if ($TestMode) {
        Write-Info "[TEST MODE] Would configure IDE"
        return
    }

    # VS Code tasks.json
    $vscodeDir = ".vscode"
    $tasksJson = @"
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "CloudCode: Run with Bedrock",
            "type": "shell",
            "command": "claude-code",
            "args": [
                "run",
                "--provider", "bedrock",
                "--model", "$($Config.ModelId)",
                "--prompt", "`${input:userPrompt}"
            ],
            "problemMatcher": [],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "Bedrock: List Models",
            "type": "shell",
            "command": "aws",
            "args": [
                "bedrock", "list-foundation-models",
                "--region", "$($Config.BedrockRegion)",
                "--profile", "$($Config.BedrockProfile)"
            ],
            "problemMatcher": []
        },
        {
            "label": "Bedrock: Test Connectivity",
            "type": "shell",
            "command": "pwsh",
            "args": [
                "-File", "$PSScriptRoot\\cloudcode-test.ps1"
            ],
            "problemMatcher": []
        }
    ],
    "inputs": [
        {
            "id": "userPrompt",
            "type": "promptString",
            "description": "Enter your coding prompt",
            "default": "Write a Python function to..."
        }
    ]
}
"@

    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
    }

    Set-Content -Path "$vscodeDir\tasks.json" -Value $tasksJson
    Write-Success "VS Code tasks.json created"

    Write-Info "Para usar en VS Code:"
    Write-Info "  Ctrl+Shift+P → Tasks: Run Task → CloudCode: Run with Bedrock"
}

# ============================================================================
# PASO 8: Crear Documentación
# ============================================================================

function Create-Documentation {
    Write-Header "Creando Documentación"

    $docsContent = @"
# CloudCode CLI + AWS Bedrock Setup Guide

## 🎯 Overview

Este entorno proporciona:
- **CloudCode CLI** con soporte AWS Bedrock
- **Oh My Posh** con información de AWS en el prompt
- **IDE Integration** para VS Code y Zed
- **Scripts de automatización** para agentes

---

## 📋 Prerequisites

- Windows 10/11
- Node.js 18+ ([https://nodejs.org/](https://nodejs.org/))
- AWS Account con acceso a Bedrock
- VS Code o Zed (opcional para IDE integration)

---

## 🚀 Quick Start

### 1. Ejecutar Setup Script

``````powershell
.\setup-cloudcode-bedrock.ps1
``````

Esto instalará y configurará:
- CloudCode CLI
- AWS CLI con perfil "bedrock"
- Oh My Posh
- Scripts de automatización
- IDE tasks

### 2. Verificar Instalación

``````powershell
# Test CloudCode
cloudcode-test

# List Bedrock models
bedrock-models

# Launch terminal con entorno Bedrock
launch-bedrock
``````

---

## 🛠️ Usage

### Comando Directo

``````powershell
claude-code run --provider bedrock --model $($Config.ModelId) --prompt "Write Python code to..."
``````

### Scripts de Automatización

``````powershell
# Test connectivity
cloudcode-test

# Run CloudCode con prompt custom
cloudcode-run --prompt "Create a REST API"

# Open IDE con entorno Bedrock
open-ide-bedrock -IDE code -ProjectPath .
``````

### Desde VS Code

1. Abrir proyecto
2. **Ctrl+Shift+P** → **Tasks: Run Task**
3. Seleccionar **CloudCode: Run with Bedrock**
4. Ingresar prompt

---

## 📂 Files Created

| File | Purpose |
|------|---------|
| ``launch-bedrock.ps1`` | Lanzar terminal con entorno completo |
| ``cloudcode-test.ps1`` | Test CloudCode + Bedrock connectivity |
| ``open-ide-bedrock.ps1`` | Abrir IDE con variables de entorno |
| ``.vscode/tasks.json`` | VS Code tasks para CloudCode |

---

## ⚙️ Configuration

### Variables de Entorno

``````powershell
`$env:AWS_PROFILE = "$($Config.BedrockProfile)"
`$env:AWS_REGION = "$($Config.BedrockRegion)"
`$env:CLOUDCODE_PROVIDER = "bedrock"
`$env:CLOUDCODE_MODEL = "$($Config.ModelId)"
``````

### PowerShell Aliases

| Alias | Command |
|-------|---------|
| ``cloudcode-test`` | Test Bedrock connectivity |
| ``cloudcode-run`` | Run CloudCode with Bedrock |
| ``bedrock-models`` | List available models |
| ``launch-bedrock`` | Launch configured terminal |
| ``open-ide-bedrock`` | Open IDE with environment |

---

## 🔧 Troubleshooting

### CloudCode not found

``````powershell
# Refresh PATH
`$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Or reinstall
npm install -g @anthropic-ai/claude-code
``````

### Bedrock Access Denied

Verifica permisos IAM:
- ``bedrock:ListFoundationModels``
- ``bedrock:InvokeModel``

``````powershell
aws sts get-caller-identity --profile bedrock
``````

### Oh My Posh no muestra AWS info

Recarga perfil PowerShell:
``````powershell
. `$PROFILE.CurrentUserAllHosts
``````

---

## 📞 Support

- CloudCode CLI: [https://github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)
- AWS Bedrock Docs: [https://docs.aws.amazon.com/bedrock/](https://docs.aws.amazon.com/bedrock/)
- Oh My Posh: [https://ohmyposh.dev/](https://ohmyposh.dev/)

---

**Last Updated**: $(Get-Date -Format "yyyy-MM-dd")
**Environment**: Windows PowerShell + Node.js + AWS Bedrock
"@

    $docsPath = "$PSScriptRoot\README-CLOUDCODE.md"
    Set-Content -Path $docsPath -Value $docsContent
    Write-Success "Documentation created: README-CLOUDCODE.md"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    Write-Header "CloudCode CLI + AWS Bedrock Setup"

    Write-Info "Configuration:"
    Write-Info "  Region: $($Config.BedrockRegion)"
    Write-Info "  Profile: $($Config.BedrockProfile)"
    Write-Info "  Model: $($Config.ModelId)"

    if ($TestMode) {
        Write-Warning-Custom "RUNNING IN TEST MODE"
    }

    # Step 1: Verify Node.js
    if (-not (Test-NodeInstallation)) {
        exit 1
    }

    # Step 2: Install CloudCode CLI
    Install-CloudCodeCLI

    # Step 3: Verify AWS Bedrock
    if (-not (Test-BedrockAccess)) {
        Write-Warning-Custom "Bedrock access failed. Configure AWS CLI first."
    }

    # Step 4: Configure environment variables
    Configure-EnvironmentVariables

    # Step 5: Install Oh My Posh
    if (-not $SkipOhMyPosh) {
        Install-OhMyPosh
        Configure-OhMyPosh
    }

    # Step 6: Create automation scripts
    Create-AutomationScripts

    # Step 7: Configure IDE
    if (-not $SkipIDE) {
        Configure-IDEIntegration
    }

    # Step 8: Create documentation
    Create-Documentation

    # Final summary
    Write-Header "Setup Complete!"

    Write-Success "CloudCode CLI + AWS Bedrock configurado exitosamente"
    Write-Info ""
    Write-Info "Próximos pasos:"
    Write-Info "  1. Reinicia PowerShell para cargar aliases"
    Write-Info "  2. Ejecuta: launch-bedrock"
    Write-Info "  3. Test: cloudcode-test"
    Write-Info "  4. Abre VS Code y usa Ctrl+Shift+P → Tasks: Run Task"
    Write-Info ""
    Write-Info "Documentación completa en: README-CLOUDCODE.md"
}

# Run
Main
