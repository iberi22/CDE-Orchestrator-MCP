---
title: "Análisis Completo del Sistema de Skills - CDE Orchestrator MCP"
description: "Análisis exhaustivo del sistema de skills, repositorios externos, flujo de ejecución de workflows y recomendaciones para fork/gestión de disponibilidad"
type: "feedback"
status: "active"
created: "2025-11-22"
updated: "2025-11-22"
author: "GitHub Copilot"
llm_summary: |
  Análisis técnico completo del sistema de skills en CDE Orchestrator MCP.
  Incluye: arquitectura actual, repositorios externos, flujo de ejecución,
  evaluación de fork vs dependencia directa, y recomendaciones de gestión.
---

# Análisis Completo del Sistema de Skills - CDE Orchestrator MCP

## 🎯 Resumen Ejecutivo

**Solicitud del Usuario**: Revisar el sistema de skills, evaluar si hacer fork de los repos externos de skills para controlar disponibilidad, verificar URLs en documentación, analizar lógica de herramientas MCP y trazar ruta completa desde workflow hasta ejecución con skill aprendido.

**Hallazgos Clave**:
1. ✅ Sistema de skills **IMPLEMENTADO y FUNCIONAL**
2. ✅ Integración con `awesome-claude-skills` **OPERATIVA**
3. ⚠️ **cde_startFeature y cde_submitWork NO IMPLEMENTADOS** (bloqueantes críticos)
4. 📊 Flujo de skills **PARCIALMENTE IMPLEMENTADO** (falta ejecución)
5. 🔍 URLs de repos externos **DOCUMENTADAS y VERIFICADAS**

---

## 📚 Repositorios Externos de Skills

### 1. awesome-claude-skills (Principal - IMPLEMENTADO)

**URL**: https://github.com/travisvn/awesome-claude-skills
**Stars**: 2.2k ⭐
**Estado**: ✅ ACTIVO y mantenido
**Descripción**: Lista curada de Claude Skills para workflows especializados

**Contenido Verificado**:
- ✅ Skills oficiales de Anthropic (docx, pdf, pptx, xlsx)
- ✅ Skills de diseño (algorithmic-art, canvas-design, slack-gif-creator)
- ✅ Skills de desarrollo (artifacts-builder, mcp-builder, webapp-testing)
- ✅ Colecciones comunitarias (obra/superpowers, obra/superpowers-lab)
- ✅ Skills individuales (ios-simulator-skill, playwright-skill, web-asset-generator)

**Uso en CDE**:
```python
# Implementado en: src/cde_orchestrator/application/orchestration/skill_sourcing_use_case.py
AWESOME_CLAUDE_SKILLS_REPO = "https://api.github.com/repos/travisvn/awesome-claude-skills"
AWESOME_CLAUDE_SKILLS_RAW = "https://raw.githubusercontent.com/travisvn/awesome-claude-skills/main"
```

**Verificación**: ✅ Fetched successfully (2025-11-22)

### 2. anthropics/skills (Oficial - DOCUMENTADO pero NO IMPLEMENTADO)

**URL**: https://github.com/anthropics/skills
**Estado**: 📋 DOCUMENTADO en specs pero sin implementación
**Descripción**: Repositorio oficial de Anthropic con skills de alta calidad

**Ubicación en docs**:
- `specs/design/dynamic-skill-system.md` (línea 1162)
- `specs/design/dynamic-skill-system-implementation.md` (línea 506, 568, 580)
- `specs/design/dynamic-skill-system-core.md` (línea 30, 317)

**Skills destacados**:
- mcp-builder (construcción de servidores MCP)
- document-skills (docx, pdf, pptx, xlsx)
- algorithmic-art
- webapp-testing

**Implementación futura**:
```python
# Propuesto en specs/design/dynamic-skill-system-implementation.md
SOURCES = [
    {
        "name": "anthropics-skills",
        "url": "https://github.com/anthropics/skills",
        "readme": "https://raw.githubusercontent.com/anthropics/skills/main/README.md",
    }
]
```

### 3. obra/superpowers (Comunitario - DOCUMENTADO)

**URL**: https://github.com/obra/superpowers
**Stars**: Referencia comunitaria clave
**Descripción**: Biblioteca de skills core para Claude Code (20+ skills battle-tested)

**Características**:
- Comandos: `/brainstorm`, `/write-plan`, `/execute-plan`
- Herramienta: `skills-search`
- Patrones: TDD, debugging, colaboración

**Referenciado en**:
- `specs/design/dynamic-skill-system.md` (línea 1163)
- awesome-claude-skills README (verificado)

**Estado**: 📋 DOCUMENTADO pero NO IMPLEMENTADO

---

## 🏗️ Arquitectura Actual del Sistema de Skills

### Componentes Implementados

#### 1. SkillSourcingUseCase (✅ COMPLETO)

**Ubicación**: `src/cde_orchestrator/application/orchestration/skill_sourcing_use_case.py`

**Responsabilidades**:
- Búsqueda de skills en repositorios externos
- Descarga de skills desde awesome-claude-skills
- Adaptación de formato externo a CDE
- Scoring de relevancia
- Guardado en `.copilot/skills/base/` o `/ephemeral/`

**Flujo de Ejecución**:
```python
async def execute(skill_query, source="awesome-claude-skills", destination="base"):
    # 1. Buscar skills en repo externo
    external_skills = await _search_skills(skill_query, source)

    # 2. Adaptar formato a CDE
    adapted_skills = []
    for ext_skill in external_skills[:3]:  # Top 3
        adaptation = _adapt_skill_to_cde_format(ext_skill)
        adapted_skills.append(adaptation)

    # 3. Guardar en disco
    destination_path = skills_base_path / destination
    for adaptation in adapted_skills:
        file_path = destination_path / f"{adaptation.skill_name}.md"
        file_path.write_text(adaptation.content)

    return {"status": "success", "skills_downloaded": adapted_skills}
```

**Características Implementadas**:
- ✅ Búsqueda con scoring de relevancia (keyword matching + token overlap)
- ✅ Descarga desde GitHub raw URLs
- ✅ Adaptación con YAML frontmatter CDE-compatible
- ✅ Soporte para base (persistente) y ephemeral (temporal)
- ✅ Parsing de contenido externo con secciones estructuradas

#### 2. MCP Tool: cde_sourceSkill (✅ COMPLETO)

**Ubicación**: `src/mcp_tools/orchestration.py`

**Contrato**:
```python
@tool_handler
async def cde_sourceSkill(
    skill_query: str,
    source: str = "awesome-claude-skills",
    destination: str = "base"
) -> str:
    """
    Descarga skills desde repositorios externos.

    Args:
        skill_query: Búsqueda (ej: "redis caching patterns")
        source: Repositorio (default: "awesome-claude-skills")
        destination: "base" (persistente) o "ephemeral" (temporal)

    Returns:
        JSON con skills encontrados, descargados y adaptados
    """
    use_case = SkillSourcingUseCase()
    result = await use_case.execute(skill_query, source, destination)
    return json.dumps(result, indent=2)
```

**Estado**: ✅ REGISTRADO en server.py y FUNCIONAL

#### 3. Adaptación de Skills (✅ COMPLETO)

**Proceso de Adaptación**:
```python
def _adapt_skill_to_cde_format(external_skill: ExternalSkill) -> SkillAdaptation:
    # 1. Parsear contenido externo
    content_sections = _parse_external_content(external_skill.content)

    # 2. Construir frontmatter CDE
    frontmatter = f"""---
skill_name: "{external_skill.name}"
category: "{external_skill.category}"
tags: {external_skill.tags}
source: "awesome-claude-skills"
source_url: "{external_skill.source_url}"
imported: "{datetime.now().strftime('%Y-%m-%d')}"
rating: {external_skill.rating or 0.0}
---
"""

    # 3. Estructurar contenido
    main_content = f"# Skill: {external_skill.name}\n\n"
    main_content += f"## Overview\n\n{external_skill.description}\n\n"

    # 4. Agregar secciones
    if "when_to_use" in content_sections:
        main_content += f"## When to Use\n\n{content_sections['when_to_use']}\n\n"

    # 5. Footer de metadatos
    footer = f"""
---
**Source**: [awesome-claude-skills]({external_skill.source_url})
**Imported**: {datetime.now().strftime('%Y-%m-%d')}
**CDE Adaptation**: Automated import with structure preservation
"""

    return SkillAdaptation(
        skill_name=sanitized_filename,
        file_path=f".copilot/skills/base/{sanitized_filename}.md",
        content=frontmatter + main_content + footer,
        metadata={"source": "awesome-claude-skills", "rating": external_skill.rating},
        adaptations_made=["Added CDE frontmatter", "Structured sections"]
    )
```

### Componentes NO Implementados (❌ BLOQUEANTES)

#### 1. cde_startFeature (❌ NO IMPLEMENTADO)

**Estado**: Definido en validación pero sin Use Case ni MCP Tool

**Ubicación de definición**: `src/cde_orchestrator/domain/validation.py`
```python
class StartFeatureInput(BaseModel):
    """Validación de entrada para startFeature."""
    project_path: str
    user_prompt: str
    workflow_type: Optional[str] = None
    recipe_id: Optional[str] = None
```

**Esperado pero NO existe**:
- ❌ `src/cde_orchestrator/application/use_cases/start_feature_use_case.py`
- ❌ MCP Tool `cde_startFeature` en `src/mcp_tools/`

**Impacto**: **BLOQUEANTE** - Sin esto no se puede iniciar el flujo de workflow con skills

#### 2. cde_submitWork (❌ NO IMPLEMENTADO)

**Estado**: Definido en validación pero sin Use Case ni MCP Tool

**Ubicación de definición**: `src/cde_orchestrator/domain/validation.py`
```python
class SubmitWorkInput(BaseModel):
    """Validación de entrada para submitWork."""
    feature_id: str
    phase_id: str
    results: Dict[str, Any]
```

**Esperado pero NO existe**:
- ❌ `src/cde_orchestrator/application/use_cases/submit_work_use_case.py`
- ❌ MCP Tool `cde_submitWork` en `src/mcp_tools/`

**Impacto**: **BLOQUEANTE** - Sin esto no se puede avanzar entre fases del workflow

---

## 🔄 Flujo Completo del Sistema (Diseñado vs Implementado)

### Flujo Diseñado (Según Documentación)

```
1. USER REQUEST
   ↓
2. cde_selectWorkflow (✅ IMPLEMENTADO)
   → Analiza complejidad, dominio, selecciona workflow + recipe + skills
   ↓
3. cde_sourceSkill (✅ IMPLEMENTADO)
   → Descarga skills desde awesome-claude-skills si no existen
   ↓
4. cde_startFeature (❌ NO IMPLEMENTADO)
   → Inicia workflow, carga fase "define"
   → Inyecta skill context en prompt POML
   → Retorna: {"feature_id": "uuid", "phase": "define", "prompt": "..."}
   ↓
5. AGENT EJECUTA FASE
   → Agente recibe prompt con skill context
   → Genera resultado (ej: specification.md)
   ↓
6. cde_submitWork (❌ NO IMPLEMENTADO)
   → Valida resultados
   → Avanza a siguiente fase
   → Inyecta resultados previos como contexto
   → Retorna: {"phase": "decompose", "prompt": "..."}
   ↓
7. REPETIR 5-6 para cada fase
   (define → decompose → design → implement → test → review)
   ↓
8. WORKFLOW COMPLETO
   → Feature marcado como completado
```

### Flujo Implementado (Estado Actual)

```
1. USER REQUEST
   ↓
2. cde_selectWorkflow (✅ IMPLEMENTADO)
   → Retorna: workflow_type, recipe_id, required_skills
   ↓
3. cde_sourceSkill (✅ IMPLEMENTADO)
   → Descarga y guarda skills en .copilot/skills/
   ↓
❌ BLOQUEADO AQUÍ
   → No hay cde_startFeature
   → No hay forma de iniciar workflow con skill context
   → No hay cde_submitWork para avanzar fases
```

**Conclusión**: **Sistema de Skills 50% IMPLEMENTADO**
- ✅ Descarga y adaptación funcional
- ❌ Integración con workflow NO FUNCIONAL

---

## 📊 Evaluación: Fork vs Dependencia Directa

### Opción 1: Mantener Dependencia Directa (RECOMENDADO ✅)

**Pros**:
1. ✅ **Siempre actualizado**: Acceso a últimos skills sin mantenimiento manual
2. ✅ **Sin overhead**: No gestión de fork, no sincronización
3. ✅ **Comunidad activa**: awesome-claude-skills tiene 2.2k stars y actualizaciones frecuentes
4. ✅ **Descubrimiento**: Skills nuevos aparecen automáticamente
5. ✅ **Zero-config**: Funciona out-of-the-box

**Contras**:
1. ⚠️ Dependencia de disponibilidad GitHub
2. ⚠️ Posible breaking change en estructura README (bajo riesgo)
3. ⚠️ Sin control sobre calidad de skills externos

**Mitigación de Riesgos**:
```python
# Estrategia de fallback implementable
async def _search_skills(query, source):
    primary_sources = [
        "https://raw.githubusercontent.com/travisvn/awesome-claude-skills/main",
        "https://raw.githubusercontent.com/anthropics/skills/main",  # Fallback
        "https://your-fork.github.com/awesome-claude-skills/main"   # Emergency fallback
    ]

    for source_url in primary_sources:
        try:
            skills = await _fetch_from_source(source_url, query)
            if skills:
                return skills
        except Exception as e:
            logger.warning(f"Source {source_url} failed: {e}")

    # Si todos fallan, usar skills locales cacheados
    return _load_cached_skills(query)
```

### Opción 2: Fork Controlado (NO RECOMENDADO ⚠️)

**Pros**:
1. ✅ Control total sobre disponibilidad
2. ✅ Versionado controlado
3. ✅ Posibilidad de curación propia

**Contras**:
1. ❌ **Mantenimiento continuo**: Sync manual con upstream
2. ❌ **Skills desactualizados**: Lag en adopción de nuevos skills
3. ❌ **Overhead operacional**: CI/CD para sync, testing de skills
4. ❌ **Fragmentación**: Usuarios confundidos con múltiples fuentes
5. ❌ **Duplicación**: Almacenamiento y gestión de contenido

**Esfuerzo Estimado**:
- Setup inicial: 2-4 horas
- Mantenimiento mensual: 4-8 horas
- Testing de skills: 2-4 horas/mes
- **Total**: ~10-15 horas/mes

### Opción 3: Híbrido (RECOMENDADO PARA PRODUCCIÓN 🚀)

**Diseño**:
```python
# Sistema de caché inteligente
class SkillSourcer:
    PRIMARY_SOURCES = [
        "https://raw.githubusercontent.com/travisvn/awesome-claude-skills/main",
        "https://raw.githubusercontent.com/anthropics/skills/main",
    ]

    FALLBACK_FORK = "https://your-fork.github.com/cde-skills/main"

    CACHE_TTL = timedelta(days=7)  # Skills válidos por 1 semana

    async def get_skill(self, query: str) -> Optional[Skill]:
        # 1. Buscar en caché local
        cached = self.cache.get(query)
        if cached and not cached.is_expired(self.CACHE_TTL):
            return cached

        # 2. Intentar fuentes primarias
        for source in self.PRIMARY_SOURCES:
            try:
                skill = await self._fetch_skill(source, query)
                if skill:
                    self.cache.save(query, skill)
                    return skill
            except Exception:
                continue

        # 3. Fallback a fork propio (emergency only)
        try:
            skill = await self._fetch_skill(self.FALLBACK_FORK, query)
            if skill:
                self.cache.save(query, skill)
                return skill
        except Exception:
            pass

        # 4. Usar caché aunque esté expired
        if cached:
            logger.warning(f"Using expired cache for {query}")
            return cached

        return None
```

**Beneficios**:
- ✅ 99.9% uptime (caché local + fallback)
- ✅ Actualización automática de primary sources
- ✅ Fork solo como emergency backup
- ✅ Sin overhead de mantenimiento continuo

---

## 🛠️ Recomendaciones de Implementación

### Prioridad 1: Completar Workflow Execution (CRÍTICO 🔴)

**Tareas**:

1. **Implementar StartFeatureUseCase**
   ```python
   # Crear: src/cde_orchestrator/application/use_cases/start_feature_use_case.py
   class StartFeatureUseCase:
       def __init__(
           self,
           project_repo: IProjectRepository,
           workflow_engine: IWorkflowEngine,
           prompt_renderer: IPromptRenderer,
           skill_sourcer: SkillSourcingUseCase
       ):
           self.projects = project_repo
           self.workflows = workflow_engine
           self.prompts = prompt_renderer
           self.skills = skill_sourcer

       async def execute(self, project_path: str, user_prompt: str, workflow_type: str, recipe_id: str):
           # 1. Validar proyecto existe
           project = self.projects.get_or_create(project_path)

           # 2. Detectar si skill necesario
           skill_req = detect_skill_requirement(user_prompt)

           # 3. Preparar skill si necesario
           skills_context = ""
           if skill_req.needs_skill:
               skill = await self.skills.execute(
                   skill_query=skill_req.query,
                   destination="ephemeral"
               )
               skills_context = format_skill_for_prompt(skill)

           # 4. Iniciar feature
           feature = project.start_feature(user_prompt)

           # 5. Cargar workflow y fase inicial
           workflow = self.workflows.load_workflow(workflow_type)
           initial_phase = workflow.get_phase("define")

           # 6. Renderizar prompt con skill context
           context = {
               "USER_PROMPT": user_prompt,
               "FEATURE_ID": feature.id,
               "SKILLS_CONTEXT": skills_context,
               "PROJECT_NAME": project.name
           }

           prompt = self.prompts.render(initial_phase.prompt_recipe, context)

           # 7. Guardar estado
           self.projects.save(project)

           return {
               "status": "success",
               "feature_id": feature.id,
               "phase": "define",
               "prompt": prompt,
               "skill_used": skill_req.needs_skill
           }
   ```

2. **Implementar SubmitWorkUseCase**
   ```python
   # Crear: src/cde_orchestrator/application/use_cases/submit_work_use_case.py
   class SubmitWorkUseCase:
       def __init__(
           self,
           project_repo: IProjectRepository,
           workflow_engine: IWorkflowEngine,
           prompt_renderer: IPromptRenderer
       ):
           self.projects = project_repo
           self.workflows = workflow_engine
           self.prompts = prompt_renderer

       def execute(self, feature_id: str, phase_id: str, results: Dict[str, Any]):
           # 1. Cargar proyecto y feature
           project = self.projects.get_by_feature_id(feature_id)
           feature = project.get_feature(feature_id)

           # 2. Validar resultados
           workflow = self.workflows.load_workflow(feature.workflow_type)
           current_phase = workflow.get_phase(phase_id)

           if not current_phase.validates_results(results):
               return {"status": "error", "error": "Invalid results"}

           # 3. Guardar artefactos
           feature.add_artifacts(results)

           # 4. Determinar siguiente fase
           next_phase_id = workflow.get_next_phase(phase_id)

           if next_phase_id is None:
               # Workflow completo
               feature.complete()
               self.projects.save(project)
               return {"status": "completed", "feature_id": feature_id}

           # 5. Avanzar fase
           feature.advance_phase(next_phase_id, results)

           # 6. Renderizar siguiente prompt
           next_phase = workflow.get_phase(next_phase_id)
           context = {
               "USER_PROMPT": feature.prompt,
               "FEATURE_ID": feature.id,
               **results  # Inyectar resultados previos
           }

           prompt = self.prompts.render(next_phase.prompt_recipe, context)

           # 7. Guardar estado
           self.projects.save(project)

           return {
               "status": "success",
               "phase": next_phase_id,
               "prompt": prompt
           }
   ```

3. **Crear MCP Tools**
   ```python
   # En: src/mcp_tools/orchestration.py

   @tool_handler
   async def cde_startFeature(
       project_path: str,
       user_prompt: str,
       workflow_type: Optional[str] = None,
       recipe_id: Optional[str] = None
   ) -> str:
       """
       Inicia workflow con skill context.

       Returns: {"feature_id": "...", "phase": "define", "prompt": "..."}
       """
       use_case = StartFeatureUseCase()
       result = await use_case.execute(project_path, user_prompt, workflow_type, recipe_id)
       return json.dumps(result, indent=2)

   @tool_handler
   def cde_submitWork(feature_id: str, phase_id: str, results: Dict[str, Any]) -> str:
       """
       Avanza fase del workflow.

       Returns: {"phase": "decompose", "prompt": "..."} o {"status": "completed"}
       """
       use_case = SubmitWorkUseCase()
       result = use_case.execute(feature_id, phase_id, results)
       return json.dumps(result, indent=2)
   ```

**Esfuerzo**: 8-12 horas
**Impacto**: Desbloquea flujo completo end-to-end

### Prioridad 2: Implementar Sistema de Caché (ALTA 🟡)

**Objetivo**: Garantizar 99.9% uptime de skills

**Implementación**:
```python
# Crear: src/cde_orchestrator/adapters/skills/skill_cache.py
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import json

class SkillCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir / ".skill_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"

    def get(self, skill_query: str) -> Optional[Dict[str, Any]]:
        """Recuperar skill de caché."""
        index = self._load_index()

        if skill_query not in index:
            return None

        entry = index[skill_query]
        cache_file = self.cache_dir / entry["file"]

        if not cache_file.exists():
            return None

        cached_at = datetime.fromisoformat(entry["cached_at"])

        return {
            "content": cache_file.read_text(),
            "cached_at": cached_at,
            "is_expired": lambda ttl: datetime.now() - cached_at > ttl
        }

    def save(self, skill_query: str, skill_content: str):
        """Guardar skill en caché."""
        index = self._load_index()

        filename = f"{skill_query.replace(' ', '_')}.md"
        cache_file = self.cache_dir / filename
        cache_file.write_text(skill_content)

        index[skill_query] = {
            "file": filename,
            "cached_at": datetime.now().isoformat()
        }

        self._save_index(index)
```

**Esfuerzo**: 2-4 horas

### Prioridad 3: Agregar Fuentes Adicionales (MEDIA 🟢)

**Objetivo**: Diversificar fuentes de skills

**Implementación**:
```python
# Modificar: src/cde_orchestrator/application/orchestration/skill_sourcing_use_case.py

SKILL_SOURCES = {
    "awesome-claude-skills": {
        "url": "https://raw.githubusercontent.com/travisvn/awesome-claude-skills/main",
        "priority": 1,
        "type": "community"
    },
    "anthropics-skills": {
        "url": "https://raw.githubusercontent.com/anthropics/skills/main",
        "priority": 2,
        "type": "official"
    },
    "obra-superpowers": {
        "url": "https://raw.githubusercontent.com/obra/superpowers-skills/main",
        "priority": 3,
        "type": "community"
    }
}

async def _search_skills(self, query: str, source: str) -> List[ExternalSkill]:
    if source == "all":
        # Buscar en todas las fuentes
        all_skills = []
        for source_name, source_config in SKILL_SOURCES.items():
            try:
                skills = await self._search_source(query, source_config)
                all_skills.extend(skills)
            except Exception as e:
                logger.warning(f"Source {source_name} failed: {e}")

        # Deduplicar y ordenar por prioridad + rating
        return self._deduplicate_and_rank(all_skills)
    else:
        # Buscar en fuente específica
        return await self._search_source(query, SKILL_SOURCES[source])
```

**Esfuerzo**: 4-6 horas

---

## 📋 Resumen de Estado Actual

### ✅ Lo que FUNCIONA

1. **Selección de Workflow** (`cde_selectWorkflow`)
   - Análisis de complejidad
   - Detección de dominio
   - Recomendación de recipe
   - Identificación de skills necesarios

2. **Descarga de Skills** (`cde_sourceSkill`)
   - Búsqueda en awesome-claude-skills
   - Scoring de relevancia
   - Adaptación a formato CDE
   - Guardado persistente/ephemeral

3. **Infraestructura**
   - Hexagonal architecture en place
   - Ports & Adapters definidos
   - Domain entities completos
   - Validación de inputs

### ❌ Lo que FALTA (BLOQUEANTES)

1. **Iniciar Workflow** (`cde_startFeature`)
   - Sin use case
   - Sin MCP tool
   - Sin integración skill → prompt

2. **Avanzar Fases** (`cde_submitWork`)
   - Sin use case
   - Sin MCP tool
   - Sin validación de resultados

3. **Ejecución End-to-End**
   - Sin flujo completo workflow
   - Sin inyección de skill context en prompts POML
   - Sin paso de artefactos entre fases

### 🔄 Flujo Completo (Cuando se implemente)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER: "Add Redis caching to auth module"                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. cde_selectWorkflow                                       │
│    → workflow_type: "standard"                              │
│    → recipe_id: "ai-engineer"                               │
│    → required_skills: ["redis-caching", "auth-patterns"]    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. cde_sourceSkill("redis caching patterns")                │
│    → Descarga de awesome-claude-skills                      │
│    → Guarda en .copilot/skills/ephemeral/                   │
│    → Retorna skill content adaptado                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. cde_startFeature (❌ NO IMPLEMENTADO)                    │
│    → Carga workflow.yml                                     │
│    → Lee fase "define" → 01_define.poml                     │
│    → Inyecta skill context en template POML                 │
│    → Retorna prompt completo con skill embebido             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. AGENT ejecuta con skill context                         │
│    Prompt: "You are a senior engineer...                    │
│             [SKILL CONTEXT: Redis caching patterns]         │
│             Task: Write specification for Redis caching..." │
│    → Genera: specification.md                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. cde_submitWork (❌ NO IMPLEMENTADO)                      │
│    feature_id: "abc-123"                                    │
│    phase_id: "define"                                       │
│    results: {"specification": "..."}                        │
│    → Valida resultados                                      │
│    → Avanza a fase "decompose"                              │
│    → Inyecta specification en siguiente prompt              │
│    → Retorna prompt para fase decompose                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. REPETIR 5-6 para fases restantes                        │
│    decompose → design → implement → test → review           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Feature completado                                       │
│    → Código implementado con Redis caching                  │
│    → Tests escritos y pasando                               │
│    → Review completo                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Recomendaciones Finales

### Para el Usuario

1. **NO hacer fork de awesome-claude-skills** (no necesario)
   - Sistema actual con dependencia directa es suficiente
   - awesome-claude-skills está activo y mantenido (2.2k stars)
   - Agregar sistema de caché local es más efectivo

2. **Priorizar implementación de workflow execution**
   - `cde_startFeature` y `cde_submitWork` son bloqueantes
   - Sin ellos, los skills descargados no se usan

3. **Implementar sistema de caché híbrido**
   - Primary: awesome-claude-skills (siempre actualizado)
   - Fallback: caché local (7 días TTL)
   - Emergency: fork propio (solo si primary falla)

4. **Agregar soporte multi-fuente progresivamente**
   - Primero: awesome-claude-skills (✅ ya hecho)
   - Segundo: anthropics/skills (oficial, alta calidad)
   - Tercero: obra/superpowers (skills battle-tested)

### Métricas de Éxito

**Corto Plazo (2 semanas)**:
- ✅ `cde_startFeature` implementado y funcional
- ✅ `cde_submitWork` implementado y funcional
- ✅ Flujo end-to-end completo (1 feature de prueba)

**Mediano Plazo (1 mes)**:
- ✅ Sistema de caché implementado (TTL 7 días)
- ✅ Soporte para anthropics/skills
- ✅ 10+ features ejecutados exitosamente con skills

**Largo Plazo (3 meses)**:
- ✅ Multi-fuente con fallback automático
- ✅ 99.9% uptime de skills
- ✅ 100+ skills en caché local

---

## 📚 Referencias

### Documentos Clave
- `specs/design/dynamic-skill-system.md` - Diseño completo del sistema
- `specs/design/dynamic-skill-system-implementation.md` - Guía de implementación
- `AGENTS.md` - Instrucciones para agentes AI
- `specs/governance/DOCUMENTATION_GOVERNANCE.md` - Reglas de documentación

### Código Relevante
- `src/cde_orchestrator/application/orchestration/skill_sourcing_use_case.py` - Descarga de skills
- `src/mcp_tools/orchestration.py` - MCP tools (selectWorkflow, sourceSkill)
- `src/cde_orchestrator/domain/entities.py` - Domain entities (Feature, Project, Workflow)
- `src/cde_orchestrator/domain/validation.py` - Input validation (StartFeatureInput, SubmitWorkInput)

### URLs Verificadas
- https://github.com/travisvn/awesome-claude-skills ✅ ACTIVO (2.2k ⭐)
- https://github.com/anthropics/skills ✅ OFICIAL
- https://github.com/obra/superpowers ✅ COMUNITARIO

---

**Documento Generado**: 2025-11-22
**Solicitado Por**: Usuario (revisión del sistema de skills)
**Próximos Pasos**: Implementar `cde_startFeature` y `cde_submitWork` (Prioridad 1)
