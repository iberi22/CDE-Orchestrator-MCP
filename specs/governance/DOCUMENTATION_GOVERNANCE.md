# Documentation Governance Framework

> **Purpose**: Establish rules and patterns for systematic documentation organization
> **Status**: Active
> **Last Updated**: 2025-01-11
> **Owner**: CDE Orchestrator Team

---

## 🎯 Overview

This document defines governance rules for documentation in the CDE Orchestrator MCP project. The goal is to:

- ✅ Maintain a **single source of truth** for all documentation
- ✅ Prevent **documentation sprawl** (random .md files across repo)
- ✅ Establish **clear ownership** of each document
- ✅ Enable **automated enforcement** through pre-commit hooks
- ✅ Provide **clear guidelines** for AI agents and humans

---

## 📍 Core Principle: Single Source of Truth

**The Rule**: All markdown documentation must reside in designated locations according to its purpose.

No `.md` files are allowed in the root of the repository **except** project-level metadata:

```
❌ NOT ALLOWED (Root level):
- RANDOM_THOUGHTS.md
- SESSION_NOTES.md
- ANALYSIS.md
- TEMP_SUMMARY.md

✅ ALLOWED (Root level only):
- README.md (Project identity)
- CHANGELOG.md (Version history)
- CONTRIBUTING.md (Contribution guidelines)
- CODE_OF_CONDUCT.md (Community standards)
- LICENSE (Legal)
```

---

## 📂 Directory Structure & Rules

### 1. **`/specs/features/`** - Feature Specifications

**Purpose**: Document user-facing features and requirements
**Ownership**: Feature authors
**Pattern**: `feature-<feature_name>.md` or `<feature_name>.md`

**Examples**:
- `specs/features/user-authentication.md`
- `specs/features/multi-project-management.md`
- `specs/features/integrated-management-system.md`

**Rule**: Every new feature **must** start with a spec in this directory before any code is written.

---

### 2. **`/specs/design/`** - Technical Designs & Architecture

**Purpose**: Document internal implementation, architecture decisions, technical approaches
**Ownership**: Technical leads / architects
**Pattern**: `<domain>-<decision>.md` or `<architecture_topic>.md`

**Examples**:
- `specs/design/hexagonal-architecture.md`
- `specs/design/dynamic-skill-system.md`
- `specs/design/smart-reuse-strategy.md`
- `specs/design/ephemeral-skill-reuse.md`

**Rule**: Major design decisions **must** be documented with:
- Problem statement
- Proposed solution
- Trade-offs considered
- Implementation approach
- Metrics for success

---

### 3. **`/specs/tasks/`** - Task Management & Roadmaps

**Purpose**: Track project roadmap and work breakdown
**Ownership**: Project managers
**Pattern**: `<type>-roadmap.md` or `<milestone>-tasks.md`

**Examples**:
- `specs/tasks/improvement-roadmap.md` (Quarterly priorities)
- `specs/tasks/phase-1-implementation.md` (Phase breakdown)
- `specs/tasks/research-tasks.md` (R&D activities)

**Rule**: Large initiatives must have a task breakdown linking to features and designs.

---

### 4. **`/specs/governance/`** - Process & Governance

**Purpose**: Document how the project operates, rules, processes
**Ownership**: Technical steering committee
**Pattern**: `<process>-governance.md`

**Examples**:
- `specs/governance/DOCUMENTATION_GOVERNANCE.md` (This file)
- `specs/governance/code-review-guidelines.md`
- `specs/governance/decision-making-process.md`

**Rule**: All governance documents must be reviewable and follow semantic versioning.

---

### 5. **`/agent-docs/`** - Agent-Generated Documentation 🆕

**Purpose**: Store transitory agent outputs (session summaries, execution reports, feedback, research)
**Ownership**: AI agents (automated)
**Pattern**: `<category>/<type>-<topic>-<YYYY-MM>.md`
**Lifecycle**: Preserved indefinitely, except `research/` (auto-archived after 90 days)

**Subdirectories**:

1. **`agent-docs/sessions/`** - Session summaries
   - Pattern: `session-<topic>-<YYYY-MM-DD>.md`
   - Example: `session-onboarding-review-2025-01-15.md`

2. **`agent-docs/execution/`** - Workflow execution reports
   - Pattern: `execution-<workflow>-<YYYY-MM-DD>.md`
   - Example: `execution-onboarding-2025-01.md`

3. **`agent-docs/feedback/`** - Analysis and recommendations
   - Pattern: `feedback-<topic>-<YYYY-MM>.md`
   - Example: `feedback-governance-improvements-2025-01.md`

4. **`agent-docs/research/`** - Web research summaries
   - Pattern: `research-<topic>-<YYYY-MM-DD>.md`
   - Example: `research-best-practices-2025-01-10.md`
   - **Special**: Auto-archived to `agent-docs/research/archived/` after 90 days

**Naming Patterns**:
- Date format: ISO 8601 (`YYYY-MM-DD` or `YYYY-MM`)
- Lowercase with hyphens
- Topic descriptors: specific and searchable (e.g., `governance-improvements` not `fixes`)

**Rules for AI Agents**:
- ✅ **DO**: Place session summaries in `agent-docs/sessions/`
- ✅ **DO**: Use templates from `specs/templates/` (session-summary.md, execution-report.md, feedback-report.md)
- ✅ **DO**: Include metadata block (date, agent, duration, status)
- ✅ **DO**: Link to source code/specs with absolute paths
- ❌ **DON'T**: Create .md files in project root (use appropriate subdirectory)
- ❌ **DON'T**: Mix permanent specs with transitory reports
- ❌ **DON'T**: Use vague names (`REPORT.md` → `feedback-multi-project-analysis-2025-01.md`)

**Example Metadata**:
```yaml
---
date: 2025-01-15
agent: KERNEL v3.1
duration: 2h 30m
status: completed
related_tasks: [TASK-001, TASK-042]
---
```

**Migration from Root**: Legacy reports (EXECUTION_REPORT.md, ONBOARDING_REVIEW_REPORT.md) must be moved to agent-docs/ with `git mv` to preserve history.

---

### 6. **`/docs/`** - User-Facing Documentation

**Purpose**: External documentation for end users
**Ownership**: Documentation team
**Pattern**: Organized by section

**Examples**:
- `docs/user-guide/getting-started.md`
- `docs/api-reference/endpoints.md`
- `docs/troubleshooting/common-issues.md`

**Rule**: User docs must be reviewed before deployment.

---

### 6. **`/.cde/`** - Workflow & Automation

**Purpose**: CDE workflow definitions, prompts, recipes
**Ownership**: Workflow engineers
**Pattern**: YAML workflows, POML prompts, JSON recipes

**Examples**:
- `.cde/workflow.yml`
- `.cde/prompts/01_define.poml`
- `.cde/recipes/research.json`

---

### 7. **`/memory/`** - Project Constitution & Principles

**Purpose**: Document project values, decision-making philosophy
**Ownership**: Founding team
**Pattern**: Single canonical file

**Examples**:
- `memory/constitution.md` (Project principles)

**Rule**: Constitution is immutable except by unanimous consent.

---

## ⚠️ Exceptions & Special Cases

### When can .md files exist in root?

1. **Project Metadata** (Auto-generated or standards):
   - `README.md` - Project identity & quickstart
   - `CHANGELOG.md` - Version history
   - `CONTRIBUTING.md` - How to contribute
   - `CODE_OF_CONDUCT.md` - Community values
   - `LICENSE` / `LICENSE.md` - Legal

2. **Never in root** (Always moved):
   - Summary documents from design sessions → `specs/design/`
   - Task breakdowns → `specs/tasks/`
   - Feature ideas → `specs/features/`
   - Meeting notes → Move to feature/task after 24 hours
   - Investigation results → `specs/design/research/`

### Temporary Documents?

**Rule**: No temporary .md files that bypass this structure.

If you need to capture session notes:
1. **During session**: Use inline comments in code/spec
2. **After session**: Distill into appropriate spec/design/task files within 24 hours
3. **Keep reference**: Link from summary docs if context is valuable

---

## 🤖 Rules for AI Agents (LLMs/Copilot)

When agents (including GitHub Copilot) create documentation:

### ✅ DO:
- Ask: "Is this a feature spec, design doc, or process guideline?"
- Check existing structure for similar documents
- Place files in the correct directory from the start
- Link files using relative paths for navigation
- Include clear ownership and update dates

### ❌ DON'T:
- Create `.md` files in root directory
- Create `SUMMARY.md`, `REVIEW.md`, `NOTES.md` files anywhere
- Bypass the directory structure "for convenience"
- Auto-delete or replace governance files
- Create documents without context about their purpose

### 📋 Checklist for AI Doc Generation:

```markdown
[ ] Purpose of document identified (feature/design/task/governance)
[ ] Correct directory selected per rules above
[ ] File naming convention followed
[ ] Ownership specified (who maintains?)
[ ] Update date included
[ ] Linked to related documents
[ ] Pre-commit hook would approve this location
```

---

## 🔧 Enforcement Mechanism

### Pre-Commit Hook

A local pre-commit hook (`.git/hooks/pre-commit`) prevents commits with violations:

```bash
#!/bin/bash
# Reject .md files in disallowed root locations

DISALLOWED_MD_PATTERNS=(
  "^[A-Z_]*_[A-Z_]*\.md$"           # SCREAMING_SNAKE_CASE (likely temp notes)
  "^SESSION.*\.md$"                  # SESSION_*.md
  "^MEETING.*\.md$"                  # MEETING_*.md
  "^SUMMARY.*\.md$"                  # SUMMARY_*.md
  "^REVIEW.*\.md$"                   # REVIEW_*.md
  "^NOTES.*\.md$"                    # NOTES_*.md
)

# Exception list (always allowed in root)
ALLOWED_ROOT=(
  "README.md"
  "CHANGELOG.md"
  "CONTRIBUTING.md"
  "CODE_OF_CONDUCT.md"
)

# Check staged files
for file in $(git diff --cached --name-only); do
  if [[ "$file" == *.md && "$file" != */* ]]; then
    filename=$(basename "$file")

    # Check if in allowed list
    if [[ ! " ${ALLOWED_ROOT[@]} " =~ " ${filename} " ]]; then
      echo "❌ ERROR: $file cannot be created in root"
      echo "   Move to: specs/features/, specs/design/, specs/tasks/, or specs/governance/"
      exit 1
    fi
  fi
done

exit 0
```

### Markdown Linting

Additional rules in `.markdownlintrc` enforce consistency:

```json
{
  "MD041": false,  // Don't require H1 (specs use H2+)
  "MD013": { "line_length": 100 },  // Line length limit
  "MD032": true,   // Lists must be surrounded by blanks
  "MD040": true    // Fenced code blocks must have language
}
```

---

## 📊 Document Lifecycle

Every documentation artifact should follow this lifecycle:

```
┌─────────────────────────────────────────────────────┐
│ 1. INITIATE (Purpose identified)                    │
│    └─ Developer/AI identifies need for doc          │
│    └─ Determines purpose (feature/design/task)      │
└────────────────────┬────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────────┐
│ 2. CREATE (In correct location)                     │
│    └─ Create in specs/{features,design,tasks}       │
│    └─ Follow naming convention                      │
│    └─ Include metadata (owner, date, purpose)       │
└────────────────────┬────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────────┐
│ 3. REVIEW (Governance check)                        │
│    └─ Pre-commit hook validates location            │
│    └─ Linter validates formatting                   │
│    └─ Peer review for content                       │
└────────────────────┬────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────────┐
│ 4. PUBLISH (Merge & notify)                         │
│    └─ Merge to main branch                          │
│    └─ Update DOCUMENT_INDEX_V2.md if major          │
│    └─ Notify team in #docs channel                  │
└────────────────────┬────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────────┐
│ 5. MAINTAIN (Regular updates)                       │
│    └─ Update date when modified                     │
│    └─ Keep links working                            │
│    └─ Archive obsolete docs (no delete!)            │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Migration & Cleanup

### For Existing Violations

If root-level .md files exist that violate these rules:

1. **Identify**: `find . -maxdepth 1 -name "*.md" -type f`
2. **Classify**: Is it feature/design/task/governance?
3. **Move**: To appropriate `specs/*/` directory
4. **Update references**: In README.md and docs
5. **Archive**: Keep git history (don't delete, move)

### Deprecation Process

For documents being replaced:

```
OLD: `specs/design/old-approach.md`
NEW: `specs/design/new-approach.md`

In NEW file, add at top:
<!-- markdownlint-disable-file -->
**Supersedes**: old-approach.md (See git history)
**Reason**: New requirements changed approach
```

---

## 📚 Navigation & Discoverability

To help users find documentation:

1. **Index File**: `specs/DOCUMENT_INDEX_V2.md` (regularly updated)
2. **README**: Root README.md links to specs/ for detailed docs
3. **Breadcrumbs**: Each spec includes "See also:" linking to related docs
4. **Hierarchy**: Structure reflects project organization

---

## 🚀 Implementation Timeline

**Phase 1 (Now)**: Document this governance framework
- [ ] Create `specs/governance/DOCUMENTATION_GOVERNANCE.md` ✅ (THIS FILE)
- [ ] Create `.markdownlintrc` with rules
- [ ] Create pre-commit hook

**Phase 2 (Week 1)**: Enforce with tooling
- [ ] Install pre-commit framework
- [ ] Run against all current .md files
- [ ] Fix any violations

**Phase 3 (Week 2)**: Team adoption
- [ ] Train team on new structure
- [ ] Update agent instructions
- [ ] Monitor for exceptions

**Phase 4 (Ongoing)**: Maintenance
- [ ] Monthly review of structure
- [ ] Update docs as project evolves
- [ ] Refine rules based on feedback

---

## ❓ FAQ

### Q: Can I create a summary document after a design session?
**A**: Store the **summary in the design spec itself**, not as a separate file. If it's too long, break into multiple design docs in `specs/design/`.

### Q: What about temporary research notes?
**A**: Use a comment in the spec: `<!-- Research notes: ... -->`. After 24 hours, either integrate into the spec or move to `specs/design/research/`.

### Q: Can I have a doc in both `/docs` and `specs/`?
**A**: No. Use DRY principle:
- Source of truth in `specs/design/` or `specs/features/`
- Generate user docs in `/docs/` from specs (or link)

### Q: Who enforces these rules?
**A**: The pre-commit hook enforces automatically. If hook is bypassed (`--no-verify`), code review catches it.

### Q: What if a rule doesn't fit my case?
**A**: Open an issue in `specs/governance/` directory for discussion. Rules can evolve with consensus.

---

## 📖 Related Documents

- **`memory/constitution.md`** - Project principles (includes documentation values)
- **`specs/design/hexagonal-architecture.md`** - How components organize (inspired this structure)
- **`.github/copilot-instructions.md`** - Agent guidelines (references this governance)
- **`CONTRIBUTING.md`** - Root-level contributor guide (links to this framework)

---

## ✍️ Amendment History

| Date | Change | Author |
|------|--------|--------|
| 2025-01-11 | Initial framework created | AI Agent (KERNEL) |
| (Future) | Rule additions | (TBD) |

---

**Signed**: CDE Orchestrator Governance Committee
**Status**: 🟢 **Active & Enforced**
**Review Date**: Quarterly
