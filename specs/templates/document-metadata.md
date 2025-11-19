---
title: Document Metadata Pattern
description: 'title: "Document Title (Human-Readable)" description: "One-sentence
  summary (50-150 chars)"'
type: guide
status: draft
created: '2025-11-02'
updated: '2025-11-02'
author: Auto-Generated
tags:
- api
- architecture
- authentication
- deployment
- document
- mcp
llm_summary: "User guide for Document Metadata Pattern.\n  > **Purpose**: Standard\
  \ YAML frontmatter pattern for all markdown documents > **Status**: Active Standard\
  \ > **Last Updated**: 2025-11-01 > **Owner**: CDE Orchestrator Team title: \"Document\
  \ Title (Human-Readable)\"\n  Reference when working with guide documentation."
---

# Document Metadata Pattern

> **Purpose**: Standard YAML frontmatter pattern for all markdown documents
> **Status**: Active Standard
> **Last Updated**: 2025-11-01
> **Owner**: CDE Orchestrator Team

---

## 📋 Standard Frontmatter Pattern

Every `.md` document in the repository **must** start with YAML frontmatter following this pattern:

```yaml
---
title: "Document Title (Human-Readable)"
description: "One-sentence summary (50-150 chars)"
type: "feature|design|task|guide|governance|session|execution|feedback|research"
status: "draft|active|deprecated|archived"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Human Name or Agent ID"
related_docs:
  - "path/to/related/doc.md"
  - "path/to/another/doc.md"
tags:
  - "tag1"
  - "tag2"
llm_summary: |
  Brief summary optimized for LLM context (2-3 sentences).
  Answers: What is this? Why does it exist? When to use it?
---
```

---

## 🎯 Field Definitions

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | string | Human-readable document title | `"Python 3.14 Migration Plan"` |
| `description` | string | One-sentence summary (50-150 chars) | `"Complete migration strategy from Python 3.12 to 3.14"` |
| `type` | enum | Document category (see types below) | `"design"` |
| `status` | enum | Lifecycle status (see statuses below) | `"active"` |
| `created` | date | ISO 8601 date document was created | `"2025-11-01"` |
| `updated` | date | ISO 8601 date document was last updated | `"2025-11-01"` |
| `author` | string | Creator name or agent ID | `"KERNEL (GPT-5)"` or `"John Doe"` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `related_docs` | list | Paths to related documents (relative to repo root) | `["specs/design/architecture/README.md"]` |
| `tags` | list | Searchable keywords | `["python", "migration", "testing"]` |
| `llm_summary` | string | Optimized summary for LLMs (2-3 sentences) | See example below |
| `version` | string | Semantic version for versioned docs | `"2.1.0"` |
| `deprecated_by` | string | Path to replacement doc (if deprecated) | `"specs/design/new-approach.md"` |
| `owner` | string | Team or person responsible | `"Platform Team"` |

---

## 📚 Document Types

### Core Types

| Type | Location | Purpose |
|------|----------|---------|
| `feature` | `specs/features/` | User-facing feature specification |
| `design` | `specs/design/` | Technical architecture and design decisions |
| `task` | `specs/tasks/` | Roadmap, milestones, work breakdown |
| `governance` | `specs/governance/` | Process, rules, standards |
| `guide` | `docs/` | User guides, how-tos, tutorials |

### Agent-Generated Types

| Type | Location | Purpose |
|------|----------|---------|
| `session` | `agent-docs/sessions/` | Session summary/completion report |
| `execution` | `agent-docs/execution/` | Workflow/task execution report |
| `feedback` | `agent-docs/feedback/` | Agent analysis and recommendations |
| `research` | `agent-docs/research/` | Temporary research notes (90-day retention) |

---

## 🚦 Status Values

| Status | Meaning | When to Use |
|--------|---------|-------------|
| `draft` | Work in progress, not reviewed | Initial creation, subject to change |
| `active` | Current and approved | Production-ready, canonical reference |
| `deprecated` | Replaced by newer doc | Old approach, kept for history |
| `archived` | No longer relevant but preserved | Historical reference only |

---

## 💡 LLM Summary Best Practices

The `llm_summary` field is **critical** for AI agent comprehension. Write it like this:

### ✅ Good LLM Summary

```yaml
llm_summary: |
  Migration plan for upgrading project from Python 3.12 to 3.14.
  Covers dependency validation, code audit, testing strategy, and rollback plan.
  Use when planning major Python version upgrades.
```

**Why it works**:

- First sentence: WHAT (specific artifact)
- Second sentence: COVERS (key contents)
- Third sentence: WHEN TO USE (context for retrieval)

### ❌ Bad LLM Summary

```yaml
llm_summary: "This document describes the migration."
```

**Why it fails**:

- Too vague (migration of what?)
- No actionable keywords
- Missing context for when to reference

---

## 📝 Examples

### Example 1: Feature Specification

```yaml
---
title: "User Authentication System"
description: "JWT-based authentication with OAuth2 social login support"
type: "feature"
status: "active"
created: "2025-10-15"
updated: "2025-11-01"
author: "Jane Smith"
related_docs:
  - "specs/design/security-architecture.md"
  - "specs/api/auth-endpoints.yaml"
tags:
  - "authentication"
  - "security"
  - "oauth2"
  - "jwt"
llm_summary: |
  Feature specification for user authentication system with JWT tokens.
  Includes OAuth2 social login (Google, GitHub), refresh tokens, and RBAC.
  Reference when implementing or modifying authentication flows.
version: "1.2.0"
owner: "Security Team"
---
```

### Example 2: Design Document

```yaml
---
title: "Hexagonal Architecture Implementation"
description: "Clean architecture pattern with ports and adapters for CDE Orchestrator"
type: "design"
status: "active"
created: "2025-09-20"
updated: "2025-10-25"
author: "Tech Lead Team"
related_docs:
  - "specs/design/dependency-injection.md"
  - "specs/tasks/architecture-migration.md"
tags:
  - "architecture"
  - "hexagonal"
  - "clean-code"
  - "design-patterns"
llm_summary: |
  Architectural design document defining hexagonal (ports and adapters) pattern.
  Covers domain layer, application layer, adapters, and dependency rules.
  Reference when adding new features or refactoring existing code.
---
```

### Example 3: Session Summary (Agent)

```yaml
---
title: "Onboarding System Implementation Session"
description: "Session implementing automated project onboarding with Spec-Kit compatibility"
type: "session"
status: "archived"
created: "2025-01-15"
updated: "2025-01-15"
author: "KERNEL (GPT-5)"
related_docs:
  - "specs/features/onboarding-system.md"
  - "agent-docs/execution/execution-onboarding-2025-01.md"
tags:
  - "onboarding"
  - "automation"
  - "spec-kit"
llm_summary: |
  Agent session summary for implementing automated onboarding system.
  Completed: OnboardingAnalyzer, POML recipe, MCP tool integration.
  Reference when understanding onboarding feature development history.
---
```

### Example 4: Execution Report (Agent)

```yaml
---
title: "Python 3.14 Migration Execution Report"
description: "Detailed execution report for Python 3.14 upgrade including test results"
type: "execution"
status: "active"
created: "2025-11-01"
updated: "2025-11-01"
author: "KERNEL (GPT-5)"
related_docs:
  - "specs/features/python-314-migration.md"
  - "specs/design/python-314-migration-plan.md"
tags:
  - "python"
  - "migration"
  - "testing"
  - "deployment"
llm_summary: |
  Execution report documenting Python 3.14 migration process and outcomes.
  Includes test results, dependency validation, and rollback procedures tested.
  Reference when planning future Python upgrades or troubleshooting migration issues.
---
```

---

## 🔧 Validation Rules

Metadata will be validated by pre-commit hooks. Documents must pass:

### Required Field Checks

- ✅ All required fields present
- ✅ `type` matches valid enum values
- ✅ `status` matches valid enum values
- ✅ Dates in ISO 8601 format (`YYYY-MM-DD`)
- ✅ `description` between 50-150 characters
- ✅ `llm_summary` between 100-500 characters

### Location Checks

- ✅ Document type matches directory (e.g., `type: feature` only in `specs/features/`)
- ✅ Related docs exist and paths are correct
- ✅ No orphaned documents (must link from index or related doc)

### Content Checks

- ✅ `llm_summary` follows 3-sentence pattern (what/covers/when)
- ✅ Tags are lowercase and hyphen-separated
- ✅ Author is non-empty string

---

## 🛠️ Migration Tools

### Auto-Add Metadata Script

Use `scripts/metadata/add-metadata.py` to automatically add frontmatter to documents missing it:

```bash
python scripts/metadata/add-metadata.py --path specs/features/my-doc.md
```

The script will:

1. Analyze document content
2. Generate appropriate metadata
3. Insert frontmatter at top of file
4. Preserve existing content

### Validate All Metadata

```bash
python scripts/validation/validate-metadata.py --all
```

Checks all `.md` files and reports missing or invalid metadata.

---

## 📖 For AI Agents

When creating or updating documents:

1. **Always start with frontmatter** using this pattern
2. **Infer type from location**: If creating in `specs/features/`, use `type: feature`
3. **Write LLM summary last**: After document is complete, summarize in 3 sentences
4. **Link related docs**: Include paths to parent/child/sibling documents
5. **Use ISO dates**: `created` is original date, `updated` is modification date
6. **Choose status carefully**:
   - `draft` during creation
   - `active` after review and approval
   - `deprecated` when replaced
   - `archived` when no longer relevant but preserved

---

## ✅ Checklist for New Documents

- [ ] YAML frontmatter present at top of file
- [ ] All required fields filled
- [ ] Type matches document location
- [ ] Status reflects current state
- [ ] Dates in ISO 8601 format
- [ ] Description is 50-150 characters
- [ ] LLM summary follows 3-sentence pattern
- [ ] Related docs exist and are linked
- [ ] Tags are relevant and searchable
- [ ] Document linked from parent index or related doc

---

**Last Updated**: 2025-11-01
**Owner**: CDE Orchestrator Team
**Enforcement**: Pre-commit hooks + CI/CD validation
