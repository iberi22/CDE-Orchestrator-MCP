---
title: CDE Orchestrator MCP
description: '[![CI](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/wo'
type: guide
status: draft
created: '2025-11-02'
updated: '2025-11-02'
author: Auto-Generated
tags:
- api
- architecture
- documentation
- mcp
- migration
- orchestration
llm_summary: "User guide for CDE Orchestrator MCP.\n  [![CI](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml)\
  \ [![codecov](https://codecov.io/gh/iberi22/CDE-Orchestrator-MCP/branch/main/graph/badge.svg)](https://codecov.io/gh/iberi22/CDE-Orchest\n\
  \  Reference when working with guide documentation."
---

# CDE Orchestrator MCP

[![CI](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/iberi22/CDE-Orchestrator-MCP/branch/main/graph/badge.svg)](https://codecov.io/gh/iberi22/CDE-Orchestrator-MCP)
[![Python Versions](https://img.shields.io/badge/python-3.14+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-AGPL3-red)](LICENSE-DUAL.md)

The CDE Orchestrator is the reference implementation of the **Context-Driven Engineering (CDE)** methodology for AI-assisted software development with continuous research and improvement. It is a smart MCP (Model Context Protocol) server designed to guide AI coding assistants through a structured, phase-based software development lifecycle with built-in research, dependency analysis, and project intelligence gathering.

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

📧 **Interested?** Contact us: [enterprise@cde-orchestrator.dev](mailto:enterprise@cde-orchestrator.dev)

📄 **Learn more:** See [Enterprise Services Analysis](agent-docs/execution/enterprise-services-analysis-2025-11-05.md) for full details.

---

> **📋 Project Status:** Currently in active improvement phase. See [Executive Summary](EXECUTIVE_SUMMARY.md) for roadmap and [Improvement Roadmap](specs/tasks/improvement-roadmap.md) for detailed tasks.

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

The following tools are currently implemented and available for use. For a detailed guide, see [MCP Tools Manual](docs/mcp-tools-manual.md).

### Onboarding & Documentation Tools
- `cde_onboardingProject(project_path: str)`: Analyzes a project's structure, languages, and dependencies.
- `cde_publishOnboarding(documents: dict, project_path: str, approve: bool)`: Writes generated documents to the repository.
- `cde_scanDocumentation(project_path: str)`: Performs a high-level scan of documentation structure and metadata.
- `cde_analyzeDocumentation(project_path: str)`: Conducts a deep analysis of documentation quality, including link validation.
- `cde_createSpecification(feature_name: str, description: str, author: str)`: Creates a new feature specification file.

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

For detailed integration documentation, see [INTEGRATION.md](INTEGRATION.md). For Codex CLI usage, see [CODEX.md](CODEX.md).

## 📚 Documentation

### Core Documentation
- **[Executive Summary](EXECUTIVE_SUMMARY.md)** - Project status, roadmap and metrics
- **[Improvement Roadmap](specs/tasks/improvement-roadmap.md)** - Detailed task breakdown and tracking
- **[Technical Review](INFORME_REVISION_PROFESIONAL.md)** - Comprehensive technical analysis
- **[Agent Guide](AGENTS.md)** - Guide for AI agents using this MCP

### Feature Documentation
- **[Onboarding System](ONBOARDING_FEATURE.md)** - Repository onboarding feature details
- **[Integration Guide](INTEGRATION.md)** - External service integration
- **[Codex Integration](CODEX.md)** - Using with Codex CLI
- **[Planning Document](PLANNING.md)** - Original project vision and architecture

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
