# Herramientas de Testing para Servidores MCP

> **Fecha**: 2025-11-16
> **Propósito**: Documentar herramientas disponibles para testing automatizado de servidores MCP
> **Audiencia**: Desarrolladores de servidores MCP, equipos de QA

---

## 🎯 Resumen Ejecutivo

Existen varias herramientas oficiales y de la comunidad para realizar testing automatizado de servidores MCP. La herramienta principal es **MCP Inspector**, que ofrece tanto interfaz gráfica como CLI para testing interactivo y automatizado.

---

## 🛠️ Herramientas Principales

### 1. **MCP Inspector** (Oficial - Anthropic)

#### **Descripción**
Herramienta oficial de desarrollo para testing y debugging de servidores MCP. Consiste en dos componentes:
- **MCP Inspector Client (MCPI)**: UI web React para testing interactivo
- **MCP Proxy (MCPP)**: Servidor Node.js que actúa como bridge de protocolo

#### **Repositorio**
- GitHub: https://github.com/modelcontextprotocol/inspector
- ⭐ Stars: 7.5k+
- 👥 Contribuidores: 117+
- 📦 Última versión: 0.17.3 (hace 3 días)

#### **Instalación y Uso**

**Modo UI (Interactivo)**:
```bash
# Ejecutar directamente con npx
npx @modelcontextprotocol/inspector

# El servidor inicia en http://localhost:6274
```

**Modo CLI (Automatizado)**:
```bash
# Uso básico
npx @modelcontextprotocol/inspector --cli node build/index.js

# Listar herramientas disponibles
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list

# Llamar a una herramienta específica
npx @modelcontextprotocol/inspector --cli node build/index.js \
  --method tools/call \
  --tool-name mytool \
  --tool-arg key=value

# Listar recursos
npx @modelcontextprotocol/inspector --cli node build/index.js --method resources/list

# Listar prompts
npx @modelcontextprotocol/inspector --cli node build/index.js --method prompts/list

# Con archivo de configuración
npx @modelcontextprotocol/inspector --cli \
  --config path/to/config.json \
  --server myserver \
  --method tools/list

# Conectar a servidor remoto (SSE)
npx @modelcontextprotocol/inspector --cli https://my-mcp-server.example.com

# Conectar a servidor remoto (HTTP)
npx @modelcontextprotocol/inspector --cli https://my-mcp-server.example.com \
  --transport http \
  --method tools/list \
  --header "X-API-Key: your-api-key"
```

#### **Características Principales**

**UI Mode (Testing Interactivo)**:
- ✅ Conexión a servidores por múltiples transportes (stdio, SSE, HTTP)
- ✅ Exploración visual de recursos, tools y prompts
- ✅ Testing de herramientas con inputs personalizados
- ✅ Visualización de respuestas en tiempo real
- ✅ Historial de requests
- ✅ Monitoreo de notificaciones y logs
- ✅ Soporte para OAuth/Bearer token authentication
- ✅ Exportación de configuraciones para clientes MCP

**CLI Mode (Testing Automatizado)**:
- ✅ Comandos scriptables para CI/CD
- ✅ Salida en formato JSON para parsing
- ✅ Testing de tools, resources y prompts
- ✅ Integración con coding assistants (Cursor, Copilot)
- ✅ Ideal para automatización y feedback loops

#### **Ventajas para Testing Automatizado**
- 🚀 **Integración CI/CD**: Modo CLI perfecto para pipelines
- 📊 **Salida JSON**: Fácil de parsear en scripts
- 🔄 **Feedback rápido**: Ideal para desarrollo iterativo
- 🤖 **AI Assistant Integration**: Integración con Cursor/Copilot para desarrollo asistido
- 🔐 **Seguridad**: Autenticación por default con tokens de sesión

#### **Docker Support**
```bash
docker run --rm --network host -p 6274:6274 -p 6277:6277 \
  ghcr.io/modelcontextprotocol/inspector:latest
```

---

### 2. **mcp-cli** (Community - wong2)

#### **Descripción**
CLI inspector para MCP desarrollado por la comunidad, enfocado en interacción rápida y scripting.

#### **Repositorio**
- GitHub: https://github.com/wong2/mcp-cli
- NPM: https://www.npmjs.com/package/@wong2/mcp-cli
- ⭐ Stars: 394
- 👥 Contribuidores: 4
- 📦 Licencia: GPL-3.0

#### **Instalación y Uso**

```bash
# Sin argumentos (usa config de Claude Desktop)
npx @wong2/mcp-cli

# Con archivo de configuración
npx @wong2/mcp-cli -c config.json

# Conectar a servidor NPM
npx @wong2/mcp-cli npx <package-name> <args>

# Conectar a servidor local
npx @wong2/mcp-cli node path/to/server/index.js args...

# Conectar a servidor HTTP
npx @wong2/mcp-cli --url http://localhost:8000/mcp

# Conectar a servidor SSE
npx @wong2/mcp-cli --sse http://localhost:8000/sse
```

#### **Modo No-Interactivo (Automatización)**

```bash
# Llamar herramienta sin argumentos
npx @wong2/mcp-cli -c config.json call-tool filesystem:list_files

# Llamar herramienta con argumentos (JSON)
npx @wong2/mcp-cli -c config.json call-tool filesystem:read_file \
  --args '{"path": "package.json"}'

# Leer recurso
npx @wong2/mcp-cli -c config.json read-resource \
  filesystem:file://system/etc/hosts

# Usar prompt con argumentos
npx @wong2/mcp-cli -c config.json get-prompt filesystem:create_summary \
  --args '{"text": "Hello world"}'
```

#### **Características**
- ✅ Modo interactivo con menús
- ✅ Modo no-interactivo para scripting
- ✅ Soporte OAuth para SSE y HTTP
- ✅ Listar tools, resources, prompts
- ✅ Ejecutar tools, leer resources, usar prompts
- ✅ Compatible con config de Claude Desktop

---

### 3. **Vitest** (Testing Framework para TypeScript)

#### **Descripción**
Framework de testing moderno usado en el repositorio oficial de servidores MCP.

#### **Repositorio**
- Repo oficial MCP: https://github.com/modelcontextprotocol/servers
- Documentación: https://vitest.dev/

#### **Uso en MCP Servers**

Según el README del repo oficial:
> "Add vitest testing guidelines to CONTRIBUTING.md"

Esto indica que Vitest es el framework recomendado para unit testing de servidores MCP.

**Ejemplo de configuración**:
```bash
# Instalar Vitest
npm install -D vitest

# Configurar en package.json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

---

## 📊 Comparativa de Herramientas

| Característica | MCP Inspector | mcp-cli | Vitest |
|----------------|--------------|---------|---------|
| **Tipo** | Inspector oficial | CLI comunitario | Framework testing |
| **UI Gráfica** | ✅ | ❌ | ❌ |
| **CLI Automatizado** | ✅ | ✅ | ✅ |
| **CI/CD Integration** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Transportes** | stdio/SSE/HTTP | stdio/SSE/HTTP | N/A |
| **OAuth Support** | ✅ | ✅ | N/A |
| **Docker Support** | ✅ | ❌ | N/A |
| **Modo Interactivo** | ✅ | ✅ | ❌ |
| **JSON Output** | ✅ | ✅ | ✅ |
| **Unit Testing** | ❌ | ❌ | ✅ |
| **Community Size** | 7.5k stars | 394 stars | 14k+ stars |

---

## 🎯 Recomendaciones por Caso de Uso

### Para Desarrollo Local
**Usar**: MCP Inspector (Modo UI)
- Interfaz visual para exploración
- Debugging interactivo
- Testing manual de features

### Para CI/CD Pipelines
**Usar**: MCP Inspector (Modo CLI) + Vitest
```bash
# En GitHub Actions / GitLab CI
- name: Test MCP Server
  run: |
    npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list
    npm run test  # Vitest unit tests
```

### Para Scripting y Automatización
**Usar**: mcp-cli (Modo no-interactivo)
```bash
#!/bin/bash
# Script de testing automatizado
echo "Testing MCP Server..."
npx @wong2/mcp-cli -c config.json call-tool filesystem:read_file \
  --args '{"path": "test.txt"}' | jq .
```

### Para Unit Testing
**Usar**: Vitest
```typescript
// tests/server.test.ts
import { describe, it, expect } from 'vitest'
import { MyMCPServer } from '../src/server'

describe('MCP Server', () => {
  it('should list tools correctly', async () => {
    const server = new MyMCPServer()
    const tools = await server.listTools()
    expect(tools).toHaveLength(5)
  })
})
```

---

## 🔧 Configuración para Nuestro Proyecto

### **Configuración Recomendada**

**1. Agregar al `package.json`**:
```json
{
  "scripts": {
    "test": "vitest",
    "test:inspector": "npx @modelcontextprotocol/inspector --cli python src/server.py",
    "test:tools": "npx @modelcontextprotocol/inspector --cli python src/server.py --method tools/list",
    "test:ci": "npm run test && npm run test:tools"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "@modelcontextprotocol/inspector": "latest"
  }
}
```

**2. Crear archivo de configuración** `mcp-test-config.json`:
```json
{
  "mcpServers": {
    "cde-orchestrator": {
      "command": "python",
      "args": ["src/server.py", "--scan-paths", "E:\\scripts-python"],
      "env": {
        "CDE_AUTO_DISCOVER": "true",
        "CDE_LOG_LEVEL": "INFO",
        "PYTHONPATH": "src"
      }
    }
  }
}
```

**3. Integrar en CI/CD** (`.github/workflows/test-mcp.yml`):
```yaml
name: Test MCP Server

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          npm install -g @modelcontextprotocol/inspector

      - name: Run MCP Tests
        run: |
          npx @modelcontextprotocol/inspector --cli \
            --config mcp-test-config.json \
            --server cde-orchestrator \
            --method tools/list

      - name: Test Specific Tools
        run: |
          npx @modelcontextprotocol/inspector --cli \
            --config mcp-test-config.json \
            --server cde-orchestrator \
            --method tools/call \
            --tool-name cde_scanDocumentation \
            --tool-arg 'project_path=.'
```

---

## 📚 Recursos Adicionales

### **Documentación Oficial**
- MCP Inspector: https://modelcontextprotocol.io/docs/tools/inspector
- MCP Testing Guide: https://modelcontextprotocol.io/docs/tools/testing
- MCP Debugging: https://modelcontextprotocol.io/docs/tools/debugging

### **Repositorios de Referencia**
- MCP Inspector: https://github.com/modelcontextprotocol/inspector
- MCP Servers (ejemplos oficiales): https://github.com/modelcontextprotocol/servers
- mcp-cli: https://github.com/wong2/mcp-cli

### **Testing en la Comunidad**
- AltTester MCP: https://alttester.com/docs/desktop/latest/pages/ai-extension.html
- Debugg.AI: https://github.com/debugg-ai/debugg-ai-mcp (Zero-Config E2E Testing)
- LambdaTest MCP: https://www.lambdatest.com/mcp

---

## 🚀 Próximos Pasos

### **Para Implementar**
1. ✅ Instalar MCP Inspector: `npm install -g @modelcontextprotocol/inspector`
2. ✅ Crear `mcp-test-config.json` con nuestra configuración
3. ✅ Agregar scripts de testing al `package.json`
4. ✅ Probar manualmente con Modo UI
5. ✅ Automatizar con Modo CLI
6. ✅ Integrar en CI/CD pipeline

### **Para Validar**
```bash
# 1. Test básico de conectividad
npx @modelcontextprotocol/inspector --cli python src/server.py

# 2. Listar herramientas disponibles
npx @modelcontextprotocol/inspector --cli python src/server.py --method tools/list

# 3. Test de herramienta específica
npx @modelcontextprotocol/inspector --cli python src/server.py \
  --method tools/call \
  --tool-name cde_scanDocumentation \
  --tool-arg 'project_path=.'

# 4. Verificar salida JSON
npx @modelcontextprotocol/inspector --cli python src/server.py \
  --method tools/list | jq '.tools[].name'
```

---

## 📝 Conclusión

Para testing automatizado de nuestro servidor MCP, recomendamos:

**🥇 Prioridad 1**: **MCP Inspector (Modo CLI)**
- Es la herramienta oficial
- Soporte completo para stdio/SSE/HTTP
- Perfecto para CI/CD
- Activamente mantenido por Anthropic

**🥈 Prioridad 2**: **Vitest** (Para unit tests)
- Framework moderno y rápido
- Usado en el repo oficial de MCP
- Ideal para testing de lógica de negocio

**🥉 Prioridad 3**: **mcp-cli** (Alternativa ligera)
- Para scripting rápido
- Buena opción si no necesitas UI
- Comunidad activa

---

**Siguiente acción recomendada**: Ejecutar prueba básica con MCP Inspector para validar nuestro servidor.
