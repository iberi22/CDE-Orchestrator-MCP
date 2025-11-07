---
author: Auto-Generated
created: '2025-11-02'
description: This directory contains API specifications and contracts for CDE Orchestrator
  MCP.
llm_summary: "User guide for API Specifications.\n  This directory contains API specifications\
  \ and contracts for CDE Orchestrator MCP. All API documentation should be stored\
  \ here, following OpenAPI/Swagger standards when applicable. CDE Orchestrator exposes\
  \ several MCP tools:\n  Reference when working with guide documentation."
status: draft
tags:
- api
- documentation
- mcp
- readme
- workflow
title: API Specifications
type: design
updated: '2025-11-02'
---

# API Specifications

This directory contains API specifications and contracts for CDE Orchestrator MCP.

## Purpose

All API documentation should be stored here, following OpenAPI/Swagger standards when applicable.

## Structure

```
specs/api/
├── README.md           # This file
├── mcp-tools.yaml      # MCP tool definitions (if using OpenAPI format)
└── endpoints/          # Endpoint-specific docs
```

## MCP Tools API

CDE Orchestrator exposes several MCP tools:

### Core Tools
- `cde_startFeature` - Start new feature workflow
- `cde_submitWork` - Submit phase results and advance
- `cde_getFeatureStatus` - Get current feature status
- `cde_listFeatures` - List all features

### Onboarding Tools
- `cde_onboardingProject` - Analyze and configure project structure
- `cde_publishOnboarding` - Apply onboarding documents

### Service Integration Tools
- `cde_createGitBranch` - Create Git branch for feature
- `cde_createGitHubIssue` - Create GitHub issue
- `cde_commitWork` - Commit changes to Git

### Recipe Management
- `cde_listRecipes` - List available POML recipes
- `cde_useRecipe` - Use specific recipe
- `cde_suggestRecipe` - Get recipe suggestion

## Documentation Format

API specs should include:
- Endpoint/tool name
- Parameters (types, required/optional)
- Return values (schemas)
- Examples
- Error cases

## Links

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [CDE Workflow](../../.cde/workflow.yml)
- [Feature Specifications](../features/)
