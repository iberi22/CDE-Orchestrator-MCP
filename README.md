---
title: Nexus AI (formerly CDE Orchestrator)
description: '[![CI](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/wo'
type: guide
status: active
created: '2025-11-02'
updated: '2025-11-23'
author: Nexus AI Team
tags:
- api
- architecture
- documentation
- mcp
- orchestration
- nexus-ai
- ceo-agent
- multi-agent
llm_summary: "User guide for Nexus AI (formerly CDE Orchestrator).
  The AI CEO that manages software development like a company.
  Orchestrates agents, manages high-availability tools, and runs in Docker."
---

# Nexus AI (formerly CDE Orchestrator)

[![CI](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/iberi22/CDE-Orchestrator-MCP/branch/main/graph/badge.svg)](https://codecov.io/gh/iberi22/CDE-Orchestrator-MCP)
[![Python Versions](https://img.shields.io/badge/python-3.14+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-AGPL3-red)](LICENSE-DUAL.md)

**Nexus AI** is the evolution of the CDE Orchestrator into a comprehensive **AI CEO** system. It is designed to manage software development projects like a company, orchestrating multiple specialized agents, managing high-availability tools, and running securely within a containerized environment.

## 🧠 The Vision: AI CEO

Nexus AI goes beyond simple tool execution. It acts as the **Chief Executive Officer** of your AI workforce:

*   **Orchestration:** Breaks down complex features into tasks and delegates them to specialized "Employee" agents (Coder, QA, DevOps).
*   **High Availability:** Ensures tools (web scrapers, linters, test runners) are always available via a scalable worker queue system.
*   **Internal Runtime:** Runs CLI-based agents (like GitHub Copilot CLI) securely within its own environment (Docker/VPS).
*   **Context-Driven:** Maintains deep project context and enforces governance across all activities.

## ⚖️ License - Fair & Ethical

**Licensed under Fair Source License 1.0** - Free for all, voluntary support for commercial use.

- ✅ **100% Free:** Personal, educational, research, and commercial use
- 💚 **Voluntary Support:** Commercial users encouraged to contribute $5+ (honor system)
- 🌍 **Open Source:** All derivatives must remain open source
- 🤖 **AI-Friendly:** Must remain accessible to LLM models for training
- 📜 See [`LICENSE`](LICENSE) for complete terms

### 💰 Support This Project

If this project helps your business, **consider supporting** our mission:

| Tier | Contribution | Benefits |
|------|--------------|----------|
| Supporter | $5+/month | ❤️ Badge on README |
| Contributor | $25+/month | 🌟 Priority support + badge |
| Partner | $50+/month | 🚀 Logo on website |
| Sponsor | $100+/month | 💎 Dedicated support |

**100% voluntary. No requirements. No audits. Honor system.**

[![GitHub Sponsors](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-pink)](https://github.com/sponsors/iberi22)
[![Open Collective](https://img.shields.io/badge/support-Open%20Collective-blue)](https://opencollective.com/cde-orchestrator)

> **All funds support AI research, accessibility, and open-source sustainability.**

---

## 🏢 Enterprise Services

Need managed cloud hosting, 24×7 support, or dedicated infrastructure for your organization?

We offer **enterprise-grade services** while keeping the software 100% open source:

| Service | Description | Pricing |
|---------|-------------|---------|
| **Managed Cloud** | Fully managed CDE deployment on AWS/GCP/Azure | Starting at **$500/mo** |
| **Priority Support** | Business hours support with <4hr response SLA | Included in Pro tier |
| **24×7 Premium Support** | Around-the-clock support with <1hr critical response | Starting at **$2000/mo** |
| **RAG/Embeddings Setup** | Custom vector database configuration (Pinecone, Weaviate, Qdrant) | Included in Enterprise |
| **Dedicated Infrastructure** | Isolated compute instances, custom SLAs, multi-region | Custom pricing |
| **Consulting & Training** | Team onboarding, custom workflows, integration support | $150/hr |

**Perfect for:**
- 🏢 Enterprises with compliance requirements (SOC2, HIPAA, GDPR)
- 🚀 Startups scaling AI development workflows
- 🎓 Research institutions managing 100+ projects
- 💼 Consulting firms needing white-label solutions

📧 **Interested?** Contact us: [enterprise@nexus-ai.dev](mailto:enterprise@nexus-ai.dev)

📄 **Learn more:** Contact us for full details.

---

## 📋 Project Status

**Current Phase:** ✅ Phase 1 Complete (2025-11-23) | ⏸️ Phase 2 Ready (Docker Optional)

### Nexus AI Transformation Progress

| Phase | Status | Description | Completion |
|-------|--------|-------------|------------|
| **Phase 1** | ✅ **COMPLETE** | Foundation & Local CEO | **100%** |
| **Phase 2** | ⏸️ **READY** | Docker Containerization (Optional) | 90% (files ready) |
| **Phase 3** | ⏸️ Pending | High Availability & Async | 0% |
| **Phase 4** | ⏸️ Pending | Multi-Agent Orchestration | 0% |
| **Phase 5** | ⏸️ Pending | VPS/Cloud Deployment | 0% |

### Phase 1 Achievements ✅

**Validation Date:** 2025-11-23
**Status:** ✅ 25/25 Tests Passing
**Deployment:** PRODUCTION-READY (Local)

**Core Components:**
- ✅ **Rust Module:** `cde_rust_core-0.2.0` compiled and installed
  - 12 parallel threads (Rayon auto-detected)
  - High-speed documentation scanning
  - Workflow validation
  - Project structure analysis
- ✅ **MCP Server:** FastMCP with 25 registered tools
  - Tool discovery and registration
  - Async/sync tool compatibility
  - Structured logging and telemetry
- ✅ **AI Orchestration:** Complete workflow system
  - `cde_selectWorkflow` - Intelligent routing
  - `cde_executeWithBestAgent` - Multi-agent execution
  - `cde_startFeature` / `cde_submitWork` - Workflow management
- ✅ **Validation Suite:** Comprehensive testing
  - 6 validation phases
  - 25 automated tests
  - Performance benchmarking

**Performance Metrics:**
- Server startup: **< 2s**
- Rust module load: **< 1s**
- Memory usage: **~50MB** (server only)
- Parallel threads: **12** (auto-detected)

**Quick Start:** See [QUICKSTART_LOCAL.md](QUICKSTART_LOCAL.md) for immediate usage

**Full Details:** [Local Validation Report](LOCAL_VALIDATION_REPORT.md) | [Estado del Proyecto](RESUMEN_ESTADO_PROYECTO.md)

---

## 🚀 Quick Start (Local - Recommended)

### Prerequisites
- Python 3.11+ (tested with 3.14.0)
- Rust toolchain (tested with 1.88.0)

### Option 1: Automated (Recommended)

```powershell
# Clone repository
git clone https://github.com/iberi22/CDE-Orchestrator-MCP.git
cd CDE-Orchestrator-MCP

# Run validation and start server
.\start_local.ps1 -Validate
```

### Option 2: Manual

```powershell
# 1. Setup virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .

# 2. Compile Rust module
cd rust_core
maturin develop --release
cd ..

# 3. Validate installation
python validate_local.py

# 4. Start server
$env:PYTHONPATH = "$PWD\src"
python src/server.py
```

### What You Get

- **MCP Server**: 25 AI orchestration tools
- **Rust Performance**: 12-thread parallel processing
- **Validation Suite**: Automated testing
- **Documentation**: Complete guides and specs

See [QUICKSTART_LOCAL.md](QUICKSTART_LOCAL.md) for detailed instructions.

---

## Core Concepts

### Context-Driven Engineering (CDE)
A methodology where development is a series of state transitions, defined in a version-controlled `workflow.yml`. Each phase produces artifacts that serve as context for the next.

### Workflow as Code
The entire development process is defined in `.cde/workflow.yml`. This makes the process transparent, repeatable, and versionable.

### POML-Powered Prompts
Each phase in the workflow is powered by a **Prompt Object Markup Language (`.poml`)** file. This formalizes the instructions given to the AI, making them modular and reusable.

### Orchestration, not just Execution
This MCP doesn't just provide tools; it manages the project's state and guides the agent on what to do next.

## Features (MCP Tools)

The following tools are currently implemented and available for use. For a detailed guide, see [MCP Tools Manual](specs/api/mcp-tools.md).

### 🆕 Progressive Disclosure (Token Optimization)

**NEW (2025-11-09)**: CDE Orchestrator now implements Anthropic's progressive disclosure pattern, achieving **99% token reduction** for multi-project management.

**Phase 1** (Completed): In-memory tool discovery via `cde_searchTools`
**Phase 2** (Completed): Filesystem-based discovery via auto-generated `./servers/cde/` structure

**Key Benefits**:
- **99.0% reduction** in tool discovery overhead (39,568 → 377 bytes)
- **99.7% reduction** for multi-project workflows (118,704 → 390 bytes for 3 projects)
- **Scales to 1000+ projects** in the same token budget as 1 traditional project
- **Auto-generated filesystem** for minimal overhead (one `.py` file per tool)

**How It Works**:
All documentation and discovery tools now support a `detail_level` parameter:

| Level | Use Case | Token Reduction |
|-------|----------|----------------|
| `name_only` | Quick overview, list items | **90-99%** |
| `summary` | Moderate detail, filtering | **50-80%** |
| `full` | Complete information | **0%** (baseline) |

**Filesystem Discovery**:
The server auto-generates `./servers/cde/` on startup with one Python file per tool:
- **name_only**: List files = 377 bytes (99.0% reduction)
- **summary**: Import metadata = ~3KB (92% reduction)
- **full**: Load actual tool = ~40KB (baseline)

**Example**:
```python
# Traditional approach (BAD): 40 MB for 1000 projects
projects = [load_full_project(p) for p in all_projects]

# Progressive disclosure (GOOD): 390 bytes for 1000 projects
projects = cde_listProjects(detail_level="name_only")  # 99.999% reduction
filtered = cde_listProjects(detail_level="summary")    # 99.96% reduction
details = cde_getProjectInfo(selected, detail_level="full")
```

**Tools with Progressive Disclosure**:
- ✅ `cde_scanDocumentation(project_path, detail_level="summary")`
- ✅ `cde_searchTools(query, detail_level="name_and_description")` **(NEW)**

See [AGENTS.md - Progressive Disclosure](AGENTS.md#multi-project-support-with-progressive-disclosure-) for complete documentation.

### Onboarding & Documentation Tools
- `cde_onboardingProject(project_path: str)`: Analyzes a project's structure, languages, and dependencies.
- `cde_publishOnboarding(documents: dict, project_path: str, approve: bool)`: Writes generated documents to the repository.
- `cde_scanDocumentation(project_path: str, detail_level: str = "summary")`: Performs a high-level scan of documentation structure and metadata with token-efficient responses.
- `cde_analyzeDocumentation(project_path: str)`: Conducts a deep analysis of documentation quality, including link validation.
- `cde_createSpecification(feature_name: str, description: str, author: str)`: Creates a new feature specification file.

### Tool Discovery (NEW)
- `cde_searchTools(query: str = "", detail_level: str = "name_and_description")`: Discover MCP tools without loading full schemas. Supports keyword search and auto-tagging (9 categories: analysis, skills, orchestration, execution, setup, documentation, workflow, project, agents).

### Orchestration & Agent Tools
- `cde_selectWorkflow(prompt: str)`: Suggests a workflow based on the user's prompt.
- `cde_listAvailableAgents()`: Lists the agents configured in the system.
- `cde_selectAgent(prompt: str)`: Recommends the best agent for a given task.
- `cde_executeWithBestAgent(prompt: str)`: Selects and executes a task with the most appropriate agent.
- `cde_sourceSkill(skill: str)`: Searches for a skill in the skill library.
- `cde_updateSkill(skill: str, source: str)`: Updates a skill from a specified source.

## Requirements

- **Python 3.14+** (minimum required version)
- Git (for repository operations)
- GitHub CLI or GitHub Personal Access Token (optional, for GitHub integration)

> **Note**: Python 3.14 is required for optimal performance. This version provides 10-20% faster asyncio operations and improved garbage collection for long-running servers.

## Quick Start

1. **Ensure Python 3.14 is installed:**
   ```bash
   python --version  # Should show Python 3.14.x
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/iberi22/CDE-Orchestrator-MCP.git
   cd CDE-Orchestrator-MCP
   ```

3. **Set up the environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .[dev]
   ```

3. **Configure Environment Variables:**
   Create a `.env` file with the necessary credentials:
   ```
   GITHUB_TOKEN=your_github_pat
   ```

4. **Run the server:**
   ```bash
   python src/server.py
   ```

## VS Code Integration

To connect to the CDE Orchestrator MCP from VS Code, configure your MCP settings:

```json
{
  "mcpServers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": ["src/server.py"],
      "env": {
        "PYTHONPATH": "src"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Reload VS Code and verify the connection in your AI assistant extension.

## Project Structure

```
├── .cde/                 # CDE Workflow definitions
│   ├── workflow.yml      # The main workflow definition
│   └── prompts/          # POML prompt templates
├── specs/                # Specification documents
│   ├── features/         # Feature specifications
│   ├── api/              # API specifications
│   ├── design/           # Technical design documents
│   └── reviews/          # Code reviews and validations
├── src/                  # Python source code for the MCP server
├── tests/                # Unit tests
├── memory/               # Project constitution and context
├── .env                  # Environment variables
├── Dockerfile            # Containerization
└── pyproject.toml        # Python project configuration
```

## The CDE Workflow

The core of the CDE Orchestrator is the `workflow.yml` file. A typical workflow includes:

1. **`define`**: Clearly define the feature or bug to be worked on
2. **`decompose`**: Break down the work into smaller, manageable tasks
3. **`design`**: Create technical design documents
4. **`implement`**: Write the code for each task
5. **`test`**: Create and run tests to ensure the code works
6. **`review`**: Review the code for quality, correctness, and standards
7. **`integrate`**: Merge the code into the main branch

## Repository Onboarding & Cleanup

The CDE Orchestrator provides intelligent repository analysis and onboarding:

- **Repository synthesis:** Summarizes directories, file types, and tech stack
- **Automated cleanup:** Recommends test relocations and obsolete file removal
- **Spec-Kit compliance:** Ensures alignment with specification-as-code principles
- **Stateful tracking:** Maintains audit trail of all changes and recommendations

## External Service Integration

The CDE Orchestrator supports seamless integration with external MCP servers:

### Automatic MCP Detection
- **GitHub MCP**: Automatically detected from your MCP configuration
- **Git Operations**: Always available for local repositories
- **Fallback Mechanisms**: Graceful degradation when services are unavailable

### Quick Setup
```bash
export GITHUB_TOKEN=your-token-here
```

For detailed integration documentation, see [Agent Integration](specs/design/new-agent-integration.md).

## 📚 Documentation

### Core Documentation
- **[Executive Summary](specs/design/executive_summary_v2.md)** - Project status, roadmap and metrics
- **[Improvement Roadmap](specs/tasks/improvement-roadmap.md)** - Detailed task breakdown and tracking
- **[Agent Guide](AGENTS.md)** - Guide for AI agents using this MCP

### Feature Documentation
- **[Onboarding System](specs/features/onboarding-system.md)** - Repository onboarding feature details
- **[Planning Document](specs/tasks/planning-overview.md)** - Original project vision and architecture

### Specifications (Spec-Kit)
- **[specs/](specs/)** - Feature specifications and designs
- **[memory/constitution.md](memory/constitution.md)** - Project principles and rules

## 🚧 Current Improvements

The project is undergoing professional hardening to reach production-ready status. Key areas of focus:

### Phase 1: Critical Fixes (Weeks 1-2) 🔴
- ✅ Comprehensive analysis completed
- ⏳ State validation with Pydantic models
- ⏳ Error handling with retry logic
- ⏳ Prompt sanitization against injection

### Phase 2: Testing Infrastructure (Weeks 3-4) 🟠
- ⏳ Pytest setup with 80% coverage target
- ⏳ Unit tests for all managers
- ⏳ Integration tests for workflows
- ⏳ CI/CD pipeline with GitHub Actions

### Phase 3-5: Performance & Features (Weeks 5-8) 🟡
- ⏳ Async/await migration
- ⏳ Intelligent caching
- ⏳ Documentation restructuring
- ⏳ Advanced features (streaming, webhooks)

**Quick Wins Available:** 3 tasks totaling 5 hours can eliminate 70% of current errors. See [roadmap](specs/tasks/improvement-roadmap.md#-quick-wins---implementación-inmediata) for details.

## 🔍 Type Checking with Pyrefly

The project uses **[Pyrefly](https://github.com/facebook/pyrefly)**, a fast type checker by Meta/Facebook written in Rust:

### Why Pyrefly?

- ⚡ **6-8x faster** than mypy on multi-core systems
- 🧠 **Flow-sensitive** type analysis (refines types based on control flow)
- 🔍 **Type inference** for variables and return types
- 🚀 **Parallel checking** using Rayon for maximum performance

### Pyrefly Commands

```bash
# Check entire project
pyrefly check src

# Watch mode (recheck on file changes)
python scripts/pyrefly_check.py --watch

# Generate detailed report
python scripts/pyrefly_check.py --report
```

### Auto-fix Common Issues

```bash
# Automatically fix common type errors
python scripts/pyrefly_autofix.py
```

### Configuration

- **`pyrefly.toml`** - Main Pyrefly configuration
- **`pyproject.toml`** - Additional settings in `[tool.pyrefly]` section
- **`.pre-commit-config.yaml`** - Pre-commit hook for automatic checking

See generated reports in `agent-docs/execution/EXECUTIONS-pyrefly-*.md` for detailed analysis.
