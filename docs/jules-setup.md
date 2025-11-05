---
title: "Jules Setup for CDE Orchestrator MCP"
description: "Setup configuration and automation script for Jules AI Agent"
type: "guide"
status: "active"
created: "2025-11-04"
updated: "2025-11-04"
author: "CDE Team"
---

## Quick Start

Jules will automatically:

1. Clone the repository into `/app`
2. Execute `setup.sh` to configure the environment
3. Run validation tests
4. Create a snapshot for faster future startups

## Environment Requirements

The project requires:

- **Python:** 3.11+ (Jules has Python 3.12 by default)
- **Dependencies:** All specified in `requirements.txt` and `pyproject.toml`
- **Disk Space:** ~500MB for dependencies and virtual environment

## Setup Script Overview

The `setup.sh` script performs these steps:

### Environment Validation

- Check Python version (3.11+)
- Verify pip is available
- Check git availability

### Virtual Environment Setup

- Create .venv directory
- Install setuptools, wheel
- Upgrade pip to latest

### Dependencies Installation

- Install from requirements.txt
- Install dev dependencies for testing
- Install project in editable mode

### Project Structure Verification

- Verify src/, tests/, specs/ directories
- Check critical files (pyproject.toml, README.md, server.py)

### Component Initialization

- Create .copilot/skills directories (DSMS)
- Create logs/ directory
- Initialize project structure

### Validation Tests

- Test critical imports (fastmcp, pydantic, SkillManager)
- Validate MCP server initialization
- Verify all components load correctly

## Key Features

### Dynamic Skill Management System (DSMS)

- Automatically initialized in `.copilot/skills/`
- Ready for Phase 2 implementation (SkillSourcer, SkillGenerator)
- All models and storage adapters loaded

### MCP Server

- FastMCP 2.12.3 with 11 registered tools
- Modular tool architecture in `src/mcp_tools/`
- Clean error handling and logging

### Testing Infrastructure

- pytest configured for unit and integration tests
- Test fixtures and mocking support
- Coverage reporting with pytest-cov

## Dependencies Overview

### Core Libraries

- **fastmcp** (2.12.3): FastMCP framework for MCP servers
- **pydantic**: Data validation with type hints
- **pyyaml**: YAML parsing for configuration
- **python-dotenv**: Environment variable management

### Data Processing

- **lxml**: XML/HTML parsing
- **beautifulsoup4**: HTML scraping support
- **aiohttp**: Async HTTP client for web research

### Development Tools

- **pytest**: Testing framework
- **black, isort, flake8**: Code formatting and linting
- **mypy**: Type checking
- **pytest-cov**: Coverage reporting

## What Jules Will Do

### Step 1: Clone Repository

Clones `iberi22/CDE-Orchestrator-MCP` into `/app` automatically.

### Step 2: Run Setup Script

Executes `setup.sh` to:

- Create virtual environment
- Install all dependencies
- Verify project structure
- Initialize DSMS components

### Step 3: Test Environment

Runs validation tests to:

- Check imports
- Verify MCP server loads
- Confirm all components working

### Step 4: Create Snapshot

After successful setup:

- Environment is snapshotted
- Future jobs start faster (5-10 seconds vs 60+ seconds)
- No need to re-run setup each time

## Jules Configuration

### In Jules Setup Tab

```
Setup script: setup.sh
Environment variables: (none required, optional .env)
```

### First Session Workflow

1. Jules receives configuration
2. Repo cloned automatically
3. `setup.sh` executed
4. Validation tests run
5. Environment snapshotted
6. Ready for work

### Subsequent Sessions

1. Environment restored from snapshot
2. Much faster startup (5-10 seconds vs 60+ seconds)
3. Ready to begin tasks

## Project Structure After Setup

```
/app/
├── .venv/                    # Virtual environment
├── .copilot/
│   └── skills/
│       ├── base/             # Base skills (persistent)
│       └── ephemeral/        # Ephemeral skills (temporary)
├── src/
│   ├── server.py            # MCP server entry point
│   ├── cde_orchestrator/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── adapters/
│   │   └── skills/          # DSMS implementation (Phase 1)
│   └── mcp_tools/           # MCP tool definitions
├── tests/                   # Test suite
├── specs/                   # Specifications
├── requirements.txt         # Dependencies
├── pyproject.toml          # Project configuration
└── setup.sh                # Setup script
```

## Troubleshooting

### Python Version Issue

- Jules provides Python 3.12 (compatible)
- Minimum required: Python 3.11+
- If older Python: `setup.sh` will fail and report version

### Dependency Conflict

- Clear pip cache: `pip cache purge`
- Reinstall: `pip install -r requirements.txt --force-reinstall`

### Import Errors

- Verify virtual environment activated
- Check: `python -c "import src.server"`
- Review error logs in `/app/logs/`

### MCP Server Won't Start

- Check logs: `tail logs/mcp_server.log`
- Verify all tools registered in `src/server.py`
- Test with: `python src/server.py`

## After Setup

### Run MCP Server

```bash
python src/server.py
```

### Run Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src
```

### Development

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/
```

## References

- **Documentation:** See `.github/copilot-instructions.md` and `AGENTS.md`
- **Architecture:** `specs/design/ARCHITECTURE.md`
- **Roadmap:** `specs/tasks/improvement-roadmap.md`
- **DSMS:** `specs/design/dynamic-skill-system.md`

## Next Steps for Jules

After setup completes, Jules can:

1. **Implement Phase 2:** Skill sourcing and generation
2. **Add MCP Tools:** Wire DSMS into MCP server
3. **Create Tests:** Comprehensive unit and integration tests
4. **Documentation:** Update AGENTS.md with DSMS patterns
5. **Deployment:** Package for production use

---

**Status:** ✅ Ready for Jules

**Last Updated:** 2025-11-04

**Confidence:** 100% (tested with Phase 1 DSMS)
