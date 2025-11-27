---
title: "Server.py Refactorización Modular (OPCIÓN C)"
description: "Refactorizar server.py (1054 LOC) a estructura modular siguiendo best practices industria 2025"
type: feature
status: active
created: "2025-11-03"
updated: "2025-11-03"
author: "CDE System"
tags:
  - refactoring
  - architecture
  - mcp
  - fastmcp
  - modularity
llm_summary: |
  Especificación técnica para refactorizar server.py de 1054 líneas a estructura modular.
  Divide MCP tools en 4 módulos temáticos (<200 LOC cada uno). Mantiene 100% funcionalidad.
  Optimizado para LLMs (5 archivos), testing, y escalabilidad. Incluye criterios de aceptación.
---

# Feature Spec: Server.py Refactorización Modular (OPCIÓN C)

## 📋 Resumen Ejecutivo

**Problema**: `src/server.py` tiene 1054 líneas (exceeds industria standard 800 LOC)
**Solución**: Dividir en módulos temáticos manteniendo 100% funcionalidad
**Tiempo Estimado**: 2 horas
**Prioridad**: HIGH (bloquea TASK-09)

---

## 🎯 Objetivos

### Cumplir Estándares Industria
- ✅ Cada archivo < 200 líneas
- ✅ Clear separation of concerns
- ✅ Fácil testing unitario
- ✅ Escalable para TASK-09+

### Optimizar para LLMs
- ✅ Solo 5 archivos (vs 1 monolítico)
- ✅ Context manageable
- ✅ Clear imports chain

### Mantener Funcionalidad
- ✅ 0 breaking changes
- ✅ Todas las MCP tools funcionan idénticamente
- ✅ Backward compatible

---

## 📐 Arquitectura Propuesta

### Estado Actual (1054 LOC)
```
src/server.py
├── Lines 1-50: Imports, config, constants
├── Lines 51-88: Error handlers (_serialize_error, tool_handler)
├── Lines 90-282: cde_onboardingProject (192 LOC)
├── Lines 283-345: cde_publishOnboarding (63 LOC)
├── Lines 346-398: cde_scanDocumentation (53 LOC)
├── Lines 399-468: cde_analyzeDocumentation (70 LOC)
├── Lines 469-572: cde_selectWorkflow (104 LOC)
├── Lines 573-659: cde_sourceSkill (87 LOC)
├── Lines 660-765: cde_updateSkill (106 LOC)
├── Lines 766-917: cde_delegateToJules (152 LOC)
└── Lines 918-1054: cde_listAvailableAgents (137 LOC)
```

### Estado Target (5 archivos, ~150 LOC cada uno)
```
src/
├── server.py (140 LOC)
│   ├── Imports from mcp_tools
│   ├── FastMCP app initialization
│   ├── Tool registration (@app.tool())
│   └── if __name__ == "__main__": app.run()
│
└── mcp_tools/
    ├── __init__.py (10 LOC)
    │   └── Export all tools
    │
    ├── _base.py (30 LOC)
    │   ├── _serialize_error()
    │   └── tool_handler decorator
    │
    ├── onboarding.py (130 LOC)
    │   ├── cde_onboardingProject
    │   └── cde_publishOnboarding
    │
    ├── documentation.py (140 LOC)
    │   ├── cde_scanDocumentation
    │   └── cde_analyzeDocumentation
    │
    ├── orchestration.py (180 LOC)
    │   ├── cde_selectWorkflow
    │   ├── cde_sourceSkill
    │   └── cde_updateSkill
    │
    └── agents.py (200 LOC)
        ├── cde_delegateToJules
        └── cde_listAvailableAgents
```

---

## 🔧 Implementación Detallada

### FASE 1: Crear Estructura Base (20 min)

#### Archivo 1: `src/mcp_tools/_base.py`
```python
"""
Base utilities for MCP tools.

Shared error handling and tool decoration.
"""
from functools import wraps
from typing import Any, Callable
import json


def _serialize_error(error: Exception) -> dict:
    """
    Serialize error for JSON response.

    Args:
        error: Exception to serialize

    Returns:
        Dict with error details
    """
    return {
        "error": type(error).__name__,
        "message": str(error),
        "details": str(error.__cause__) if error.__cause__ else None
    }


def tool_handler(func: Callable) -> Callable:
    """
    Wrap MCP tool function with error handling.

    Ensures all tools return JSON strings and handle exceptions gracefully.

    Args:
        func: Async function to wrap

    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> str:
        try:
            result = await func(*args, **kwargs)
            # Ensure string return
            return result if isinstance(result, str) else json.dumps(result, indent=2)
        except Exception as e:
            return json.dumps(_serialize_error(e), indent=2)
    return wrapper
```

#### Archivo 2: `src/mcp_tools/__init__.py`
```python
"""
MCP Tools Package.

Exports all CDE Orchestrator MCP tools for registration in server.py.
"""
from .onboarding import cde_onboardingProject, cde_publishOnboarding
from .documentation import cde_scanDocumentation, cde_analyzeDocumentation
from .orchestration import cde_selectWorkflow, cde_sourceSkill, cde_updateSkill
from .agents import cde_delegateToJules, cde_listAvailableAgents

__all__ = [
    # Onboarding
    "cde_onboardingProject",
    "cde_publishOnboarding",

    # Documentation
    "cde_scanDocumentation",
    "cde_analyzeDocumentation",

    # Orchestration
    "cde_selectWorkflow",
    "cde_sourceSkill",
    "cde_updateSkill",

    # Agents
    "cde_delegateToJules",
    "cde_listAvailableAgents",
]
```

---

### FASE 2: Extraer Tools por Dominio (60 min)

#### Archivo 3: `src/mcp_tools/onboarding.py`
**Responsabilidad**: Project onboarding y document publication

**Contenido**:
- Copiar `cde_onboardingProject` completo (lines 90-282)
- Copiar `cde_publishOnboarding` completo (lines 283-345)
- Añadir imports necesarios:
  ```python
  import json
  from typing import Dict, Any
  from fastmcp import Context
  from pathlib import Path
  from ._base import tool_handler
  from ..application.onboarding import OnboardingUseCase, PublishOnboardingUseCase
  ```

**NO modificar lógica** - Solo mover código.

---

#### Archivo 4: `src/mcp_tools/documentation.py`
**Responsabilidad**: Documentation scanning y analysis

**Contenido**:
- Copiar `cde_scanDocumentation` completo (lines 346-398)
- Copiar `cde_analyzeDocumentation` completo (lines 399-468)
- Añadir imports necesarios:
  ```python
  import json
  from typing import Dict, Any
  from ._base import tool_handler
  from ..application.documentation import (
      ScanDocumentationUseCase,
      AnalyzeDocumentationUseCase
  )
  ```

---

#### Archivo 5: `src/mcp_tools/orchestration.py`
**Responsabilidad**: Workflow selection, skill sourcing/updating

**Contenido**:
- Copiar `cde_selectWorkflow` completo (lines 469-572)
- Copiar `cde_sourceSkill` completo (lines 573-659)
- Copiar `cde_updateSkill` completo (lines 660-765)
- Añadir imports necesarios:
  ```python
  import json
  from typing import List, Dict, Any
  from pathlib import Path
  from ._base import tool_handler
  from ..application.orchestration import (
      WorkflowSelectorUseCase,
      SkillSourcingUseCase,
      WebResearchUseCase
  )
  ```

---

#### Archivo 6: `src/mcp_tools/agents.py`
**Responsabilidad**: AI agent delegation y listing

**Contenido**:
- Copiar `cde_delegateToJules` completo (lines 766-917)
- Copiar `cde_listAvailableAgents` completo (lines 918-1054)
- Añadir imports necesarios:
  ```python
  import json
  import os
  import shutil
  from typing import Dict, Any, List
  from pathlib import Path
  from ._base import tool_handler
  from ..adapters.agents import JulesAsyncAdapter
  ```

---

### FASE 3: Actualizar server.py (20 min)

#### Archivo 7: `src/server.py` (NUEVO - 140 LOC)
```python
"""
CDE Orchestrator MCP Server.

FastMCP server providing Context-Driven Engineering tools for AI agents.
All tools are organized in mcp_tools/ package for modularity.

Usage:
    python src/server.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from fastmcp import FastMCP

# Import all MCP tools
from mcp_tools import (
    # Onboarding
    cde_onboardingProject,
    cde_publishOnboarding,

    # Documentation
    cde_scanDocumentation,
    cde_analyzeDocumentation,

    # Orchestration
    cde_selectWorkflow,
    cde_sourceSkill,
    cde_updateSkill,

    # Agents
    cde_delegateToJules,
    cde_listAvailableAgents,
)

# Load environment variables
load_dotenv()

# Initialize FastMCP app
app = FastMCP(
    name="CDE Orchestrator",
    description="Context-Driven Engineering MCP Server"
)

# --- Tool Registration ---
# Register all tools with FastMCP
# Note: @tool_handler decorator is already applied in each module

# Onboarding Tools
app.tool()(cde_onboardingProject)
app.tool()(cde_publishOnboarding)

# Documentation Tools
app.tool()(cde_scanDocumentation)
app.tool()(cde_analyzeDocumentation)

# Orchestration Tools
app.tool()(cde_selectWorkflow)
app.tool()(cde_sourceSkill)
app.tool()(cde_updateSkill)

# Agent Tools
app.tool()(cde_delegateToJules)
app.tool()(cde_listAvailableAgents)

# --- Server Entry Point ---
if __name__ == "__main__":
    """Run MCP server in development mode."""
    app.run()
```

---

### FASE 4: Validación (20 min)

#### 4.1 Type Checking
```bash
mypy src/ --strict
```

**Expected**: 0 errors (todos los tipos existentes preserved)

#### 4.2 Code Formatting
```bash
black src/ --check
ruff check src/
```

**Expected**: Pass o auto-fixable warnings

#### 4.3 Tests Existentes
```bash
pytest tests/ -v
```

**Expected**: 56/56 tests pass (0 breaking changes)

#### 4.4 MCP Integration Test
```bash
# Test tool discovery
python -c "from fastmcp import FastMCP; from mcp_tools import *; print('✅ All tools imported')"

# Test server starts
python src/server.py &
sleep 2
kill $!
```

**Expected**: Server starts without errors

---

## ✅ Criterios de Aceptación

### Estructura
- [ ] `src/mcp_tools/` directory created
- [ ] 6 archivos creados (\_\_init\_\_.py, \_base.py, 4 modules)
- [ ] `src/server.py` reducido a ~140 líneas
- [ ] Cada módulo < 200 líneas

### Funcionalidad
- [ ] All 9 MCP tools registered correctly
- [ ] `@app.tool()` decorator presente en server.py
- [ ] `@tool_handler` decorator presente en cada tool
- [ ] Error handling preserved (\_serialize_error)
- [ ] All docstrings preserved (100% documentation)

### Quality
- [ ] `mypy src/` pasa sin errores
- [ ] `black src/` pasa (formatted)
- [ ] `ruff check src/` pasa o warnings menores
- [ ] `pytest tests/` - 56/56 tests pass
- [ ] Pre-commit hooks pass

### Testing Manual
- [ ] `python src/server.py` starts successfully
- [ ] MCP client can discover all 9 tools
- [ ] `cde_onboardingProject` ejecutable via MCP
- [ ] `cde_listAvailableAgents` ejecutable via MCP

---

## 🚨 Consideraciones Críticas

### NO Modificar Lógica
- ❌ **NO cambiar** implementación de tools
- ❌ **NO refactorizar** lógica interna
- ✅ **SOLO mover** código a nuevos archivos
- ✅ **SOLO ajustar** imports

### Preservar 100% Funcionalidad
- Todos los docstrings completos
- Todos los @app.tool() decorators
- Todos los @tool_handler decorators
- Todos los use cases llamados idénticamente
- Todos los JSON returns idénticos

### FastMCP Requirements
- `@app.tool()` debe estar en server.py (NO en módulos)
- Functions deben ser async donde ya lo eran
- Tool names deben mantenerse idénticos
- Tool signatures (params) deben mantenerse idénticas

---

## 📊 Métricas de Éxito

| Métrica | Antes | Después | Target |
|---------|-------|---------|--------|
| server.py LOC | 1054 | 140 | < 150 |
| Largest module LOC | 1054 | 200 | < 200 |
| Total files | 1 | 7 | 5-7 |
| Import depth | 0 | 1 | < 2 |
| Tests passing | 56/56 | 56/56 | 100% |
| Type errors | 0 | 0 | 0 |

---

## 📝 Notas para Implementador (Jules)

### Orden de Ejecución Recomendado
1. Crear `src/mcp_tools/_base.py` (copy lines 54-88)
2. Crear `src/mcp_tools/__init__.py` (imports vacíos por ahora)
3. Crear `src/mcp_tools/onboarding.py` (copy lines 90-345)
4. Crear `src/mcp_tools/documentation.py` (copy lines 346-468)
5. Crear `src/mcp_tools/orchestration.py` (copy lines 469-765)
6. Crear `src/mcp_tools/agents.py` (copy lines 766-1054)
7. Actualizar `src/mcp_tools/__init__.py` (add exports)
8. Reescribir `src/server.py` (nuevo archivo limpio)
9. Validar: mypy, black, ruff, pytest
10. Test manual: python src/server.py

### Tips de Implementación
- **Copy-paste exacto**: Preserva whitespace, comments, docstrings
- **Imports relativos**: Usa `from ._base import` en módulos
- **Imports absolutos**: Usa `from mcp_tools import` en server.py
- **Git staging**: Stage cambios por fase (4 commits)
- **Rollback plan**: Keep backup de server.py original

### Debugging
Si tests fallan:
1. Check import paths (relative vs absolute)
2. Verify all @app.tool() in server.py
3. Verify all @tool_handler in modules
4. Check FastMCP app initialization
5. Rollback y retry fase por fase

---

## 🎯 Próximos Pasos (Post-Refactor)

Una vez completado:
1. ✅ Commit: "refactor: split server.py into modular mcp_tools package"
2. ✅ Update documentation: AGENTS.md, GEMINI.md
3. ✅ Continue with TASK-09: cde_selectAgent implementation
4. ✅ Escalar: Agregar nuevos tools es trivial (nuevo archivo en mcp_tools/)

---

## 📚 Referencias

- **Spec-Kit Documentation**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **Architecture Guide**: `specs/design/architecture/README.md`
- **Improvement Roadmap**: `specs/tasks/improvement-roadmap.md`
- **FastMCP Docs**: https://github.com/jlowin/fastmcp
- **Python Best Practices**: PEP 8, PEP 20
