---
title: "Mypy Type Annotation Errors - Tracking & Analysis"
description: "Comprehensive tracking of 100+ mypy type annotation errors across codebase"
type: "feedback"
status: "active"
created: "2025-11-11"
updated: "2025-11-11"
author: "GitHub Copilot"
llm_summary: |
  Tracking document for 100+ mypy errors blocking type-safe development.
  Categorized by severity and file. Ready for systematic fixing in dedicated PR.
---

## Overview

**Status**: ⚠️ Type checking disabled in CI (SKIP=mypy)
**Impact**: Reduces type safety, but doesn't block deployment
**Priority**: Medium (nice to have, not critical)
**Effort**: 2-3 days systematic fixing

---

## Error Categories (100+ total)

### 1. Missing Return Type Annotations (30+)

**Severity**: 🟡 Medium
**Fix Pattern**: Add `-> ReturnType` to function signatures

Files affected:

- src/cde_orchestrator/ui/system_notifications.py:35 (15 functions)
- src/cde_orchestrator/adapters/service/service_adapter.py (8 functions)
- scripts/validation/enforce-doc-governance.py
- scripts/validation/validate-metadata.py
- scripts/validation/validate-docs.py
- scripts/orchestration/mcp-configure-jules-consolidation.py
- scripts/metadata/fix-document-types.py
- scripts/migration/rename-execution-files.py
- scripts/setup/configure_agents.py
- scripts/setup/bedrock_setup.py
- scripts/progress_tracker.py

**Example Fix**:

```python
# BEFORE
def send_notification(title, message):
    pass

# AFTER
def send_notification(title: str, message: str) -> None:
    pass
```

### 2. Missing Argument Type Annotations (25+)

**Severity**: 🟡 Medium

Fix types for all parameters in these files:

- src/cde_orchestrator/domain/ports.py:139
- src/cde_orchestrator/application/onboarding/project_analysis_use_case.py:57
- src/cde_orchestrator/application/documentation/analyze_documentation_use_case.py:90
- src/cde_orchestrator/application/orchestration/web_research_use_case.py:96
- scripts/validation/validate-docs.py:138
- scripts/jules_monitor.py:12

### 3. Missing Library Stubs (10+)

**Severity**: 🔴 High

Install stub packages:

- `pip install types-PyYAML`
- `pip install types-requests`

Files needing stubs:

- src/cde_orchestrator/application/documentation/create_specification_use_case.py
- src/cde_orchestrator/adapters/workflow/workflow_adapter.py
- src/cde_orchestrator/infrastructure/dependency_injection.py
- scripts/metadata/fix-document-types.py
- scripts/metadata/add-metadata.py
- scripts/validation/validate-metadata.py
- scripts/validation/validate-docs.py
- scripts/consolidation/weekly-cleanup-with-grok.py
- tests/test_workflow_manager.py

### 4. Type Compatibility Issues (20+)

**Severity**: 🟡 Medium

Fix type hints where object/Collection types don't support list methods:

- src/cde_orchestrator/application/onboarding/onboarding_use_case.py (Lines 55-70)
- src/cde_orchestrator/application/documentation/scan_documentation_use_case.py (Lines 134-270)
- src/cde_orchestrator/adapters/service/service_adapter.py (Line 284)
- src/cde_orchestrator/adapters/agents/multi_agent_orchestrator.py (Line 247)
- src/cde_orchestrator/domain/documentation/entities.py (Line 113)

### 5. Optional Type Issues (15+)

**Severity**: 🟡 Medium

Add Optional annotations for arguments defaulting to None:

- src/cde_orchestrator/adapters/agents/agent_selection_policy.py:185
- src/cde_orchestrator/adapters/agents/multi_agent_orchestrator.py:267
- src/mcp_tools/_progress_reporter.py:68

### 6. Attribute or Method Name Errors (8+)

**Severity**: 🟡 Medium

Fix typos in attribute names (Jules vs Julius):

- scripts/orchestration/mcp-configure-jules-consolidation.py:79
- scripts/orchestration/mcp-configure-jules-consolidation.py:134
- scripts/orchestration/mcp-configure-jules-consolidation.py:254
- scripts/orchestration/mcp-configure-jules-consolidation.py:290
- scripts/orchestration/mcp-configure-jules-consolidation.py:331
- scripts/orchestration/mcp-configure-jules-consolidation.py:350

### 7. Variable Annotation Issues (8+)

**Severity**: 🟡 Medium

Add explicit type hints for local variables:

- src/cde_orchestrator/application/documentation/analyze_documentation_use_case.py:153
- src/cde_orchestrator/application/orchestration/web_research_use_case.py:478
- src/cde_orchestrator/application/ai_config/ai_config_use_case.py:187
- scripts/validation/validate-docs.py:247
- scripts/validation/validate-docs.py:459

### 8. Return Value Type Mismatches (5+)

**Severity**: 🟡 Medium

Ensure return types match function declarations:

- tests/performance/benchmark_scan_docs.py:41
- tests/performance/benchmark_scan_docs.py:44
- src/cde_orchestrator/adapters/service/service_adapter.py:562
- scripts/consolidation/weekly-cleanup-with-grok.py:143

---

## Recommended Fix Strategy

Phase 1 (Quick Wins): Fix typos and install stubs (1 day)

- Fix attribute name typos in scripts/orchestration/ (8 errors)
- Install: `pip install types-PyYAML types-requests`

Phase 2 (Low-Hanging Fruit): Missing annotations (1 day)

- Add missing return annotations to scripts/ (15+ functions)
- Add missing argument type annotations (25+)
- Fix Optional type issues (15+)

Phase 3 (Complex Fixes): Type compatibility (1 day)

- Fix use_cases with untyped list/dict variables
- Add proper type guards and conversions
- Fix variable annotations (8+)

Phase 4 (Verification): Run mypy check (1 hour)

- Run: `mypy src/ --strict-optional`
- Remove `SKIP=mypy` from CI workflow
- Target: < 10 errors in main codebase

---

## Acceptance Criteria

Completed when:

- Less than 10 mypy errors in src/ directory
- All library stubs installed and configured
- Mypy enabled in CI pipeline (no skip)
- CI passes with mypy check enabled

---

## Low Priority Tasks

Items that can be deferred:

- Bare `# noqa: E402` in test files (needed for sys.path)
- Type stubs for internal modules (optional optimization)
