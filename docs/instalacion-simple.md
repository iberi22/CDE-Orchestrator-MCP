---
title: "Instalación Simple - CDE Orchestrator MCP"
description: "Guía de instalación en 3 pasos para comenzar a usar el MCP inmediatamente"
type: guide
status: active
created: "2025-11-10"
updated: "2025-11-10"
author: "CDE Team"
tags:
  - installation
  - quickstart
  - setup
llm_summary: |
  Guía de instalación rápida del CDE Orchestrator MCP en 3 pasos simples.
  Cubre Windows, Linux y macOS. Incluye configuración para Claude Desktop y VS Code.
---

# ⚡ Instalación Simple - CDE Orchestrator MCP

> **Objetivo**: Tener el MCP funcionando en **menos de 5 minutos**
> **Requisitos**: Python 3.11+ (Python 3.14 funciona pero no es requerido)

---

## 🚀 Método 1: Instalación Rápida (Recomendado)

### Paso 1: Clonar e Instalar

**Windows (PowerShell)**:
```powershell
# 1. Clonar repositorio
cd E:\scripts-python
git clone https://github.com/iberi22/CDE-Orchestrator-MCP.git
cd "CDE Orchestrator MCP"

# 2. Crear virtualenv e instalar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# 3. Verificar instalación
python src/server.py
# Deberías ver: "✅ Generated X MCP tool files"
# Presiona Ctrl+C para detener
```

**Linux/macOS (bash)**:
```bash
# 1. Clonar repositorio
cd ~/projects
git clone https://github.com/iberi22/CDE-Orchestrator-MCP.git
cd CDE-Orchestrator-MCP

# 2. Crear virtualenv e instalar
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3. Verificar instalación
python src/server.py
# Deberías ver: "✅ Generated X MCP tool files"
# Presiona Ctrl+C para detener
```

✅ **¡Listo!** El servidor está instalado y funcional.

---

## 🔌 Paso 2: Configurar Tu Cliente MCP

Elige tu cliente preferido:

### Opción A: Claude Desktop (Anthropic)

**1. Ubicar archivo de configuración**:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**2. Editar configuración**:

```json
{
  "mcpServers": {
    "cde-orchestrator": {
      "command": "python",
      "args": [
        "E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py"
      ],
      "env": {
        "CDE_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Ajusta la ruta** según tu instalación:
- Windows: `E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py`
- Linux/macOS: `/home/user/projects/CDE-Orchestrator-MCP/src/server.py`

**3. Reiniciar Claude Desktop**

**4. Verificar conexión**:
```
@cde_orchestrator ¿Estás funcionando?
```

### Opción B: VS Code con GitHub Copilot

**1. Crear `.vscode/settings.json` en tu workspace**:

```json
{
  "github.copilot.advanced": {
    "mcp.enabled": true,
    "mcp.servers": {
      "cde-orchestrator": {
        "command": "python",
        "args": ["E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py"],
        "env": {
          "CDE_LOG_LEVEL": "INFO"
        }
      }
    }
  }
}
```

**2. Reiniciar VS Code**

**3. Verificar en el chat de Copilot**:
```
@cde_orchestrator Lista las herramientas disponibles
```

### Opción C: Cursor / Windsurf

Similar a VS Code, edita las settings del editor:

**Cursor**: `.cursor/config.json`
**Windsurf**: `.windsurf/config.json`

```json
{
  "mcpServers": {
    "cde-orchestrator": {
      "command": "python",
      "args": ["<RUTA_COMPLETA>/src/server.py"]
    }
  }
}
```

---

## ✅ Paso 3: Verificar Funcionamiento

### Prueba Rápida desde Python

```python
# test_mcp.py
import json
from mcp_tools import cde_setupProject, cde_listAvailableAgents

# Test 1: Setup básico
result = json.loads(cde_setupProject(project_path="."))
print(f"✅ Setup: {result['status']}")

# Test 2: Listar agentes
agents = json.loads(cde_listAvailableAgents())
print(f"✅ Agentes disponibles: {len(agents['available_agents'])}")

print("\n🎉 ¡MCP funcionando correctamente!")
```

Ejecutar:
```powershell
# Asegúrate de estar en el virtualenv
.\.venv\Scripts\Activate.ps1
cd "E:\scripts-python\CDE Orchestrator MCP"
python test_mcp.py
```

### Prueba desde Cliente MCP

**En Claude Desktop / Copilot / Cursor**:

```markdown
@cde_orchestrator Por favor ejecuta estas verificaciones:

1. Lista las herramientas disponibles
2. Analiza el proyecto en: E:\scripts-python\CDE Orchestrator MCP
3. Muéstrame los agentes AI disponibles
```

Deberías recibir respuestas estructuradas con JSON.

---

## 🛠️ Instalación Avanzada (Opcional)

### Con Rust Core (Aceleración Opcional)

**Solo si necesitas performance extra**:

```powershell
# Windows
winget install -e --id Rustlang.Rust.MSVC

# Activar virtualenv
.\.venv\Scripts\Activate.ps1

# Instalar con Rust
pip install -e ".[dev]"
maturin develop --release

# Verificar
python -c "from cde_orchestrator.rust_core import rust_available; print(rust_available())"
# Esperado: True
```

**Nota**: Rust es **opcional**. El MCP funciona perfectamente sin él (fallback a Python puro).

### Variables de Entorno (Opcional)

Crear `.env` en la raíz del proyecto:

```bash
# Logging
CDE_LOG_LEVEL=INFO  # DEBUG para troubleshooting

# Jules API (si usas el agente)
JULIUS_API_KEY=your-api-key-here

# Configuración de paths (opcional)
CDE_PROJECTS_ROOT=E:\mis-proyectos
```

---

## 🚨 Troubleshooting

### Error: "Module 'fastmcp' not found"

```powershell
# Reinstalar dependencias
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e ".[dev]"
```

### Error: "Python version 3.14 required"

**No es cierto**. Python 3.11+ funciona perfectamente:

```powershell
python --version
# Si es 3.11 o superior → Editar pyproject.toml
```

```toml
# pyproject.toml línea 10
requires-python = ">=3.11"  # Cambiar de 3.14 a 3.11
```

Luego:
```powershell
pip install -e ".[dev]"
```

### Error: "No such file or directory: src/server.py"

**Verifica la ruta**:
```powershell
# Windows
Get-Item "E:\scripts-python\CDE Orchestrator MCP\src\server.py"

# Si no existe, verifica dónde clonaste
cd "E:\scripts-python\CDE Orchestrator MCP"
dir src\server.py
```

Actualiza la configuración con la **ruta absoluta correcta**.

### Error: "Port 8766 already in use"

El MCP **no usa puertos** por defecto. Si ves este error:

```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :8766

# Matar proceso (reemplaza <PID>)
taskkill /PID <PID> /F
```

### Claude Desktop no detecta el servidor

1. **Verifica la ruta** en `claude_desktop_config.json`
2. **Usa rutas absolutas** (no relativas)
3. **Escapa backslashes** en Windows: `E:\\path\\to\\file`
4. **Reinicia Claude Desktop completamente** (cerrar + reabrir)
5. **Verifica logs**:
   - Windows: `%APPDATA%\Claude\logs\`
   - macOS: `~/Library/Logs/Claude/`

---

## 📊 Verificación Completa

Ejecuta este checklist para confirmar todo funciona:

```powershell
# Activar virtualenv
.\.venv\Scripts\Activate.ps1

# 1. Server arranca
python src/server.py
# Esperado: "✅ Generated X MCP tool files"
# Ctrl+C para detener

# 2. Tests pasan
pytest tests/integration/mcp_tools/test_documentation_tools.py::TestDocumentationTools::test_cde_setupProject_runs_successfully -v
# Esperado: PASSED

# 3. Herramientas accesibles
python -c "from mcp_tools import cde_listAvailableAgents; print('✅ MCP tools importables')"

# 4. Cliente MCP conectado
# En Claude/Copilot: @cde_orchestrator ¿Estás ahí?
```

✅ **Si todo pasa → Instalación exitosa** 🎉

---

## 🎯 Próximos Pasos

Una vez instalado:

1. **Lee la guía de inicio**: `docs/guia-inicio-paso-a-paso.md`
2. **Prueba onboarding**: `cde_onboardingProject(project_path="tu-proyecto")`
3. **Explora herramientas**: `cde_searchTools()` para ver todas las opciones
4. **Lee AGENTS.md**: Para workflows completos

---

## 💡 Consejos Pro

### Instalación Global (Sin virtualenv)

**NO recomendado**, pero si prefieres:

```powershell
pip install git+https://github.com/iberi22/CDE-Orchestrator-MCP.git
```

**Problema**: Conflictos de dependencias con otros proyectos.

### Instalación en Múltiples Máquinas

**Script de instalación automatizada**:

```powershell
# install-cde.ps1
$REPO = "https://github.com/iberi22/CDE-Orchestrator-MCP.git"
$INSTALL_PATH = "E:\scripts-python\CDE Orchestrator MCP"

git clone $REPO "$INSTALL_PATH"
cd "$INSTALL_PATH"
python -m venv .venv
& ".\.venv\Scripts\Activate.ps1"
pip install -e ".[dev]"
Write-Host "✅ CDE Orchestrator MCP instalado en: $INSTALL_PATH"
```

Ejecutar:
```powershell
powershell -ExecutionPolicy Bypass -File install-cde.ps1
```

### Actualización a Última Versión

```powershell
cd "E:\scripts-python\CDE Orchestrator MCP"
git pull origin main
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]" --upgrade
```

---

## 📞 Soporte

**Si algo no funciona**:

1. **Revisa logs**: Ejecuta con `CDE_LOG_LEVEL=DEBUG python src/server.py`
2. **Verifica tests**: `pytest tests/integration/ -v`
3. **Abre issue**: https://github.com/iberi22/CDE-Orchestrator-MCP/issues
4. **Incluye**:
   - Output de `python --version`
   - Output de `pip list | findstr "fastmcp\|pydantic"`
   - Archivo de configuración (sin secrets)

---

## ✅ Resumen de Comandos

**Instalación completa en 3 comandos**:

```powershell
git clone https://github.com/iberi22/CDE-Orchestrator-MCP.git
cd "CDE Orchestrator MCP"
python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -e ".[dev]"
```

**Verificación**:
```powershell
python src/server.py  # Debería arrancar sin errores
```

**Configuración cliente**:
- Editar `claude_desktop_config.json` o VS Code settings
- Agregar ruta absoluta a `src/server.py`
- Reiniciar cliente

🎉 **¡Listo para usar el MCP!**
