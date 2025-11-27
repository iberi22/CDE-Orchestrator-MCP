---
title: "Legacy Features Directory"
description: "Old feature specification structure (DEPRECATED)"
type: "guide"
status: "deprecated"
created: "2025-11-23"
updated: "2025-11-23"
author: "CDE Team"
llm_summary: |
  Legacy feature directory (specs/features/).
  DEPRECATED in favor of Spec-Kit structure (specs/[feature-name]/).
  Contains archived proposals and migrated features.
---

# Legacy Features Directory (DEPRECATED)

**Status**: ⚠️ **DEPRECATED** (2025-11-23)

**New Standard**: Use `specs/[feature-name]/` structure with Spec-Kit files (spec.md, plan.md, tasks.md)

**Migration Date**: 2025-11-23 (Phase 3 of Spec-Kit adoption)

---

## Migration Status

| Feature | Priority | Status | New Location |
|---------|----------|--------|--------------|
| **ai-assistant-config** | 🔴 HIGH | ✅ MIGRATED | `specs/ai-assistant-config/` |
| **onboarding-system** | 🔴 HIGH | ✅ MIGRATED | `specs/onboarding-system/` |
| **python-314-migration** | 🟡 MEDIUM | ⏸️ IN PROGRESS | (80% complete, not migrated) |
| **server-refactoring-modular** | 🟡 MEDIUM | ⏸️ PENDING | (not yet implemented) |
| **amazon-q-integration** | 🟡 MEDIUM | ⏸️ PENDING | (proposal, not implemented) |
| **advanced-research-features** | 🟢 LOW | 📦 ARCHIVED | (proposal, no implementation) |
| **integrated-management-system** | 🟢 LOW | 📦 ARCHIVED | (conceptual, superseded) |
| **onboarding-performance-enhancement** | 🟢 LOW | 📦 ARCHIVED | (proposal, not needed) |
| **user-authentication** | 🟢 LOW | 📦 ARCHIVED | (example/template) |

---

## For New Features

**❌ DON'T**: Create `.md` files in `specs/features/`

**✅ DO**: Use MCP tool to create Spec-Kit structure:

```python
# Agent calls MCP tool
cde_startFeature(
    user_prompt="Add OAuth2 authentication",
    workflow_type="standard"
)

# MCP auto-creates:
# specs/oauth2-authentication/
# ├── spec.md      (PRD)
# ├── plan.md      (technical design)
# └── tasks.md     (executable checklist)
```

**Manual Creation** (if MCP unavailable):

```bash
# 1. Create directory
mkdir specs/my-feature-name/

# 2. Copy templates
cp specs/templates/spec.md specs/my-feature-name/spec.md
cp specs/templates/plan.md specs/my-feature-name/plan.md
cp specs/templates/tasks.md specs/my-feature-name/tasks.md

# 3. Edit placeholders
# Replace [FEATURE NAME], [DATE], [AUTHOR] in all 3 files
```

---

## Archived Features (LOW Priority)

These features are **proposals or examples** with no implementation. Kept for reference only.

### 1. advanced-research-features.md

**Status**: 📦 ARCHIVED (proposal)

**Reason**: No implementation, low priority, may revisit in future

**Content**: Research-focused features (web scraping, paper analysis, etc.)

### 2. integrated-management-system.md

**Status**: 📦 ARCHIVED (conceptual)

**Reason**: Superseded by current CDE architecture, no longer relevant

**Content**: Project management system integration

### 3. onboarding-performance-enhancement.md

**Status**: 📦 ARCHIVED (proposal)

**Reason**: Current onboarding (<5s) already meets requirements

**Content**: Performance optimization ideas for onboarding system

### 4. user-authentication.md

**Status**: 📦 ARCHIVED (example)

**Reason**: Template/example feature, not needed for MCP server

**Content**: User authentication system (not applicable to CLI/MCP)

---

## Pending Migrations (MEDIUM Priority)

These features may be migrated to Spec-Kit structure in future sessions.

### 1. python-314-migration.md

**Status**: ⏸️ IN PROGRESS (80% complete)

**Implementation**: Partial (tests passing on 3.14)

**Next**: Complete migration, create Spec-Kit docs

### 2. server-refactoring-modular.md

**Status**: ⏸️ PENDING (not yet implemented)

**Implementation**: None (design proposal)

**Next**: Evaluate priority, implement if needed

### 3. amazon-q-integration.md

**Status**: ⏸️ PENDING (proposal)

**Implementation**: None (proposal for future AI assistant)

**Next**: Assess demand, low priority

---

## Governance

**Reference**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`

**Rule**: `specs/features/` is DEPRECATED for new features (Section 2)

**Enforcement**: Pre-commit hooks warn on new files in `specs/features/`

**Exception**: Existing files remain for reference (not deleted)

---

## Migration History

**Phase 1** (2025-11-02): Governance update, templates created

**Phase 2** (2025-11-02): Tooling updated (cde_startFeature, entities, use cases)

**Phase 3** (2025-11-23): Feature migration (ai-assistant-config, onboarding-system)

**Phase 4** (TBD): Archive LOW priority, migrate remaining MEDIUM priority

---

**For More Info**: See `specs/governance/DOCUMENTATION_GOVERNANCE.md`
