# CDE Orchestrator MCP - Improvement Roadmap

**Versión:** 2.0
**Fecha:** 31 de octubre de 2025
**Estado:** En Planificación

---

## 📋 Resumen de Tareas

Este documento organiza todas las tareas de mejora identificadas en el análisis profesional del proyecto. Las tareas están priorizadas y organizadas por fases de implementación.

**Documentos Relacionados:**
- Resumen ejecutivo: [`EXECUTIVE_SUMMARY.md`](../../EXECUTIVE_SUMMARY.md)
- Análisis completo: [`TASK.md`](../../TASK.md)
- Revisión técnica: [`INFORME_REVISION_PROFESIONAL.md`](../../INFORME_REVISION_PROFESIONAL.md)

---

## 🔴 FASE 1: Corrección de Errores Críticos (Semanas 1-2)

### CORE-01: Validación Robusta de Estado
**Prioridad:** 🔴 CRÍTICA | **Esfuerzo:** 3 días | **Asignado:** TBD

**Descripción:**
Implementar validación completa del estado de features usando Pydantic para prevenir corrupción de datos.

**Tareas:**
- [ ] CORE-01.1: Crear enums para estados válidos (FeatureStatus, PhaseStatus)
- [ ] CORE-01.2: Implementar modelos Pydantic completos con validators
- [ ] CORE-01.3: Agregar backup automático antes de guardar estado
- [ ] CORE-01.4: Implementar migración de schemas antiguos
- [ ] CORE-01.5: Agregar logging de cambios de estado

**Archivos Afectados:**
- `src/cde_orchestrator/models.py` (nuevo FeatureState model)
- `src/cde_orchestrator/state_manager.py` (validación)
- `src/server.py` (cde_listFeatures, cde_submitWork)

**Tests Requeridos:**
- `tests/unit/test_state_validation.py`
- `tests/integration/test_state_persistence.py`

**Criterios de Aceptación:**
```python
def test_state_validation():
    invalid_state = {"status": "invalid_status", "current_phase": "define"}
    with pytest.raises(ValidationError):
        FeatureState(**invalid_state)

    valid_state = {"status": "defining", "current_phase": "define", ...}
    feature = FeatureState(**valid_state)
    assert feature.status == FeatureStatus.DEFINING
```

**Dependencias:** Ninguna

---

### CORE-02: Error Handling y Retry Logic
**Prioridad:** 🔴 CRÍTICA | **Esfuerzo:** 2 días | **Asignado:** TBD

**Descripción:**
Implementar circuit breaker, retry logic y timeouts en todas las operaciones externas.

**Tareas:**
- [ ] CORE-02.1: Instalar `tenacity` para retry logic
- [ ] CORE-02.2: Implementar circuit breaker en ServiceConnectorFactory
- [ ] CORE-02.3: Agregar timeouts configurables (default 10s)
- [ ] CORE-02.4: Mejorar `tool_handler` decorator con context manager
- [ ] CORE-02.5: Implementar fallback strategies

**Archivos Afectados:**
- `src/cde_orchestrator/service_connector.py`
- `src/server.py` (tool_handler decorator)
- `requirements.txt` (add tenacity)

**Tests Requeridos:**
- `tests/unit/test_retry_logic.py`
- `tests/integration/test_service_resilience.py`

**Criterios de Aceptación:**
- API calls retried 3 times con backoff exponencial
- Timeouts aplicados a todas las operaciones de red
- Fallback a local storage cuando servicios externos fallan

**Dependencias:** Ninguna

---

### CORE-03: Sanitización de Prompts
**Prioridad:** 🟠 ALTA | **Esfuerzo:** 1 día | **Asignado:** TBD

**Descripción:**
Prevenir injection attacks mediante sanitización de variables de contexto y validación de templates.

**Tareas:**
- [ ] CORE-03.1: Instalar `markupsafe` para escape
- [ ] CORE-03.2: Crear whitelist de placeholders permitidos
- [ ] CORE-03.3: Implementar validación de templates POML
- [ ] CORE-03.4: Agregar detección de unreplaced placeholders
- [ ] CORE-03.5: Unit tests para injection attacks

**Archivos Afectados:**
- `src/cde_orchestrator/prompt_manager.py`
- `requirements.txt` (add markupsafe)

**Tests Requeridos:**
- `tests/unit/test_prompt_sanitization.py`
- `tests/security/test_injection_prevention.py`

**Criterios de Aceptación:**
- Todas las variables sanitizadas antes de inyección
- Templates validados contra whitelist de placeholders
- Zero vulnerabilidades en security scan

**Dependencias:** Ninguna

---

## 🟠 FASE 2: Testing Infrastructure (Semanas 3-4)

### TEST-01: Setup de Testing Framework
**Prioridad:** 🟠 ALTA | **Esfuerzo:** 2 días | **Asignado:** TBD

**Descripción:**
Configurar infraestructura completa de testing con pytest, coverage y CI/CD.

**Tareas:**
- [ ] TEST-01.1: Configurar pytest con coverage
- [ ] TEST-01.2: Crear fixtures reutilizables (workflows, states, prompts)
- [ ] TEST-01.3: Implementar mocks para servicios externos (GitHub, Git)
- [ ] TEST-01.4: Setup CI/CD con GitHub Actions para auto-testing
- [ ] TEST-01.5: Configurar pre-commit hooks

**Archivos Nuevos:**
- `tests/conftest.py`
- `tests/fixtures/`
- `.github/workflows/ci.yml`
- `pytest.ini`
- `.pre-commit-config.yaml`

**Criterios de Aceptación:**
- Tests ejecutables con `pytest`
- Coverage report generado automáticamente
- CI/CD pipeline ejecutando tests en cada PR
- Pre-commit hooks validando código antes de commit

**Dependencias:** Ninguna

---

### TEST-02: Unit Tests (80% Coverage Target)
**Prioridad:** 🟠 ALTA | **Esfuerzo:** 5 días | **Asignado:** TBD

**Descripción:**
Implementar tests unitarios completos para todos los managers y models.

**Tareas:**
- [ ] TEST-02.1: Tests para WorkflowManager (100% coverage)
- [ ] TEST-02.2: Tests para StateManager (100% coverage)
- [ ] TEST-02.3: Tests para PromptManager (100% coverage)
- [ ] TEST-02.4: Tests para RecipeManager (100% coverage)
- [ ] TEST-02.5: Tests para Models con edge cases
- [ ] TEST-02.6: Tests para RepoIngestor
- [ ] TEST-02.7: Tests para OnboardingAnalyzer

**Archivos Nuevos:**
- `tests/unit/test_workflow_manager.py`
- `tests/unit/test_state_manager.py`
- `tests/unit/test_prompt_manager.py`
- `tests/unit/test_recipe_manager.py`
- `tests/unit/test_models.py`
- `tests/unit/test_repo_ingest.py`
- `tests/unit/test_onboarding_analyzer.py`

**Criterios de Aceptación:**
- Coverage > 80% en src/cde_orchestrator/
- Todos los edge cases cubiertos
- Tests ejecutables en <30 segundos

**Dependencias:** TEST-01

---

### TEST-03: Integration Tests
**Prioridad:** 🟡 MEDIA | **Esfuerzo:** 3 días | **Asignado:** TBD

**Descripción:**
Tests de integración para workflows completos y operaciones multi-componente.

**Tareas:**
- [ ] TEST-03.1: Test completo de startFeature -> submitWork flow
- [ ] TEST-03.2: Test de Git operations con repo temporal
- [ ] TEST-03.3: Test de recipe loading y context injection
- [ ] TEST-03.4: Test de onboarding flow end-to-end

**Archivos Nuevos:**
- `tests/integration/test_feature_lifecycle.py`
- `tests/integration/test_git_operations.py`
- `tests/integration/test_recipe_system.py`
- `tests/integration/test_onboarding_flow.py`

**Criterios de Aceptación:**
- Feature lifecycle completo testeado
- Operaciones Git funcionando en repos temporales
- Onboarding completado exitosamente en tests

**Dependencias:** TEST-01, TEST-02

---

## 🟡 FASE 3: Optimización de Performance (Semana 5)

### PERF-01: Async/Await Migration
**Prioridad:** 🟡 MEDIA | **Esfuerzo:** 3 días | **Asignado:** TBD

**Descripción:**
Migrar operaciones I/O bound a async/await para mejorar performance.

**Tareas:**
- [ ] PERF-01.1: Convertir RepoIngestor a async
- [ ] PERF-01.2: Implementar concurrent file reading con asyncio
- [ ] PERF-01.3: Async Git operations
- [ ] PERF-01.4: Async HTTP calls en ServiceConnectors
- [ ] PERF-01.5: Benchmarks antes/después

**Archivos Afectados:**
- `src/cde_orchestrator/repo_ingest.py`
- `src/cde_orchestrator/service_connector.py`
- `src/cde_orchestrator/onboarding_analyzer.py`

**Criterios de Aceptación:**
- 60% reducción en tiempo de repo ingestion
- Operaciones concurrentes sin race conditions
- Backwards compatibility mantenida

**Dependencias:** TEST-02 (para detectar regresiones)

---

### PERF-02: Caching Strategy
**Prioridad:** 🟡 MEDIA | **Esfuerzo:** 2 días | **Asignado:** TBD

**Descripción:**
Implementar caching de operaciones costosas para mejorar performance.

**Tareas:**
- [ ] PERF-02.1: Implementar diskcache para repo digests
- [ ] PERF-02.2: Cache de workflow parsing con TTL
- [ ] PERF-02.3: LRU cache para token encoding
- [ ] PERF-02.4: Cache invalidation strategies

**Archivos Afectados:**
- `src/cde_orchestrator/repo_ingest.py`
- `src/cde_orchestrator/workflow_manager.py`
- `requirements.txt` (add diskcache)

**Criterios de Aceptación:**
- 80% reducción en tiempo de operaciones repetidas
- Cache invalidation correcta en cambios
- Cache size limitado y manejado

**Dependencias:** Ninguna

---

### PERF-03: Token Estimation Accuracy
**Prioridad:** 🟡 MEDIA | **Esfuerzo:** 1 día | **Asignado:** TBD

**Descripción:**
Reemplazar heurística simple con tiktoken para estimación precisa de tokens.

**Tareas:**
- [ ] PERF-03.1: Integrar tiktoken para GPT-4 encoding
- [ ] PERF-03.2: Implementar chunking inteligente por tokens
- [ ] PERF-03.3: Agregar estimación de costo por API call
- [ ] PERF-03.4: Benchmarks de precisión vs heurística actual

**Archivos Afectados:**
- `src/cde_orchestrator/repo_ingest.py`
- `requirements.txt` (add tiktoken)

**Criterios de Aceptación:**
- Precisión de estimación > 95%
- Chunking respeta límites de tokens correctamente
- Performance no degradada significativamente

**Dependencias:** Ninguna

---

## 🟡 FASE 4: Consolidación de Documentación (Semana 6)

### DOC-01: Restructuración Spec-Kit
**Prioridad:** 🟡 MEDIA | **Esfuerzo:** 2 días | **Asignado:** TBD

**Descripción:**
Reorganizar documentación siguiendo estructura Spec-Kit para mejor navegación.

**Tareas:**
- [ ] DOC-01.1: Crear estructura docs/ según plan
- [ ] DOC-01.2: Migrar archivos existentes a nueva ubicación
- [ ] DOC-01.3: Crear index y navigation en cada sección
- [ ] DOC-01.4: Agregar mkdocs.yml para documentación web
- [ ] DOC-01.5: Setup CI para auto-deploy de docs

**Nueva Estructura:**
```
docs/
├── architecture/
├── guides/
├── reference/
├── tutorials/
└── operations/
```

**Criterios de Aceptación:**
- Documentación navegable con índice claro
- Links funcionando entre documentos
- Docs deployables con mkdocs
- Zero archivos markdown huérfanos en raíz

**Dependencias:** Ninguna

---

### DOC-02: ADRs (Architecture Decision Records)
**Prioridad:** 🟢 BAJA | **Esfuerzo:** 2 días | **Asignado:** TBD

**Descripción:**
Documentar decisiones arquitectónicas importantes con ADRs.

**Tareas:**
- [ ] DOC-02.1: Template ADR con formato estándar
- [ ] DOC-02.2: ADR-001: Elección de FastMCP como framework
- [ ] DOC-02.3: ADR-002: POML como formato de templates
- [ ] DOC-02.4: ADR-003: JSON para state vs SQLite
- [ ] DOC-02.5: ADR-004: ServiceConnectorFactory pattern

**Archivos Nuevos:**
- `docs/architecture/decisions/template.md`
- `docs/architecture/decisions/001-fastmcp.md`
- `docs/architecture/decisions/002-poml-templates.md`
- `docs/architecture/decisions/003-state-storage.md`
- `docs/architecture/decisions/004-service-connectors.md`

**Criterios de Aceptación:**
- 5 ADRs documentados
- Formato consistente
- Linked desde architecture overview

**Dependencias:** DOC-01

---

### DOC-03: API Reference Auto-generada
**Prioridad:** 🟢 BAJA | **Esfuerzo:** 1 día | **Asignado:** TBD

**Descripción:**
Generar documentación API automáticamente desde docstrings.

**Tareas:**
- [ ] DOC-03.1: Setup sphinx-autodoc
- [ ] DOC-03.2: Mejorar docstrings con ejemplos
- [ ] DOC-03.3: Generar docs de tools MCP
- [ ] DOC-03.4: Docs de modelos Pydantic

**Archivos Nuevos:**
- `docs/conf.py` (Sphinx config)
- `docs/reference/api/` (auto-generated)

**Criterios de Aceptación:**
- API reference completa y navegable
- Ejemplos de código en docstrings
- Auto-regenerable en CI/CD

**Dependencias:** DOC-01

---

## 🟢 FASE 5: Features Avanzados [OPCIONAL] (Semanas 7-8)

### FEAT-01: Streaming de Outputs
**Prioridad:** 🟢 BAJA | **Esfuerzo:** 3 días | **Asignado:** TBD

**Descripción:**
Implementar streaming para feedback en tiempo real de operaciones largas.

**Tareas:**
- [ ] FEAT-01.1: Implementar SSE transport para FastMCP
- [ ] FEAT-01.2: Streaming de repo ingest progress
- [ ] FEAT-01.3: Streaming de tool execution logs
- [ ] FEAT-01.4: Progress bars en CLI

**Criterios de Aceptación:**
- Progress updates cada 5%
- No blocking en UI durante operaciones
- Compatible con clientes existentes

**Dependencias:** PERF-01

---

### FEAT-02: Webhook Support
**Prioridad:** 🟢 BAJA | **Esfuerzo:** 2 días | **Asignado:** TBD

**Descripción:**
Soporte para webhooks de GitHub para automatización.

**Tareas:**
- [ ] FEAT-02.1: Endpoint webhook para GitHub events
- [ ] FEAT-02.2: Auto-trigger workflows en PR creation
- [ ] FEAT-02.3: Status reporting back a GitHub

**Criterios de Aceptación:**
- Webhooks procesados correctamente
- Workflows triggered automáticamente
- Status visible en GitHub UI

**Dependencias:** CORE-02, TEST-03

---

### FEAT-03: Multi-Tenant Support
**Prioridad:** 🟢 BAJA | **Esfuerzo:** 4 días | **Asignado:** TBD

**Descripción:**
Soporte para múltiples usuarios/proyectos en una instancia.

**Tareas:**
- [ ] FEAT-03.1: User/Project isolation
- [ ] FEAT-03.2: Per-project state management
- [ ] FEAT-03.3: Resource quotas y rate limiting
- [ ] FEAT-03.4: Authentication/Authorization layer

**Criterios de Aceptación:**
- Usuarios completamente aislados
- Quotas aplicadas correctamente
- Auth funcionando con tokens

**Dependencias:** CORE-01, TEST-02

---

## ⚡ Quick Wins - Implementación Inmediata

### QUICK-01: Fix Feature List Tool
**Prioridad:** 🔴 CRÍTICA | **Esfuerzo:** 2 horas | **Status:** ⏳ Pendiente

**Descripción:** Validar estado antes de devolver en cde_listFeatures

**Archivo:** `src/server.py` línea 260

**Asignado:** TBD

---

### QUICK-02: Add Timeout to Service Calls
**Prioridad:** 🔴 CRÍTICA | **Esfuerzo:** 1 hora | **Status:** ⏳ Pendiente

**Descripción:** Agregar timeout=10 a todas las requests

**Archivo:** `src/cde_orchestrator/service_connector.py`

**Asignado:** TBD

---

### QUICK-03: Add Input Validation Decorator
**Prioridad:** 🟠 ALTA | **Esfuerzo:** 2 horas | **Status:** ⏳ Pendiente

**Descripción:** Decorator para validar inputs con Pydantic

**Archivos:** `src/cde_orchestrator/validation.py` (nuevo), `src/server.py`

**Asignado:** TBD

---

## 📊 Tracking y Métricas

### Progress Overview

| Fase | Tareas | Completadas | En Progreso | Pendientes | % Completado |
|------|--------|-------------|-------------|------------|--------------|
| Quick Wins | 3 | 0 | 0 | 3 | 0% |
| Fase 1 | 15 | 0 | 0 | 15 | 0% |
| Fase 2 | 12 | 0 | 0 | 12 | 0% |
| Fase 3 | 13 | 0 | 0 | 13 | 0% |
| Fase 4 | 11 | 0 | 0 | 11 | 0% |
| Fase 5 | 9 | 0 | 0 | 9 | 0% |
| **Total** | **63** | **0** | **0** | **63** | **0%** |

### Métricas de Calidad

| Métrica | Baseline | Target | Actual | Status |
|---------|----------|--------|--------|--------|
| Test Coverage | 0% | 80% | 0% | 🔴 |
| Tool Error Rate | ~15% | <2% | ~15% | 🔴 |
| Avg Response Time | 2-5s | <1s | 2-5s | 🟡 |
| Documentation | 40% | 95% | 40% | 🟡 |
| Security Score | N/A | A+ | N/A | ⚪ |

---

## 🔄 Proceso de Actualización

Este documento debe actualizarse:
- **Semanalmente:** Durante stand-ups de equipo
- **Al completar tarea:** Marcar como ✅ y actualizar %
- **Al bloquear tarea:** Documentar blocker y asignado
- **Al cambiar prioridad:** Justificar cambio en comentario

**Responsable:** Tech Lead
**Última actualización:** 31 de octubre de 2025

---

*Este roadmap es un documento vivo y debe evolucionar con el proyecto.*
