---
title: "Quick Start - MCP Status Bar MVP"
description: "Guía paso a paso para implementar el MVP minimalista en 2-3 días"
type: guide
status: active
created: "2025-11-06"
updated: "2025-11-06"
author: "CDE Team"
---

# 🚀 Quick Start - MCP Status Bar MVP

> **Objetivo**: Implementar status bar en VS Code que muestre progreso de MCP tools
> **Timeline**: 2-3 días (8-11 horas)
> **Spec Completa**: `specs/design/mcp-status-bar-minimal-mvp.md`

---

## 📋 Pre-requisitos

```bash
# Python
python --version  # 3.10+
pip install websockets

# Node.js
node --version    # 18+
npm --version     # 9+

# VS Code Extension tools
npm install -g @vscode/vsce
npm install -g yo generator-code  # opcional, para scaffold
```

---

## 🎯 Fase 1: MCP Proxy (HOY - 2-3 horas)

### Paso 1.1: Crear archivo proxy

```bash
cd "E:\scripts-python\CDE Orchestrator MCP"
mkdir -p mcp-monitor/proxy
cd mcp-monitor/proxy

# Crear mcp_proxy.py
# (copiar código de specs/design/mcp-status-bar-minimal-mvp.md líneas 118-318)
```

### Paso 1.2: Probar proxy standalone

```bash
# Terminal 1: Probar WebSocket server
python mcp_proxy.py CDE python ../../src/server.py

# Debería mostrar:
# 🚀 Starting MCP proxy for: CDE
# 📡 WebSocket server listening on ws://localhost:8766
```

### Paso 1.3: Probar con herramienta simple

```bash
# Terminal 2: Usar cliente WebSocket simple
pip install websocket-client

python -c "
import websocket
ws = websocket.WebSocket()
ws.connect('ws://localhost:8766')
print('✅ Conectado!')
ws.send('ping')
print(ws.recv())
ws.close()
"

# Debería ver "pong"
```

### ✅ Checkpoint 1

- [ ] `mcp_proxy.py` creado
- [ ] WebSocket server escucha en puerto 8766
- [ ] Ping/pong funciona

---

## 🎯 Fase 2: VS Code Extension (MAÑANA - 4-5 horas)

### Paso 2.1: Scaffold proyecto

```bash
cd "E:\scripts-python\CDE Orchestrator MCP"
mkdir mcp-status-bar
cd mcp-status-bar

# Opción A: Manual
npm init -y

# Opción B: Con generador (recomendado)
yo code
# Seleccionar:
# - New Extension (TypeScript)
# - Name: mcp-status-bar
# - Identifier: mcp-status-bar
# - Description: Show MCP progress in status bar
# - Git: No
```

### Paso 2.2: Configurar package.json

Reemplazar con:

```json
{
  "name": "mcp-status-bar",
  "displayName": "MCP Status Bar",
  "description": "Show MCP server progress in status bar",
  "version": "0.1.0",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["Other"],
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "configuration": {
      "title": "MCP Status Bar",
      "properties": {
        "mcpStatusBar.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable MCP progress in status bar"
        },
        "mcpStatusBar.proxyUrl": {
          "type": "string",
          "default": "ws://localhost:8766",
          "description": "MCP Proxy WebSocket URL"
        }
      }
    }
  },
  "scripts": {
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "package": "vsce package"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "@types/node": "^20.x",
    "@types/ws": "^8.5.10",
    "typescript": "^5.2.0"
  },
  "dependencies": {
    "ws": "^8.14.2"
  }
}
```

### Paso 2.3: Configurar TypeScript

`tsconfig.json`:

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "ES2020",
    "outDir": "out",
    "lib": ["ES2020"],
    "sourceMap": true,
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true
  },
  "exclude": ["node_modules", ".vscode-test"]
}
```

### Paso 2.4: Crear extension.ts

`src/extension.ts` - copiar código de `specs/design/mcp-status-bar-minimal-mvp.md` líneas 142-250

### Paso 2.5: Instalar dependencias y compilar

```bash
npm install
npm run compile

# Debería crear: out/extension.js
```

### ✅ Checkpoint 2

- [ ] Proyecto scaffolded
- [ ] package.json configurado
- [ ] extension.ts creado
- [ ] Compila sin errores

---

## 🎯 Fase 3: Integración (MAÑANA - 2-3 horas)

### Paso 3.1: Instalar extensión local

```bash
cd mcp-status-bar
npm run package

# Crear .vsix
code --install-extension mcp-status-bar-0.1.0.vsix
```

### Paso 3.2: Actualizar `.vscode/mcp.json`

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": [
        "E:\\scripts-python\\CDE Orchestrator MCP\\mcp-monitor\\proxy\\mcp_proxy.py",
        "CDE",
        "python",
        "src/server.py"
      ],
      "env": {
        "PYTHONPATH": "src",
        "CDE_AUTO_DISCOVER": "true"
      }
    }
  }
}
```

### Paso 3.3: Testing end-to-end

```bash
# 1. Recargar VS Code: Ctrl+Shift+P → "Developer: Reload Window"

# 2. Abrir Copilot Chat

# 3. Ejecutar: @CDE_Orchestrator scan documentation

# 4. Observar status bar (inferior derecha):
#    $(sync~spin) CDE: scanDocs 47% (12.3s)
```

### ✅ Checkpoint 3

- [ ] Extensión instalada
- [ ] VS Code conecta a proxy
- [ ] Status bar muestra progreso
- [ ] Auto-hide después de completar

---

## 🎯 Fase 4: Testing Multi-Server (PASADO MAÑANA - 2-3 horas)

### Paso 4.1: Agregar GitHub MCP

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": ["mcp-monitor/proxy/mcp_proxy.py", "CDE", "python", "src/server.py"]
    },
    "GitHub": {
      "command": "python",
      "args": [
        "mcp-monitor/proxy/mcp_proxy.py",
        "GitHub",
        "npx",
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<tu_token>"
      }
    }
  }
}
```

### Paso 4.2: Probar múltiples servers

```bash
# En Copilot Chat:

# Test 1: CDE
@CDE_Orchestrator scan documentation

# Test 2: GitHub
@GitHub search repositories query:"fastmcp"

# Verificar que status bar muestra ambos
```

### ✅ Checkpoint 4

- [ ] Al menos 2 MCP servers funcionan con proxy
- [ ] Status bar cambia según operación activa
- [ ] No hay crashes
- [ ] Latency < 200ms

---

## 📊 Success Criteria

MVP está completo cuando:

- ✅ Status bar muestra progress de MCP tools
- ✅ Funciona con ≥ 2 MCP servers diferentes
- ✅ Latency event → UI < 200ms
- ✅ Auto-hide después de 5 segundos
- ✅ Auto-reconnect si proxy reinicia
- ✅ Tooltip muestra detalles (server, tool, elapsed, message)

---

## 🐛 Troubleshooting

### Problema: "Cannot connect to ws://localhost:8766"

**Causa**: Proxy no está corriendo

**Fix**:
```bash
# Verificar que proxy está activo
netstat -an | findstr 8766

# Si no aparece, reiniciar VS Code
```

### Problema: "Status bar no aparece"

**Causa**: Extensión no está activada

**Fix**:
```bash
# Ver output de extensión
Ctrl+Shift+P → "Developer: Show Running Extensions"
# Buscar: mcp-status-bar

# Ver logs
Ctrl+Shift+P → "Developer: Toggle Developer Tools"
# Console → buscar errores
```

### Problema: "Progress nunca llega"

**Causa**: MCP server no envía `notifications/progress`

**Fix**:
```python
# En tu MCP tool, agregar:
async def my_tool(ctx):
    ctx.report_progress(0.0, "Starting...")
    # ... trabajo ...
    ctx.report_progress(0.5, "Half done...")
    # ... más trabajo ...
    ctx.report_progress(1.0, "Complete!")
```

---

## 📚 Referencias

- **Spec Completa**: `specs/design/mcp-status-bar-minimal-mvp.md`
- **Código Proxy**: Líneas 118-318 de spec
- **Código Extension**: Líneas 142-250 de spec
- **MCP Protocol**: https://spec.modelcontextprotocol.io/
- **VS Code Extension API**: https://code.visualstudio.com/api

---

## 🚀 Próximos Pasos (Fase 2)

Después de MVP funcional:

1. **TreeView Sidebar** - Lista de operaciones activas + historial
2. **Panel de Output** - Logs en tiempo real
3. **Comandos** - Show History, Clear History, Export Logs
4. **Dashboard Web** - Para múltiples proyectos

Ver: `specs/design/universal-mcp-monitor.md` (Fase 2 completa)

---

**Status**: ✅ Ready to Build
**Effort**: 8-11 horas (2-3 días)
**Impact**: 🚀 Primera extensión universal para MCP progress
