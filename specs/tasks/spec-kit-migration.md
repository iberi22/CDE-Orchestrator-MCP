---
title: "Migration to Spec-Kit Documentation Standard"
description: "Roadmap for migrating from current documentation structure to Spec-Kit standard (specs/[feature]/)."
type: "task"
status: "active"
created: "2025-11-23"
updated: "2025-11-23"
author: "GitHub Copilot"
llm_summary: |
  Task list for migrating to Spec-Kit.
  Includes governance updates, template porting, MCP tool updates, and feature migration.
---

# Migration to Spec-Kit Documentation Standard

> **Status**: Active
> **Priority**: High
> **Owner**: CDE Orchestrator Team

## Overview

We are adopting [Spec-Kit](https://github.com/github/spec-kit) to unify our documentation and execution workflow. This involves moving from a split `specs/` vs `agent-docs/` model to a feature-centric `specs/[feature]/` model.

## Tasks

### Phase 1: Preparation & Governance

- [x] **Update Governance**: Modify `specs/governance/DOCUMENTATION_GOVERNANCE.md` to allow `specs/[feature]/` structure.
- [x] **Define New Standards**: Document the `spec.md`, `plan.md`, `tasks.md` requirement.
- [x] **Port Templates**:
  - [x] Copy `spec-template.md` to `specs/templates/spec.md`
  - [x] Copy `plan-template.md` to `specs/templates/plan.md`
  - [x] Copy `tasks-template.md` to `specs/templates/tasks.md`

### Phase 2: Tooling Updates

- [x] **Update `cde_startFeature`**:
  - [x] Logic to create `specs/[feature-name]/` directory.
  - [x] Logic to populate `spec.md` from template.
- [x] **Update `cde_submitWork`**:
  - [x] Logic to update `tasks.md` status.
  - [x] Logic to commit changes to the feature folder.

### Phase 3: Migration

- [ ] **Migrate Active Features**:
  - [ ] Identify active features in `specs/features/`.
  - [ ] Create new folders for them.
  - [ ] Move content to `spec.md`.
  - [ ] Create `plan.md` and `tasks.md` for them.
- [ ] **Cleanup**:
  - [ ] Deprecate `agent-docs/execution/` for new features.
  - [ ] Update `AGENTS.md` instructions.

## Acceptance Criteria

- [x] All new features start with `specs/[feature]/` structure.
- [x] `agent-docs` is used ONLY for sessions, general research, and feedback.
- [x] MCP tools automatically generate the correct structure.
- [ ] All active features migrated from old structure (Phase 3)
- [ ] AGENTS.md instructions updated (Phase 3)
- [ ] Full test suite passing (Phase 3)

## Status Summary

**Phase 1**: ✅ COMPLETE (Governance + Templates)
**Phase 2**: ✅ COMPLETE (Tooling Updates)
**Phase 3**: ⏳ PENDING (Migration + Testing)
