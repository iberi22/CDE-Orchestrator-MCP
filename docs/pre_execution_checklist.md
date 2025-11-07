---
title: "Checklist de Pre-Ejecución: Validar Agentes y Configuración"
description: "Pasos para verificar que Claude Code, Aider, Codex y Jules están listos para meta-orquestación"
type: "guide"
status: "active"
created: "2025-11-05"
updated: "2025-11-05"
author: "GitHub Copilot"
---

# ✅ Checklist Pre-Ejecución: Validar Todo Antes de Iniciar

## 🎯 Objetivo

Asegurarte de que todos los agentes están correctamente instalados y configurados ANTES de ejecutar `orchestrate.py`.

---

## 📋 Paso 1: Verificar Python y MCP Server

### 1.1 Verificar Python 3.14+

```powershell
# Windows PowerShell
python --version
```

**Esperado**: `Python 3.14.0` o superior

**Si falla**:
```powershell
# Instalar Python 3.14
winget install Python.Python.3.14

# O descargar desde https://www.python.org/downloads/
```

### 1.2 Verificar que MCP Server inicia

```powershell
# Windows PowerShell
cd "E:\scripts-python\CDE Orchestrator MCP"

python -c "
import sys
sys.path.insert(0, 'src')
from server import app
print('✅ MCP Server OK')
"
```

**Esperado**: `✅ MCP Server OK`

**Si falla**:
```powershell
pip install -r requirements.txt
```

### 1.3 Verificar que orchest ración módulos existen

```powershell
python -c "
from src.cde_orchestrator.infrastructure.multi_agent_orchestrator import MultiAgentOrchestrator
from src.mcp_tools.full_implementation import FullImplementationOrchestrator
print('✅ Módulos de orquestración OK')
"
```

**Esperado**: `✅ Módulos de orquestración OK`

---

## 🤖 Paso 2: Validar Agentes Disponibles

### 2.1 Detectar Agentes Automáticamente

```powershell
# Windows PowerShell
python << 'EOF'
from src.cde_orchestrator.infrastructure.multi_agent_orchestrator import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator(".")
available = orchestrator._detect_available_agents()

print(f"\n🤖 AGENTES DETECTADOS:")
print(f"   Total: {len(available)}")
for agent in available:
    print(f"   ✅ {agent.value}")

if not available:
    print(f"   ⚠️  NO AGENTES DETECTADOS - Ver paso 2.2+")
EOF
```

**Esperado**: Al menos 1 agente listado (idealmente 2-4)

---

## 🔧 Paso 3: Configurar Cada Agente

### 3.1 Claude Code (Bedrock) - PRIORITARIO

**Mejor para**: Tareas complejas de arquitectura/compilación

#### 3.1.1 Instalar Claude Code CLI

```powershell
# Windows PowerShell
pip install claude-code

# Verificar instalación
claude-code --version
```

**Esperado**: `claude-code version X.Y.Z`

**Si falla**:
```powershell
# Instalar desde pip
pip install --upgrade claude-code

# O descargar CloudCode: https://cloud.google.com/sdk/docs/install
```

#### 3.1.2 Configurar AWS Bedrock

```powershell
# Instalar AWS CLI
pip install awscli

# Configurar credenciales
aws configure --profile bedrock

# Ingresa:
# AWS Access Key ID: [Tu acceso key]
# AWS Secret Access Key: [Tu secret key]
# Default region: us-east-1
# Default output format: json

# Verificar configuración
aws bedrock list-foundation-models --region us-east-1 --profile bedrock --output json | ConvertFrom-Json | Select-Object -ExpandProperty modelSummaries | Select-Object -First 1
```

**Esperado**: Modelos de Bedrock listados

**Si falla**:
```powershell
# Verificar que tienes credenciales AWS válidas
# En AWS Console:
# 1. IAM → Usuarios
# 2. Crear access key si es necesario
# 3. Verificar que bedrock-user tiene permisos
```

#### 3.1.3 Verificar Conectividad Claude Code

```powershell
# Probar con mensagem simple
claude-code suggest "create a hello world python script"

# O con modo interactivo
claude-code run --provider bedrock
```

**Esperado**: Sugerencias de código o interfaz interactiva

**Si falla**:
```powershell
# Verificar variable de entorno
$env:AWS_PROFILE = "bedrock"

# Re-intentar
claude-code suggest "test"
```

---

### 3.2 Aider (Multi-File Safe Editing) - RECOMENDADO

**Mejor para**: Edición segura de múltiples archivos

#### 3.2.1 Instalar Aider CLI

```powershell
# Windows PowerShell
pip install aider-chat

# Verificar instalación
aider --version
```

**Esperado**: `aider X.Y.Z`

**Si falla**:
```powershell
pip install --upgrade aider-chat
```

#### 3.2.2 Verificar Conectividad Aider

```powershell
# Crear proyecto temporal
mkdir temp_aider_test
cd temp_aider_test

# Inicializar git
git init
echo "# Test" > README.md

# Probar aider
aider --help
```

**Esperado**: Help menu mostrado

**Si falla**:
```powershell
# Aider necesita SSH keys para algunos backends
# Generar SSH key si no existe:
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\id_ed25519"

# O permitir HTTPS:
git config --global url."https://".insteadOf git://
```

---

### 3.3 GitHub Copilot CLI - RECOMENDADO

**Mejor para**: Snippets rápidos y tests

#### 3.3.1 Instalar GitHub CLI

```powershell
# Windows PowerShell - Opción 1: winget
winget install GitHub.cli

# Opción 2: Chocolatey
choco install gh

# Verificar
gh --version
```

**Esperado**: `gh version X.Y.Z`

#### 3.3.2 Autenticarse con GitHub

```powershell
# Iniciar autenticación
gh auth login

# Elegir opciones:
# 1. GitHub.com
# 2. HTTPS
# 3. Y - para usar token git credential manager
# 4. Paste an authentication token
#    → Generar en: https://github.com/settings/tokens/new
#    → Scopes: repo, read:org, gist

# Verificar
gh auth status
```

**Esperado**: Autenticado con tu usuario de GitHub

#### 3.3.3 Verificar Copilot CLI

```powershell
# Probar sugerencia
gh copilot suggest "create hello world in python"

# O en modo interactivo
gh copilot explain "def fibonacci(n): ..."
```

**Esperado**: Sugerencias de Copilot

**Si falla**:
```powershell
# Verificar que tienes acceso a GitHub Copilot
# https://github.com/copilot_cli
# Puede requerir Plan Copilot (no es gratis)

# Alternativa: Usar solo Claude Code y Aider
```

---

### 3.4 Jules (Full Context Agent) - FALLBACK

**Mejor para**: Tareas muy complejas multiarchivo

Jules ya está integrado vía `cde_delegateToJules()`, no requiere instalación adicional.

#### 3.4.1 Verificar disponibilidad

```powershell
python << 'EOF'
from src.mcp_tools.agents import cde_listAvailableAgents
import json

agents = cde_listAvailableAgents()
print(json.dumps(agents, indent=2))
EOF
```

**Esperado**: Jules listado en available_agents

---

## 🔍 Paso 4: Validación Completa del Sistema

### 4.1 Ejecutar validador de configuración

```powershell
# Windows PowerShell
python << 'EOF'
import subprocess
import sys
from pathlib import Path

print("=" * 80)
print("🔍 VALIDACIÓN COMPLETA DE CONFIGURACIÓN")
print("=" * 80 + "\n")

agents_to_check = {
    "Claude Code": ("claude-code", ["--version"]),
    "Aider": ("aider", ["--version"]),
    "GitHub CLI": ("gh", ["--version"]),
    "AWS CLI": ("aws", ["--version"]),
}

results = {}

for name, (cmd, args) in agents_to_check.items():
    try:
        result = subprocess.run(
            [cmd] + args,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.strip().split('\n')[0]
            results[name] = ("✅", version_line)
        else:
            results[name] = ("❌", result.stderr.strip())
    except FileNotFoundError:
        results[name] = ("❌", "No encontrado en PATH")
    except subprocess.TimeoutExpired:
        results[name] = ("⏳", "Timeout")
    except Exception as e:
        results[name] = ("❌", str(e))

print("📋 RESULTADOS:")
for name, (status, info) in results.items():
    print(f"   {status} {name:20} {info}")

print("\n" + "=" * 80)

# Contar disponibles
available_count = sum(1 for status, _ in results.values() if status == "✅")
print(f"✅ {available_count}/4 agentes disponibles")

if available_count == 0:
    print("❌ CRÍTICO: No hay agentes disponibles")
    sys.exit(1)
elif available_count < 2:
    print("⚠️  RECOMENDADO: Instalar al menos 2 agentes para redundancia")
else:
    print("✅ CONFIGURACIÓN ÓPTIMA")

print("=" * 80 + "\n")
EOF
```

**Esperado**: Al menos 2 agentes listados como ✅

---

## 🧪 Paso 5: Test de Ejecución (Dry Run)

### 5.1 Ejecutar Modo Dry-Run (Sin cambios reales)

```powershell
# Windows PowerShell
cd "E:\scripts-python\CDE Orchestrator MCP"

python orchestrate.py --phase phase1 --dry-run --verbose
```

**Esperado**: Simula tareas sin ejecutarlas realmente

**Si falla**:
```powershell
# Verificar que módulos están importables
python -c "
from src.mcp_tools.full_implementation import FullImplementationOrchestrator
print('✅ FullImplementationOrchestrator OK')
"
```

---

## 🚀 Paso 6: Prepararse para Ejecución Real

### 6.1 Backup de Estado Actual

```powershell
# Windows PowerShell
# Hacer backup de archivos importantes
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
mkdir "backups\pre_orchestration_$timestamp"

# Copiar archivos críticos
Copy-Item "src\*" "backups\pre_orchestration_$timestamp\src" -Recurse
Copy-Item ".cde\state.json" "backups\pre_orchestration_$timestamp\" -ErrorAction SilentlyContinue
```

### 6.2 Crear Log Directory

```powershell
# Crear directorio para logs
mkdir logs -ErrorAction SilentlyContinue

# Verificar permisos de escritura
echo "test" > "logs\test.txt"
Remove-Item "logs\test.txt"

echo "✅ Logs directory OK"
```

### 6.3 Verificar Espacio en Disco

```powershell
# Verificar al menos 10 GB libres
$drive = (Get-Location).Drive.Name
$disk = Get-Volume -DriveLetter $drive.Trim(':')
$freeGB = [math]::Round($disk.SizeRemaining / 1GB, 2)

Write-Host "💾 Espacio libre: $freeGB GB"

if ($freeGB -lt 10) {
    Write-Host "⚠️  ADVERTENCIA: Menos de 10 GB libres (se necesita para compilación Rust)"
}
```

---

## 📊 Paso 7: Checklist Final

**Antes de ejecutar `orchestrate.py`:**

```
[ ] Python 3.14+ instalado
[ ] MCP Server inicia sin errores
[ ] Módulos de orquestración importan correctamente
[ ] Al menos 2 agentes disponibles
[ ] Claude Code verificado (si disponible)
[ ] Aider verificado (si disponible)
[ ] GitHub Copilot verificado (si disponible)
[ ] AWS Bedrock configurado y funcional
[ ] Validador de configuración pasa
[ ] Dry-run ejecuta sin errores
[ ] Backup de estado actual hecho
[ ] Directorio de logs creado
[ ] Al menos 10 GB de espacio libre
```

---

## 🎯 Si Todo Está ✅

**¡Ahora ejecuta!**

```powershell
# Ejecutar Fase 1 (2 horas)
python orchestrate.py --phase phase1 --verbose

# Monitorear progreso
tail -f logs/orchestration.log
```

---

## ⚠️ Troubleshooting

### Problema: "Agent not found in PATH"

**Solución**:
```powershell
# Agregar a PATH
$env:PATH += ";$env:USERPROFILE\AppData\Local\Programs\claude-code\bin"
$env:PATH += ";$env:USERPROFILE\.cargo\bin"  # Para Rust

# Persistir (agregar a Variables de Entorno)
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")
```

### Problema: "AWS Bedrock credentials invalid"

**Solución**:
```powershell
# Re-configurar AWS
aws configure --profile bedrock

# Verificar credenciales
aws sts get-caller-identity --profile bedrock
```

### Problema: "aider: fatal: not a git repository"

**Solución**:
```powershell
# Aider necesita un repo Git
cd "E:\scripts-python\CDE Orchestrator MCP"
git init  # Si no existe
git add .
git commit -m "Initial commit"
```

### Problema: "gh: command not found"

**Solución**:
```powershell
# Instalar GitHub CLI
winget install GitHub.cli

# Re-abrir PowerShell
pwsh
```

---

## 📞 Soporte

Si algo falla:

1. **Revisa logs**:
   ```powershell
   tail -f logs/orchestration.log
   ```

2. **Ejecuta validador**:
   ```powershell
   python -c "...validador..."  # Del Paso 4.1
   ```

3. **Consulta documentación**:
   - Claude Code: https://cloud.google.com/docs/codechat
   - Aider: https://aider.chat/
   - GitHub Copilot CLI: https://github.com/copilot_cli
   - Jules: `specs/design/dynamic-skill-system.md`

---

**¡Cuando todo esté verde, estás listo para comenzar la meta-orquestación! 🚀**
