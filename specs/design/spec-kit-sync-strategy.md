---
title: "Spec-Kit Template Synchronization Strategy"
description: "Hybrid Native-First approach for maintaining 100% Spec-Kit conformity"
type: "design"
status: "active"
created: "2025-11-25"
updated: "2025-11-25"
author: "CDE Orchestrator Team"
llm_summary: |
  Architectural strategy for synchronizing CDE templates with GitHub Spec-Kit.
  Uses hybrid approach: native generation (context-rich) + automated sync (conformity).
  Includes GitHub Actions workflow, customization scripts, and validation tools.
---

# Spec-Kit Template Synchronization Strategy

> **Decision**: Hybrid Native-First Approach
> **Status**: Approved for Implementation
> **Date**: 2025-11-25

---

## 🎯 Executive Summary

**Problem**: Mantener templates CDE 100% conformes con GitHub Spec-Kit sin perder capacidades context-aware de generación nativa.

**Solution**: Sistema de sincronización híbrido que:
1. **Genera specs nativamente** con contexto completo del proyecto
2. **Sincroniza templates automáticamente** desde upstream Spec-Kit
3. **Aplica customizaciones CDE** post-descarga
4. **Valida conformidad** en CI/CD

**Key Benefits**:
- ✅ 100% Spec-Kit conformity
- ✅ Zero external dependencies for users
- ✅ Automatic template updates
- ✅ Context-aware spec generation
- ✅ Extensible for CDE-specific features

---

## 📊 Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│  LAYER 1: MCP Tools (Native Generation - PRIMARY)           │
│  ✅ cde_generateSpec → Context-aware spec generation         │
│  ✅ cde_startFeature → Workflow orchestration               │
│  ✅ cde_submitWork   → Phase tracking                        │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│  LAYER 2: Sync & Validation (Conformity Assurance)          │
│  🆕 GitHub Actions → Weekly automatic sync from Spec-Kit     │
│  🆕 customize_templates.py → Apply CDE extensions            │
│  🆕 validate_spec_kit_conformity.py → Validate compliance   │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│  LAYER 3: Manual Tools (Optional - Power Users)             │
│  🆕 cde_syncTemplates → Manual sync trigger                 │
│  🆕 cde_validateSpec  → Validate generated specs             │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Design Decisions

### Decision 1: Native Generation as Primary Method

**Chosen**: Generate specs internally with `cde_generateSpec`

**Rationale**:
- **Context Advantage**: Access to full project analysis (files, architecture, patterns)
- **Zero Dependencies**: No need for users to install `specify-cli`
- **Performance**: In-process generation (1-2s) vs CLI invocation (5-10s)
- **Integration**: Seamless with CDE workflows

**Alternative Rejected**: Wrap `specify-cli` directly
- Would limit context to CLI inputs
- Requires `uv` + `specify-cli` installation
- Slower execution (subprocess overhead)
- Less control over customizations

---

### Decision 2: Automated Sync with Manual Trigger

**Chosen**: GitHub Actions weekly sync + manual `cde_syncTemplates` tool

**Rationale**:
- **Automation**: Spec-Kit updates captured without manual intervention
- **Review**: PRs ensure human review before applying changes
- **Flexibility**: Power users can trigger sync on-demand
- **Safety**: Validation step before merge

**Alternative Rejected**: Git submodules
- Complex for average users
- Manual update burden
- Submodule management issues

**Alternative Rejected**: Real-time webhooks
- Requires infrastructure (webhook receiver)
- Overkill for templates that change weekly/monthly
- More complexity than value

---

### Decision 3: Post-Download Customization

**Chosen**: Download pure Spec-Kit templates → Apply CDE customizations with script

**Rationale**:
- **Traceability**: Clear separation of upstream vs CDE-specific
- **Maintainability**: Easy to update CDE extensions independently
- **Conformity**: Base templates are 100% Spec-Kit standard
- **Extensibility**: Add/remove CDE features without breaking conformity

**Implementation**:
```python
# scripts/customize_templates.py
def customize_spec_template(upstream_content: str) -> str:
    """Apply CDE extensions to upstream Spec-Kit template."""
    # 1. Parse YAML frontmatter
    # 2. Add llm_summary field (CDE extension)
    # 3. Add MCP tools section (CDE extension)
    # 4. Add recipe suggestions (CDE extension)
    # 5. Preserve 100% Spec-Kit structure
    return customized_content
```

---

## 🛠️ Implementation Components

### Component 1: GitHub Actions Workflow

**File**: `.github/workflows/sync-spec-kit-templates.yml`

**Triggers**:
- Weekly schedule (Sunday 00:00 UTC)
- Manual workflow dispatch
- (Future) Repository dispatch from Spec-Kit releases

**Steps**:
```yaml
1. Download templates from github/spec-kit (raw.githubusercontent.com)
2. Apply CDE customizations (scripts/customize_templates.py)
3. Validate conformity (scripts/validate_spec_kit_conformity.py)
4. Create PR if changes detected (peter-evans/create-pull-request)
```

**Output**: PR titled "🔄 Sync Spec-Kit Templates" for human review

---

### Component 2: Customization Script

**File**: `scripts/customize_templates.py`

**Purpose**: Apply CDE-specific extensions while preserving Spec-Kit conformity

**Customizations Applied**:

| Template | CDE Extension | Rationale |
|----------|---------------|-----------|
| spec.md | `llm_summary` in YAML frontmatter | AI agent optimization |
| spec.md | **MCP Tools** section | Reference available tools |
| plan.md | **Hexagonal Architecture** section | CDE standard pattern |
| plan.md | **MCP Tool Patterns** section | Implementation guidelines |
| tasks.md | **Phase Tracking** section | CDE workflow integration |
| tasks.md | References to `cde_submitWork` | Tool usage examples |

**Example Output**:
```markdown
---
title: "Feature Specification: [FEATURE]"
# ... standard Spec-Kit frontmatter ...
llm_summary: |  # CDE EXTENSION
  Brief summary for AI agents. Includes user stories, requirements,
  and acceptance criteria in 2-3 sentences.
---

## ... Standard Spec-Kit Sections ...

## 🛠️ MCP Tools Available  <!-- CDE EXTENSION -->

For this feature, consider using:
- `cde_selectWorkflow` - Analyze complexity and recommend workflow
- `cde_sourceSkill` - Download relevant skills
- `cde_startFeature` - Initialize feature directory

... rest of template ...
```

---

### Component 3: Validation Script

**File**: `scripts/validate_spec_kit_conformity.py` (already exists, will enhance)

**Purpose**: Validate CDE templates against Spec-Kit standard

**Checks**:
1. **YAML Frontmatter**: Required fields present (title, description, type, status, created, updated, author)
2. **Section Structure**: All required sections present in correct order
3. **Naming Conventions**: File and directory names match Spec-Kit patterns
4. **Task Format**: Tasks follow `[ID] [P?] [Story] Description` format
5. **Link Integrity**: Internal links resolve correctly

**Output**: JSON report with conformity score (0-100)

**Usage in CI**:
```yaml
- name: Validate conformity
  run: |
    python scripts/validate_spec_kit_conformity.py \
      --templates specs/templates/ \
      --min-score 95 \
      --fail-on-low-score
```

---

### Component 4: MCP Tools (Manual Sync/Validation)

#### Tool: `cde_syncTemplates`

**Purpose**: Manual template synchronization for power users

**Parameters**:
- `project_path` (str): Path to project (default: ".")
- `force` (bool): Overwrite existing templates (default: False)
- `source` (str): Source repo URL (default: github/spec-kit)

**Example**:
```python
result = cde_syncTemplates(force=True)
# Downloads latest templates, applies customizations, validates
```

**Return**:
```json
{
  "status": "success",
  "templates_synced": ["spec.md", "plan.md", "tasks.md"],
  "customizations_applied": ["llm_summary", "mcp_tools_section"],
  "conformity_score": 97,
  "next_steps": ["Review changes in specs/templates/"]
}
```

---

#### Tool: `cde_validateSpec`

**Purpose**: Validate generated spec against Spec-Kit standard

**Parameters**:
- `spec_directory` (str): Path to feature spec directory
- `project_path` (str): Project root (default: ".")
- `strict` (bool): Fail on any conformity issue (default: False)

**Example**:
```python
result = cde_validateSpec("specs/add-redis-caching/")
# Checks spec.md, plan.md, tasks.md against standard
```

**Return**:
```json
{
  "status": "success",
  "conformity_score": 98,
  "issues": [
    "⚠️ spec.md: Optional section 'Non-Functional Requirements' missing"
  ],
  "passed_checks": [
    "✅ YAML frontmatter complete",
    "✅ Required sections present",
    "✅ Task format correct"
  ],
  "recommendations": [
    "Consider adding NFRs section for completeness"
  ]
}
```

---

## 📋 Workflow Examples

### Workflow 1: Standard Feature Development (No Manual Sync)

```
User → cde_selectWorkflow → cde_startFeature → cde_submitWork → Complete
          ↓                      ↓
     (uses internal        (uses synced
      templates)            templates)
```

**User Experience**:
1. User calls `cde_selectWorkflow("Add auth module")`
2. CDE recommends workflow + recipe
3. User calls `cde_startFeature(...)`
4. **Behind the scenes**: Uses latest synced templates from `specs/templates/`
5. Feature directory created with 100% Spec-Kit conformant files
6. User proceeds through phases with `cde_submitWork`

**No manual sync required** - templates are auto-updated weekly

---

### Workflow 2: Power User Manual Sync

```
User → cde_syncTemplates (force=True) → Review PR → Merge → Continue
```

**User Experience**:
1. Spec-Kit released new version this morning
2. Power user wants immediate update
3. Calls `cde_syncTemplates(force=True)`
4. Templates downloaded + customized + validated
5. PR auto-created for review
6. User reviews changes → merges → templates updated

---

### Workflow 3: Automated Weekly Sync (Background)

```
GitHub Actions (Weekly) → Download → Customize → Validate → Create PR
                                                               ↓
                                            Human Review → Merge
```

**No User Interaction** - happens automatically every Sunday

---

## 🔍 Validation Strategy

### Conformity Checks (CI/CD)

**When**: On every PR that modifies `specs/templates/`

**Checks**:
```yaml
- name: Validate Spec-Kit Conformity
  run: |
    python scripts/validate_spec_kit_conformity.py \
      --templates specs/templates/ \
      --reference /tmp/spec-kit/templates/ \
      --min-score 95 \
      --output conformity-report.json
```

**Blocking**: PR fails if conformity score < 95

---

### Customization Validation

**When**: After customization script runs

**Checks**:
1. **Idempotency**: Running customization twice produces same output
2. **Reversibility**: Can extract pure Spec-Kit template from customized one
3. **Conformity**: Customized template still passes validation
4. **No Breakage**: Existing features still work with new templates

---

## 📊 Success Metrics

### Conformity Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Conformity Score | 95%+ | TBD | ⏳ |
| Required Fields | 100% | TBD | ⏳ |
| Section Structure | 100% | TBD | ⏳ |
| Naming Conventions | 100% | TBD | ⏳ |

### Automation Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Weekly Sync Success Rate | 95%+ | ⏳ |
| PR Auto-Creation | 100% | ⏳ |
| Customization Script Success | 100% | ⏳ |
| Validation Script Accuracy | 100% | ⏳ |

### User Experience Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Manual Sync Usage | <5% features | ⏳ |
| Template Complaints | <1% users | ⏳ |
| Spec Generation Success | 100% | ⏳ |

---

## 🛡️ Risk Mitigation

### Risk 1: Spec-Kit Breaking Changes

**Probability**: Medium
**Impact**: High (breaks spec generation)

**Mitigation**:
- Automated tests catch breaking changes immediately
- PR review before merging upstream changes
- Rollback capability (git revert)
- Pin to last known good Spec-Kit version if needed

---

### Risk 2: Customization Script Fails

**Probability**: Low
**Impact**: Medium (PR not created, manual fix needed)

**Mitigation**:
- Comprehensive test suite for customization script
- Dry-run mode for testing without side effects
- Fallback to manual customization if script fails
- Alert on-call if automation fails

---

### Risk 3: Conformity Drift

**Probability**: Low
**Impact**: Medium (lose Spec-Kit compatibility)

**Mitigation**:
- CI validation on every PR
- Weekly conformity reports
- Automated alerts if score drops below 90%
- Quarterly manual audits

---

## 🚀 Implementation Plan

### Phase 1: Infrastructure (Week 1)

- [x] T004: Enhance `validate_spec_kit_conformity.py` (full validation)
- [ ] T005: Create `customize_templates.py` (apply CDE extensions)
- [ ] T006: Create GitHub Actions workflow (weekly sync)

### Phase 2: MCP Tools (Week 2)

- [ ] T007: Implement `cde_syncTemplates` tool
- [ ] T008: Implement `cde_validateSpec` tool
- [ ] T009: Update `cde_generateSpec` to use synced templates

### Phase 3: Documentation (Week 2)

- [ ] T009: Update `AGENTS.md` with new tools
- [ ] T009: Update `docs/configuration-guide.md`
- [ ] T009: Create user guide for manual sync

### Phase 4: Testing & Rollout (Week 3)

- [ ] T010: Run full dogfooding suite
- [ ] T010: Validate conformity score 95%+
- [ ] T010: Deploy to main branch
- [ ] T010: Monitor for issues

---

## 📖 References

### Upstream

- **Spec-Kit Repository**: https://github.com/github/spec-kit
- **Spec-Kit Documentation**: https://github.github.io/spec-kit/
- **Template Files**: https://github.com/github/spec-kit/tree/main/templates

### CDE Documentation

- **CDE Governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **CDE Architecture**: `specs/design/architecture/README.md`
- **Dogfooding Plan**: `specs/cde-dogfooding-feedback/spec.md`

### Tools

- **GitHub Actions**: https://docs.github.com/en/actions
- **create-pull-request**: https://github.com/peter-evans/create-pull-request

---

## 📝 Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-25 | Hybrid Native-First Approach | Balance context-awareness with conformity |
| 2025-11-25 | Weekly automated sync | Spec-Kit changes infrequently, weekly is sufficient |
| 2025-11-25 | Post-download customization | Clear separation of upstream vs CDE-specific |
| 2025-11-25 | PR-based review | Human oversight before template changes |

---

## ✅ Approval

**Approved By**: CDE Team
**Date**: 2025-11-25
**Status**: Ready for Implementation

---

**Next Steps**:
1. Review this document with stakeholders
2. Proceed with Phase 1 implementation
3. Run dogfooding validation (T010)
4. Deploy to production

---

**Last Updated**: 2025-11-25
**Version**: 1.0
**Document Owner**: CDE Orchestrator Team
