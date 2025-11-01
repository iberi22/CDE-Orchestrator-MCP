# Scripts Directory

> **Purpose**: Organized collection of utility and validation scripts for CDE Orchestrator MCP
> **Last Updated**: 2025-11-01

---

## 📂 Directory Structure

```text
scripts/
├── validation/         # Validation and enforcement scripts
│   ├── enforce-doc-governance.py
│   ├── check-governance.sh
│   ├── validate-metadata.py
│   └── validate-test-structure.py
├── metadata/          # Metadata management scripts
│   └── add-metadata.py
└── setup/             # Setup and installation scripts
    └── (future scripts)
```

---

## 🎯 Purpose

This directory contains all project utility scripts organized by function. Each subdirectory serves a specific purpose:

### `/validation/` - Validation Scripts

Scripts that enforce project standards and validate structure:

| Script | Purpose | Usage |
|--------|---------|-------|
| `enforce-doc-governance.py` | Enforces documentation governance rules (pre-commit hook) | Called automatically by git pre-commit |
| `check-governance.sh` | Wrapper script for enforce-doc-governance.py | Called by pre-commit hooks |
| `validate-metadata.py` | Validates YAML frontmatter in markdown files | `python scripts/validation/validate-metadata.py --all` |
| `validate-test-structure.py` | Validates test file organization | `python scripts/validation/validate-test-structure.py` |

### `/metadata/` - Metadata Management

Scripts for managing document metadata:

| Script | Purpose | Usage |
|--------|---------|-------|
| `add-metadata.py` | Auto-generates and inserts YAML frontmatter | `python scripts/metadata/add-metadata.py --path <file>` |

### `/setup/` - Setup Scripts

Scripts for project setup and initialization (to be added).

---

## 🚀 Common Tasks

### Validate All Documentation

```bash
# Check documentation governance
python scripts/validation/enforce-doc-governance.py < <(find . -name "*.md")

# Validate metadata in all docs
python scripts/validation/validate-metadata.py --all

# Validate test structure
python scripts/validation/validate-test-structure.py
```

### Add Metadata to Documents

```bash
# Single file
python scripts/metadata/add-metadata.py --path specs/features/my-doc.md

# All files in directory
python scripts/metadata/add-metadata.py --directory specs/features/

# Dry run (preview changes)
python scripts/metadata/add-metadata.py --all --dry-run
```

### Fix Test Structure

```bash
# Check test organization
python scripts/validation/validate-test-structure.py

# Auto-fix issues
python scripts/validation/validate-test-structure.py --fix
```

---

## 🔧 Integration with Pre-Commit

These scripts are integrated with Git pre-commit hooks via `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      # Documentation governance
      - id: check-doc-governance
        entry: bash scripts/validation/check-governance.sh

      # Metadata validation
      - id: validate-metadata
        entry: python scripts/validation/validate-metadata.py --staged

      # Test structure validation
      - id: validate-test-structure
        entry: python scripts/validation/validate-test-structure.py --staged
```

### Install Pre-Commit Hooks

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install hooks in repository
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📝 Script Standards

All scripts in this directory must follow these standards:

### File Organization

- ✅ Place in appropriate subdirectory (validation/, metadata/, setup/)
- ✅ Use descriptive names (verb-noun pattern: `validate-metadata.py`)
- ✅ Include shebang line (`#!/usr/bin/env python3` or `#!/bin/bash`)

### Code Quality

- ✅ Include docstring at top of file explaining purpose and usage
- ✅ Use type hints in Python scripts
- ✅ Include `--help` argument for CLI scripts
- ✅ Return appropriate exit codes (0 = success, 1 = failure)

### Documentation

- ✅ Add entry to this README with description and usage
- ✅ Include usage examples in docstring
- ✅ Document all command-line arguments

---

## 🧪 Testing Scripts

To test scripts locally:

```bash
# Test governance enforcement
echo "specs/features/test.md" | python scripts/validation/enforce-doc-governance.py

# Test metadata validation
python scripts/validation/validate-metadata.py --path README.md

# Test structure validation
python scripts/validation/validate-test-structure.py
```

---

## 📚 Related Documentation

- **Governance Framework**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **Metadata Pattern**: `specs/templates/document-metadata.md`
- **Pre-Commit Config**: `.pre-commit-config.yaml`

---

## ✅ Checklist for Adding New Scripts

When adding a new script:

- [ ] Place in appropriate subdirectory
- [ ] Include shebang and docstring
- [ ] Add to this README with description and usage
- [ ] Add pre-commit hook if needed
- [ ] Test locally before committing
- [ ] Make executable: `chmod +x script.py`

---

**Last Updated**: 2025-11-01
**Maintained By**: CDE Orchestrator Team
