---
title: "Adoption of Spec-Kit for Documentation & Workflow"
description: "Proposal to adopt GitHub's Spec-Kit methodology to unify specifications and execution tracking, reducing duplication between specs and agent-docs."
type: "design"
status: "draft"
created: "2025-11-23"
updated: "2025-11-23"
author: "GitHub Copilot"
llm_summary: |
  Proposes adopting Spec-Kit to structure documentation by feature (specs/[feature]/).
  Redefines agent-docs to focus on temporal logs (sessions) and general research.
  Aims to eliminate "double documentation" by making specs the single source of truth for both definition and execution status.
---

# Adoption of Spec-Kit for Documentation & Workflow

## 1. Problem Statement

Currently, the project maintains two parallel documentation structures:

1. `specs/`: Contains feature specifications (`features/`), design docs (`design/`), and tasks (`tasks/`).
2. `agent-docs/`: Contains execution reports (`execution/`), session logs (`sessions/`), and research (`research/`).

**Issues:**

- **Duplication**: Execution reports in `agent-docs` often duplicate the status tracking that should be in `specs/tasks`.
- **Disconnect**: The "Plan" and "Tasks" are often separated from the "Spec".
- **Manual Overhead**: `agent-docs` are currently created manually by agents, not managed by MCP tools.

## 2. The Spec-Kit Approach

[Spec-Kit](https://github.com/github/spec-kit) proposes a **Spec-Driven Development (SDD)** workflow where the specification is the source of truth.

**Key Concepts:**

- **Feature-Centric Structure**: All documents for a feature live in `specs/[branch-name]/` (or `specs/[feature-name]/`).
- **Core Documents**:
  - `spec.md`: The Product Requirements Document (PRD).
  - `plan.md`: The technical Implementation Plan.
  - `tasks.md`: The executable Task List.
- **Workflow**: Spec -> Plan -> Tasks -> Code.

## 3. Proposed Architecture

We will adopt the Spec-Kit structure, adapting it to our Hexagonal Architecture and MCP workflow.

### 3.1 Directory Structure

```text
specs/
├── [feature-name]/          # Feature-specific folder (NEW)
│   ├── spec.md              # PRD (formerly specs/features/X.md)
│   ├── plan.md              # Technical Design & Plan
│   ├── tasks.md             # Executable Tasks (Status tracked here)
│   └── research.md          # Feature-specific research (Optional)
├── design/                  # Cross-cutting architectural decisions (Keep)
├── governance/              # Process rules (Keep)
└── templates/               # Spec-Kit templates (Update)
```

### 3.2 Redefining `agent-docs/`

`agent-docs/` will be streamlined to focus on **temporal logs** and **cross-cutting artifacts**:

- `sessions/`: **KEEP**. Audit logs of agent interactions. Immutable history.
- `execution/`: **DEPRECATE** for features. Execution status should be updated directly in `specs/[feature]/tasks.md`.
- `research/`: **RETAIN** for *general* research (e.g., "Python 3.14 capabilities") that doesn't fit a single feature. Feature-specific research goes to `specs/[feature]/research.md`.
- `feedback/`: **KEEP**. General system feedback.

### 3.3 Workflow Changes

**Current:**

1. `cde_startFeature` -> Creates `specs/features/X.md`.
2. Agent works -> Creates `agent-docs/execution/X.md`.

**Proposed:**

1. `cde_startFeature` -> Creates `specs/[feature]/spec.md`.
2. Agent analyzes -> Creates `specs/[feature]/plan.md`.
3. Agent decomposes -> Creates `specs/[feature]/tasks.md`.
4. Agent executes -> Updates checkboxes in `specs/[feature]/tasks.md`.
5. `cde_submitWork` -> Commits changes to `specs/[feature]/`.

## 4. Migration Plan

1. **Update Governance**: Modify `DOCUMENTATION_GOVERNANCE.md` to sanction the `specs/[feature]/` structure.
2. **Port Templates**: Copy `spec.md`, `plan.md`, `tasks.md` templates from Spec-Kit to `specs/templates/`.
3. **Update MCP Tools**:
    - Modify `cde_startFeature` to generate the new folder structure.
    - Modify `cde_submitWork` to support task updates.
4. **Migrate Active Features**: Move existing active feature specs to the new structure.

## 5. Benefits

- **Single Source of Truth**: No more checking `agent-docs` to see if a `spec` was implemented. The `tasks.md` tells the truth.
- **Better Context**: LLMs get the Spec, Plan, and Tasks in one folder context.
- **Reduced Noise**: `agent-docs` becomes a clean audit log, not a workspace.
