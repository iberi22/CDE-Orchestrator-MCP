# MCP Server Automated Testing

> **Herramienta implementada**: Sistema de testing automatizado para CDE Orchestrator MCP Server

## 🎯 Resumen Ejecutivo

Este proyecto ahora incluye un **sistema completo de testing automatizado** para el servidor MCP:

- ✅ **Test directo en Python** (`test_mcp_server.py`) - Sin dependencias externas
- ✅ **CI/CD con GitHub Actions** (`.github/workflows/test-mcp-server.yml`)
- ✅ **Guía de herramientas** (`docs/mcp-testing-tools.md`) - MCP Inspector, mcp-cli, Vitest

## 🚀 Inicio Rápido

### Ejecutar Tests Localmente

```bash
# Test directo (más rápido, sin dependencias npm)
python test_mcp_server.py

# Output esperado:
# [OK] ALL TESTS PASSED - MCP Server is working correctly!
# Tests Passed: 4/4
```

### Ejecutar Tests con MCP Inspector (Opcional)

```bash
# Opción 1: npm (requiere Node.js 22+)
npx @modelcontextprotocol/inspector \
  --cli python src/server.py \
  --method tools/list

# Opción 2: Docker (sin instalación)
docker run --rm \
  -v $(pwd):/workspace \
  ghcr.io/modelcontextprotocol/inspector:latest \
  --cli python src/server.py \
  --method tools/list
```

## 📋 Tests Implementados

### Test Suite Principal (`test_mcp_server.py`)

| Test | Herramienta | Resultado |
|------|-------------|-----------|
| **Progressive Disclosure** | `cde_searchTools` | ✅ Pasa (16 tools encontrados) |
| **Token Optimization** | `cde_searchTools` (detail_level) | ✅ Pasa (6 doc tools) |
| **Multi-Project** | `cde_scanDocumentation` | ✅ Pasa (916 archivos escaneados) |
| **Intelligent Orchestration** | `cde_selectWorkflow` | ✅ Pasa (workflow: standard, complexity: simple) |

### Métricas de Ejecución

```
Duración: < 2 segundos
Dependencias: Solo Python stdlib + proyecto actual
Tests: 4/4 pasando
Cobertura: Funcionalidades core del MCP server
```

## 🔧 Arquitectura del Sistema de Testing

```
CDE Orchestrator MCP/
├── test_mcp_server.py          # ⭐ Test directo en Python
├── .github/
│   └── workflows/
│       └── test-mcp-server.yml # CI/CD automatizado
├── docs/
│   └── mcp-testing-tools.md    # Guía completa de herramientas
└── src/
    └── mcp_tools/              # Implementaciones reales testeadas
        ├── tool_search.py
        ├── documentation.py
        └── orchestration.py
```

## 📊 Comparación de Herramientas

| Herramienta | Tipo | Uso | Estado |
|-------------|------|-----|--------|
| **test_mcp_server.py** | Direct Python | Local testing | ✅ Funcionando |
| **MCP Inspector** | Official Anthropic | Integration testing | ⚠️ npm issue (use Docker) |
| **mcp-cli** | Community | Scripting | ✅ Alternativa funcional |
| **GitHub Actions** | CI/CD | Automated testing | ✅ Configurado |

## 🛠️ Uso de Herramientas Avanzadas

### MCP Inspector (Modo CLI)

```bash
# Listar herramientas
npx @modelcontextprotocol/inspector \
  --cli python src/server.py \
  --method tools/list

# Llamar herramienta específica
npx @modelcontextprotocol/inspector \
  --cli python src/server.py \
  --method tools/call \
  --tool-name cde_searchTools \
  --tool-arg 'query=documentation' \
  --tool-arg 'detail_level=name_and_description'

# Listar recursos
npx @modelcontextprotocol/inspector \
  --cli python src/server.py \
  --method resources/list
```

### mcp-cli (Alternativa Comunitaria)

```bash
# Modo interactivo
npx @wong2/mcp-cli python src/server.py

# Modo no-interactivo (scripting)
npx @wong2/mcp-cli \
  -c mcp-test-config.json \
  call-tool cde-orchestrator:cde_searchTools \
  --args '{"query": "", "detail_level": "name_only"}'
```

### Docker (Sin Instalación Local)

```bash
# MCP Inspector en Docker
docker run --rm \
  -p 6274:6274 -p 6277:6277 \
  -v $(pwd):/workspace \
  ghcr.io/modelcontextprotocol/inspector:latest
```

## 🔄 CI/CD Pipeline

El pipeline de GitHub Actions ejecuta automáticamente:

1. **Tests directos** en Python 3.11, 3.12, 3.13, 3.14
2. **Tests con MCP Inspector** (opcional, requiere Node.js)
3. **Subida de artefactos** si hay fallos
4. **Resumen en GitHub** con resultados

### Configuración

```yaml
# .github/workflows/test-mcp-server.yml
on:
  push:
    branches: [ main, develop ]
  pull_request:
  workflow_dispatch:  # Ejecución manual
```

### Triggers

- ✅ **Push** a `main` o `develop`
- ✅ **Pull Request** a esas ramas
- ✅ **Manual** desde GitHub Actions UI

## 📖 Documentación Completa

Ver `docs/mcp-testing-tools.md` para:

- Instalación detallada de todas las herramientas
- Comparación exhaustiva de características
- Ejemplos de configuración para CI/CD
- Troubleshooting común
- Referencias a documentación oficial

## 🐛 Troubleshooting

### Error: npm "cb.apply is not a function"

**Solución 1: Usar Docker**
```bash
docker run --rm ghcr.io/modelcontextprotocol/inspector:latest
```

**Solución 2: Limpiar caché npm**
```bash
npm cache clean --force
npm install -g npm@latest
npx @modelcontextprotocol/inspector --version
```

**Solución 3: Usar mcp-cli como alternativa**
```bash
npx @wong2/mcp-cli python src/server.py
```

### Error: Unicode en Windows

El script `test_mcp_server.py` ya incluye fix automático:

```python
if sys.platform == "win32":
    os.system("chcp 65001 > NUL 2>&1")
    sys.stdout.reconfigure(encoding='utf-8')
```

### Error: Módulos no encontrados

```bash
# Verificar paths
python -c "import sys; print('\n'.join(sys.path))"

# Reinstalar dependencias
pip install -r requirements.txt
```

## 📈 Próximos Pasos

- [ ] Expandir test suite con más herramientas MCP
- [ ] Agregar tests de integración con Copilot CLI
- [ ] Implementar tests de rendimiento (latencia, throughput)
- [ ] Configurar coverage reporting
- [ ] Agregar tests de seguridad (autenticación, autorización)

## 🔗 Referencias

- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **mcp-cli**: https://github.com/wong2/mcp-cli
- **MCP Protocol**: https://modelcontextprotocol.io
- **Documentación local**: `docs/mcp-testing-tools.md`

---

**Status**: ✅ Sistema de testing completamente funcional y documentado

**Last Updated**: 2025-11-16

**Author**: CDE Team
