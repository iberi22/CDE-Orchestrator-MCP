# Archive Directory - Design Documentation

This directory contains deprecated design documents that are no longer actively maintained but preserved for historical reference and migration context.

## Deprecated Files

### architecture.md.deprecated

**Date Deprecated**: 2025-11-18

**Reason**:
- Exceeded governance limit (1443 lines > 800 lines max)
- Monolithic structure violated single-responsibility principle
- Difficult to maintain and navigate

**Replacement**: **[specs/design/architecture/](../architecture/README.md)** - Modular architecture documentation (10 focused files)

**Migration Path**:
1. Read [Architecture Overview](../architecture/architecture-overview.md) for core principles
2. Navigate to specific topics via [README](../architecture/README.md)
3. Use reading paths (first-time, implementation, integration)

**Original Content Mapping**:
- Introduction → architecture-overview.md
- Domain Layer → architecture-domain-layer.md
- Ports & Interfaces → architecture-ports.md
- Application Layer → architecture-use-cases.md
- Adapters → architecture-adapters.md
- Multi-Project Design → architecture-multi-project.md
- Copilot CLI → architecture-copilot-integration.md
- DI Container → architecture-di-container.md
- Testing & LLM → architecture-testing-patterns.md

---

## Notes

- **DO NOT** reference deprecated files in new documentation
- **DO NOT** import or use patterns from deprecated files
- **DO** use modular architecture documentation for all new work
- Files preserved for historical reference and understanding evolution
