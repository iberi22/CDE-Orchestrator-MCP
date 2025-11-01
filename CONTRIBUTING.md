# Contributing to CDE Orchestrator MCP

Thank you for contributing! This document provides guidelines for contributing code and documentation to the CDE Orchestrator MCP project.

## Documentation Governance

We follow a **single source of truth** principle for all documentation. This prevents sprawl and maintains clarity.

### Directory Structure

All documentation must be placed in one of these designated directories:

| Directory | Purpose | Example Files |
|-----------|---------|----------------|
| `specs/features/` | User-facing feature specifications | `authentication.md`, `multi-project-support.md` |
| `specs/design/` | Technical architecture & design decisions | `dynamic-skill-system.md`, `hexagonal-architecture.md` |
| `specs/tasks/` | Roadmap and project tracking | `improvement-roadmap.md` |
| `specs/governance/` | Process and governance rules | `DOCUMENTATION_GOVERNANCE.md` |
| `docs/` | User-facing guides and documentation | `INDEX.md`, `QUICK_START.md` |
| `.cde/` | Workflows, prompts, and recipes | `workflow.yml`, `prompts/`, `recipes/` |
| `memory/` | Constitution and project principles | `constitution.md` |

### Root-Level Exceptions

**ONLY** these .md files are allowed in the repository root:

- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contributor guidelines (this file)
- `CODE_OF_CONDUCT.md` - Community standards
- `LICENSE` - Legal license

### Enforcement

**Pre-Commit Hook**: When you commit, a hook will automatically:

1. Check all markdown files for governance compliance
2. Run markdown linting (120-char line length, consistent formatting)
3. Reject commits that violate the rules

**GitHub Actions**: All PRs will have governance checks run automatically. Violations will block merge.

## Code Contributions

### Hexagonal Architecture

We follow **hexagonal architecture (clean architecture)** principles. Always respect the dependency rule:

**✅ Dependencies point INWARD only:**

- Application → Domain
- Adapters → Application → Domain

**❌ Never:**

- Domain → Adapters (NEVER!)
- Domain → Infrastructure (NEVER!)

### Code Structure

```python
src/cde_orchestrator/
├── domain/              # 🔷 HEXAGON CORE (no external dependencies)
│   ├── entities.py      # Business logic (Project, Feature)
│   ├── ports.py         # Interface contracts
│   └── exceptions.py    # Domain errors
├── application/         # Use cases (orchestration)
├── adapters/            # Implementations (filesystem, API calls, etc)
└── infrastructure/      # DI, config, setup
```

### Code Style

- **Type hints**: All Python functions must have type hints
- **Naming**: Follow conventions (CamelCase for classes, snake_case for functions)
- **Docstrings**: Include for all public classes and methods
- **Testing**: Unit tests in `tests/unit/`, integration tests in `tests/integration/`

### Tests

Before submitting a PR:

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src/cde_orchestrator --cov-report=html
```

Aim for **80%+ code coverage** for new features.

## Creating New Features

1. **Create a Specification** in `specs/features/`

   ```markdown
   # Feature: My Feature Name

   ## Problem
   What problem does this solve?

   ## Solution
   How do we solve it?

   ## Acceptance Criteria
   - [ ] Clear, testable criteria
   ```

2. **Create a GitHub Issue** (not a TASK.md file)

   ```bash
   gh issue create \
     --title "Implement my feature" \
     --body "See specs/features/my-feature.md" \
     --label "feature,core"
   ```

3. **Use CDE Workflow**

   ```python
   # Start a feature with the CDE system
   cde_startFeature(
       project_path="e:\\scripts-python\\CDE",
       user_prompt="Implement my feature as per spec"
   )
   ```

4. **Follow Hexagonal Pattern**
   - Domain: Business rules, no dependencies
   - Application: Orchestration, coordinates entities
   - Adapters: Infrastructure details, implements ports
   - Tests: Unit → Integration → E2E

5. **Document as You Go**
   - Update `specs/design/` with architecture decisions
   - Update `docs/INDEX.md` if user-facing
   - Link related specifications

## Git Workflow

### Branch Naming

- Feature: `feature/my-feature-name`
- Bug fix: `fix/issue-description`
- Docs: `docs/what-changed`

### Commit Messages

Use conventional commits:

```text
feat: add smart reuse for ephemeral skills
fix: correct staleness detection logic
docs: update governance documentation
test: add integration tests for skill manager
refactor: extract method for clarity
```

### Pull Requests

- Write descriptive title and description
- Link related issues
- Ensure all tests pass locally before submitting
- Add labels: `code`, `docs`, `feature`, `bug`, etc
- Request review from maintainers

## Markdown Standards

All markdown files are automatically checked with:

- **Line length**: 120 characters (soft limit, hard enforced)
- **Headings**: Must be surrounded by blank lines
- **Code blocks**: Must be fenced (```)
- **Lists**: Must be consistent (- or *)
- **No trailing whitespace**

Violations will be automatically fixed or rejected by pre-commit hooks.

## Questions?

- Check `memory/constitution.md` for project principles
- Read `ARCHITECTURE.md` for system design
- See `.github/copilot-instructions.md` for AI agent guidelines
- Open an issue if something is unclear

---

**Thank you for contributing to CDE Orchestrator MCP!** 🚀
