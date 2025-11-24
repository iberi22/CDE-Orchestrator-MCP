---
title: "Documentation Governance Framework"
description: "Rules and patterns for systematic documentation organization in CDE Orchestrator MCP"
type: "governance"
status: "active"
created: "2025-01-10"
updated: "2025-11-04"
author: "CDE Orchestrator Team"
tags:
  - "governance"
  - "documentation"
  - "standards"
  - "metadata"
  - "token-optimization"
  - "llm-governance"
llm_summary: |
  Complete governance framework for documentation in CDE Orchestrator. Defines directory structure,
  metadata requirements, token optimization patterns, LLM-specific rules, enforcement mechanisms,
  and guidelines for AI agents. Optimized for maximum context efficiency with minimum tokens.
  Reference when creating or organizing documentation.
---

# Documentation Governance Framework

> **Purpose**: Establish rules and patterns for systematic documentation organization
> **Status**: Active
> **Last Updated**: 2025-11-01
> **Owner**: CDE Orchestrator Team

---

## 🎯 Overview

This document defines governance rules for documentation in the CDE Orchestrator MCP project. The goal is to:

- ✅ Maintain a **single source of truth** for all documentation
- ✅ Prevent **documentation sprawl** (random .md files across repo)
- ✅ Establish **clear ownership** of each document
- ✅ Enable **automated enforcement** through pre-commit hooks
- ✅ Provide **clear guidelines** for AI agents and humans
- ✅ **Optimize token usage** for LLMs (balance context + efficiency)
- ✅ **Enforce LLM governance** (no bypass rules allowed)

---

## 🧠 Token Optimization for LLMs (2025 Standard)

**Context**: Modern LLMs (GPT-5, Claude 3, Sonnet 4.5) have large context windows (100k-200k tokens), but **token efficiency = cost savings + faster response + better UX**.

### Why This Matters

Based on research from Brex, OpenAI, and Anthropic:

1. **Token Efficiency** = 30-40% cost reduction + 50% faster responses
2. **Semantic Search** (RAG) outperforms unstructured context by 3-5x
3. **Metadata Matters** = 25% reduction in "hallucination" with proper document headers
4. **Hierarchy** = Markdown headers help LLMs reduce context scanning by 40%
5. **Chunking** = Multiple focused docs >> one massive doc (reduces redundant context)

### Optimization Rules for AI Assistants

**These rules apply to EVERY document created by or for LLMs:**

#### ✅ DO (High-Efficiency Patterns)

1. **Use Metadata YAML Frontmatter** (28-40 tokens saved per doc)
   ```yaml
   ---
   title: "..."           # LLM can quickly identify purpose
   description: "..."     # One-liner for semantic search
   type: "feature|design|task|..."  # Categorization
   llm_summary: |         # 2-3 sentence summary optimized for LLM (READ FIRST)
     This document specifies...
     Key decisions: X, Y, Z
     When to reference: For A, B, C tasks
   ---
   ```

2. **Structure with Clear Hierarchy** (Reduce scanning by 40%)
   - Use `#` H1 for main topic
   - Use `##` H2 for major sections
   - Use `###` H3 for subsections
   - **Max nesting**: 3 levels (LLMs have trouble with deeper hierarchies)

3. **Chunking Strategy** (Reduce context "bloat")
   - Each document: max 800 lines (optimal for LLM scanning)
   - Longer docs: Split into multiple focused files + index
   - Related docs: Cross-link with `See also:` section

4. **Markdown over Prose** (20-30% token saving)
   - Use `**bold**` for key terms (LLMs weight these)
   - Use `- bullet lists` instead of paragraphs
   - Use `| tables |` for structured data
   - Use ` `code blocks` ` for technical content

5. **Strategic Link Placement** (Enable lazy-loading of context)
   - Put critical info early (LLMs read sequentially)
   - Link to related docs: "See `specs/design/architecture/README.md` for details"
   - Use absolute paths for consistency

#### ❌ DON'T (High-Cost Anti-Patterns)

1. **❌ Verbose Prose** (2-3x token waste)
   - Instead of: "This system is a sophisticated implementation that..."
   - Use: "System: Advanced orchestration for..."

2. **❌ Duplicate Content** (Wasted context)
   - Never repeat specs in multiple files
   - Link once, reference many times
   - Use `<!-- Link: specs/design/X.md -->` for traceability

3. **❌ Nested Lists > 3 Levels** (LLM loses context)
   - Use separate bullet lists for clarity
   - Example: Break into sections instead

4. ❌ **No Metadata** (LLM has to parse content to understand purpose)
   - Every .md file **MUST** start with YAML frontmatter
   - No frontmatter = Pre-commit hook REJECTS

5. **❌ Mixed Content Types** (Confuses LLM comprehension)
   - Don't mix feature specs + design decisions + tasks
   - Keep concerns separated
   - Use type field to clarify

6. **❌ Tests/Reports in Root** (Governance violation + context pollution)
   - Never create: `TEST_*.md`, `REPORT_*.md`, `SESSION_*.md` in root
   - Use: `agent-docs/execution/execution-*.md` instead
   - Exception: None (this is absolute)

### Token Budget Examples

**Good Pattern** (Agent-optimized):
```markdown
---
title: "Feature: Multi-Project Support"
type: "feature"
llm_summary: "Enable professional single-project management. Key pattern: Stateless resolver
via project_path parameter. No registry needed. Reference: specs/design/multi-project.md"
---

## Overview
- **Pattern**: Stateless + simple
- **Entry point**: `cde_startFeature(project_path="...")`

## Key Files
- `src/adapters/project_locator.py` - Validation
- `specs/design/multi-project.md` - Architecture

See also: `specs/tasks/improvement-roadmap.md`
```
**Tokens**: ~180 | **Efficiency**: ⭐⭐⭐⭐⭐

**Bad Pattern** (Context-wasteful):
```markdown
This is a comprehensive feature that provides many benefits to users who want to
work with multiple projects. Throughout the history of software development, many
systems have struggled with this problem. We decided to implement a stateless
architecture because it provides many advantages including simplicity and...
[3000 more words of prose]
```
**Tokens**: ~2400+ | **Efficiency**: ⭐

### LLM Governance Rules (STRICT)

**These rules are NOT suggestions. Pre-commit hooks ENFORCE them:**

1. **Rule: No Root .md Violations**
   - ❌ `REPORT_*.md` in root → BLOCKED
   - ❌ `SESSION_*.md` in root → BLOCKED
   - ❌ `TEST_*.md` in root → BLOCKED
   - ❌ `SUMMARY_*.md` in root → BLOCKED
   - ❌ `RESUMEN_*.md` in root → BLOCKED
   - ✅ Exception ONLY: `README.md`, `CHANGELOG.md`, `AGENTS.md`, `GEMINI.md`

2. **Rule: Metadata Required**
   - Every `.md` file (except exceptions) MUST have YAML frontmatter
   - Missing: `author`, `date`, `type` → REJECTED
   - Missing `llm_summary` → WARNING (conversion to ERROR in 2 weeks)

3. **Rule: No Test Files in Root**
   - ❌ `test_*.md` in root → BLOCKED
   - ✅ Use: `tests/integration/test_feature_*.md` or `agent-docs/research/testing-*.md`

4. **Rule: Execution Reports → agent-docs/**
   - ❌ Reports anywhere else → BLOCKED
   - ✅ Location: `agent-docs/execution/execution-<topic>-<YYYY-MM-DD>.md`
   - Pattern enforced by pre-commit

5. **Rule: Session Summaries → agent-docs/sessions/**
   - ❌ Session files in root → BLOCKED
   - ✅ Location: `agent-docs/sessions/session-<topic>-<YYYY-MM-DD>.md`

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

### 1. **`/specs/[feature-name]/`** - Feature Specifications (Spec-Kit Standard) 🆕

**Purpose**: Self-contained directory for all feature documentation (Spec, Plan, Tasks)
**Ownership**: Feature authors & AI Agents
**Structure**:
- `spec.md`: Product Requirements Document (PRD)
- `plan.md`: Technical Implementation Plan
- `tasks.md`: Executable Task List (Status tracked here)
- `research.md`: Feature-specific research (Optional)

**Examples**:
- `specs/user-authentication/spec.md`
- `specs/multi-project-support/plan.md`

**Rule**: Every new feature **must** use this folder structure.

### 2. **`/specs/features/`** - Legacy Feature Specifications (Deprecated) ⚠️

**Purpose**: Legacy location for feature specs.
**Status**: **DEPRECATED**. Do not create new files here. Migrate active features to `specs/[feature-name]/`.

---

### 3. **`/specs/design/`** - Technical Designs & Architecture

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

### 6. **`/agent-docs/`** - Agent-Generated Documentation 🆕

**Purpose**: Store transitory agent outputs (session summaries, feedback, general research)
**Ownership**: AI agents (automated)
**Pattern**: `<category>/<type>-<topic>-<YYYY-MM>.md`
**Lifecycle**: Preserved indefinitely, except `research/` (auto-archived after 90 days)

**Subdirectories**:

1. **`agent-docs/sessions/`** - Session summaries
   - Pattern: `session-<topic>-<YYYY-MM-DD>.md`
   - Example: `session-onboarding-review-2025-01-15.md`

2. **`agent-docs/execution/`** - Workflow execution reports (DEPRECATED for Features) ⚠️
   - **Note**: Feature execution status is now tracked in `specs/[feature]/tasks.md`.
   - Use this ONLY for non-feature workflows (e.g., maintenance scripts).

3. **`agent-docs/feedback/`** - Agent feedback & analysis
   - Pattern: `feedback-<topic>-<YYYY-MM>.md`

4. **`agent-docs/research/`** - General Research
   - **Note**: Feature-specific research goes to `specs/[feature]/research.md`.
   - Use this for cross-cutting research (e.g., "Python 3.14 capabilities").
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

## 🤖 AI Agent Governance Rules (CRITICAL)

### Golden Rule: Agents CANNOT Write to Root

**This is absolute. No exceptions. Pre-commit hooks enforce this.**

```
❌ AGENT-GENERATED FILES NOT ALLOWED IN ROOT:
- REPORT_*.md
- SESSION_*.md
- SUMMARY_*.md
- RESUMEN_*.md
- TEST_*.md
- PHASE_*.md
- EXECUTION_*.md
- FEEDBACK_*.md
- Any other .md not in approved list
```

### Approved Root Files (Agents CAN create/modify)

Only these files can be modified by AI agents in root:
- `README.md` - Project overview (modify only: links, status section)
- `CHANGELOG.md` - Version history (add entries only)
- No other files

### Mandatory Workflow for AI Agents

**BEFORE creating ANY documentation**, agents must:

1. **Identify Type**: Is this a feature spec? Design decision? Session summary? Execution report?

2. **Select Correct Location**:
   ```
   Feature Spec?      → specs/features/feature-name.md
   Design Decision?   → specs/design/architecture-topic.md
   Task/Roadmap?      → specs/tasks/roadmap-topic.md
   Session Summary?   → agent-docs/sessions/session-topic-YYYY-MM-DD.md
   Execution Report?  → agent-docs/execution/execution-topic-YYYY-MM-DD.md
   Feedback/Analysis? → agent-docs/feedback/feedback-topic-YYYY-MM.md
   Web Research?      → agent-docs/research/research-topic-YYYY-MM-DD.md
   Tests/Prototypes?  → tests/integration/ (NOT agent-docs)
   ```

3. **Include Metadata**:
   ```yaml
   ---
   title: "..."
   description: "..."
   type: "feature|design|task|execution|session|feedback|research"
   status: "draft|active|deprecated"
   created: "YYYY-MM-DD"
   updated: "YYYY-MM-DD"
   author: "Agent Name"
   llm_summary: |
     2-3 sentence summary optimized for LLM context
   ---
   ```

4. **Link from Index/Parent**:
   - Add entry to `specs/DOCUMENT_INDEX_V2.md`
   - Or link from parent document
   - OR link from issue/task tracker
   - No orphaned documents allowed

5. **Validate with Pre-commit**:
   - Run locally: `pre-commit run --all-files`
   - Must pass ALL checks before commit
   - If fails: Fix and re-run (no `--no-verify` bypass)

### Token-Optimized AI Agent Checklist

**EVERY AI agent must follow this before submitting documentation:**

- [ ] **Metadata**: YAML frontmatter with all required fields
- [ ] **Structure**: Clear hierarchy (H1, H2, H3 max)
- [ ] **Efficiency**: Uses Markdown (bold, lists, tables, code) over prose
- [ ] **Linking**: Cross-references with absolute paths
- [ ] **Chunking**: max 800 lines per document (not monolithic)
- [ ] **No Duplication**: Content appears in only one place
- [ ] **Location**: Placed in correct directory per rules above
- [ ] **Pre-commit**: Passes all hooks without `--no-verify`
- [ ] **Linked**: Referenced from parent/index documents
- [ ] **llm_summary**: Present and optimized for LLM scanning

### Violations and Consequences

| Violation | Pre-commit Behavior | Agent Action |
|-----------|-------------------|--------------|
| `.md` file in root (non-approved) | ❌ BLOCKS commit | Move to correct directory |
| Missing YAML frontmatter | ⚠️ WARNING (error in 2 weeks) | Add metadata |
| `type` field incorrect/missing | ❌ BLOCKS commit | Fix type value |
| `llm_summary` missing | ⚠️ WARNING | Add LLM-optimized summary |
| Vague filename (`REPORT.md`) | ❌ BLOCKS commit | Use pattern: `execution-topic-YYYY-MM-DD.md` |
| File > 2000 lines | ⚠️ WARNING | Split into multiple files |
| File < 100 lines | ⚠️ WARNING | Merge with related doc or expand |

### AI Agent Prompt Template

When creating documentation, agents should use this template:

```markdown
---
title: "[DOCUMENT PURPOSE IN 5-7 WORDS]"
description: "[One sentence describing this document. 50-150 characters.]"
type: "execution"  # ← One of: feature, design, task, execution, session, feedback, research
status: "completed"  # ← One of: draft, active, completed, archived, deprecated
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "[Agent Name] (e.g., KERNEL v3.1)"
llm_summary: |
  [2-3 sentence summary optimized for LLM reading]
  Focus on: What is this? Why does it exist? When to reference?
  Target: Brevity + context + usefulness
---

# [TITLE - H1 Only]

## Section 1  # ← H2
- Bullet point 1
- Bullet point 2

### Subsection 1.1  # ← H3 (max nesting)

## Section 2

See also:
- `path/to/related/spec.md` - Description
- `path/to/related/design.md` - Description
```

---

## 📚 Navigation & Discoverability

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

2. **AI Assistant Instructions** (Industry standards):
   - `AGENTS.md` - OpenAI/general AI agents format (comprehensive, all agents)
   - `GEMINI.md` - Google AI Studio format (Gemini-specific optimizations)
   - `.github/copilot-instructions.md` - GitHub Copilot configuration (uses GitHub-specific frontmatter: `description`, `applyTo` only)

3. **GitHub-Specific Directories** (Tool-specific formats):
   - `.github/workflows/*.yml` - GitHub Actions workflows

4. **Never in root** (Always moved):
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

## 🧾 Metadata Requirement (Mandatory)

All markdown documents must begin with a YAML frontmatter block that follows the standard in `specs/templates/document-metadata.md`.

Minimum required fields:

```yaml
---
title: "Human-readable title"
description: "One-sentence summary (50–150 chars)"
type: "feature|design|task|guide|governance|session|execution|feedback|research"
status: "draft|active|deprecated|archived"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Name or Agent ID"
---
```

**Exceptions**: Files with tool-specific frontmatter formats (e.g., `.github/copilot-instructions.md`) are exempt from this requirement.

Validation and enforcement:
- Commits are blocked if a `.md` file is missing frontmatter or has invalid metadata
- Use `scripts/metadata/add-metadata.py` to auto-add missing frontmatter
- Use `scripts/validation/validate-metadata.py --all` to audit repository-wide
- Metadata validation skips `.github/` directory (tool-specific formats)

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
