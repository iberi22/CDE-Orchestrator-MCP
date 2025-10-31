# Agent Guide: CDE Orchestrator MCP

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

- `cde_onboardingProject()` → Prepare onboarding draft; use with your model to generate documents; apply via `cde_publishOnboarding`.
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

1) Onboard → generate docs → `cde_publishOnboarding`
2) Start feature → use returned `prompt` to produce outputs
3) Submit outputs via `cde_submitWork` to progress

## Integration

- External MCPs are auto-detected from standard configs (`.vscode/mcp.json`, `~/.cursor/mcp.json`).
- GitHub: Prefer MCP server; fallback to API via `GITHUB_TOKEN`.

## Safety

- Prefer small, reversible changes per phase.
- Respect `.gitignore` and avoid writing binaries.
- Keep prompts and outputs under token budgets.

## Style

- Python: type hints, clear naming, cohesive functions.
- Docs: concise, action-oriented, example-first.

