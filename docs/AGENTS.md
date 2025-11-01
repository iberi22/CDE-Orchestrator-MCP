---
title: "Agent Guide - CDE Orchestrator MCP"
description: "Quick reference for AI agents working with CDE Orchestrator MCP tools and workflows"
type: "guide"
status: "active"
created: "2025-10-31"
updated: "2025-11-01"
author: "CDE Orchestrator Team"
tags:
  - "ai-agents"
  - "mcp-tools"
  - "workflow"
  - "contracts"
llm_summary: |
  Reference guide for AI agents using CDE Orchestrator MCP. Covers tool contracts, workflow rules,
  and core principles. Use when working with MCP tools or understanding project structure.
---

# CDE Orchestrator MCP - Agent Guide

This repository is designed for AI agents. Keep human-facing docs minimal and machine contracts explicit. Follow these rules when interacting with the MCP tools and repository.

## Principles

- LLM-first: All tools return JSON strings. Parse, reason, and act deterministically.
- Workflow-as-code: Treat `.cde/workflow.yml` as the source of truth for phases and prompts.
- Context chaining: Each phase produces artifacts used as inputs for the next.
- Minimalism: Change only what’s needed; avoid broad refactors in a single step.

## Contracts

- Tool outputs: JSON with either `status` or `error` keys.
- Errors: `{ "error": <code>, ... }` — inspect and branch accordingly.
- State: Project state lives in `.cde/state.json` via the StateManager; avoid manual edits.
- Prompts: POML files in `.cde/prompts/` provide role, context, task, and output format.

## Core Tools

- `cde_onboardingProject()` → Prepare onboarding draft, repository synthesis, and cleanup plan (`state['onboarding']['plan']`); use with your model to generate documents; apply via `cde_publishOnboarding`.
- `cde_startFeature(prompt)` → Returns `feature_id`, `phase`, `prompt`, `progress`.
- `cde_submitWork(feature_id, phase_id, results)` → Advance phase or complete workflow.
- `cde_getFeatureStatus(feature_id)`, `cde_listFeatures()` → Inspect current state.
- `cde_listRecipes()`, `cde_suggestRecipe()`, `cde_useRecipe()` → Recipe discovery and prompt generation.
- Git/GitHub: `cde_createGitBranch`, `cde_createGitHubIssue`, `cde_commitWork`, `cde_getServiceStatus`.

## Results payloads by phase

- `define`: `{ "specification": "markdown" }`
- `decompose`: `{ "task_breakdown": "markdown" }`
- `design`: `{ "design_document": "markdown" }`
- `review`: `{ "review_document": "markdown" }`

## Workflows

1) Onboard → review `state['onboarding']['plan']` (docs + cleanup plan) → generate docs → `cde_publishOnboarding`
2) Start feature → use returned `prompt` to produce outputs
3) Submit outputs via `cde_submitWork` to progress

## Onboarding Deliverables

- `cleanup_plan.tests_to_move`: Move stray tests into `tests/` while preserving imports.
- `cleanup_plan.files_to_archive`: Remove/relocate legacy planning files (e.g., `TASK.md`) that conflict with Spec-as-Code.
- `cleanup_plan.documentation_updates`: Regenerate READMEs/constitutions to match Integrated Management System principles.
- `questions_for_human`: Surface approval checkpoints; always pause until the human confirms the recommended action.

## Integration

- External MCPs are auto-detected from standard configs (`.vscode/mcp.json`, `~/.cursor/mcp.json`).
- GitHub: Prefer MCP server; fallback to API via `GITHUB_TOKEN`.

## Safety

- Prefer small, reversible changes per phase.
- Respect `.gitignore` and avoid writing binaries.
- Execute the onboarding `cleanup_plan` (test relocations, obsolete file archiving, doc refresh) with human approval before merging.
- Keep prompts and outputs under token budgets.

## Style

- Python: type hints, clear naming, cohesive functions.
- Docs: concise, action-oriented, example-first.
