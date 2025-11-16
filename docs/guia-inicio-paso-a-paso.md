---
title: "Guía de Inicio Paso a Paso - CDE Orchestrator MCP"
description: "Guía práctica para comenzar a usar el MCP para administrar desarrollo de proyectos"
type: guide
status: active
created: "2025-11-10"
updated: "2025-11-10"
author: "CDE Team"
tags:
  - quickstart
  - tutorial
  - getting-started
llm_summary: |
  Guía paso a paso para comenzar a usar CDE Orchestrator MCP en tus proyectos.
  Incluye verificación de estado, configuración inicial, y primeros flujos de trabajo.
---

# 🚀 Guía de Inicio Paso a Paso - CDE Orchestrator MCP

> **Estado actual**: El MCP está **OPERATIVO** con funcionalidad core completa
> **Última revisión**: 10 de noviembre de 2025
> **Tests pasando**: 394 tests (algunas features en desarrollo activo)

---

## 📊 Estado Actual del Sistema

### ✅ Funcionalidad LISTA para Uso

**Core completamente funcional** (Fase 1 completada al 100%):

1. ✅ **Validación de estado robusta** (Pydantic + enums)
2. ✅ **Error handling con retry logic** (circuit breaker)
3. ✅ **Backups automáticos** de estado (`.cde/backups/`)
4. ✅ **Logging estructurado** de cambios
5. ✅ **Service connectors** (GitHub, Git, MCP detection)
6. ✅ **Repository ingestion** (análisis de código)
7. ✅ **Onboarding analyzer** (compliance con Spec-Kit)

**Herramientas MCP disponibles** (13 tools registradas):

| Tool | Estado | Propósito |
|------|--------|-----------|
| `cde_selectWorkflow` | ✅ LISTO | Analiza solicitud y recomienda workflow |
| `cde_sourceSkill` | ✅ LISTO | Descarga skills de repositorios externos |
| `cde_updateSkill` | ✅ LISTO | Actualiza skills con web research |
| `cde_scanDocumentation` | ✅ LISTO | Escanea estructura de documentación |
| `cde_analyzeDocumentation` | ✅ LISTO | Analiza calidad de docs |
| `cde_onboardingProject` | ✅ LISTO | Analiza proyecto nuevo |
| `cde_setupProject` | ✅ LISTO | Genera configs (.gitignore, AGENTS.md) |
| `cde_publishOnboarding` | ✅ LISTO | Aplica docs de onboarding |
| `cde_listAvailableAgents` | ✅ LISTO | Lista agentes AI disponibles |
| `cde_selectAgent` | ✅ LISTO | Selecciona mejor agente para tarea |
| `cde_executeWithBestAgent` | ✅ LISTO | Ejecuta tarea con agente óptimo |
| `cde_searchTools` | ✅ LISTO | Descubrimiento progresivo de tools |
| `cde_installMcpExtension` | ✅ LISTO | Instala extensión de VS Code |

### ⚠️ En Desarrollo Activo

- Jules API/CLI dual-mode integration (algunos tests fallando)
- Rust core fallback mechanism (en testing)
- Full implementation orchestration (beta)

### ❌ Pendiente (Fase 2)

- Use cases completos (en desarrollo)
- Multi-project auto-discovery
- Workflow state machine (startFeature, submitWork)

---

## 🎯 Paso 1: Verificar Instalación

### 1.1 Comprobar requisitos

```powershell
# Python 3.10+ requerido
python --version
# Esperado: Python 3.14.0 (o 3.10+)

# Verificar virtualenv activo
pip list | Select-String "fastmcp|pydantic"
# Esperado: fastmcp, pydantic en la lista
```

### 1.2 Ejecutar tests básicos

```powershell
# Cambiar al directorio del proyecto
cd "E:\scripts-python\CDE Orchestrator MCP"

# Activar virtualenv
.\.venv\Scripts\Activate.ps1

# Ejecutar tests de herramientas principales
pytest tests/integration/mcp_tools/test_documentation_tools.py -v
pytest tests/integration/adapters/test_git_adapter.py -v

# Verificar que pasen (algunos pueden estar en desarrollo)
```

### 1.3 Iniciar servidor MCP

```powershell
# Desde el directorio raíz del proyecto
python src/server.py

# Deberías ver:
# ✅ Generated X MCP tool files
# 📁 Filesystem structure: ./servers/cde/
# Starting CDE Orchestrator MCP Server
# ✅ Progressive tool discovery enabled
```

**Si hay errores**, verifica:
- ¿Está el virtualenv activado?
- ¿Instalaste las dependencias? `pip install -r requirements.txt`
- ¿Tienes `.env` configurado? (opcional, pero recomendado)

---

## 🎯 Paso 2: Configurar Tu Primer Proyecto

### 2.1 Crear estructura básica

El MCP espera que tu proyecto tenga esta estructura mínima:

```
tu-proyecto/
├── .cde/                    # Directorio de estado (se crea automáticamente)
│   ├── workflow.yml         # Opcional: flujo personalizado
│   └── state.json           # Estado del proyecto (auto-generado)
├── specs/                   # REQUERIDO para gobernanza
│   ├── features/            # Especificaciones de features
│   ├── design/              # Decisiones técnicas
│   └── tasks/               # Roadmaps
└── README.md                # Documentación del proyecto
```

### 2.2 Onboarding automático

**Opción A: Desde GitHub Copilot / Claude Desktop**

```markdown
@cde_orchestrator Por favor analiza mi proyecto y genera la configuración inicial:
- Ruta: E:\mis-proyectos\mi-app
```

El MCP ejecutará `cde_onboardingProject` automáticamente.

**Opción B: Desde Python (scripting)**

```python
import json
from mcp_tools import cde_onboardingProject

# Analizar proyecto
result_json = cde_onboardingProject(project_path="E:\\mis-proyectos\\mi-app")
result = json.loads(result_json)

print(f"Estado: {result['status']}")
print(f"Documentos generados: {len(result['generated_docs'])}")

# Ver recomendaciones
for rec in result['recommendations'][:5]:
    print(f"- {rec}")
```

### 2.3 Aplicar configuración generada

```python
from mcp_tools import cde_publishOnboarding

# Aplicar documentos generados
documents = {
    ".gitignore": "# Contenido generado...",
    "AGENTS.md": "# Instrucciones para agentes...",
    "specs/README.md": "# Estructura de specs..."
}

result_json = cde_publishOnboarding(
    documents=documents,
    project_path="E:\\mis-proyectos\\mi-app",
    approve=True
)

result = json.loads(result_json)
print(f"Archivos creados: {result['files_created']}")
```

---

## 🎯 Paso 3: Tu Primer Flujo de Trabajo

### Escenario: Agregar autenticación a tu proyecto

### 3.1 Analizar la solicitud

```python
from mcp_tools import cde_selectWorkflow

# El MCP analiza complejidad y recomienda workflow
result_json = cde_selectWorkflow(
    user_prompt="Agregar autenticación de usuarios con JWT"
)

result = json.loads(result_json)
print(f"Workflow recomendado: {result['workflow_type']}")
print(f"Complejidad: {result['complexity']}")
print(f"Duración estimada: {result['estimated_duration']}")
print(f"Skills requeridas: {result['required_skills']}")
```

**Output esperado**:
```json
{
  "workflow_type": "standard",
  "complexity": "moderate",
  "recipe_id": "ai-engineer",
  "estimated_duration": "1-2 hours",
  "required_skills": ["jwt-auth", "security-best-practices"],
  "phases_to_skip": [],
  "reasoning": "Moderate complexity security feature",
  "confidence": 0.85,
  "domain": "security"
}
```

### 3.2 Descargar skills necesarias

```python
from mcp_tools import cde_sourceSkill

# Descargar skill de autenticación JWT
result_json = cde_sourceSkill(
    skill_query="jwt authentication patterns",
    destination="ephemeral"  # Temporal para esta tarea
)

result = json.loads(result_json)
print(f"Skills encontradas: {result['skills_found']}")
print(f"Skills descargadas: {len(result['skills_downloaded'])}")

# Los skills se guardan en .copilot/skills/ephemeral/
```

### 3.3 Escanear documentación actual

```python
from mcp_tools import cde_scanDocumentation

# Escanear estado actual del proyecto
result_json = cde_scanDocumentation(
    project_path="E:\\mis-proyectos\\mi-app"
)

result = json.loads(result_json)
print(f"Total documentos: {result['total_docs']}")
print(f"Documentos sin metadata: {len(result['missing_metadata'])}")
print(f"Recomendaciones: {result['recommendations'][:3]}")
```

### 3.4 Seleccionar agente AI para ejecutar

```python
from mcp_tools import cde_selectAgent

# El MCP selecciona el mejor agente disponible
result_json = cde_selectAgent(
    task_description="Implementar autenticación JWT en FastAPI"
)

result = json.loads(result_json)
print(f"Agente seleccionado: {result['selected_agent']}")
print(f"Razonamiento: {result['reasoning']}")
print(f"Capacidades: {result['capabilities']}")
```

### 3.5 (OPCIONAL) Ejecutar con agente

**⚠️ NOTA**: Esta funcionalidad requiere configuración adicional de Jules/Copilot CLI.

```python
from mcp_tools import cde_executeWithBestAgent

# Ejecutar tarea con agente óptimo
result_json = cde_executeWithBestAgent(
    task_description="Implementar autenticación JWT en FastAPI",
    project_path="E:\\mis-proyectos\\mi-app",
    timeout=1800
)

result = json.loads(result_json)
print(f"Estado: {result['status']}")
print(f"Agente usado: {result['selected_agent']}")
print(f"Tiempo: {result['execution_time']}s")
```

---

## 🎯 Paso 4: Integración con GitHub Copilot / Claude Desktop

### 4.1 Configurar como servidor MCP

**Para Claude Desktop**, edita `claude_desktop_config.json`:

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

**Para VS Code con Copilot**, asegúrate de tener:

```json
// .vscode/settings.json
{
  "github.copilot.advanced": {
    "mcp.enabled": true,
    "mcp.servers": {
      "cde-orchestrator": {
        "command": "python",
        "args": ["src/server.py"]
      }
    }
  }
}
```

### 4.2 Usar desde el chat

```markdown
@cde_orchestrator Analiza mi proyecto en E:\mis-proyectos\mi-app
```

El agente automáticamente:
1. Llama `cde_onboardingProject`
2. Escanea documentación
3. Genera recomendaciones
4. Te las muestra estructuradas

---

## 🎯 Paso 5: Flujos de Trabajo Comunes

### Flujo 1: Análisis de Documentación

```python
from mcp_tools import cde_scanDocumentation, cde_analyzeDocumentation

# 1. Escanear estructura
scan_result = json.loads(cde_scanDocumentation("."))

# 2. Analizar calidad
analysis_result = json.loads(cde_analyzeDocumentation("."))

print(f"Score de calidad: {analysis_result['quality_score']}/100")
print(f"Links rotos: {analysis_result['link_analysis']['broken_links']}")
print(f"Issues encontrados: {len(analysis_result['issues'])}")
```

### Flujo 2: Investigación Web para Skills

```python
from mcp_tools import cde_updateSkill

# Actualizar skill con info reciente
result_json = cde_updateSkill(
    skill_name="jwt-auth",
    topics=["JWT security vulnerabilities 2025", "FastAPI JWT best practices"]
)

result = json.loads(result_json)
print(f"Insights encontrados: {len(result['insights'])}")
print(f"Versiones descubiertas: {result['version_info']}")

# La skill se actualiza automáticamente con notas de research
```

### Flujo 3: Selección Inteligente de Agentes

```python
from mcp_tools import cde_listAvailableAgents, cde_selectAgent

# 1. Ver qué agentes están disponibles
agents_json = cde_listAvailableAgents()
agents = json.loads(agents_json)

print("Agentes disponibles:")
for agent in agents['available_agents']:
    print(f"- {agent['name']}: {agent['status']}")

# 2. Seleccionar mejor agente para tarea específica
selection_json = cde_selectAgent(
    task_description="Refactorizar arquitectura de base de datos"
)
selection = json.loads(selection_json)

print(f"Recomendado: {selection['selected_agent']}")
print(f"Complejidad detectada: {selection['complexity']}")
```

---

## 🚧 Limitaciones Actuales (Fase 2 en desarrollo)

### ❌ NO disponible aún:

1. **Workflow state machine completa**:
   - `cde_startFeature()` - En desarrollo
   - `cde_submitWork()` - En desarrollo
   - `cde_getFeatureStatus()` - Planificado

2. **Multi-project auto-discovery**:
   - Escaneo automático de 1000+ proyectos
   - Indexación en segundo plano
   - (Workaround: especifica `project_path` manualmente)

3. **Jules integration completa**:
   - API mode funciona
   - CLI mode en testing
   - Algunos tests fallando (no crítico)

### ✅ Workarounds disponibles:

**Para workflows**, usa actualmente:
```python
# En lugar de:
# cde_startFeature(user_prompt="...")

# Usa la secuencia manual:
recommendation = cde_selectWorkflow(user_prompt)
skills = cde_sourceSkill(skill_query)
agent = cde_selectAgent(task_description)

# Luego ejecuta manualmente con tu agente preferido
```

**Para multi-project**, especifica paths:
```python
# En lugar de auto-discovery:
projects = ["E:\\project1", "E:\\project2", "E:\\project3"]

for project_path in projects:
    result = cde_onboardingProject(project_path=project_path)
    # Procesar resultado...
```

---

## 📚 Recursos Adicionales

### Documentación clave:

1. **AGENTS.md** - Instrucciones completas para agentes AI
2. **specs/design/ARCHITECTURE.md** - Arquitectura hexagonal
3. **specs/tasks/improvement-roadmap.md** - Roadmap de desarrollo (63 tareas)
4. **docs/mcp-tools-manual.md** - Referencia completa de herramientas

### Scripts útiles:

```powershell
# Ver estado de gobernanza de docs
python scripts/validation/validate-docs.py --all

# Agregar metadata faltante
python scripts/metadata/add-metadata.py --path specs/features/mi-feature.md

# Verificar tests
pytest tests/integration/mcp_tools/ -v

# Generar reporte de coverage
pytest --cov=src/cde_orchestrator --cov-report=html
```

---

## 🎯 Próximos Pasos Recomendados

### Para usar YA:

1. ✅ **Onboarding de proyectos** - `cde_onboardingProject` listo
2. ✅ **Análisis de documentación** - `cde_scanDocumentation` + `cde_analyzeDocumentation`
3. ✅ **Selección de workflows** - `cde_selectWorkflow` funciona perfecto
4. ✅ **Sourcing de skills** - `cde_sourceSkill` + `cde_updateSkill` operativos

### Para esperar Fase 2 (próximas 2-3 semanas):

- Workflow state machine completa
- Multi-project discovery automático
- Jules dual-mode 100% estable
- Use cases completos con tests al 80%+

---

## ❓ FAQ

### ¿Puedo usar esto en producción?

**Sí, con limitaciones**:
- ✅ Onboarding de proyectos
- ✅ Análisis de documentación
- ✅ Selección de workflows/agents
- ⚠️ Workflow completo aún no (Fase 2)

### ¿Qué agentes AI soporta?

Actualmente detecta:
- GitHub Copilot CLI
- Jules (API + CLI)
- Gemini CLI
- Qwen CLI
- Deep Agents
- Codex
- Rovo Dev

### ¿Cómo reporto problemas?

1. Crea un issue en GitHub
2. Incluye logs: `CDE_LOG_LEVEL=DEBUG python src/server.py`
3. Adjunta output de `pytest tests/integration/ -v`

---

## 🎉 ¡Listo para Empezar!

**Tu checklist**:

- [ ] Servidor MCP arranca sin errores
- [ ] Tests básicos pasan (`pytest tests/integration/mcp_tools/`)
- [ ] Onboarding funciona en un proyecto de prueba
- [ ] Scan de documentación retorna resultados
- [ ] SelectWorkflow recomienda workflow correcto

**Si todo pasa → Ya puedes administrar proyectos con el MCP** 🚀

Para más ayuda:
- Lee `AGENTS.md` para workflows completos
- Revisa `specs/tasks/improvement-roadmap.md` para ver qué viene
- Únete a discusiones en GitHub Issues
