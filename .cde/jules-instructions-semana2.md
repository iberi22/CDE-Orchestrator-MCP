# DELEGACIÓN A JULES: SEMANA 2 DOCUMENTATION CLEANUP

## 🎯 MISIÓN PRINCIPAL

Mejorar conformidad de governance de documentación:
- **Desde**: 88 errores de governance
- **Hacia**: <20 errores
- **Métrica**: Compliance score: 54.8/100 → 85+/100

## 📋 TAREAS (Orden de Ejecución)

### TAREA 1: Agregar Metadata YAML a 160+ Archivos (3-4 horas)

**Prioridad**: 🔴 CRÍTICA

**Descripción**: Agregar frontmatter YAML obligatorio a archivos sin metadata

**Ubicaciones target**:
- agent-docs/execution/ (30+ files)
- agent-docs/sessions/ (15+ files)
- agent-docs/feedback/ (8+ files)
- agent-docs/research/ (5+ files)
- specs/design/ (20+ files)
- specs/features/ (10+ files)
- specs/tasks/ (5+ files)
- docs/ (80+ files)

**Formato requerido**:
```yaml
---
title: "Document Title"
description: "One sentence (50-150 chars)"
type: "execution|session|feedback|research|design|feature|task|guide"
status: "active|archived|deprecated|draft"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Jules AI"
llm_summary: "2-3 sentence summary optimized for LLM context"
---
```

**Automatización disponible**:
```bash
python scripts/automation/semana2-cleanup.py --phase 1
```

**Success Criteria**:
- ✅ 160+ archivos con frontmatter válido
- ✅ Todos los campos requeridos presentes
- ✅ llm_summary generado para archivos >500 líneas
- ✅ Valores type correctos según directorio

---

### TAREA 2: Corregir Violaciones de Metadata (2-3 horas)

**Prioridad**: 🔴 CRÍTICA

**Descripción**: Arreglar errores en valores de enum y formatos

#### 2A: Corregir Status Enum
Cambiar valores inválidos a valores permitidos:

| INCORRECTO | CORRECTO |
|-----------|----------|
| "completed" | "archived" |
| "in-progress" | "active" |
| "ready" | "active" |
| "done" | "archived" |

**Affected files**: ~25 archivos en agent-docs/

#### 2B: Corregir Formato de Fechas
Cambiar ISO 8601 a YYYY-MM-DD:

```
INCORRECTO: "2025-11-05T20:45:00Z"
CORRECTO: "2025-11-05"
```

**Affected files**: ~10 archivos

#### 2C: Campos Faltantes
Validar presencia de:
- title
- description
- type
- status
- created
- updated
- author

**Automatización disponible**:
```bash
python scripts/automation/semana2-cleanup.py --phase 2
```

**Success Criteria**:
- ✅ 0 status enum violations
- ✅ 0 date format violations
- ✅ 0 missing required fields
- ✅ Governance errors: 88 → <30

---

### TAREA 3: Normalizar Convenciones de Nombres (1-2 horas)

**Prioridad**: 🟡 MEDIA

**Descripción**: Convertir nombres UPPERCASE a lowercase-hyphens

#### Pattern Conversion
```
INCORRECTO → CORRECTO
ARCHITECTURE.md → architecture.md
EXECUTIVE_SUMMARY.md → executive-summary.md
SESSION_SUMMARY_V2_REVISION.md → session-summary-v2-revision.md
DOCUMENTATION_GOVERNANCE.md → documentation-governance.md
```

**Directorios target**:
- specs/design/ (8 files)
- specs/governance/ (3 files)
- specs/templates/ (3 files)
- specs/ root (5+ files)
- docs/ (20+ files)

**Proceso**:
1. ✅ Usar `git mv` para preservar historia Git
2. ✅ Actualizar todos los links internos
3. ✅ Verificar que no hay referencias rotas
4. ✅ Hacer commit de cambios

**Automatización disponible**:
```bash
python scripts/automation/semana2-cleanup.py --phase 3
```

**Success Criteria**:
- ✅ 75+ archivos renombrados a lowercase-hyphens
- ✅ Todos los links internos actualizados
- ✅ 0 referencias rotas
- ✅ Governance warnings: 66 → <5

---

## 🔍 ARCHIVOS DE REFERENCIA CLAVE

| Archivo | Propósito |
|---------|-----------|
| `specs/governance/DOCUMENTATION_GOVERNANCE.md` | Reglas maestras de governance |
| `specs/templates/document-metadata.md` | Template de metadata |
| `.pre-commit-config.yaml` | Validación automática |
| `scripts/validation/validate-docs.py` | Validador de compliance |
| `agent-docs/execution/delegation-semana2-to-jules-2025-11-07.md` | Detalles de delegación |

---

## 📊 VALIDACIÓN Y VERIFICACIÓN

Después de completar cada fase:

```bash
# Validar compliance
python scripts/validation/validate-docs.py --all

# Expected output:
# Errors: 88 → 30 → <20
# Warnings: 66 → 10 → <5
```

---

## 💾 SCRIPTS AUTOMATION DISPONIBLES

### Script Principal (Multi-fase)
```bash
python scripts/automation/semana2-cleanup.py --all
```

### Fases Individuales
```bash
python scripts/automation/semana2-cleanup.py --phase 1  # Metadata
python scripts/automation/semana2-cleanup.py --phase 2  # Fix Enums
python scripts/automation/semana2-cleanup.py --phase 3  # Rename Files
```

---

## 📈 IMPACTO ESTIMADO

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Governance Errors | 88 | <20 | ✅ 77% |
| Governance Warnings | 66 | <5 | ✅ 92% |
| Compliance Score | 54.8/100 | 85+/100 | ✅ 55% |
| Tokens LLM Saved | 0 | 56,000/month | ✅ $1.68-$37.5K |
| Files with Metadata | 60% | 100% | ✅ 40% |

---

## 🚀 ORDEN DE EJECUCIÓN RECOMENDADO

```
1. Phase 1: Metadata (3-4h)
   → Commit después de completar

2. Phase 2: Fix Enums (2-3h)
   → Validate después de completar
   → Commit

3. Phase 3: Normalize Names (1-2h)
   → Update links
   → Commit

4. Final Validation (30m)
   → Run validate-docs.py
   → Report results
```

---

## 📞 STATUS REPORTING

Reportar progreso después de cada fase con formato:

```
feat(metadata): Complete Phase [1/2/3] - [X/Y] tasks done

- Completed: [description]
- Governance Score: [before] → [after]
- Files processed: [count]
- Errors remaining: [count]

See: [commit-sha]
```

---

## ✅ DEFINICIÓN DE LISTO ("Done Done")

- [ ] Phase 1: 160+ files con metadata valid
- [ ] Phase 2: Todos los enums corregidos
- [ ] Phase 3: Todos los nombres normalizados
- [ ] Validación: <20 errors, <5 warnings
- [ ] Pre-commit: Todos los checks pasan
- [ ] Git: Commits limpios con mensajes claros
- [ ] Documentación: Actualizada

---

## 🎓 CONOCIMIENTO CLAVE

### Governance Rules
- Max 1500 líneas por archivo
- Metadata YAML obligatoria (excepto root exceptions)
- Type debe ser: feature|design|task|guide|governance|session|execution|feedback|research
- Status debe ser: active|archived|deprecated|draft
- Dates en YYYY-MM-DD (NO ISO 8601)
- Filenames lowercase-hyphens (NO UPPERCASE, NO spaces)

### Directories
- Specifications: `specs/features/`, `specs/design/`, `specs/tasks/`
- Executions: `agent-docs/execution/`
- Sessions: `agent-docs/sessions/`
- Feedback: `agent-docs/feedback/`
- Research: `agent-docs/research/`
- Docs: `docs/`

---

## 🔗 CONTACTS & RESOURCES

**Pre-commit Validation**: `.pre-commit-config.yaml`
**Validation Script**: `scripts/validation/validate-docs.py`
**Reference Guide**: `.github/copilot-instructions.md`

---

**¿LISTO PARA EJECUTAR?**

La automatización está disponible en:
- `scripts/automation/semana2-cleanup.py`

Ejecutar con:
```bash
cd "E:\scripts-python\CDE Orchestrator MCP"
python scripts/automation/semana2-cleanup.py --all
```

O ejecutar fases individuales según necesidad.

---

**Delegado por**: GitHub Copilot
**Fecha**: 2025-11-07
**Target Completion**: 2025-11-09 (Semana 2)
