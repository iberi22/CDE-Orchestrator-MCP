---
title: "Pyrefly Type Checking Report"
description: "Análisis de tipos estáticos del proyecto CDE Orchestrator MCP"
type: "execution"
status: "active"
created: "2025-11-20"
updated: "2025-11-20"
author: "Pyrefly Type Checker"
---

# Pyrefly Type Checking Report

**Fecha**: 2025-11-20 14:55:17
**Total de errores**: 112

## 📊 Resumen por Categoría

| Categoría | Cantidad | Criticidad |
|-----------|----------|------------|
| `missing-attribute` | 52 | 🔴 Alta |
| `other` | 34 | 🟡 Media |
| `missing-import` | 6 | 🔴 Alta |
| `bad-argument-type` | 5 | 🟡 Media |
| `bad-assignment` | 4 | 🔴 Alta |
| `deprecated` | 4 | 🟡 Media |
| `not-iterable` | 3 | 🟡 Media |
| `bad-index` | 3 | 🟡 Media |
| `unbound-name` | 1 | 🟡 Media |

## 🔍 Detalles por Categoría

### missing-attribute (52 errores)

#### `unknown`

- **ERROR**: Object of class `NoneType` has no attribute `sessions` [missing-attribute
- **ERROR**: Object of class `NoneType` has no attribute `sessions` [missing-attribute
- **ERROR**: Object of class `NoneType` has no attribute `id` [missing-attribute

  *...y 49 errores más en este archivo*

### other (34 errores)

#### `unknown`

- **ERROR**: Default `None` is not assignable to parameter `available_agents` with type `list[AgentType
- **ERROR**: No matching overload found for function `min` called with arguments: (Literal[10
- **ERROR**: Expected a callable, got `None` [not-callable

  *...y 31 errores más en este archivo*

### missing-import (6 errores)

#### `unknown`

- **ERROR**: Could not find import of `julius_agent_sdk` [missing-import
- **ERROR**: Could not find import of `cde_orchestrator.adapters.agents.julius_async_adapter` [missing-import
- **ERROR**: Could not find import of `cde_orchestrator.adapters.agents.julius_cli_adapter` [missing-import

  *...y 3 errores más en este archivo*

### bad-argument-type (5 errores)

#### `unknown`

- **ERROR**: Argument `None` is not assignable to parameter `tools` with type `list[dict[str, Any
- **ERROR**: Argument `None` is not assignable to parameter `obj` with type `Sized` in function `len` [bad-argument-type
- **ERROR**: Argument `list[dict[str, Any

  *...y 2 errores más en este archivo*

### bad-assignment (4 errores)

#### `unknown`

- **ERROR**: `list[dict[str, Any
- **ERROR**: `list[dict[str, Any
- **ERROR**: `None` is not assignable to `dict[str, Any

  *...y 1 errores más en este archivo*

### deprecated (4 errores)

#### `unknown`

- **WARN**: `pydantic.main.BaseModel.dict` is deprecated [deprecated
- **WARN**: `pydantic.main.BaseModel.dict` is deprecated [deprecated
- **WARN**: `pydantic.main.BaseModel.dict` is deprecated [deprecated

  *...y 1 errores más en este archivo*

### not-iterable (3 errores)

#### `unknown`

- **ERROR**: `in` is not supported between `Literal['files'
- **ERROR**: `in` is not supported between `Literal['files'
- **ERROR**: Type `None` is not iterable [not-iterable

### bad-index (3 errores)

#### `unknown`

- **ERROR**: Cannot index into `object` [bad-index
- **ERROR**: Cannot index into `object` [bad-index
- **ERROR**: Cannot index into `list[Unknown

### unbound-name (1 errores)

#### `unknown`

- **ERROR**: `timeout_value` is uninitialized [unbound-name


## 💡 Recomendaciones

### Prioridad Alta 🔴

1. **Missing Attributes**: Revisar accesos a atributos que pueden ser `None`
   - Usar `Optional[]` type hints
   - Agregar validaciones `if obj is not None:`
   - Usar `getattr()` con valores por defecto

2. **Missing Imports**: Agregar dependencias faltantes
   - `julius_agent_sdk`: Verificar instalación
   - `plyer`: Para notificaciones del sistema
   - `websocket`: Para comunicación en tiempo real

3. **Bad Assignments**: Corregir tipos incompatibles
   - Revisar inicializaciones con `None`
   - Usar `Union[]` o `Optional[]` cuando sea necesario

### Prioridad Media 🟡

4. **Deprecated Warnings**: Actualizar código obsoleto
   - Reemplazar `pydantic.BaseModel.dict()` por `model_dump()`
   - Actualizar a APIs modernas

5. **Type Inference**: Mejorar hints de tipos
   - Agregar type hints explícitos en funciones
   - Usar `TypedDict` para dictionaries estructurados

## 🛠️ Próximos Pasos

1. **Fase 1**: Corregir errores críticos (missing-attribute, missing-import)
2. **Fase 2**: Resolver bad-assignments y type incompatibilities
3. **Fase 3**: Actualizar código deprecated
4. **Fase 4**: Mejorar type hints generales
5. **Fase 5**: Integrar Pyrefly en CI/CD

## 📝 Notas

- Este reporte fue generado automáticamente por Pyrefly
- Pyrefly es un type checker de Meta/Facebook escrito en Rust
- Más rápido que mypy con inferencia de tipos flow-sensitive
- Configuración: `pyrefly.toml` y `pyproject.toml`
