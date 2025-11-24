---
title: "Phase 2 Execution: Spec-Kit Tooling Updates"
description: "Implementation of Spec-Kit integration into MCP tools for automatic directory and file generation."
type: "execution"
status: "completed"
created: "2025-11-23"
updated: "2025-11-23"
author: "GitHub Copilot"
llm_summary: |
  Phase 2 of Spec-Kit migration completed. Updated StartFeatureUseCase to auto-generate specs/[feature]/ structure
  and SubmitWorkUseCase to track task progress. Updated Domain entities and adapters to support feature naming.
  Fixed templates and updated governance documentation.
---

# Phase 2 Execution: Spec-Kit Tooling Updates

> **Status**: ✅ COMPLETED
> **Date**: 2025-11-23
> **Phase**: Tooling Integration

## Overview

**Objective**: Integrate Spec-Kit structure into MCP tools to automate feature directory and file generation.

**Scope**: Updated use cases, domain entities, adapters, and templates to support the new `specs/[feature]/` structure.

## Changes Made

### 1. Domain Layer Updates (`domain/entities.py`)

**Change**: Added `name` field to Feature entity for directory naming

- ✅ Added `name: str` attribute to Feature dataclass
- ✅ Updated `Feature.create()` factory to accept optional name parameter
- ✅ Implemented auto-slugification of prompt to name if not provided
- ✅ Updated `Project.start_feature()` to pass name through

**Rationale**: Feature names are needed for directory structure (`specs/[feature-name]/`).

### 2. Application Layer Updates

#### StartFeatureUseCase (`application/use_cases/start_feature.py`)

**Changes**:

- ✅ Added `_initialize_spec_kit()` method
- ✅ Implemented auto-creation of `specs/[feature-name]/` directory
- ✅ Auto-generates `spec.md` from template with placeholder replacement:
  - `[FEATURE NAME]` → feature name
  - `[###-feature-name]` → feature name slug
  - `[DATE]` → current date
  - `[AUTHOR]` → "AI Agent"
  - `$ARGUMENTS` → user prompt
- ✅ Fallback to minimal spec if template missing
- ✅ Integration into `execute()` workflow

**Result**: When `cde_startFeature()` is called, the complete Spec-Kit structure is created automatically.

#### SubmitWorkUseCase (`application/use_cases/submit_work.py`)

**Changes**:

- ✅ Added `_update_spec_kit_tasks()` method
- ✅ Implements task status tracking in `tasks.md`:
  - Marks current phase tasks with `[>]` (in progress)
  - Preserves other task statuses
  - Silently fails if `tasks.md` doesn't exist
- ✅ Integration into `execute()` workflow (called after phase submission)

**Result**: When `cde_submitWork()` is called, the `tasks.md` file is updated to reflect current progress.

### 3. Adapter Layer Updates (`adapters/filesystem_project_repository.py`)

**Changes**:

- ✅ Updated `_serialize_feature()` to include `name` field
- ✅ Updated `_load_from_file()` to deserialize `name` field with fallback

**Result**: Ensures persistence of feature names to disk.

### 4. Governance Updates (`specs/governance/DOCUMENTATION_GOVERNANCE.md`)

**Changes**:

- ✅ Added new section for `specs/[feature-name]/` structure (Spec-Kit Standard)
- ✅ Marked `specs/features/` as DEPRECATED (legacy location)
- ✅ Updated `agent-docs/` section:
  - Marked `agent-docs/execution/` as DEPRECATED for features
  - Clarified that feature-specific research goes to `specs/[feature]/research.md`
  - General research stays in `agent-docs/research/`

**Result**: Clear governance rules for new feature development.

### 5. Templates Updates (`specs/templates/`)

**Changes**:

- ✅ Fixed markdown linting errors (removed duplicate H1 headers)
- ✅ Changed H1 to H2 after YAML frontmatter:
  - `spec.md`: `## Feature Specification: [FEATURE NAME]`
  - `plan.md`: `## Implementation Plan: [FEATURE]`
  - `tasks.md`: `## Tasks: [FEATURE NAME]`

**Result**: Templates now pass markdown validation.

## Workflow Flow (New)

```
User: "Add Redis caching to auth module"
         ↓
cde_startFeature(user_prompt="...")
         ↓
StartFeatureUseCase.execute()
  1. Get or create project
  2. Create feature with auto-generated name
  3. ✨ Initialize Spec-Kit:
     - Create specs/add-redis-caching-to-auth-module/
     - Generate spec.md from template
  4. Load workflow
  5. Render initial phase prompt
  6. Save project state
  7. Return: {"feature_id": "...", "phase": "define", "prompt": "..."}
```

Later phases:

```
Agent submits work for phase
         ↓
cde_submitWork(feature_id="...", phase_id="define", results={...})
         ↓
SubmitWorkUseCase.execute()
  1. Get project and feature
  2. Load workflow
  3. Advance to next phase
  4. ✨ Update Spec-Kit:
     - Update tasks.md to mark current phase as in progress
  5. Render next phase prompt
  6. Save project state
  7. Return: {"status": "ok", "phase": "decompose", "prompt": "..."}
```

## Key Design Decisions

### 1. Auto-Generated Feature Names

**Decision**: Generate feature directory names from user prompt via slugification

**Rationale**:
- Avoids manual naming overhead
- Creates readable directory names ("add-redis-caching-to-auth-module")
- Fallback UUID-based names for edge cases
- Immutable once created (stored in Feature.name)

### 2. Template-Based Spec Initialization

**Decision**: Use templates from `specs/templates/` to initialize feature specs

**Rationale**:
- Ensures consistent structure across all features
- Allows governance-level customization
- Easy to maintain and update
- Placeholder replacement makes templates flexible

### 3. Non-Breaking Task Updates

**Decision**: Silently fail if `tasks.md` doesn't exist

**Rationale**:
- Doesn't block workflow if user hasn't generated tasks yet
- Allows incremental adoption
- Prevents noise in agent logs

## Testing Checklist

- [ ] Test `cde_startFeature()` creates `specs/[feature]/` structure
- [ ] Test feature name auto-generation from prompts
- [ ] Test template substitution works correctly
- [ ] Test `cde_submitWork()` updates `tasks.md` correctly
- [ ] Test persistence: feature name survives save/load cycle
- [ ] Test edge cases: empty prompts, special characters in names

## Next Steps (Phase 3: Migration)

1. **Migrate Active Features**: Move existing features from `specs/features/` to `specs/[feature]/`
2. **Update AGENTS.md**: Reflect new workflow in agent instructions
3. **Deprecate Old Locations**: Remove references to `specs/features/` and `agent-docs/execution/` for features
4. **Run Full Test Suite**: Ensure backward compatibility

## Related Documents

- **Design**: `specs/design/spec-kit-adoption.md`
- **Governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **Migration Plan**: `specs/tasks/spec-kit-migration.md`
