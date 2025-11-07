---
title: 'Codex CLI + MCP: CDE Orchestrator'
description: This guide shows how to use the CDE Orchestrator MCP with Codex CLI and
  how to connect additional MCP tools (e.g., GitHub MCP) for a fully agentic wor
type: guide
status: draft
created: '2025-11-02'
updated: '2025-11-02'
author: Auto-Generated
tags:
- api
- authentication
- codex
- mcp
- python
- workflow
llm_summary: "User guide for Codex CLI + MCP: CDE Orchestrator.\n  This guide shows\
  \ how to use the CDE Orchestrator MCP with Codex CLI and how to connect additional\
  \ MCP tools (e.g., GitHub MCP) for a fully agentic workflow. - Prerequisites: -\
  \ Python 3.11+ - `pip install -r requirements.txt`\n  Reference when working with\
  \ guide documentation."
---

# Codex CLI + MCP: CDE Orchestrator

This guide shows how to use the CDE Orchestrator MCP with Codex CLI and how to connect additional MCP tools (e.g., GitHub MCP) for a fully agentic workflow.

## Quick Start

- Prerequisites:
  - Python 3.11+
  - `pip install -r requirements.txt`
  - Optional: `GITHUB_TOKEN` for API fallback

### Run server (STDIO)

```bash
python src/server.py
```

Codex connects to MCP servers via STDIO. Point Codex to run `python src/server.py` in your project.

## Configure MCP servers

Codex and many IDEs support the common MCP config schema (same as Cursor/VS Code). Place one of the following configs:

### Option A: Project scoped

Add `.vscode/mcp.json` (already included):

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": ["src/server.py"],
      "env": { "PYTHONPATH": "src" },
      "disabled": false,
      "autoApprove": ["cde_onboardingProject"]
    }
  }
}
```

### Option B: User scoped

Add `~/.cursor/mcp.json` or `~/.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": ["src/server.py"],
      "env": { "PYTHONPATH": "src" },
      "disabled": false
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "your-token-here" },
      "disabled": false
    }
  }
}
```

Note: Codex can read the same schema and will launch the servers under the given names.

## LLM-first tool I/O contracts

All CDE tools return JSON strings for machine-readability. Key endpoints:

- `cde_onboardingProject() -> { status, message?, draft_preview? }` (full plan + cleanup recommendations saved under `.cde/state.json` → `onboarding.plan`)
- `cde_publishOnboarding(documents, approve) -> { status, created, failed }`
- `cde_startFeature(prompt) -> { feature_id, phase, prompt, progress }`
- `cde_submitWork(feature_id, phase_id, results) -> { phase, prompt } | { status: "completed" }`
- `cde_getFeatureStatus(feature_id) -> { ...state }`
- `cde_listFeatures() -> { features }`
- `cde_listRecipes() -> { category: [ids] }`
- `cde_suggestRecipe(prompt, phase_id) -> { recipe_id, ... }`
- `cde_useRecipe(recipe_id, prompt) -> { prompt }`
- `cde_createGitBranch(...) -> { success, ... }`
- `cde_createGitHubIssue(...) -> { success, ... }`
- `cde_commitWork(...) -> { success, ... }`
- `cde_getServiceStatus() -> { github, git }`

Errors return `{ "error": <code>, ... }`.

## Minimal workflows for agents

1) Onboard a repo

```json
call: cde_onboardingProject()
-> { status: "draft_ready", draft_preview }
```

Use `draft_preview` with your model to produce concrete files, then:

```json
call: cde_publishOnboarding({ "specs/README.md": "...", "memory/constitution.md": "..." }, true)
-> { status: "applied", created: [ ... ] }
```

The onboarding plan (including `cleanup_plan`, `repository_synthesis`, and stakeholder questions) is persisted at `.cde/state.json` under `onboarding.plan`.

2) Start a feature

```json
call: cde_startFeature("Add user authentication")
-> { feature_id, phase: "define", prompt, progress }
```

3) Submit phase work, progress to next prompt

```json
call: cde_submitWork(feature_id, "define", { "specification": "# Feature Spec..." })
-> { phase: "decompose", prompt, progress }
```

Repeat for subsequent phases.

## Tips

- Prefer calling `cde_getServiceStatus()` before GitHub operations
- Keep `results` payloads small and phase-appropriate
- Use `cde_suggestRecipe()` to select a tuned recipe for define/decompose/design
- Repo digest respects `.gitignore` (PathSpec). Use `force_refresh=True` if you need a fresh read.
- After onboarding, review `state['onboarding']['plan']['cleanup_plan']` to execute test relocations, archive obsolete docs, and refresh READMEs in line with the Integrated Management System principles.

## Troubleshooting

- Missing prompts: ensure `.cde/prompts/01_define.poml .. 06_review.poml` exist
- Workflow file: `.cde/workflow.yml` must exist
- GitHub MCP vs API: set up either MCP or `GITHUB_TOKEN` env var

## Next

See `INTEGRATION.md` for external services and `ONBOARDING_REVIEW_REPORT.md` for roadmap and best practices.
