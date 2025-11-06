---
title: "Meta-Orchestration: Usando Agentes CLI para Completar 100% del Proyecto"
description: "Guía para ejecutar la orquestación meta que delega a Claude Code, Aider y Codex para completar el CDE Orchestrator"
type: "guide"
status: "active"
created: "2025-11-05"
updated: "2025-11-05"
author: "GitHub Copilot"
tags:
  - "orchestration"
  - "agents"
  - "automation"
  - "cli"
  - "bedrock"
llm_summary: |
  Usa la nueva herramienta cde_executeFullImplementation para orquestar agentes CLI
  (Claude Code, Aider, Codex) delegando tareas automáticamente. Meta: que el proyecto
  se complete a sí mismo usando su propia infraestructura. Ejecuta 4 fases en 6 semanas.
---

# Meta-Orchestration: Completar el 100% del Proyecto con Agentes CLI

## 🎯 Concepto: Usando el Proyecto para Completar el Proyecto

El CDE Orchestrator ahora tiene una **herramienta meta-orquestradora** que:

1. **Analiza tareas pendientes** (Fases 1-4 del roadmap)
2. **Selecciona el mejor agente CLI** (Claude Code, Aider, Codex)
3. **Delega automáticamente** usando skills y workflows
4. **Mantiene contexto** entre agentes
5. **Valida y publica** resultados

**La premisa**: El proyecto se completa a sí mismo usando su propia infraestructura.

---

## 🛠️ Arquitectura

```
┌─────────────────────────────────────┐
│  MCP Server (CDE Orchestrator)      │
├─────────────────────────────────────┤
│                                     │
│  cde_executeFullImplementation()    │ ← Nueva herramienta meta
│  ↓                                  │
│  ┌─────────────────────────────┐   │
│  │ FullImplementationOrchestrator   │
│  ├─────────────────────────────┤   │
│  │ - Phase 1-4 definitions     │   │
│  │ - Task management           │   │
│  │ - Skills integration        │   │
│  └────────────┬────────────────┘   │
│               ↓                     │
│  ┌─────────────────────────────┐   │
│  │ MultiAgentOrchestrator      │   │
│  ├─────────────────────────────┤   │
│  │ - Agent detection           │   │
│  │ - Task selection            │   │
│  │ - Execution delegation      │   │
│  │ - Context management        │   │
│  └────────┬────────┬───────┬───┘   │
└───────────┼────────┼───────┼────────┘
            ↓        ↓       ↓
        ┌──────┐┌──────┐┌──────┐
        │Claude││Aider ││Codex │
        │Code  ││CLI   ││CLI   │
        │(BR)  ││      ││      │
        └──────┘└──────┘└──────┘
         Bedrock  SSH    GitHub
```

---

## 📦 Componentes Nuevos

### 1. `MultiAgentOrchestrator`

**Archivo**: `src/cde_orchestrator/infrastructure/multi_agent_orchestrator.py`

**Responsabilidades**:
- Detectar agentes disponibles en sistema
- Seleccionar mejor agente para cada tarea
- Ejecutar con CLI apropiada
- Mantener estado/contexto
- Registrar logs de ejecución

**Agentes Soportados**:
```python
class AgentType(Enum):
    CLAUDE_CODE = "claude-code"      # Bedrock via CloudCode
    AIDER = "aider"                   # Aider CLI
    CODEX = "codex"                   # GitHub Copilot CLI
    JULES = "jules"                   # Jules AI agent
    CODEIUM = "codeium"               # Codeium CLI
```

### 2. `FullImplementationOrchestrator`

**Archivo**: `src/mcp_tools/full_implementation.py`

**Responsabilidades**:
- Definir fases y tareas (Phase 1-4)
- Orquestar flujo de ejecución
- Gestionar depende cias entre fases
- Reportar progreso

### 3. `cde_executeFullImplementation` MCP Tool

**Nueva herramienta MCP** que activa toda la orquestación.

**Parámetros**:
- `start_phase` (default: "phase1"): Desde qué fase comenzar
- `phases` (optional): Fases específicas a ejecutar

**Retorno**: JSON con resultados de todas las tareas

---

## 🚀 Uso: Completar el 100% en 3 Comandos

### Opción 1: Usar MCP Tool Directamente (Recomendado)

```bash
# Opción 1A: Desde cliente MCP (cursor, aider, etc)
# Dentro de tu agente AI, ejecuta:
cde_executeFullImplementation(start_phase="phase1")

# Esto inicia todo automáticamente
```

### Opción 2: Script Python Directo

```bash
# Ejecutar todas las fases
python -m cde_orchestrator.infrastructure.multi_agent_orchestrator

# O ejecutar desde Python
python << 'EOF'
import asyncio
from src.mcp_tools.full_implementation import cde_executeFullImplementation

result = asyncio.run(cde_executeFullImplementation(start_phase="phase1"))
print(result)
EOF
```

### Opción 3: CLI Wrapper (Próximamente)

```bash
# Una vez implementado:
python -m cde_tools orchestrate --start-phase phase1 --agents claude-code,aider
```

---

## 📋 Las 4 Fases Explicadas

### ⏱️ Fase 1: Verificación y Compilación Rust (2 horas)

**Objetivo**: Compilar Rust, ejecutar tests, verificar performance

**Tareas**:

```python
TaskDefinition(
    task_id="phase1-rust-install",
    title="Instalar Rust Toolchain",
    description="Instala rustup, cargo, rustc",
    complexity="simple",
    required_skills=["rust-installation"]
)

TaskDefinition(
    task_id="phase1-rust-compile",
    title="Compilar cde_rust_core con maturin",
    description="cd rust_core && maturin develop --release",
    complexity="simple",
    required_skills=["rust-compilation", "pyo3"]
)

TaskDefinition(
    task_id="phase1-run-tests",
    title="Ejecutar suite completa de tests",
    description="pytest tests/ -v (objetivo: 0 skipped)",
    complexity="simple"
)

TaskDefinition(
    task_id="phase1-coverage",
    title="Generar coverage report >85%",
    description="pytest --cov con HTML report",
    complexity="simple"
)

TaskDefinition(
    task_id="phase1-benchmark",
    title="Benchmark de performance",
    description="Validar 6x speedup Rust vs Python",
    complexity="moderate"
)
```

**Agente Seleccionado**: Claude Code (análisis de compilación) o Aider (ejecución)

---

### 📝 Fase 2: Optimización de Documentación (4 horas)

**Objetivo**: 100% compliance governance + LLM optimization

**Tareas**:

```python
TaskDefinition(
    task_id="phase2-metadata-update",
    title="Actualizar metadata YAML faltante",
    complexity="simple",
    estimated_hours=0.5
)

TaskDefinition(
    task_id="phase2-llm-summary",
    title="Agregar llm_summary a documentos clave",
    complexity="simple",
    estimated_hours=1.0
)

TaskDefinition(
    task_id="phase2-governance-validation",
    title="Validar 100% compliance governance",
    complexity="simple",
    estimated_hours=0.5
)

TaskDefinition(
    task_id="phase2-token-optimization",
    title="Optimizar token usage (30-40% reducción)",
    complexity="moderate",
    estimated_hours=2.0
)
```

**Agente Seleccionado**: Aider o Codex (edición de archivos .md)

---

### 🔧 Fase 3: Implementar `cde_setupProject` (4 horas)

**Objetivo**: Completar herramienta MCP faltante (11/11)

**Tareas**:

```python
TaskDefinition(
    task_id="phase3-setup-use-case",
    title="Implementar ProjectSetupUseCase",
    description="Generar AGENTS.md, GEMINI.md, .gitignore dinámicamente",
    complexity="moderate",
    estimated_hours=2.0
)

TaskDefinition(
    task_id="phase3-setup-tests",
    title="Escribir tests para cde_setupProject",
    complexity="moderate",
    estimated_hours=1.5
)

TaskDefinition(
    task_id="phase3-mcp-integration",
    title="Registrar en MCP server y documentar",
    complexity="simple",
    estimated_hours=0.5
)
```

**Agente Seleccionado**: Claude Code (arquitectura) + Aider (tests)

---

### 🚀 Fase 4: Expansión Rust - Code Analysis (7.5 horas)

**Objetivo**: Segunda funcionalidad Rust acelerada

**Tareas**:

```python
TaskDefinition(
    task_id="phase4-code-analysis-rust",
    title="Implementar code_analysis.rs",
    description="Detectar lenguajes, LOC, complejidad, funciones, clases",
    complexity="complex",
    estimated_hours=4.0
)

TaskDefinition(
    task_id="phase4-code-analysis-python",
    title="Integrar code_analysis en Python",
    complexity="moderate",
    estimated_hours=2.0
)

TaskDefinition(
    task_id="phase4-code-analysis-tests",
    title="Tests y benchmarks (8x+ speedup)",
    complexity="moderate",
    estimated_hours=1.5
)
```

**Agente Seleccionado**: Claude Code (Rust complexo) + Aider (Python integration)

---

## 🔀 Lógica de Selección de Agente

El orquestrador automáticamente elige el mejor agente:

```python
def _select_best_agent(self, task: TaskDefinition) -> AgentType:
    """
    Heurística de selección:

    Tareas COMPLEJAS de arquitectura
        → Claude Code (mejor análisis)

    Tareas de EDICIÓN múltiple
        → Aider (filesystem seguro)

    Tareas de TESTS y snippets
        → Codex (rápido)

    Tareas MULTI-FASE complejas
        → Jules (full context)
    """
```

**Matriz de Selección**:

| Tarea | Complexity | Phase | Agent Preferido |
|-------|-----------|-------|-----------------|
| Instalar Rust | simple | verify | Aider/Codex |
| Compilar Rust | simple | verify | Claude Code |
| Run Tests | simple | test | Aider |
| Coverage | simple | verify | Aider |
| Setup Use Case | moderate | implement | Claude Code |
| Write Tests | moderate | test | Aider |
| Code Analysis Rust | complex | implement | Claude Code |
| Integration Python | moderate | implement | Aider |

---

## 📊 Monitoreo de Progreso

### Ver Estado en Tiempo Real

```bash
# Via MCP cliente
result = cde_executeFullImplementation(start_phase="phase1")

# JSON con estado actual
{
  "status": "success",
  "completion": {
    "total_tasks": 18,
    "completed_tasks": 5,
    "completion_percentage": 27.8,
    "phases_status": {
      "phase1": {
        "total": 5,
        "completed": 5,
        "estimated_hours": 2.0
      },
      "phase2": {
        "total": 4,
        "completed": 2,
        "estimated_hours": 4.0
      }
    }
  },
  "execution_log": [
    {
      "task_id": "phase1-rust-install",
      "agent": "aider",
      "status": "success",
      "duration": 1200.5,
      "files_modified": [...]
    }
  ]
}
```

---

## ⚙️ Configuración Pre-Requisitos

### 1. Claude Code (Bedrock)

```bash
# Instalar CloudCode CLI
pip install claude-code

# Configurar AWS Bedrock
aws configure --profile bedrock
export AWS_PROFILE=bedrock

# Verificar
claude-code --version
```

### 2. Aider CLI

```bash
# Instalar Aider
pip install aider-chat

# Verificar
aider --version
```

### 3. GitHub Copilot CLI

```bash
# Instalar GitHub CLI
winget install GitHub.cli  # Windows
brew install gh            # macOS
apt install gh              # Linux

# Autenticarse
gh auth login

# Verificar
gh copilot suggest "hello world"
```

### 4. Jules (Ya disponible)

Jules ya está integrado vía `cde_delegateToJules`, no requiere setup adicional.

---

## 🔄 Flujo Completo: De Inicio a Fin

```
1. Usuario ejecuta:
   └─ cde_executeFullImplementation(start_phase="phase1")

2. Sistema analiza:
   ├─ Detecta agentes disponibles (Claude Code, Aider, Codex)
   ├─ Carga definiciones de tareas (Phase 1-4)
   └─ Resuelve orden de ejecución

3. Fase 1 comienza:
   ├─ Task 1: "Instalar Rust"
   │  ├─ Selecciona: Aider (simple execution)
   │  ├─ Ejecuta: aider --message "instala rust..."
   │  └─ Valida: rustc --version (✅ OK)
   │
   ├─ Task 2: "Compilar Rust Core"
   │  ├─ Selecciona: Claude Code (análisis de compilación)
   │  ├─ Ejecuta: claude-code run --provider bedrock ...
   │  └─ Valida: import cde_rust_core (✅ OK)
   │
   ├─ Task 3: "Run Tests"
   │  ├─ Selecciona: Aider (ejecución)
   │  ├─ Ejecuta: aider --message "ejecuta pytest..."
   │  └─ Valida: 23+ tests pasando, 0 skipped (✅ OK)
   │
   ├─ Task 4: "Coverage Report"
   │  ├─ Selecciona: Aider
   │  ├─ Ejecuta: aider --message "genera coverage >85%..."
   │  └─ Valida: coverage.xml + htmlcov/ (✅ OK)
   │
   └─ Task 5: "Benchmark Performance"
      ├─ Selecciona: Claude Code (análisis numérico)
      ├─ Ejecuta: claude-code run ...
      └─ Valida: Rust >= 6x más rápido (✅ OK)

4. Fase 1 completa:
   └─ Report: 5/5 tareas, 2.0 horas reales

5. Fase 2 comienza (depende de Fase 1):
   ├─ Task 1: "Metadata YAML"
   │  └─ Aider edita documentation...
   ├─ Task 2: "LLM Summaries"
   │  └─ Claude Code genera contextos...
   └─ ...

6. Todas las fases completan:
   └─ Final Report:
      ├─ 18/18 tareas completadas
      ├─ ~19.5 horas reales
      ├─ 100% funcionalidad lograda
      └─ Archivos modificados: 50+
```

---

## 🎯 Criterios de Éxito (100% Funcionalidad)

Cuando `cde_executeFullImplementation` finaliza:

✅ **Herramientas MCP** (11/11):
- `cde_setupProject` implementada y testeada
- `cde_analyzeCode` con Rust backend
- Todas funcionan sin errores

✅ **Rust Core** (Compilado):
- `cargo build --release` exitoso
- `maturin develop --release` exitoso
- `import cde_rust_core` sin excepciones

✅ **Performance** (Verificado):
- Documentación: 6x+ speedup Rust
- Code Analysis: 8x+ speedup Rust (próx.)
- Benchmarks documentados con números reales

✅ **Tests** (>85% coverage):
- Suite completa: 0 skipped
- Coverage report generado
- Badge codecov en README

✅ **Documentación** (100% compliant):
- `validate-docs.py --all` pasa
- 0 archivos en root (excepto 5 permitidos)
- Todos los docs con YAML frontmatter + `llm_summary`

✅ **CI/CD** (Todo en verde):
- GitHub Actions workflows pasando
- Pre-commit hooks configurados
- Codecov reportando

---

## 📊 Estimated Timeline

| Fase | Tareas | Horas | Agentes |
|------|--------|-------|---------|
| **Fase 1** | 5 | 2.0 | Claude Code, Aider |
| **Fase 2** | 4 | 4.0 | Aider, Codex |
| **Fase 3** | 3 | 4.0 | Claude Code, Aider |
| **Fase 4** | 3 | 7.5 | Claude Code, Aider |
| **TOTAL** | **18** | **17.5** | - |

**Timeline Real** (incluyendo debugging):
- Optimista: 3-4 semanas
- Realista: 5-6 semanas
- Pesimista: 7-8 semanas

---

## 🚦 Comenzar Ahora

### Paso 1: Instalar Pre-requisitos

```bash
# Claude Code (Bedrock)
pip install claude-code

# Aider
pip install aider-chat

# GitHub CLI
winget install GitHub.cli

# Verificar disponibilidad
python -c "
from src.cde_orchestrator.infrastructure.multi_agent_orchestrator import MultiAgentOrchestrator
o = MultiAgentOrchestrator('.')
print(f'Agentes: {list(o.agent_capabilities.keys())}')
"
```

### Paso 2: Ejecutar Orquestación

```bash
# Opción A: Via MCP tool (recomendado)
# Desde tu cliente MCP (Cursor, Windsurf, etc):
cde_executeFullImplementation(start_phase="phase1")

# Opción B: Via Python directo
python << 'EOF'
import asyncio
from src.mcp_tools.full_implementation import cde_executeFullImplementation
result = asyncio.run(cde_executeFullImplementation())
print(result)
EOF
```

### Paso 3: Monitorear Progreso

Ver logs en tiempo real:
```bash
# En otra terminal
tail -f logs/orchestration.log
```

---

## 🔗 Referencias

- **Multi-Agent Orchestrator**: `src/cde_orchestrator/infrastructure/multi_agent_orchestrator.py`
- **Full Implementation Tool**: `src/mcp_tools/full_implementation.py`
- **MCP Server Config**: `src/server.py` (actualizado)
- **Roadmap Original**: `agent-docs/roadmap/roadmap-100-functionality-post-pr4-2025-01.md`

---

## ⚠️ Notas Importantes

1. **No commits automáticos**: Los agentes NO harán git commit ni push. Tú controlas los cambios.

2. **Fallback robusto**: Si un agente falla, el siguiente toma control. Sistema nunca se atasca.

3. **Contexto compartido**: El estado se mantiene entre agentes vía `context_stack`.

4. **Logging completo**: Todas las acciones registradas en `execution_log`.

5. **Validación en cada paso**: Cada tarea es validada antes de pasar a la siguiente.

---

**¡Ahora ejecuta y deja que el proyecto se complete a sí mismo!** 🚀
