---
title: "CDE Orchestrator MCP - Architecture Documentation Index"
description: "Navigation hub for modular architecture documentation following governance guidelines"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Orchestrator Team"
tags:
  - "architecture"
  - "index"
  - "navigation"
  - "hexagonal"
llm_summary: |
  Index for modular architecture documentation. Each component in separate file (500-1500 lines).
  Start here to navigate hexagonal architecture, domain model, ports, adapters, and patterns.
---

## 📋 Quick Navigation

### Core Architecture

- **[Overview & Principles](architecture-overview.md)** - Executive summary, core philosophy, design principles
- **[Domain Layer](architecture-domain-layer.md)** - Entities, value objects, business rules
- **[Ports](architecture-ports.md)** - Interface definitions for all adapters
- **[Use Cases](architecture-use-cases.md)** - Application layer orchestration logic

### Implementation

- **[Adapters](architecture-adapters.md)** - Infrastructure implementations (filesystem, GitHub, etc.)
- **[Multi-Project Design](architecture-multi-project.md)** - Stateless multi-project management
- **[Copilot Integration](architecture-copilot-integration.md)** - Headless Copilot CLI adapter
- **[Dependency Injection](architecture-di-container.md)** - DI container and wiring

### Patterns & Testing

- **[Testing Strategy & LLM Patterns](architecture-testing-patterns.md)** - Unit/Integration/E2E testing + LLM optimization patterns

---

## 🎯 Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL AGENTS                          │
│         (Claude, GPT-4, Copilot, Custom LLMs)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │   PRIMARY ADAPTER (IN)      │
        │      MCP Server             │
        │  (FastMCP Implementation)   │
        └──────────────┬──────────────┘
                       │
   ┌───────────────────┴───────────────────┐
   │         APPLICATION CORE               │
   │                                        │
   │  ┌──────────────────────────────┐     │
   │  │      DOMAIN LAYER            │     │
   │  │  - Project                   │     │
   │  │  - Feature                   │     │
   │  │  - Workflow                  │     │
   │  └──────────────────────────────┘     │
   │                                        │
   │  ┌──────────────────────────────┐     │
   │  │   USE CASES (Application)    │     │
   │  │  - StartFeatureUseCase       │     │
   │  │  - SubmitWorkUseCase         │     │
   │  └──────────────────────────────┘     │
   │                                        │
   │  ┌──────────────────────────────┐     │
   │  │    PORTS (Interfaces)        │     │
   │  │  - IProjectRepository        │     │
   │  │  - IWorkflowEngine           │     │
   │  │  - ICodeExecutor             │     │
   │  └──────────────────────────────┘     │
   └────────────┬───────────────────────────┘
                │
      ┌─────────┴───────────┐
      │  SECONDARY ADAPTERS  │
      │       (OUT)          │
      └──────────────────────┘
           │          │
    ┌──────┴─────┐  ┌┴────────────┐
    │ FileSystem │  │ Copilot CLI │
    │  Adapter   │  │   Adapter   │
    └────────────┘  └─────────────┘
```

---

## 🧭 Reading Path

### For First-Time Readers

1. Start with [Overview & Principles](architecture-overview.md) - Understand philosophy
2. Read [Domain Layer](architecture-domain-layer.md) - Learn business concepts
3. Review [Ports](architecture-ports.md) - See interfaces
4. Check [Use Cases](architecture-use-cases.md) - Understand workflows

### For Implementation

1. [Adapters](architecture-adapters.md) - How to implement ports
2. [DI Container](architecture-di-container.md) - How to wire components
3. [Multi-Project Design](architecture-multi-project.md) - Stateless patterns

### For Integration

1. [Copilot Integration](architecture-copilot-integration.md) - CLI adapter
2. [Testing Strategy & LLM Patterns](architecture-testing-patterns.md) - Testing + LLM optimization

---

## 📊 Documentation Metrics

| Document | Lines | Status | Last Updated |
|----------|-------|--------|--------------|
| architecture-overview.md | ~250 | ✅ Active | 2025-11-18 |
| architecture-domain-layer.md | ~200 | ✅ Active | 2025-11-18 |
| architecture-ports.md | ~180 | ✅ Active | 2025-11-18 |
| architecture-use-cases.md | ~300 | ✅ Active | 2025-11-18 |
| architecture-adapters.md | ~200 | ✅ Active | 2025-11-18 |
| architecture-multi-project.md | ~150 | ✅ Active | 2025-11-18 |
| architecture-copilot-integration.md | ~200 | ✅ Active | 2025-11-18 |
| architecture-di-container.md | ~180 | ✅ Active | 2025-11-18 |
| architecture-testing-patterns.md | ~250 | ✅ Active | 2025-11-18 |
| **Total** | **~2010** | **10 files** | - |

**Previous**: 1 monolithic file (1443 lines) ❌
**Current**: 10 modular files (~201 lines avg) ✅
**Governance**: All files <500 lines (compliant) ✅

---

## 🔗 Related Documentation

- **[Dynamic Skill System](../dynamic-skill-system.md)** - Skill management architecture
- **[Multi-Agent Orchestration](../multi-agent-orchestration-system.md)** - Agent coordination
- **[Improvement Roadmap](../../tasks/improvement-roadmap.md)** - Development plan

---

## 🚀 Next Steps

After reading architecture documentation:

1. **Implement Feature**: Check [Use Cases](architecture-use-cases.md) for pattern
2. **Add Adapter**: Follow [Adapters](architecture-adapters.md) guide
3. **Test Code**: Use [Testing Strategy & LLM Patterns](architecture-testing-patterns.md)
4. **Integrate Agent**: See [Testing Strategy & LLM Patterns](architecture-testing-patterns.md)

---

*This modular structure follows CDE governance guidelines (500-1500 lines per document) for optimal LLM comprehension and maintenance.*
