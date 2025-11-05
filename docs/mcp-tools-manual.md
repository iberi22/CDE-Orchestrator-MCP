---
title: "Manual de Herramientas MCP"
description: "Guía de referencia para las herramientas expuestas por el CDE Orchestrator MCP."
type: "guide"
status: "active"
created: "2025-11-05"
updated: "2025-11-05"
author: "Jules"
---

# Manual de Herramientas del Servidor MCP

Este documento proporciona una referencia completa para todas las herramientas expuestas por el CDE Orchestrator a través del protocolo MCP.

## Herramientas de Onboarding

### `cde_onboardingProject`

Analiza un proyecto de software existente para recopilar información sobre su estructura, lenguajes y dependencias.

**Parámetros:**
- `project_path` (string, opcional): La ruta al proyecto a analizar. Por defecto, el directorio de trabajo actual.

**Devuelve:**
Un objeto JSON que contiene el resumen del análisis.

**Ejemplo de Uso:**
```json
{
  "tool": "cde_onboardingProject",
  "params": {
    "project_path": "/path/to/my/project"
  }
}
```

### `cde_publishOnboarding`

Escribe un conjunto de documentos en el sistema de archivos del proyecto. Es útil para aplicar la documentación generada durante el onboarding.

**Parámetros:**
- `documents` (dict): Un diccionario donde las claves son las rutas relativas de los archivos y los valores son el contenido del archivo.
- `project_path` (string, opcional): La ruta raíz del proyecto. Por defecto, el directorio actual.
- `approve` (bool, opcional): Debe ser `true` para que la escritura se realice. Por defecto, `true`.

**Devuelve:**
Un objeto JSON con el estado de la operación y la lista de archivos escritos.

**Ejemplo de Uso:**
```json
{
  "tool": "cde_publishOnboarding",
  "params": {
    "documents": {
      "docs/architecture.md": "# Arquitectura\n...",
      "CONTRIBUTING.md": "..."
    },
    "project_path": "/path/to/my/project"
  }
}
```

## Herramientas de Documentación

### `cde_scanDocumentation`

Realiza un escaneo de alto nivel de la estructura de la documentación, buscando problemas de organización y metadatos faltantes.

**Parámetros:**
- `project_path` (string, opcional): La ruta al proyecto a escanear. Por defecto, el directorio actual.

**Devuelve:**
Un informe JSON con estadísticas y recomendaciones.

**Ejemplo de Uso:**
```json
{
  "tool": "cde_scanDocumentation",
  "params": {}
}
```

### `cde_analyzeDocumentation`

Realiza un análisis profundo de la calidad de la documentación, incluyendo la validación de enlaces internos y la consistencia de los metadatos.

**Parámetros:**
- `project_path` (string, opcional): La ruta al proyecto a analizar. Por defecto, el directorio actual.

**Devuelve:**
Un informe JSON detallado con una puntuación de calidad, análisis de enlaces y problemas específicos.

**Ejemplo de Uso:**
```json
{
  "tool": "cde_analyzeDocumentation",
  "params": {}
}
```

### `cde_createSpecification`

Crea un nuevo archivo de especificación de feature en `specs/features/` con el formato y frontmatter correctos.

**Parámetros:**
- `feature_name` (string): El nombre de la nueva feature.
- `description` (string): Una breve descripción.
- `author` (string): El autor de la especificación.
- `project_path` (string, opcional): La ruta al proyecto. Por defecto, el directorio actual.

**Devuelve:**
Un objeto JSON con la ruta al archivo creado.

**Ejemplo de Uso:**
```json
{
  "tool": "cde_createSpecification",
  "params": {
    "feature_name": "Login con OAuth2",
    "description": "Permitir a los usuarios iniciar sesión con proveedores OAuth2.",
    "author": "Gemini"
  }
}
```
