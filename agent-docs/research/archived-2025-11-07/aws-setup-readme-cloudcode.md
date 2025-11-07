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

```powershell
.\setup-cloudcode-bedrock.ps1
```

Esto instalará y configurará:
- CloudCode CLI
- AWS CLI con perfil "bedrock"
- Oh My Posh
- Scripts de automatización
- IDE tasks

### 2. Verificar Instalación

```powershell
# Test CloudCode
cloudcode-test

# List Bedrock models
bedrock-models

# Launch terminal con entorno Bedrock
launch-bedrock
```

---

## 🛠️ Usage

### Comando Directo

```powershell
claude-code run --provider bedrock --model anthropic.claude-sonnet-4-5-20250929-v1:0 --prompt "Write Python code to..."
```

### Scripts de Automatización

```powershell
# Test connectivity
cloudcode-test

# Run CloudCode con prompt custom
cloudcode-run --prompt "Create a REST API"

# Open IDE con entorno Bedrock
open-ide-bedrock -IDE code -ProjectPath .
```

### Desde VS Code

1. Abrir proyecto
2. **Ctrl+Shift+P** → **Tasks: Run Task**
3. Seleccionar **CloudCode: Run with Bedrock**
4. Ingresar prompt

---

## 📂 Files Created

| File | Purpose |
|------|---------|
| `launch-bedrock.ps1` | Lanzar terminal con entorno completo |
| `cloudcode-test.ps1` | Test CloudCode + Bedrock connectivity |
| `open-ide-bedrock.ps1` | Abrir IDE con variables de entorno |
| `.vscode/tasks.json` | VS Code tasks para CloudCode |

---

## ⚙️ Configuration

### Variables de Entorno

```powershell
$env:AWS_PROFILE = "bedrock"
$env:AWS_REGION = "us-east-1"
$env:CLOUDCODE_PROVIDER = "bedrock"
$env:CLOUDCODE_MODEL = "anthropic.claude-sonnet-4-5-20250929-v1:0"
```

### PowerShell Aliases

| Alias | Command |
|-------|---------|
| `cloudcode-test` | Test Bedrock connectivity |
| `cloudcode-run` | Run CloudCode with Bedrock |
| `bedrock-models` | List available models |
| `launch-bedrock` | Launch configured terminal |
| `open-ide-bedrock` | Open IDE with environment |

---

## 🔧 Troubleshooting

### CloudCode not found

```powershell
# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Or reinstall
npm install -g @anthropic-ai/claude-code
```

### Bedrock Access Denied

Verifica permisos IAM:
- `bedrock:ListFoundationModels`
- `bedrock:InvokeModel`

```powershell
aws sts get-caller-identity --profile bedrock
```

### Oh My Posh no muestra AWS info

Recarga perfil PowerShell:
```powershell
. $PROFILE.CurrentUserAllHosts
```

---

## 📞 Support

- CloudCode CLI: [https://github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)
- AWS Bedrock Docs: [https://docs.aws.amazon.com/bedrock/](https://docs.aws.amazon.com/bedrock/)
- Oh My Posh: [https://ohmyposh.dev/](https://ohmyposh.dev/)

---

**Last Updated**: 2025-11-04
**Environment**: Windows PowerShell + Node.js + AWS Bedrock
