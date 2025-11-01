# Análisis de Gobernanza de Documentación Generada por Agentes IA

> **Fecha**: 2025-11-01
> **Agente**: KERNEL (GPT-5 Low → High)
> **Estado**: Propuesta para revisión humana

---

## 📋 Executive Summary

### Situación Actual

Tu agente implementó un **sistema de gobernanza excelente** (`DOCUMENTATION_GOVERNANCE.md` + pre-commit hooks) que previene sprawl de documentación. Sin embargo:

- **Gap identificado**: No existe una categoría clara para **documentos generados por agentes IA** (session summaries, execution reports, feedback logs)
- **Problema**: Archivos como `EXECUTION_REPORT.md`, `ONBOARDING_REVIEW_REPORT.md`, `SESSION_COMPLETION_REPORT.md` están en la raíz, violando tu propia gobernanza

### Best Practices 2025

Investigación de organizaciones líderes:

| Proyecto | Enfoque para Docs de Agentes | Ubicación |
|----------|------------------------------|-----------|
| **GitHub Copilot** | Path-specific instructions | `.github/instructions/` |
| **OpenAI Swarm** | Logs transitorios | `/logs/` |
| **AutoGPT** | AGENTS.md (estándar) | Raíz + `/docs/` |
| **Microsoft Playbook** | Separación permanente/transitorio | `/docs/` vs wikis |
| **LangChain** | AGENTS.md + CLAUDE.md | Raíz |

---

## 🎯 Propuesta: Directorio `/reports/` para Docs Generados por Agentes

### Estructura Propuesta

```text
/reports/                            # 🆕 Nuevos documentos de agentes
├── README.md                        # Índice y guías de uso
├── sessions/                        # Resúmenes de sesiones de trabajo
│   ├── 2025-01-<session-id>.md
│   ├── session-onboarding-2025-01.md
│   └── session-governance-2025-01.md
├── execution/                       # Reportes de ejecución de workflows
│   ├── workflow-execution-<id>.md
│   ├── phase-<phase>-completion.md
│   └── deployment-report-<date>.md
├── feedback/                        # Feedback de agentes para humanos
│   ├── code-review-<pr-id>.md
│   ├── improvement-suggestions.md
│   └── research-findings-<topic>.md
└── research/                        # Investigación temporal (30 días)
    ├── async-patterns-research.md
    ├── governance-benchmarks.md
    └── .archive/                    # Auto-archivado > 30 días

/specs/                              # ✅ Mantener estructura actual
├── features/                        # Especificaciones de características
├── design/                          # Diseños técnicos (permanentes)
├── tasks/                           # Roadmaps y tareas
└── governance/                      # Reglas y procesos
```

### 🔑 Rationale: ¿Por qué `/reports/`?

1. **Separación Clara**: Features (código futuro) vs Reports (trabajo pasado)
2. **Ciclo de Vida**: Reports son **transitorios** (archivables), specs son **permanentes**
3. **Audiencia**: Reports para **humanos** (feedback/review), specs para **desarrollo**
4. **Precedentes**: Inspirado en `/logs/` (Swarm) + `/docs/` (AutoGPT)

---

## 🛠️ Cambios Necesarios

### 1. Actualizar `DOCUMENTATION_GOVERNANCE.md`

Agregar nueva sección:

```markdown
### 5. **`/reports/`** - Agent-Generated Documentation 🆕

**Purpose**: Store session summaries, execution reports, feedback, and research notes
**Ownership**: AI agents & automation
**Lifecycle**: Transitory (auto-archive after 30-90 days)

**Subdirectories**:
- `reports/sessions/` - Session summaries with context and decisions
- `reports/execution/` - Workflow/task execution reports
- `reports/feedback/` - Agent feedback for human review (suggestions, findings)
- `reports/research/` - Temporary research notes (auto-archive after 30 days)

**Naming Patterns**:
- Sessions: `session-<topic>-<YYYY-MM>.md`
- Execution: `workflow-<name>-<id>.md` or `phase-<name>-completion.md`
- Feedback: `<type>-feedback-<id>.md` (e.g., `code-review-feedback-pr123.md`)
- Research: `<topic>-research-<YYYY-MM>.md`

**Rules**:
- ✅ All agent-generated summaries, reports, and feedback go here
- ✅ Include metadata: date, agent, purpose, related PRs/issues
- ✅ Auto-archive to `.archive/` after 30-90 days (configurable)
- ❌ No permanent design decisions (those go to `/specs/design/`)
- ❌ No feature specifications (those go to `/specs/features/`)

**Example**:
```markdown
# Session Summary: Governance Implementation

**Date**: 2025-01-11
**Agent**: Sonnet 4.5
**Duration**: 2 hours
**Related**: [Issue #42](link), [PR #43](link)

## Objectives Completed
- [x] Created DOCUMENTATION_GOVERNANCE.md
- [x] Implemented pre-commit hooks
- [x] Updated copilot-instructions.md

## Key Decisions
1. Use `.markdownlintrc` for consistency
2. Reject root .md files via pre-commit
3. Separate agent docs to /reports/

## Next Steps
- [ ] Test governance hook with violations
- [ ] Update CONTRIBUTING.md
- [ ] Team announcement
```
```

### 2. Actualizar `.github/copilot-instructions.md` (Section 6)

Agregar directriz específica:

```markdown
## 📊 Documentation Governance (Section 6)

### For AI Agents: Where to Place Your Documents

**When generating session summaries, reports, or feedback:**

✅ **DO**:
- Place session summaries in `reports/sessions/session-<topic>-<YYYY-MM>.md`
- Place execution reports in `reports/execution/workflow-<name>-<id>.md`
- Place feedback/suggestions in `reports/feedback/<type>-feedback-<id>.md`
- Place temporary research in `reports/research/<topic>-research-<YYYY-MM>.md`
- Include metadata: date, agent name, related issues/PRs
- Link to relevant permanent documentation (specs/features/, specs/design/)

❌ **DON'T**:
- Create .md files in the project root (except README.md, CHANGELOG.md, etc.)
- Mix permanent specs with transitory reports
- Create duplicate summaries (search `reports/sessions/` first)
- Leave orphaned reports (always link from relevant issue/PR)

**Example Metadata Block**:
```markdown
# Execution Report: Onboarding Phase Completion

> **Generated By**: Sonnet 4.5
> **Date**: 2025-01-11
> **Workflow**: Onboarding Implementation
> **Related**: [Issue #15](link), [PR #20](link), [Design Doc](specs/design/onboarding-system-redesign.md)

## Summary
...
```
```

### 3. Crear Templates en `specs/templates/`

#### `specs/templates/session-summary.md`
```markdown
# Session Summary: [Topic]

> **Generated By**: [Agent Name]
> **Date**: YYYY-MM-DD
> **Duration**: [Time]
> **Related**: [Links to Issues/PRs]

---

## 🎯 Session Objectives
- [ ] Objective 1
- [ ] Objective 2

## 📋 Work Completed
### Deliverables
- File 1: `path/to/file.ext` ([link](link))
- File 2: `path/to/file.ext` ([link](link))

### Key Decisions Made
1. Decision 1 - Rationale
2. Decision 2 - Rationale

## 🔍 Technical Details
[Any implementation notes, blockers encountered, workarounds applied]

## ✅ Acceptance Criteria Met
- [x] Criterion 1
- [x] Criterion 2

## 🚀 Next Steps
- [ ] Follow-up task 1
- [ ] Follow-up task 2

## 📎 References
- [Related Spec](specs/features/feature-name.md)
- [Design Doc](specs/design/design-name.md)
```

#### `specs/templates/execution-report.md`
```markdown
# Execution Report: [Workflow/Task Name]

> **Generated By**: [Agent/System]
> **Date**: YYYY-MM-DD
> **Workflow ID**: [ID]
> **Status**: ✅ Success | ⚠️ Partial | ❌ Failed

---

## 📊 Execution Summary
- **Start Time**: YYYY-MM-DD HH:MM:SS
- **End Time**: YYYY-MM-DD HH:MM:SS
- **Duration**: X minutes
- **Exit Code**: 0 | 1

## 🔄 Steps Executed
| Step | Status | Duration | Notes |
|------|--------|----------|-------|
| Step 1 | ✅ | 2s | - |
| Step 2 | ✅ | 5s | - |
| Step 3 | ⚠️ | 10s | Retry applied |

## 📁 Files Modified
- `path/to/file1.ext` (+15 lines)
- `path/to/file2.ext` (-3 lines)

## 🧪 Tests Executed
- Unit tests: 42/42 passed
- Integration tests: 8/8 passed
- Coverage: 87%

## ⚠️ Warnings/Issues
[Any non-fatal issues or warnings]

## 📎 Logs
[Link to full execution logs if available]
```

#### `specs/templates/feedback-report.md`
```markdown
# Feedback Report: [Topic]

> **Generated By**: [Agent Name]
> **Date**: YYYY-MM-DD
> **Context**: [What triggered this feedback]
> **Severity**: 🔴 Critical | 🟡 High | 🟢 Medium | ⚪ Low

---

## 🎯 Executive Summary
[One-sentence summary of key finding/suggestion]

## 🔍 Analysis
[Detailed explanation of what was found/analyzed]

## 💡 Recommendations
1. **Recommendation 1**
   - Rationale: ...
   - Implementation: ...
   - Impact: ...

2. **Recommendation 2**
   - Rationale: ...
   - Implementation: ...
   - Impact: ...

## 📊 Evidence
[Data, metrics, examples supporting the feedback]

## ✅ Action Items
- [ ] Action 1 (Owner: X, Due: YYYY-MM-DD)
- [ ] Action 2 (Owner: Y, Due: YYYY-MM-DD)

## 📎 References
- [Related Issue](link)
- [Design Doc](link)
```

### 4. Migrar Archivos Existentes

Mover archivos raíz violatorios a `/reports/`:

```bash
# Archivos a migrar
EXECUTION_REPORT.md         → reports/execution/onboarding-execution-2025-01.md
ONBOARDING_REVIEW_REPORT.md → reports/sessions/session-onboarding-review-2025-01.md
SESSION_COMPLETION_REPORT.md → reports/sessions/session-governance-completion-2025-01.md
VALIDATION_REPORT.md        → reports/execution/validation-report-2025-01.md
INFORME_REVISION_PROFESIONAL.md → reports/feedback/professional-review-feedback-2025-01.md

# Mantener en raíz (excepciones válidas)
README.md
CHANGELOG.md
CONTRIBUTING.md
```

### 5. Actualizar Pre-Commit Hook

```python
# scripts/enforce-doc-governance.py

ALLOWED_ROOT_MD = [
    'README.md',
    'CHANGELOG.md',
    'CONTRIBUTING.md',
    'CODE_OF_CONDUCT.md',
    'LICENSE'
]

ALLOWED_DIRECTORIES = [
    'specs/features/',
    'specs/design/',
    'specs/tasks/',
    'specs/governance/',
    'specs/templates/',  # 🆕
    'docs/',
    'reports/',           # 🆕
    '.github/'
]

# Agregar validación de estructura de reports/
def validate_reports_structure(filepath):
    if not filepath.startswith('reports/'):
        return True

    valid_subdirs = ['sessions', 'execution', 'feedback', 'research']
    parts = filepath.split('/')

    if len(parts) < 3:  # Debe ser reports/<subdir>/<file>
        return False, f"Reports must be in subdirectories: {valid_subdirs}"

    if parts[1] not in valid_subdirs:
        return False, f"Invalid reports subdirectory. Use one of: {valid_subdirs}"

    return True, None
```

---

## 🎯 Acceptance Criteria

### Criterios de Éxito

1. ✅ Directorio `/reports/` creado con README.md explicativo
2. ✅ `DOCUMENTATION_GOVERNANCE.md` actualizado con sección 5
3. ✅ `copilot-instructions.md` actualizado con directrices DO/DON'T
4. ✅ Templates creados en `specs/templates/`
5. ✅ Pre-commit hook valida estructura de `/reports/`
6. ✅ Archivos raíz migrados a `/reports/`
7. ✅ Git history preservado para archivos migrados

### Tests

```bash
# Test 1: Crear archivo en ubicación correcta (debe pasar)
touch reports/sessions/session-test-2025-01.md
git add .
git commit -m "test: valid report placement"

# Test 2: Crear archivo en raíz (debe fallar)
touch RANDOM_REPORT.md
git add .
git commit -m "test: invalid root placement"
# Expected: Pre-commit hook rejects

# Test 3: Crear archivo sin subdirectorio (debe fallar)
touch reports/orphan-report.md
git add .
git commit -m "test: missing subdirectory"
# Expected: Pre-commit hook rejects
```

---

## 📊 Comparación con Alternativas

| Enfoque | Pros | Contras | Decisión |
|---------|------|---------|----------|
| **`/reports/` (Propuesta)** | ✅ Clara separación permanente/transitorio / ✅ Escalable (subdirectorios) / ✅ Precedentes (Swarm `/logs/`) | ⚠️ Nueva estructura a adoptar | **✅ Recomendado** |
| **`/docs/sessions/`** | ✅ Ya existe `/docs/` / ✅ Menos cambios | ❌ Mezcla guías permanentes con reportes transitorios / ❌ No refleja ciclo de vida | ❌ |
| **`.github/reports/`** | ✅ Cerca de Copilot instructions | ❌ `.github/` es para CI/CD config / ❌ Rompe convención | ❌ |
| **`/memory/reports/`** | ✅ `/memory/` ya existe | ❌ `memory/constitution.md` es diferente (principios, no reportes) | ❌ |

---

## 🚀 Plan de Implementación (3 Fases)

### Fase 1: Estructura Base (30 min)
```bash
# 1. Crear estructura
mkdir -p reports/{sessions,execution,feedback,research}
touch reports/README.md

# 2. Crear templates
touch specs/templates/{session-summary.md,execution-report.md,feedback-report.md}

# 3. Commit structure
git add reports/ specs/templates/
git commit -m "feat: add /reports/ structure for agent-generated docs"
```

### Fase 2: Gobernanza (45 min)
```bash
# 4. Actualizar governance
# Editar specs/governance/DOCUMENTATION_GOVERNANCE.md
# Agregar sección 5: /reports/

# 5. Actualizar Copilot instructions
# Editar .github/copilot-instructions.md
# Agregar DO/DON'T para reports

# 6. Actualizar pre-commit hook
# Editar scripts/enforce-doc-governance.py
# Agregar validación para reports/

# 7. Test hooks
pre-commit run --all-files

# 8. Commit governance
git add specs/governance/ .github/ scripts/
git commit -m "docs: update governance for agent-generated reports"
```

### Fase 3: Migración (15 min)
```bash
# 9. Migrar archivos existentes
git mv EXECUTION_REPORT.md reports/execution/onboarding-execution-2025-01.md
git mv ONBOARDING_REVIEW_REPORT.md reports/sessions/session-onboarding-review-2025-01.md
git mv SESSION_COMPLETION_REPORT.md reports/sessions/session-governance-completion-2025-01.md
git mv VALIDATION_REPORT.md reports/execution/validation-report-2025-01.md
git mv INFORME_REVISION_PROFESIONAL.md reports/feedback/professional-review-feedback-2025-01.md

# 10. Actualizar enlaces rotos
# (Si hay referencias en otros docs)

# 11. Commit migration
git add .
git commit -m "refactor: migrate root reports to /reports/ structure"
```

**Total Time**: ~1.5 horas

---

## 📎 Referencias

### Investigación Realizada:
- [GitHub Copilot Custom Instructions Docs](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) - Path-specific instructions pattern
- [OpenAI Swarm Repository](https://github.com/openai/swarm) - `/logs/` directory for agent execution logs
- [AutoGPT Project Structure](https://github.com/Significant-Gravitas/AutoGPT) - AGENTS.md + modular docs
- [Microsoft Engineering Playbook](https://microsoft.github.io/code-with-engineering-playbook/documentation/) - Documentation best practices

### Documentos Internos:
- `specs/governance/DOCUMENTATION_GOVERNANCE.md` - Framework actual
- `.github/copilot-instructions.md` - Instrucciones para agentes IA
- `.pre-commit-config.yaml` - Hooks de validación

---

## ❓ Preguntas para el Usuario

Antes de implementar, necesito tu aprobación en:

1. **Nombre del directorio**: ¿Prefieres `/reports/`, `/agent-docs/`, o `/outputs/`?
2. **Ciclo de archivado**: ¿30, 60 o 90 días para auto-archivar research?
3. **Migración**: ¿Quieres preservar git history (usando `git mv`) o crear archivos nuevos?
4. **Prioridad**: ¿Implementar las 3 fases ahora o solo la estructura base?

**Responde con tu preferencia y procedo con la implementación.**

---

## 📝 Metadata

**Generado por**: KERNEL (GPT-5 Low → High)
**Fecha**: 2025-11-01
**Tiempo de análisis**: 45 minutos
**Investigación**: 5 fuentes externas + 3 documentos internos
**Estado**: ✅ Propuesta lista para revisión humana
