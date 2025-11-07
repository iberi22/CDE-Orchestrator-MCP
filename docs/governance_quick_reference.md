---
title: Documentation Governance Quick Reference
description: '**Last Updated**: 2025-11-01 **Status**: ✅ Active - Automated Enforcement
  Enabled'
type: guide
status: draft
created: '2025-11-02'
updated: '2025-11-02'
author: Auto-Generated
tags:
- architecture
- authentication
- documentation
- governance_quick_reference
- python
- workflow
llm_summary: "User guide for Documentation Governance Quick Reference.\n  **Last Updated**:\
  \ 2025-11-01 **Status**: ✅ Active - Automated Enforcement Enabled **Step 1: Identify\
  \ Purpose** Is this document for: - Describing a feature? → `specs/features/` -\
  \ Technical design? → `specs/design/`\n  Reference when working with guide documentation."
---

# Documentation Governance Quick Reference

**Last Updated**: 2025-11-01
**Status**: ✅ Active - Automated Enforcement Enabled

---

## 30-Second Summary

Documentation sprawl is now **prevented automatically**. Every `.md` file must be in a designated directory or it will be rejected at commit time.

```
📋 Allowed Locations for .md Files:
├── specs/features/        (User-facing feature specs)
├── specs/design/          (Technical architecture)
├── specs/tasks/           (Roadmap & tracking)
├── specs/governance/      (Process & rules)
├── docs/                  (User guides)
├── .cde/                  (Workflows & prompts)
├── memory/                (Constitution)
└── ROOT ONLY: README.md, CHANGELOG.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, LICENSE
```

---

## For Document Creators

### When Creating a New .md File

**Step 1: Identify Purpose**

Is this document for:

- Describing a feature? → `specs/features/`
- Technical design? → `specs/design/`
- Roadmap tracking? → `specs/tasks/`
- Governance/rules? → `specs/governance/`
- User guides? → `docs/`
- Workflows/prompts? → `.cde/`
- Project philosophy? → `memory/`

**Step 2: Check for Duplicates**

Before creating, search for similar documents:

```bash
grep -r "your-topic" specs/ docs/ memory/ .cde/
```

**Step 3: Create in Correct Location**

```bash
# GOOD
touch specs/design/my-architecture.md

# BAD - Will be rejected!
touch my-architecture.md    # Root not allowed
touch src/my-architecture.md # Wrong directory
```

**Step 4: Link from Index**

Add reference in the nearest `INDEX.md` or parent index:

```markdown
- [My Architecture](../design/my-architecture.md) - Explains the system design
```

**Step 5: Commit**

When you commit, the pre-commit hook will:

- ✅ Verify your .md file is in the correct location
- ✅ Check markdown formatting (120-char lines)
- ✅ Validate list spacing and headings
- ✅ If violations found, show you exactly how to fix

---

## For AI Agents

### DO ✅

- Identify document **purpose** FIRST (feature? design? task? guide?)
- Place in the **correct directory** based on purpose
- **Check if similar document exists** (avoid duplication)
- **Link from indexes** (e.g., `specs/README.md`, `docs/INDEX.md`)
- Follow naming conventions (lowercase, hyphens for spaces)
- Add document metadata (date, author, status)

### DON'T ❌

- Create .md files in the **project root** (unless in exceptions list)
- Create documents in **subdirectories with inconsistent naming**
- **Duplicate content** across multiple .md files (link instead)
- Leave new documents **orphaned** (must link from index/parent)
- Ignore `.markdownlintrc` rules
- Create documents **without clear purpose/ownership**

---

## Enforcement in Action

### When Pre-Commit Rejects Your Commit

```
❌ [FAIL] MY_DOCUMENT.md
  Root markdown file 'MY_DOCUMENT.md' violates governance.
  Allowed root files: CHANGELOG.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md,
  LICENSE, README.md
  Place this file in one of: .cde, docs, memory, specs/design, specs/fe
  atures, specs/governance, specs/tasks
  See: specs/governance/DOCUMENTATION_GOVERNANCE.md
```

**Fix**:

1. Move file to correct directory: `mv MY_DOCUMENT.md specs/design/`
2. Stage the moved file: `git add specs/design/MY_DOCUMENT.md`
3. Remove from staging (if still there): `git reset HEAD MY_DOCUMENT.md`
4. Commit again: `git commit -m "..."`

---

## Directory Reference

| Directory | When to Use | Examples |
|-----------|-----------|----------|
| `specs/features/` | User-facing feature specification | `authentication.md`, `multi-project-support.md` |
| `specs/design/` | Technical architecture & design decisions | `dynamic-skill-system.md`, `hexagonal-architecture.md` |
| `specs/tasks/` | Roadmap and project tracking | `improvement-roadmap.md` |
| `specs/governance/` | Process, rules, governance | `DOCUMENTATION_GOVERNANCE.md` |
| `docs/` | User guides, getting started, FAQ | `INDEX.md`, `QUICK_START.md` |
| `.cde/` | Workflows, prompts, recipes | `workflow.yml`, `prompts/`, `recipes/` |
| `memory/` | Constitution, principles, values | `constitution.md` |

---

## Document Lifecycle

```
1. INITIATE
   ↓ Define purpose, ownership, target location

2. CREATE
   ↓ Write in correct directory with metadata

3. REVIEW
   ↓ Link from indexes, add cross-references

4. PUBLISH
   ↓ Merge to main with governance sign-off

5. MAINTAIN
   ↓ Update timestamps, mark outdated content
```

---

## Markdown Standards

All .md files are automatically validated:

| Rule | Requirement | Example |
|------|-------------|---------|
| Line Length | Max 120 chars | Soft limit, enforced at commit |
| Headings | Blank lines above/below | `\n# Heading\n` |
| Lists | 1 space after marker | `- Item` (not `-  Item`) |
| Code Blocks | Fenced with language tag | `` ```python `` |
| Whitespace | No trailing spaces | Lines end with content, not spaces |

---

## Troubleshooting

### "Pre-commit hook rejected my file"

→ Check directory structure (see Directory Reference above)
→ Ensure file is in designated location
→ See governance framework: `specs/governance/DOCUMENTATION_GOVERNANCE.md`

### "Markdown linting failed"

→ Check line length (should be ≤120 chars)
→ Check list formatting (1 space after `-`)
→ Add blank lines before/after code blocks
→ Use language tags on fenced code: `` ```python ``

### "I need to bypass pre-commit (emergency only)"

```bash
# Force commit, skip pre-commit checks
git commit --no-verify

# But PLEASE fix the governance issue ASAP after
```

### "Where do I ask questions?"

- Check `memory/constitution.md` for project principles
- Read `CONTRIBUTING.md` for detailed contributor guide
- See `.github/copilot-instructions.md` for system design
- Open an issue if something is unclear

---

## Key Files

| File | Purpose |
|------|---------|
| `specs/governance/DOCUMENTATION_GOVERNANCE.md` | Full governance framework (comprehensive) |
| `CONTRIBUTING.md` | Contributor guide with code & doc standards |
| `.github/copilot-instructions.md` | System design & agent guidelines |
| `.pre-commit-config.yaml` | Automated enforcement configuration |
| `scripts/enforce-doc-governance.py` | Path validation logic |

---

## Checklist for New Documents

Before committing a new .md file:

- [ ] Document purpose is clear
- [ ] Located in correct directory (not root)
- [ ] Similar document doesn't already exist
- [ ] Linked from appropriate index
- [ ] File name is lowercase with hyphens
- [ ] Lines are ≤ 120 characters
- [ ] Lists have proper spacing (1 space after `-`)
- [ ] Code blocks have language tags
- [ ] No trailing whitespace
- [ ] Metadata added (date, author, status if applicable)

✅ After all checks: Commit!

---

**Remember**: Documentation governance is **automatic**. The system will tell you if something is wrong. No manual review needed!

🎯 **Goal**: Keep documentation organized, prevent sprawl, make it easier for everyone to find information.
