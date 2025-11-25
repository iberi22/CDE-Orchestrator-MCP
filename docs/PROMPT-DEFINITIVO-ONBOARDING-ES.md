# 🎯 EL PROMPT DEFINITIVO - CDE Onboarding Completo

> **Propósito**: Un solo prompt para integración completa de CDE desde 0% hasta 100%
> **Creado**: 2025-11-24
> **Idioma**: Español (para ti) + Inglés (para agentes)

---

## 📋 RESUMEN EJECUTIVO

He creado **EL PROMPT DEFINITIVO** que orquesta TODO el sistema CDE en un solo comando. Este prompt:

1. ✅ **Analiza** tu proyecto actual (cualquier % de implementación)
2. ✅ **Configura** toda la estructura CDE
3. ✅ **Genera** specs profesionales automáticamente
4. ✅ **Recomienda** el workflow óptimo
5. ✅ **Verifica** que todo funcione
6. ✅ **Guía** los próximos pasos

---

## 🚀 EL PROMPT (Cópialo y úsalo)

```
@workspace I want to integrate CDE Orchestrator as the complete orchestration system for this project. Please:

1. **ANALYZE** current project state using cde_onboardingProject
2. **SETUP** project structure with cde_setupProject
3. **CONFIGURE** .vscode/mcp.json for external project integration
4. **VERIFY** all 27 CDE tools are available with cde_healthCheck
5. **GENERATE** a professional spec for the next feature/improvement using cde_generateSpec
6. **RECOMMEND** optimal workflow with cde_selectWorkflow

Provide a comprehensive report with:
- Current project status (languages, frameworks, architecture)
- Missing structure (what needs to be created)
- AI assistant configurations (which tools detected)
- Git history insights (commits, contributors, age)
- Next steps for CDE-driven development

Execute all steps sequentially and show results for each phase.
```

---

## 💡 ¿POR QUÉ ESTE PROMPT ES PERFECTO?

### 1. **Funciona desde cualquier punto**

- **0% implementación**: Proyecto nuevo desde cero
- **50% implementación**: Proyecto existente a la mitad
- **100% implementación**: Proyecto completo que quieres mejorar

### 2. **Orquesta 6 herramientas en secuencia**

```
cde_onboardingProject
    ↓
cde_setupProject
    ↓
[Manual: .vscode/mcp.json]
    ↓
cde_healthCheck
    ↓
cde_generateSpec
    ↓
cde_selectWorkflow
```

### 3. **Output completo y estructurado**

Cada fase genera:
- ✅ **Análisis detallado** (570+ archivos, frameworks, Git)
- ✅ **Archivos creados** (AGENTS.md, specs/, .cde/, memory/)
- ✅ **Specs profesionales** (3 documentos: PRD, Design, Tasks)
- ✅ **Recomendaciones** (skills, workflow, duración)

---

## 📊 QUÉ HACE CADA FASE

### Fase 1: Análisis (cde_onboardingProject)

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

### Fase 2: Setup (cde_setupProject)

**Input**: Proyecto analizado
**Output**:
- `.cde/workflow.yml`
- `AGENTS.md`
- `GEMINI.md`
- `.github/copilot-instructions.md`
- `specs/templates/`
- `memory/constitution.md`

### Fase 3: Configuración (Manual)

**Tú creas**: `.vscode/mcp.json`
**Luego**: Reload VS Code (15 segundos)

### Fase 4: Verificación (cde_healthCheck)

**Output**:
```json
{
  "status": "healthy",
  "tools_registered": 27
}
```

### Fase 5: Generación de Spec (cde_generateSpec)

**Input**: Descripción del feature
**Output**:
- `specs/tu-feature/spec.md` (PRD - 450 líneas)
- `specs/tu-feature/plan.md` (Design - 380 líneas)
- `specs/tu-feature/tasks.md` (45 tareas)

### Fase 6: Recomendación (cde_selectWorkflow)

**Output**:
```json
{
  "workflow_type": "standard",
  "complexity": "moderate",
  "duration": "2-4 hours",
  "recipe": "ai-engineer",
  "skills": ["redis-caching", "auth-patterns"]
}
```

---

## 🎬 EJEMPLO REAL

### Tu Prompt:
```
@workspace I want to integrate CDE Orchestrator for this project.
Next feature: "Add Redis caching to authentication module"
```

### Respuesta del Agente:

**✅ FASE 1: Análisis Completo**
```
Proyecto: MiApp
- 245 archivos Python
- FastAPI 0.115.0
- Arquitectura: Hexagonal
- 156 commits, 3 contributors
- Copilot detectado
```

**✅ FASE 2: Estructura Creada**
```
Archivos creados:
- .cde/workflow.yml
- AGENTS.md
- GEMINI.md
- specs/ templates
- memory/constitution.md
```

**✅ FASE 3: Configuración Necesaria**
```
Acción requerida:
1. Crea .vscode/mcp.json (config proporcionada)
2. Reload VS Code
3. Espera 15 segundos
```

**✅ FASE 4: Verificación**
```
Health: ✅ Healthy
Tools: 27 registrados
Python: 3.14.0
```

**✅ FASE 5: Spec Generado**
```
Location: specs/add-redis-caching-to-authentication/
- spec.md (450 líneas)
- plan.md (380 líneas)
- tasks.md (45 tareas)

Recomendaciones:
- Skill: redis-caching-patterns
- Skill: auth-security-best-practices
```

**✅ FASE 6: Workflow Recomendado**
```
Tipo: Standard (6-phase)
Complejidad: Moderate
Duración: 2-4 horas
Recipe: ai-engineer.poml

Next Steps:
1. Revisar spec generado
2. cde_sourceSkill para skills
3. cde_startFeature para comenzar
```

---

## 🎯 CASOS DE USO

### Caso 1: Proyecto Nuevo (0%)
```
@workspace Nuevo proyecto FastAPI desde cero.
Integra CDE para orquestar todo el desarrollo.
```

### Caso 2: Proyecto Existente (50%)
```
@workspace Proyecto existente con 50% implementado.
Integra CDE para gestionar desarrollo futuro.
Feature próximo: "Add payment processing"
```

### Caso 3: Feature Específico
```
@workspace Analiza proyecto e integra CDE.
Genera spec profesional para: "Implement OAuth2 authentication"
```

---

## ✅ CHECKLIST DE ÉXITO

Después de usar el prompt, deberías tener:

- ✅ Proyecto analizado (570+ archivos, Git, frameworks)
- ✅ Estructura creada (specs/, memory/, .cde/)
- ✅ 27 herramientas CDE disponibles
- ✅ Spec profesional generado (3 documentos)
- ✅ Workflow recomendado
- ✅ Próximos pasos claros

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### "Tool not found"
**Solución**: Reload VS Code (Ctrl+Shift+P → Reload Window)

### "Health check < 27 tools"
**Solución**:
```powershell
.\scripts\diagnose-cde-tools.ps1
```

### "Spec generation fails"
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

```
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

- **Prompt Completo**: `docs/THE-ULTIMATE-ONBOARDING-PROMPT.md`
- **Resumen (Este)**: `docs/PROMPT-DEFINITIVO-ONBOARDING-ES.md`
- **Quick Fix**: `docs/QUICKFIX-RELOAD-TOOLS.md`
- **Configuration**: `docs/configuration-guide.md`
- **Diagnóstico**: `scripts/diagnose-cde-tools.ps1`

---

## 🎯 RESULTADO FINAL

**En 2 minutos obtienes**:
- ✅ Proyecto completamente analizado
- ✅ Estructura CDE implementada
- ✅ 27 herramientas disponibles
- ✅ Specs profesionales generados
- ✅ Workflow optimizado
- ✅ Roadmap claro

**Un solo prompt. Todo orquestado. 🚀**

---

**TL;DR**: Copia el prompt del inicio, pégalo en Copilot Chat, espera 2 minutos, CDE orquesta todo. ✅
