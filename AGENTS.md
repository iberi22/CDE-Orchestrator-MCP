---
title: AI Agent Instructions
description: Core guidelines for AI agents working on CDE Orchestrator
type: governance
status: active
created: 2025-11-24
updated: 2025-11-24
author: CDE Team
---

# AI Agent Instructions - CDE Orchestrator MCP

> **Quick Reference for AI Coding Agents**
> **Enforced by Validation Scripts**

---

## 🚨 Critical Rules (STRICTLY ENFORCED)

1.  **NO .md files in root** except: `README.md`, `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`.
    *   All other documentation must go to `specs/` or `agent-docs/`.
    *   VIOLATION: Placing files like `todo.md` or `report.md` in the root.

2.  **Spec-Kit Structure**: All features must follow the strict directory structure:
    ```
    specs/[feature-name]/
    ├── spec.md   (Requirements & User Stories)
    ├── plan.md   (Technical Architecture)
    └── tasks.md  (Implementation Checklist)
    ```
    *   **Action**: Use `cde_startFeature` to generate this automatically. Do NOT create manually if possible.

3.  **MCP-First Workflow**:
    *   Use `cde_selectWorkflow` to start tasks.
    *   Use `cde_startFeature` to create feature contexts.
    *   Use `cde_submitWork` to track progress.

---

## 🏗️ Architecture

**Pattern**: Hexagonal (Ports & Adapters)

```
Domain (entities) → Application (use_cases) → Adapters (infrastructure)
```

*   **Domain**: Pure business logic. No external imports.
*   **Application**: Use cases orchestration.
*   **Adapters**: Implementation details (Git, FileSystem, OpenAI).

---

## 📂 Directory Structure

```
specs/
├── [feature-name]/        # Feature-specific documentation
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── templates/            # Golden master templates
└── legacy-migration/     # Archived root files

agent-docs/
├── execution/            # General execution logs & session notes
└── ...
```

---

## 🔧 Development Guidelines

1.  **Always Verify**: After creating a file, read it back to confirm.
2.  **Run Tests**: When available. Note that `mcp-status-bar` has no tests.
3.  **Clean Up**: Do not leave temporary scripts in the root. Move them to `scripts/scratch/` or `tests/`.

---

**Remember**: This file is the LAW. Deviations will be rejected by pre-commit hooks.
