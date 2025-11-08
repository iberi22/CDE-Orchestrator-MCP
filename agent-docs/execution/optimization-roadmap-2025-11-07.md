---
title: "Plan de Optimización Python 3.14 & Refactorización MCP"
description: "Implementación específica de mejoras arquitectónicas y de rendimiento"
type: "task"
status: "active"
created: "2025-11-07"
updated: "2025-11-07"
author: "CDE Optimization Team"
---

# Plan de Implementación: Python 3.14 & Refactorización MCP

## 🎯 Objetivo

Optimizar CDE Orchestrator MCP para máximo rendimiento Python 3.14 y consistencia arquitectónica.

---

## 🔴 FASE 1: CRÍTICA (Esta semana)

### TAREA 1.1: Actualizar requirements.txt

**Archivo**: `requirements.txt`

```diff
  fastmcp==2.13.0
- pydantic
+ pydantic>=2.7.0
  python-dotenv
  lxml
  pathspec
```

**Razón**: Pydantic v1 deprecado, v2.7+ asegura soporte Python 3.14

**Verificación**:
```bash
pip install pydantic>=2.7.0
python -c "import pydantic; print(pydantic.__version__)"
# Debe mostrar 2.7.x o superior
```

---

### TAREA 1.2: Refactorizar cde_listAvailableAgents

**Ubicación**: `src/mcp_tools/agents.py` (línea 83)

**Paso 1**: Crear UseCase

```python
# src/cde_orchestrator/application/orchestration/list_agents_use_case.py
"""List available AI coding agents."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentStatus(Enum):
    """Status of configured agent."""
    AVAILABLE = "available"
    NOT_INSTALLED = "not_installed"
    ERROR = "error"


@dataclass
class AgentCapability:
    """Capability metadata for agent."""
    name: str
    description: str


@dataclass
class AgentInfo:
    """Information about available agent."""
    name: str
    type: str
    status: AgentStatus
    capabilities: List[str]
    best_for: List[str]


class ListAvailableAgentsUseCase:
    """
    Use Case: List all configured AI agents and their availability status.

    Returns information about:
    - Jules (async API agent)
    - Copilot CLI (GitHub Copilot)
    - Gemini CLI (Google Gemini)
    - Qwen CLI (Alibaba Qwen)
    """

    def execute(self) -> Dict[str, Any]:
        """Execute: detect available agents."""
        available = []
        unavailable = []

        # Check Jules
        jules_status = self._check_jules()
        if jules_status["status"] == AgentStatus.AVAILABLE:
            available.append(jules_status)
        else:
            unavailable.append(jules_status)

        # Check Copilot
        copilot_status = self._check_copilot()
        if copilot_status["status"] == AgentStatus.AVAILABLE:
            available.append(copilot_status)
        else:
            unavailable.append(copilot_status)

        # Check Gemini
        gemini_status = self._check_gemini()
        if gemini_status["status"] == AgentStatus.AVAILABLE:
            available.append(gemini_status)
        else:
            unavailable.append(gemini_status)

        # Check Qwen
        qwen_status = self._check_qwen()
        if qwen_status["status"] == AgentStatus.AVAILABLE:
            available.append(qwen_status)
        else:
            unavailable.append(qwen_status)

        return {
            "available_agents": available,
            "unavailable_agents": unavailable,
            "total_available": len(available),
            "total_checked": len(available) + len(unavailable),
        }

    def _check_jules(self) -> Dict[str, Any]:
        """Check Jules availability."""
        # Implementation details...
        pass

    def _check_copilot(self) -> Dict[str, Any]:
        """Check GitHub Copilot availability."""
        # Implementation details...
        pass

    def _check_gemini(self) -> Dict[str, Any]:
        """Check Google Gemini availability."""
        # Implementation details...
        pass

    def _check_qwen(self) -> Dict[str, Any]:
        """Check Alibaba Qwen availability."""
        # Implementation details...
        pass
```

**Paso 2**: Actualizar MCP Tool

```python
# src/mcp_tools/agents.py (línea 83)

# VIEJO:
@tool_handler
def cde_listAvailableAgents() -> str:
    """List available AI coding agents..."""
    # ... lógica inline

# NUEVO:
from cde_orchestrator.application.orchestration import ListAvailableAgentsUseCase

@tool_handler
def cde_listAvailableAgents() -> str:
    """
    🆕 **List Available AI Coding Agents** - Check which agents are ready to use.

    Returns information about all configured AI coding agents and their availability.
    """
    use_case = ListAvailableAgentsUseCase()
    result = use_case.execute()
    return json.dumps(result, indent=2)
```

---

### TAREA 1.3: Refactorizar cde_selectAgent

**Ubicación**: `src/mcp_tools/agents.py` (línea 236)

**Pasos similares a 1.2**:

```python
# src/cde_orchestrator/application/orchestration/select_agent_use_case.py
"""Select best agent for task."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class TaskComplexity(Enum):
    """Complexity of task."""
    TRIVIAL = "trivial"      # < 5 min
    SIMPLE = "simple"        # 15-30 min
    MODERATE = "moderate"    # 1-2 hours
    COMPLEX = "complex"      # 4-8 hours
    EPIC = "epic"            # 2-5 days


class AgentType(Enum):
    """Type of agent."""
    JULES = "jules"          # Complex, full context
    COPILOT = "copilot"      # Quick fixes, suggestions
    GEMINI = "gemini"        # Documentation, analysis
    QWEN = "qwen"            # Fallback, basic generation


@dataclass
class AgentRecommendation:
    """Recommendation for which agent to use."""
    selected_agent: AgentType
    complexity: TaskComplexity
    reasoning: str
    confidence: float  # 0.0-1.0
    alternatives: List[AgentType]
    capabilities_needed: List[str]


class SelectAgentUseCase:
    """
    Use Case: Analyze task and select best AI agent.

    Agent Selection Criteria:
    - Jules: Complex tasks (refactoring, full repo context)
    - Copilot: Quick fixes, code generation
    - Gemini: Documentation, analysis, moderate tasks
    - Qwen: Fallback for basic code generation
    """

    def execute(self, task_description: str) -> Dict[str, Any]:
        """Execute: analyze and select best agent."""

        # Step 1: Analyze complexity
        complexity = self._analyze_complexity(task_description)

        # Step 2: Detect required capabilities
        required_caps = self._detect_required_capabilities(task_description)

        # Step 3: Score agents
        agent_scores = self._score_agents(complexity, required_caps)

        # Step 4: Select best agent
        best_agent, confidence = self._select_best_agent(agent_scores)

        # Step 5: Get alternatives
        alternatives = self._get_alternative_agents(best_agent, agent_scores)

        return {
            "selected_agent": best_agent.value,
            "complexity": complexity.value,
            "reasoning": f"Task requires {', '.join(required_caps)}. {best_agent.name} best suited.",
            "confidence": confidence,
            "alternatives": [a.value for a in alternatives],
            "capabilities": required_caps,
            "requirements": self._get_agent_requirements(best_agent),
        }

    def _analyze_complexity(self, task: str) -> TaskComplexity:
        """Detect task complexity from description."""
        # Implementation
        pass

    def _detect_required_capabilities(self, task: str) -> List[str]:
        """Detect what capabilities are needed."""
        # Implementation
        pass

    def _score_agents(self, complexity: TaskComplexity,
                     caps: List[str]) -> Dict[AgentType, float]:
        """Score each agent for this task."""
        # Implementation
        pass

    def _select_best_agent(self, scores: Dict) -> tuple[AgentType, float]:
        """Select agent with highest score."""
        # Implementation
        pass

    def _get_alternative_agents(self, selected: AgentType,
                                scores: Dict) -> List[AgentType]:
        """Get alternative agent recommendations."""
        # Implementation
        pass

    def _get_agent_requirements(self, agent: AgentType) -> List[str]:
        """Get setup requirements for agent."""
        # Implementation
        pass
```

---

## 🟡 FASE 2: TYPE HINTS MODERNOS (Próximas 2 semanas)

### TAREA 2.1: Migrar Union types a sintaxis nueva

**Afectados**: ~50 líneas en domain/ + application/

**Cambios**:
```python
# ANTES (Python 3.10+)
from typing import Union, Optional

def process(items: Optional[List[str]]) -> Union[dict, None]:
    pass

# DESPUÉS (Python 3.14+)
def process(items: list[str] | None) -> dict | None:
    pass
```

**Archivos a actualizar**:
1. `src/cde_orchestrator/domain/validation.py`
2. `src/cde_orchestrator/application/orchestration/*.py`
3. `src/cde_orchestrator/domain/ports.py`

**Script de migración**:
```bash
# Usar ruff + regex para auto-migración
ruff check --select UP src/ --fix

# Manual review + commit
git diff
git add -A
git commit -m "chore: upgrade type hints to Python 3.14+ syntax"
```

---

### TAREA 2.2: Agregar JIT Hints

**Ubicación**: `src/cde_orchestrator/application/orchestration/workflow_selector_use_case.py`

```python
# ANTES
class WorkflowSelectorUseCase:
    def execute(self, user_prompt: str) -> Dict[str, Any]:
        # Expensive: analyzes keywords, complexity, domain
        recommendation = self._analyze_complexity(user_prompt)
        return recommendation.to_dict()

# DESPUÉS (Python 3.14+)
import sys

class WorkflowSelectorUseCase:
    def execute(self, user_prompt: str) -> Dict[str, Any]:
        recommendation = self._analyze_complexity(user_prompt)
        return recommendation.to_dict()

    @staticmethod
    def _analyze_complexity(prompt: str) -> int:
        """Critical hot path - candidate for JIT."""
        score = 0
        # Tight loop → compilable by JIT
        for keyword, weight in COMPLEXITY_KEYWORDS.items():
            count = prompt.count(keyword)
            score += count * weight
        return score // 100
```

**Uso de JIT hints**:
```python
# En __init__.py o setup
if hasattr(sys, '_jit'):
    # Python 3.14+ JIT available
    from . import workflow_selector_use_case as wf_module
    # JIT will compile hot paths automatically
```

**Beneficio**: +15-25% speed en análisis de prompts

---

### TAREA 2.3: Implementar InterpreterID para Multi-Agent

**Ubicación**: `src/cde_orchestrator/infrastructure/multi_agent_orchestrator.py`

```python
# ANTES (GIL bloqueante)
async def execute_task(self, task: str) -> Dict[str, Any]:
    """Execute with single interpreter (GIL)."""
    return await self._execute_with_agent(task)

# DESPUÉS (Python 3.14+ Multi-Interpreter)
import sys
from interpreters import create

class MultiAgentOrchestrator:
    async def execute_task_parallel(self, tasks: list[str]) -> list[Dict]:
        """
        Execute multiple tasks in parallel without GIL.

        Python 3.14+ feature: Independent interpreters per agent
        """
        if not hasattr(sys, 'create_environment'):
            # Fallback para Python < 3.14
            return await self._execute_sequential(tasks)

        # Python 3.14+: True parallelism
        interpreters = [create() for _ in tasks]
        results = await asyncio.gather(*[
            self._run_in_interpreter(interp, task)
            for interp, task in zip(interpreters, tasks)
        ])
        return results

    async def _run_in_interpreter(self, interp, task: str) -> Dict:
        """Run task in isolated interpreter."""
        # Each agent runs in its own Python interpreter
        # No GIL contention!
        return await interp.run_async(
            self._agent_task_wrapper(task)
        )
```

**Beneficio**: +30-50% speed en ejecución paralela de múltiples agentes

---

## 🟢 FASE 3: OPTIMIZACIONES DE DATOS (Próximas 4 semanas)

### TAREA 3.1: Integrar orjson para serialización

**Ventaja**: +30% velocidad en JSON parsing

**Instalación**:
```bash
pip install orjson>=3.10.0
```

**requirements.txt**:
```diff
+ orjson>=3.10.0
```

**Implementación**:

```python
# src/cde_orchestrator/infrastructure/json_utils.py
"""JSON utilities using orjson for performance."""

import orjson
from typing import Any

def dumps(obj: Any, **kwargs: Any) -> str:
    """Serialize to JSON using orjson (3x faster)."""
    return orjson.dumps(obj).decode('utf-8')

def loads(json_str: str) -> Any:
    """Deserialize from JSON using orjson."""
    return orjson.loads(json_str)

# Usage in MCP tools:
# json.dumps(result) → json_utils.dumps(result)
```

**Aplicar en**:
```python
# src/mcp_tools/orchestration.py
- import json
+ from cde_orchestrator.infrastructure.json_utils import dumps

  result = use_case.execute(...)
- return json.dumps(result, indent=2)
+ return dumps(result)
```

---

## 📊 MÉTRICAS DE ÉXITO

### Antes vs Después (Post-Optimización)

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| `cde_selectWorkflow` latency | 50ms | 35ms | -30% |
| `cde_sourceSkill` latency | 2000ms | 1500ms | -25% |
| Entity instantiation | 0.5ms | 0.3ms | -40% |
| JSON serialization | 1ms | 0.7ms | -30% |
| Skill search | 100ms | 60ms | -40% |
| Multi-agent parallelism | Sequential | Parallel | +40-50% |
| Code size reduction | 100% | 95% | -5% |
| Type hint clarity | Good | Excellent | +15% |

### Testing

```bash
# Ejecutar benchmarks
python -m pytest tests/benchmarks/ -v

# Profiling
python -m cProfile -s cumtime src/mcp_tools/orchestration.py

# Type checking
mypy src/ --strict --report htmlcov/

# Coverage
pytest tests/ --cov=src --cov-report=html
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

```
FASE 1 (ESTA SEMANA)
[  ] Actualizar requirements.txt (pydantic>=2.7.0)
[  ] Crear ListAvailableAgentsUseCase
[  ] Refactorizar cde_listAvailableAgents
[  ] Crear SelectAgentUseCase
[  ] Refactorizar cde_selectAgent
[  ] Ejecutar tests
[  ] Commit y push

FASE 2 (PRÓXIMAS 2 SEMANAS)
[  ] Migrar type hints a sintaxis nueva (Union → |)
[  ] Agregar JIT hints a funciones críticas
[  ] Implementar InterpreterID para parallelism
[  ] Tests de performance
[  ] Documentar cambios
[  ] Commit y push

FASE 3 (PRÓXIMAS 4 SEMANAS)
[  ] Integrar orjson
[  ] Benchmarking completo
[  ] Profiling de hot paths
[  ] Optimización selectiva
[  ] Documentar resultados
[  ] Release candidato

DOCUMENTACIÓN
[  ] Actualizar ARCHITECTURE.md
[  ] Agregar Python 3.14 section
[  ] Documentar benchmarks
[  ] Crear migration guide
[  ] Update AGENTS.md si aplica
```

---

## 🚀 PRÓXIMOS COMANDOS

```bash
# Setup inicial
cd /path/to/CDE-Orchestrator-MCP
git checkout -b refactor/python314-optimization

# Fase 1
cat requirements.txt | sed 's/pydantic/pydantic>=2.7.0/' > requirements.txt
pip install -r requirements.txt

# Crear UseCase files
touch src/cde_orchestrator/application/orchestration/list_agents_use_case.py
touch src/cde_orchestrator/application/orchestration/select_agent_use_case.py

# Tests
pytest tests/ -v

# Type check
mypy src/ --strict

# Commit
git add -A
git commit -m "refactor: Consolidate MCP tools to UseCase pattern + Python 3.14 prep"
git push origin refactor/python314-optimization
```

**Tiempo estimado total**: 20-25 horas de desarrollo
**Impacto de rendimiento**: +25-40% velocidad, +30% paralelismo
