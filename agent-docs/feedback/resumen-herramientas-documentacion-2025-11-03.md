---
title: "Resumen: Herramientas de Documentación - Análisis y Mejoras"
description: "Resumen ejecutivo del análisis de herramientas MCP para gestión de documentación con arquitectura hexagonal"
type: "feedback"
status: "draft"
created: "2025-11-03"
updated: "2025-11-03"
author: "GitHub Copilot"
tags:
  - "resumen"
  - "documentacion"
  - "mcp-tools"
  - "hexagonal"
llm_summary: |
  Resumen ejecutivo en español del análisis de herramientas MCP de documentación.
  Identifica herramienta faltante (cde_organizeAgentDocs) y recomienda patrón Gateway.
---

# Resumen: Herramientas de Documentación - Análisis y Mejoras

> **Generado**: 2025-11-03
> **Para**: Usuario (iberi22)
> **Contexto**: Mejoras para gestión de documentación con arquitectura hexagonal

---

## 🎯 Tu Pregunta

> "quiero saber en que tool se hace la limpieza y movimiento de los archivos con la especificacion de agent-docs"

## ✅ Respuesta Directa

**NO EXISTE todavía esa herramienta.**

Actualmente tienes 4 herramientas MCP de documentación:

1. ✅ `cde_onboardingProject` - Analiza y inicializa proyectos
2. ✅ `cde_publishOnboarding` - Escribe documentos generados por LLM
3. ✅ `cde_scanDocumentation` - Audita estructura de documentación
4. ✅ `cde_analyzeDocumentation` - Análisis profundo de calidad

**Pero FALTA**:
- ❌ `cde_organizeAgentDocs` - Limpieza automática de agent-docs/

---

## 📋 Lo Que Descubrí

### Herramientas Actuales

```
src/server.py (líneas 276-450)
├── cde_onboardingProject ✅ Bien implementada
├── cde_publishOnboarding ⚠️ Necesita refactorización
├── cde_scanDocumentation ✅ Bien implementada
└── cde_analyzeDocumentation ✅ Bien implementada
```

### Problemas Encontrados

1. **No hay limpieza automática de agent-docs/**
   - Los reportes quedan dispersos después de cada sesión
   - Necesitas mover manualmente archivos a subdirectorios
   - No hay archivo automático de research/ > 90 días

2. **`cde_publishOnboarding` rompe arquitectura hexagonal**
   ```python
   # ❌ MAL: Escribe archivos directamente en el MCP tool
   for path, content in documents.items():
       dest = project_root / path
       dest.write_text(content)  # NO DEBERÍA ESTAR AQUÍ
   ```

3. **No hay herramienta para crear specs profesionales**
   - Los agentes crean specs manualmente
   - No hay validación de Spec-Kit automática
   - No hay generación de metadata YAML

---

## 🆕 Herramientas Recomendadas

### 1. `cde_organizeAgentDocs` (LA QUE NECESITAS)

**Qué hace**:
- 🧹 Limpia documentos huérfanos en raíz
- 📁 Mueve a subdirectorios correctos (sessions/, execution/, feedback/)
- 📦 Archiva research/ > 90 días
- ✅ Valida metadata YAML
- 🔄 Preserva historia Git con `git mv`

**Uso**:
```python
# Vista previa (dry-run)
cde_organizeAgentDocs(dry_run=True)
# Retorna: Lista de acciones a realizar

# Ejecutar limpieza
cde_organizeAgentDocs(dry_run=False, preserve_git_history=True)
# Retorna: Archivos movidos, archivados, validados
```

**Ejemplo de salida**:
```json
{
  "actions_planned": [
    "MOVE: session-report.md → agent-docs/sessions/",
    "ARCHIVE: research/old-2024-08.md → research/.archive/",
    "ADD_METADATA: execution/report.md"
  ],
  "violations_found": 3,
  "recommendations": [
    "Run with dry_run=False to apply changes"
  ]
}
```

### 2. `cde_createSpec` (Para crear specs profesionales)

**Qué hace**:
- 📝 Crea especificaciones siguiendo Spec-Kit
- 🏷️ Genera metadata YAML automáticamente
- 🔗 Valida enlaces rotos
- 📂 Coloca en directorio correcto (specs/features/, specs/design/, etc.)

**Uso**:
```python
cde_createSpec(
    title="Redis Caching Layer",
    spec_type="design",  # feature|design|task|api
    content="""
    ## Problem
    Sistema hace llamadas repetidas a DB...

    ## Solution
    Implementar Redis con connection pooling...
    """
)
```

---

## 🏗️ Mejoras de Arquitectura: Patrón Gateway

### Problema Actual

```python
# ❌ MAL: MCP tool escribe archivos directamente
@app.tool()
def cde_publishOnboarding(documents):
    for path, content in documents.items():
        dest = project_root / path
        dest.write_text(content)  # ⚠️ Acoplamiento directo
```

### Solución: Patrón Gateway (Martin Fowler)

```
┌──────────────────────────────────────┐
│      MCP Tools (server.py)           │
│  cde_organizeAgentDocs()             │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Use Cases (application/)            │
│  OrganizeAgentDocsUseCase            │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Gateways (adapters/) 🆕             │
│  - FileSystemGateway                 │
│  - GitGateway                        │
│  - MetadataValidator                 │
└──────────────────────────────────────┘
```

**Beneficios**:
- ✅ Testeable sin I/O real
- ✅ Aislamiento de filesystem/Git
- ✅ Fácil cambiar implementación
- ✅ Arquitectura hexagonal correcta

---

## 📅 Plan de Implementación (5 Semanas)

### Semana 1: Gateway Infrastructure (CRÍTICO)

**Archivos a crear**:
- `src/cde_orchestrator/domain/ports.py` - Interfaces
- `src/cde_orchestrator/adapters/filesystem_gateway.py` 🆕
- `src/cde_orchestrator/adapters/git_gateway.py` 🆕
- `src/cde_orchestrator/adapters/metadata_validator.py` 🆕

**Esfuerzo**: 2 días

### Semana 2: Refactorizar Herramientas Existentes

**Cambios**:
- `cde_publishOnboarding` → Usar gateways
- `cde_scanDocumentation` → Usar `IFileSystemGateway`
- `cde_analyzeDocumentation` → Usar `IFileSystemGateway`

**Esfuerzo**: 2 días

### Semana 3: `cde_organizeAgentDocs` (TU PRIORIDAD)

**Archivos a crear**:
- `src/cde_orchestrator/application/documentation/organize_agent_docs_use_case.py` 🆕
- `src/server.py` - Añadir herramienta MCP
- Tests unitarios e integración

**Esfuerzo**: 3 días

### Semana 4: `cde_createSpec` (Specs profesionales)

**Archivos a crear**:
- `src/cde_orchestrator/application/documentation/create_specification_use_case.py` 🆕
- `src/server.py` - Añadir herramienta MCP
- Tests

**Esfuerzo**: 2 días

### Semana 5: Documentación y Training

**Actualizar**:
- `specs/api/mcp-tools.md` - Documentar nuevas herramientas
- `AGENTS.md` - Ejemplos de uso
- `.github/copilot-instructions.md` - Instrucciones

**Esfuerzo**: 2 días

---

## 🎯 Recomendación para Proyecto Robusto

Para usar con un proyecto real robusto, te recomiendo **este orden**:

1. **Semana 1**: Implementar Gateways (base para todo)
2. **Semana 3**: `cde_organizeAgentDocs` (necesidad inmediata)
3. **Semana 2**: Refactorizar herramientas existentes
4. **Semana 4**: `cde_createSpec` (mejora calidad de specs)
5. **Semana 5**: Documentación completa

**Prioridad justificada**:
- Gateways primero porque son la base arquitectónica
- `cde_organizeAgentDocs` segundo porque es tu necesidad inmediata
- Refactorización tercero para consolidar arquitectura
- `cde_createSpec` cuarto para mejorar calidad
- Documentación al final cuando todo está estable

---

## 📊 Comparación: Antes vs Después

### Antes (Hoy)

```bash
# Limpieza manual después de cada sesión
git mv session-report.md agent-docs/sessions/
git mv execution-log.md agent-docs/execution/
# Buscar archivos > 90 días manualmente
# Validar metadata manualmente
```

### Después (Con `cde_organizeAgentDocs`)

```python
# Una sola llamada
cde_organizeAgentDocs(dry_run=False)

# Retorna:
{
  "actions_completed": [
    "MOVED: 5 files to correct subdirectories",
    "ARCHIVED: 3 research files > 90 days",
    "FIXED_METADATA: 2 files"
  ],
  "status": "completed"
}
```

---

## 🔍 Investigación Realizada

### Fuentes Externas

1. **Martin Fowler - Gateway Pattern**
   - https://www.martinfowler.com/articles/gateway-pattern.html
   - Patrón para aislar sistemas externos
   - Ejemplos con test doubles

### Análisis de Código

1. **`src/server.py`** (líneas 83-450)
   - Herramientas MCP actuales
   - Problema en `cde_publishOnboarding`

2. **`src/cde_orchestrator/application/onboarding/`**
   - Use cases existentes
   - Patrón hexagonal actual

3. **`specs/governance/DOCUMENTATION_GOVERNANCE.md`**
   - Reglas de agent-docs/
   - Política de archivo 90 días

---

## 📚 Documentos de Referencia

**Para revisar primero**:
1. `agent-docs/feedback/documentation-management-hexagonal-analysis-2025-11-03.md` (análisis completo en inglés, 1100+ líneas)
2. `specs/governance/DOCUMENTATION_GOVERNANCE.md` (reglas actuales)
3. `specs/design/ARCHITECTURE.md` (arquitectura actual)

**Para implementación**:
1. Código de ejemplo en análisis completo
2. Interfaces de Gateway Pattern
3. Test cases sugeridos

---

## ✅ Próximos Pasos Inmediatos

### Para Ti (Decisión)

1. **Revisar análisis completo**: `agent-docs/feedback/documentation-management-hexagonal-analysis-2025-11-03.md`
2. **Decidir prioridad**: ¿Empezamos con Gateways + `cde_organizeAgentDocs`?
3. **Aprobar enfoque**: ¿Te parece bien el patrón Gateway?

### Para Mí (Implementación)

1. **Crear GitHub issues** para cada fase
2. **Empezar con Fase 1**: Implementar Gateways
3. **Continuar con Fase 3**: `cde_organizeAgentDocs`

---

## 💬 Preguntas para Ti

1. **Prioridad**: ¿Quieres `cde_organizeAgentDocs` antes que refactorizar existentes?
2. **Alcance**: ¿`cde_publishDocuments` debe reemplazar `cde_publishOnboarding` o coexistir?
3. **Testing**: ¿Tests con proyectos reales o ejemplos sintéticos?
4. **Timeline**: ¿5 semanas es razonable o necesitas más rápido?

---

## 📞 Resumen Ultra-Compacto

**Tu pregunta**: ¿Qué tool limpia agent-docs?

**Respuesta**: NO EXISTE. Necesitas `cde_organizeAgentDocs` (nueva herramienta).

**Hallazgos**:
- ✅ 4 herramientas actuales funcionan bien
- ❌ Falta limpieza automática de agent-docs/
- ⚠️ `cde_publishOnboarding` necesita refactorización
- 🆕 Recomienda patrón Gateway para arquitectura hexagonal

**Recomendación**:
1. Implementar Gateways (Semana 1)
2. Crear `cde_organizeAgentDocs` (Semana 3)
3. Refactorizar existentes (Semana 2)
4. Añadir `cde_createSpec` (Semana 4)
5. Documentar (Semana 5)

**Siguiente paso**: Revisar análisis completo y decidir prioridades.

---

**Generado por**: GitHub Copilot
**Investigación**: 45 min (web + código)
**Documento completo**: `documentation-management-hexagonal-analysis-2025-11-03.md`
