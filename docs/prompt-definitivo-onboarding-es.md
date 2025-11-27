---
title: Prompt Definitivo Onboarding Es
description: Legacy documentation file
type: guide
status: archived
created: '2025-11-27'
updated: '2025-11-27'
author: Legacy
---

# 🎯 EL PROMPT DEFINITIVO - CDE Onboarding Profesional

> **Propósito**: Un solo prompt para integración completa de CDE desde 0% hasta 100%
> **Actualizado**: 2025-11-26
> **Versión**: 2.0 - Optimizado para ejecución real
> **Idioma**: Español (para ti) + Inglés (para agentes)

---

## 📋 RESUMEN EJECUTIVO

Este documento contiene **EL PROMPT DEFINITIVO** que orquesta TODO el sistema CDE en un solo comando:

1. ✅ **Analiza** tu proyecto actual con Git history y framework detection
2. ✅ **Configura** toda la estructura CDE (specs/, memory/, .cde/)
3. ✅ **Genera** specs profesionales automáticamente (spec.md, plan.md, tasks.md)
4. ✅ **Recomienda** el workflow óptimo basado en complejidad
5. ✅ **Verifica** que todo funcione (25 herramientas MCP)
6. ✅ **Guía** los próximos pasos

---

## 🚀 EL PROMPT PROFESIONAL (Cópialo y úsalo)

```markdown
@workspace I need to integrate CDE Orchestrator as the complete development orchestration system for this project.

⚠️ CRITICAL: You MUST use the `mcp_cde` MCP server tools. Do NOT just describe - EXECUTE each tool!

## Available MCP Tools (from mcp_cde server)
These are the exact tool names you must invoke:
- `mcp_cde_cde_onboardingProject` - Deep project analysis
- `mcp_cde_cde_setupProject` - Create CDE structure
- `mcp_cde_cde_healthCheck` - Verify system health
- `mcp_cde_cde_selectWorkflow` - Recommend optimal workflow
- `mcp_cde_cde_generateSpec` - Generate Spec-Kit documentation

## Phase 1: Project Analysis
**EXECUTE** MCP tool `mcp_cde_cde_onboardingProject` with parameter `project_path="."` to perform deep analysis:
- File count and language distribution
- Framework and architecture detection
- Git history insights (commits, contributors, age)
- AI assistant configurations detected

## Phase 2: Project Setup
**EXECUTE** MCP tool `mcp_cde_cde_setupProject` with parameter `project_path="."` to create CDE structure:
- .cde/workflow.yml (6-phase workflow config)
- AGENTS.md (AI agent guidelines)
- specs/templates/ (Spec-Kit templates)
- memory/constitution.md (project principles)

## Phase 3: Health Verification
**EXECUTE** MCP tool `mcp_cde_cde_healthCheck` (no parameters needed) to verify:
- All 25 CDE tools are registered
- Python/Rust components working
- MCP server healthy

## Phase 4: Workflow Selection
**EXECUTE** MCP tool `mcp_cde_cde_selectWorkflow` with parameter `user_prompt="[DESCRIBE YOUR NEXT FEATURE HERE]"` to get:
- Recommended workflow type (standard, quick-fix, research)
- Complexity assessment (trivial → epic)
- Duration estimate
- Required skills

## Phase 5: Spec Generation
**EXECUTE** MCP tool `mcp_cde_cde_generateSpec` with parameter `feature_description="[YOUR FEATURE DESCRIPTION]"` to create:
- specs/[feature]/spec.md (Product Requirements)
- specs/[feature]/plan.md (Technical Design)
- specs/[feature]/tasks.md (Implementation Checklist)

## Output Requirements
For EACH phase, show:
- ✅ Tool executed successfully with actual output
- 📊 Key metrics and insights
- 📝 Files created or analyzed
- ➡️ Transition to next phase

If any tool fails, run `mcp_cde_cde_healthCheck` and report the issue.

⚠️ REMINDER: Use the actual MCP tools from `mcp_cde` server, not function calls!

**My next feature to implement**: [DESCRIBE YOUR FEATURE HERE]

Execute all 5 phases using the MCP tools and provide a comprehensive onboarding report.
```

---

## 💡 ¿POR QUÉ ESTE PROMPT ES PERFECTO?

### 1. **Funciona desde cualquier punto**

| Estado del Proyecto | Qué hace CDE |
|---------------------|--------------|
| **0% (Nuevo)** | Crea toda la estructura desde cero |
| **50% (En progreso)** | Analiza existente + completa faltante |
| **100% (Completo)** | Verifica conformidad + genera mejoras |

### 2. **Orquesta 5 herramientas en secuencia óptima**

```
cde_onboardingProject()     → Análisis profundo
         ↓
cde_setupProject()          → Crear estructura
         ↓
cde_healthCheck()           → Verificar sistema
         ↓
cde_selectWorkflow()        → Recomendar workflow
         ↓
cde_generateSpec()          → Crear documentación
```

### 3. **Output profesional y estructurado**

Cada fase genera:
- ✅ **Análisis con métricas reales** (archivos, líneas, frameworks)
- ✅ **Archivos creados** (AGENTS.md, specs/, .cde/, memory/)
- ✅ **Specs profesionales** (3 documentos Spec-Kit)
- ✅ **Recomendaciones** (skills, workflow, duración estimada)

---

## 📊 QUÉ HACE CADA FASE

### Fase 1: Análisis Profundo (`cde_onboardingProject`)

**Input**: Ruta del proyecto
**Output**:

```json
{
  "total_files": 245,
  "python_version": "3.14.0",
  "frameworks": ["FastAPI", "React"],
  "architecture": "Hexagonal",
  "git_commits": 156,
  "contributors": 3,
  "ai_tools": ["Copilot", "Cursor"]
}
```

### Fase 2: Setup Estructura (`cde_setupProject`)

**Input**: Proyecto analizado
**Output**: Archivos creados automáticamente

- `.cde/workflow.yml` - Configuración de workflow 6-fases
- `AGENTS.md` - Guías para agentes AI
- `specs/templates/` - Templates Spec-Kit
- `memory/constitution.md` - Principios del proyecto

### Fase 3: Verificación (`cde_healthCheck`)

**Output**:

```json
{
  "status": "healthy",
  "tools_registered": 25,
  "python_healthy": true,
  "rust_healthy": true
}
```

### Fase 4: Selección de Workflow (`cde_selectWorkflow`)

**Output**:

```json
{
  "workflow_type": "standard",
  "complexity": "moderate",
  "duration": "2-4 hours",
  "recipe": "ai-engineer",
  "required_skills": ["redis-caching", "auth-patterns"]
}
```

### Fase 5: Generación de Spec (`cde_generateSpec`)

**Input**: Descripción del feature
**Output**: Directorio completo de especificación

- `specs/[feature]/spec.md` - Product Requirements Document
- `specs/[feature]/plan.md` - Technical Design Document
- `specs/[feature]/tasks.md` - Implementation Checklist (45+ tareas)

---

## 🎬 EJEMPLO COMPLETO

### Tu Prompt

```markdown
@workspace I need to integrate CDE Orchestrator for this project.
My next feature: "Add Redis caching to authentication module"
Execute all phases and provide comprehensive report.
```

### Respuesta Esperada del Agente

#### ✅ FASE 1: Análisis Completo

```text
Proyecto: MiApp
├── 245 archivos Python
├── FastAPI 0.115.0
├── Arquitectura: Hexagonal
├── 156 commits, 3 contributors
└── Copilot detectado
```

#### ✅ FASE 2: Estructura Creada

```text
Archivos creados:
├── .cde/workflow.yml
├── AGENTS.md
├── specs/templates/
└── memory/constitution.md
```

#### ✅ FASE 3: Verificación

```text
Health: ✅ Healthy
Tools: 25 registrados
Python: 3.14.0
Rust: ✅ Active
```

#### ✅ FASE 4: Workflow Recomendado

```text
Tipo: Standard (6-phase)
Complejidad: Moderate
Duración: 2-4 horas
Recipe: ai-engineer.poml
Skills requeridos: redis-caching, auth-patterns
```

#### ✅ FASE 5: Spec Generado

```text
Location: specs/add-redis-caching-to-authentication/
├── spec.md (Product Requirements)
├── plan.md (Technical Design)
└── tasks.md (45 tareas ejecutables)
```

---

## 🎯 CASOS DE USO

### Caso 1: Proyecto Nuevo (0%)

```markdown
@workspace Nuevo proyecto FastAPI desde cero.
Integra CDE para orquestar todo el desarrollo.
```

### Caso 2: Proyecto Existente (50%)

```markdown
@workspace Proyecto existente con 50% implementado.
Integra CDE para gestionar desarrollo futuro.
Feature próximo: "Add payment processing"
```

### Caso 3: Feature Específico

```markdown
@workspace Analiza proyecto e integra CDE.
Genera spec profesional para: "Implement OAuth2 authentication"
```

---

## ✅ CHECKLIST DE ÉXITO

Después de usar el prompt, deberías tener:

- ✅ Proyecto analizado (archivos, Git, frameworks)
- ✅ Estructura creada (specs/, memory/, .cde/)
- ✅ 25 herramientas CDE disponibles
- ✅ Spec profesional generado (3 documentos)
- ✅ Workflow recomendado
- ✅ Próximos pasos claros

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Tool not found

**Solución**: Reload VS Code (Ctrl+Shift+P → Reload Window)

### Health check muestra menos de 25 tools

**Solución**:

```powershell
.\scripts\diagnose-cde-tools.ps1
```

### Spec generation fails

**Solución**: Ejecuta `cde_onboardingProject` primero

---

## 📚 DOCUMENTACIÓN COMPLETA

He creado 3 documentos:

1. **`THE-ULTIMATE-ONBOARDING-PROMPT.md`** (Inglés, 600 líneas)
   - Prompt completo
   - Explicación de cada fase
   - Ejemplos detallados
   - Troubleshooting

2. **`PROMPT-DEFINITIVO-ONBOARDING-ES.md`** (Este archivo, Español)
   - Resumen ejecutivo
   - Casos de uso
   - Ejemplos reales

3. **`docs/README.md`** (Actualizado)
   - Enlace al prompt como START HERE

---

## 🚀 FLUJO POST-ONBOARDING

Una vez integrado CDE, tu flujo de desarrollo es:

```text
1. Nuevo Feature
   ↓
2. cde_selectWorkflow("Feature X")
   ↓
3. cde_generateSpec("Feature X")
   ↓
4. cde_sourceSkill("required-skill")
   ↓
5. cde_startFeature("Feature X")
   ↓
6-11. Work phases 1-6
   ↓
12. cde_submitWork per phase
   ↓
13. Feature Complete ✅
```

---

## 💡 RECOMENDACIONES

1. **Usa el prompt completo**: No intentes hacer pasos individuales
2. **Revisa los specs generados**: CDE crea documentos profesionales pero revísalos
3. **Descarga skills**: `cde_sourceSkill` trae conocimiento externo
4. **Sigue el workflow de 6 fases**: Define → Decompose → Design → Implement → Test → Review
5. **Confía en la orquestación**: CDE sabe qué tool usar y cuándo

---

## 🎓 SIGUIENTE NIVEL: Multi-Proyecto

Para gestionar múltiples proyectos simultáneamente:

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "args": [
        "..\\src\\server.py",
        "--scan-paths",
        "E:\\proyecto1",
        "E:\\proyecto2",
        "E:\\proyecto3"
      ]
    }
  }
}
```

CDE auto-descubre todos los proyectos y rutea comandos correctamente.

---

## 📍 UBICACIONES DE ARCHIVOS

| Archivo | Descripción |
|---------|-------------|
| `docs/THE-ULTIMATE-ONBOARDING-PROMPT.md` | Prompt completo (Inglés) |
| `docs/PROMPT-DEFINITIVO-ONBOARDING-ES.md` | Este archivo (Español) |
| `docs/QUICKFIX-RELOAD-TOOLS.md` | Solución rápida de problemas |
| `docs/configuration-guide.md` | Guía de configuración |
| `scripts/diagnose-cde-tools.ps1` | Script de diagnóstico |

---

## 🎯 RESULTADO FINAL

En 2 minutos obtienes:

- ✅ Proyecto completamente analizado
- ✅ Estructura CDE implementada
- ✅ 25 herramientas disponibles
- ✅ Specs profesionales generados
- ✅ Workflow optimizado
- ✅ Roadmap claro

---

## TL;DR

Copia el prompt del inicio, pégalo en Copilot Chat, espera 2 minutos, CDE orquesta todo. ✅
