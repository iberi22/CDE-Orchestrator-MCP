---
title: "Jules Context - Amazon Q Integration Ready for Implementation"
description: "Complete context package for Jules AI to execute 10 Amazon Q integration tasks"
type: "execution"
status: "active"
created: "2025-11-04"
updated: "2025-11-04"
author: "CDE Team"
---

## Jules: Amazon Q Integration Context Package

**Date**: November 4, 2025  
**Status**: 🟢 READY FOR IMMEDIATE EXECUTION  
**Duration**: 3 days total (10 tasks organized in 3 phases)  
**Branch**: `feature/amazon-q-integration` (created and ready)

---

## 🎯 Mission Summary

Integrate **Amazon Q Developer** (AWS AI coding assistant) into CDE Orchestrator MCP, extending the multi-agent system to support AWS Bedrock models and AWS-specific development workflows.

### What Amazon Q Is

- **AWS AI Coding Assistant**: Code generation, refactoring, testing, debugging via AWS Bedrock

- **Multi-IDE**: CLI, VS Code, JetBrains, Eclipse, AWS Console

- **Free Tier**: 50 interactions/month (perfect for dev)

- **Models**: Claude 3 (default), Llama 2, Mistral (via Bedrock)

- **Unique**: AWS consulting capability, enterprise security (IAM-based)

### Why This Integration

1. **Multi-Agent Ecosystem**: Amazon Q + Jules + Copilot + Gemini = full coverage
2. **AWS Teams**: Native AWS tooling for infrastructure/cloud code
3. **Bedrock Models**: Flexible LLM selection (Claude 3, Llama 2, Mistral)
4. **Architecture Ready**: PR #2 hexagonal pattern perfectly supports it

---

## 📊 Current State Summary

### What's Complete ✅

1. **Deep Research** - Amazon Q fully analyzed
2. **PR #2 Validated** - Hexagonal architecture supports integration perfectly
3. **Spec Written** - Feature spec created (560+ lines)
4. **Tasks Organized** - 10 tasks with subtasks, criteria, dependencies
5. **Code Organization** - Clean branch created (`feature/amazon-q-integration`)
6. **Main Updated** - All documentation merged to `main` branch

### Context Documents Available

1. **`specs/features/amazon-q-integration.md`** (560+ lines)
   - Complete feature specification
   - Architecture diagrams
   - 5 components to implement
   - IAM permissions matrix
   - Success criteria

2. **`agent-docs/tasks/amazon-q-integration-roadmap.md`** (645+ lines)
   - **10 tasks organized in 3 phases**
   - Phase 1: Core integration (4 tasks, 2 days)
   - Phase 2: Advanced features (3 tasks, 1 day)
   - Phase 3: Documentation (3 tasks, 1 day)
   - Each task has subtasks, acceptance criteria, dependencies

3. **`agent-docs/execution/execution-amazon-q-integration-2025-11-04.md`** (659 lines)
   - Executive summary
   - Complete implementation plan
   - Quality metrics and standards
   - Success checklist

---

## 🚀 What You Need to Know

### Architecture Pattern (From PR #2)

The codebase follows **hexagonal architecture** (ports & adapters):

```
Domain Layer (business logic)
    ↓
Application Layer (use cases) 
    ↓
Adapters Layer (external systems)
```

**Key Principle**: Dependencies point INWARD only. Domain never imports adapters.

### Existing Pattern: AIAssistantConfigurator

Your starting point - this already exists and works for 6+ agents:

**File**: `src/cde_orchestrator/application/ai_config/ai_config_use_case.py`

**Key Structure**:
```python
AGENT_CONFIG = {
    "copilot": AgentConfig(...),
    "gemini": AgentConfig(...),
    # ADD AMAZON Q HERE ↓
    "amazon-q": AgentConfig(...)
}

class AIAssistantConfigurator:
    def detect_installed_agents(self) -> List[str]:
        """Returns ["copilot", "gemini", "amazon-q", ...] based on detection"""
        
    def generate_config_files(self, agents: List[str]) -> None:
        """Generates AGENTS.md, GEMINI.md, AMAZON-Q.md, etc."""
```

### Test Infrastructure (From PR #2)

**File**: `pytest.ini`
```
testpaths = tests
pythonpath = src/cde_orchestrator
fail_under = 80
```

**Command**: `pytest tests/ --cov`

---

## 📋 The 10 Tasks (Organized for You)

### PHASE 1: Core Integration (2 Days)

These 4 tasks build the foundation - start here:

#### Task AQ-01: AIAssistantConfigurator Integration (4 hours)

- **What**: Add Amazon Q detection to existing system

- **Files**: `ai_config_use_case.py`, `amazon_q_detector.py` (NEW)

- **How**: Add to AGENT_CONFIG, implement detector class, update methods

- **Tests**: `test_detect_amazon_q_cli`, `test_detect_amazon_q_vscode`

- **Success**: Amazon Q appears in detected agents list, >85% coverage

#### Task AQ-02: Configuration Generator (4 hours)

- **What**: Generate `AMAZON-Q.md` with setup instructions

- **Files**: `amazon_q_configurator.py` (NEW)

- **How**: Create class to generate markdown with Bedrock models, IAM policies

- **Features**: Region detection, model listing, credentials validation

- **Success**: AMAZON-Q.md generated with correct format and content

#### Task AQ-03: CLI Adapter for Code Execution (4 hours)

- **What**: Execute code generation via Amazon Q CLI

- **Files**: `amazon_q_cli_adapter.py` (NEW), implements `ICodeExecutor`

- **How**: Build CLI commands, handle responses, error handling

- **Models**: Default to claude-3-sonnet, support switching

- **Success**: Can execute prompts via `amazon-q` CLI command

#### Task AQ-04: AWS Credential Validation (3 hours)

- **What**: Validate AWS credentials and Bedrock access

- **Files**: `amazon_q_credentials.py` (NEW)

- **How**: Check ~/.aws/credentials, env vars, IAM roles via boto3

- **Caching**: Cache validation for 30 minutes

- **Success**: Validates credentials work, clear error messages

**Phase 1 Deliverables**:

- ✅ 4 new Python files created

- ✅ AIAssistantConfigurator extended

- ✅ 20+ unit tests

- ✅ >85% coverage on new code

- ✅ All tests green

---

### PHASE 2: Advanced Features (1 Day)

Build on Phase 1 with these 3 tasks:

#### Task AQ-05: IDE Plugin Detection (3 hours)

- **What**: Detect Amazon Q in VS Code, JetBrains, Eclipse

- **How**: Check standard plugin directories, extract versions

- **Success**: Detects and reports IDE integrations

#### Task AQ-06: Bedrock Model Enumeration (3 hours)

- **What**: List available Bedrock models with caching

- **How**: Call `bedrock.list_foundation_models()`, cache to JSON

- **Cache**: 7-day TTL, fallback for offline

- **Success**: Models listed with IDs, token limits, availability

#### Task AQ-07: End-to-End Integration Tests (2 hours)

- **What**: Test complete Amazon Q flow in onboarding

- **Tests**: Detection → Config generation → CLI execution

- **Success**: Full workflow tested and working

**Phase 2 Deliverables**:

- ✅ IDE detection working

- ✅ Model enumeration with caching

- ✅ 10+ integration tests

- ✅ >80% overall coverage

- ✅ Full E2E workflow validated

---

### PHASE 3: Documentation (1 Day)

Finalize with these 3 tasks:

#### Task AQ-08: Setup Guide for Users (3 hours)

- **What**: Create `docs/amazon-q-setup.md` with step-by-step instructions

- **Content**: Installation, AWS setup, Bedrock models, CDE integration, FAQ

- **Format**: Markdown with code examples

#### Task AQ-09: Update Main Documentation (2 hours)

- **What**: Add Amazon Q to README.md, INTEGRATION.md, etc.

- **How**: Link to AMAZON-Q.md spec, add to agent list, update examples

#### Task AQ-10: Update Improvement Roadmap (1 hour)

- **What**: Mark Amazon Q tasks as COMPLETED in `specs/tasks/improvement-roadmap.md`

- **How**: Add new section, link to spec, update metrics

**Phase 3 Deliverables**:

- ✅ User-facing documentation complete

- ✅ All cross-links working

- ✅ Roadmap updated

- ✅ Ready for release

---

## 🎯 Success Criteria (Definition of Done)

Each task is complete when:

- [ ] All code files created/modified per specification

- [ ] Unit tests: >85% coverage for new code

- [ ] Integration tests: >80% coverage overall

- [ ] Pre-commit hooks passing (black, ruff, isort, mypy)

- [ ] No type hints errors: `mypy src/cde_orchestrator`

- [ ] All tests passing: `pytest tests/ --cov`

- [ ] Documentation complete and links valid

- [ ] PR description clear and links to roadmap tasks

- [ ] No breaking changes to existing code

---

## 📂 Directory Structure (What Exists)

```
src/cde_orchestrator/
├── domain/              # Business logic (no external deps)
├── application/
│   ├── ai_config/       # ← WHERE YOU START (AIAssistantConfigurator)
│   │   ├── __init__.py
│   │   ├── ai_config_use_case.py (exists - extend this)
│   │   ├── amazon_q_detector.py (CREATE)
│   │   ├── amazon_q_configurator.py (CREATE)
│   │   ├── amazon_q_cli_adapter.py (CREATE)
│   │   └── amazon_q_credentials.py (CREATE)
│   └── use_cases/       # Other use cases
├── adapters/
│   ├── state/           # State persistence adapters
│   ├── recipe/          # Recipe adapters
│   └── ...
└── infrastructure/      # DI container, config

specs/
├── features/
│   └── amazon-q-integration.md (YOUR REFERENCE - 560+ lines)
└── tasks/
    └── improvement-roadmap.md (UPDATE AFTER COMPLETION)

tests/
├── unit/
│   ├── application/
│   │   └── ai_config/
│   │       └── test_ai_assistant_configurator.py (ADD TESTS HERE)
│   └── ...
└── integration/
    └── test_amazon_q_onboarding.py (CREATE E2E TESTS)

agent-docs/
└── tasks/
    └── amazon-q-integration-roadmap.md (YOUR MASTER REFERENCE - 645+ lines)

agent-docs/execution/
└── execution-amazon-q-integration-2025-11-04.md (FULL IMPLEMENTATION PLAN)
```

---

## 🔍 Reference Files to Study First

Before starting, review these to understand the pattern:

1. **`src/cde_orchestrator/application/ai_config/ai_config_use_case.py`**
   - How AIAssistantConfigurator currently works
   - Pattern for agent detection and config generation

2. **`specs/features/ai-assistant-config.md`** (if exists)
   - Similar feature spec (use as template)

3. **`tests/unit/application/ai_config/test_ai_assistant_configurator.py`**
   - Existing test patterns to follow

4. **`src/cde_orchestrator/application/code_execution/`**
   - See how ICodeExecutor interface works (you'll implement it)

5. **`specs/features/amazon-q-integration.md`**
   - YOUR COMPLETE SPEC - review Architecture section especially

---

## 🛠️ Commands You'll Need

### Running Tests
```bash
# Run all tests with coverage
pytest tests/ --cov

# Run specific test file
pytest tests/unit/application/ai_config/ -v

# Run with coverage report
pytest tests/ --cov --cov-report=html
```

### Code Quality
```bash
# Format with black
black src/ tests/

# Type check with mypy
mypy src/cde_orchestrator

# Lint with ruff
ruff check src/ tests/

# Sort imports
isort src/ tests/

# All at once (pre-commit simulation)
black src/ tests/ && isort src/ tests/ && ruff check src/ tests/ && mypy src/cde_orchestrator
```

### Git Workflow
```bash
# You're on feature/amazon-q-integration branch already
# After Phase 1: commit
git add src/cde_orchestrator/application/ai_config/
git commit -m "feat(amazon-q): implement core integration (Tasks AQ-01 to AQ-04)"

# After Phase 2: commit
git add tests/
git commit -m "feat(amazon-q): add IDE detection and E2E tests (Tasks AQ-05 to AQ-07)"

# After Phase 3: commit
git add docs/ specs/
git commit -m "docs(amazon-q): complete documentation and roadmap updates (Tasks AQ-08 to AQ-10)"

# Create PR when ready
git push origin feature/amazon-q-integration
```

---

## 🎓 Important Patterns

### 1. Agent Detection Pattern
```python
def detect_amazon_q_cli() -> bool:
    """Check if amazon-q CLI is installed"""
    try:
        result = subprocess.run(["amazon-q", "--version"], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
```

### 2. Config Generation Pattern
```python
class AmazonQConfigurator:
    def generate_amazon_q_md(self, region: str = "us-east-1") -> str:
        """Generate AMAZON-Q.md with Bedrock configuration"""
        # Return markdown string with:
        # - Installation instructions
        # - AWS credential setup
        # - Available models
        # - IAM policies required
```

### 3. Test Pattern
```python
def test_detect_amazon_q_cli_when_installed():
    """Test Amazon Q CLI detection"""
    # Arrange: Mock subprocess call
    # Act: Call detect_amazon_q_cli()
    # Assert: Returns True
```

---

## ✅ Pre-Implementation Checklist

Before you start, confirm:

- [ ] You have PR #2 (hexagonal architecture) in local repo

- [ ] You have `feature/amazon-q-integration` branch (created and ready)

- [ ] You've read `specs/features/amazon-q-integration.md` (architecture section)

- [ ] You understand hexagonal pattern (domain → application → adapters)

- [ ] You've reviewed `AIAssistantConfigurator` code

- [ ] You've reviewed test patterns in `test_ai_assistant_configurator.py`

- [ ] You have AWS credentials (for Task AQ-04 validation)

- [ ] You understand boto3 library (for Bedrock interaction)

---

## 🚀 Start Here

### Phase 1, Task AQ-01 is your entry point:

1. **Read**: `specs/features/amazon-q-integration.md` → Architecture section
2. **Study**: `src/cde_orchestrator/application/ai_config/ai_config_use_case.py`
3. **Review**: `tests/unit/application/ai_config/test_ai_assistant_configurator.py`
4. **Create**: `src/cde_orchestrator/application/ai_config/amazon_q_detector.py`
5. **Modify**: `ai_config_use_case.py` to add Amazon Q detection
6. **Write**: Tests for detection (>85% coverage)
7. **Verify**: `pytest tests/ --cov` passes
8. **Commit**: Phase 1 work

Then proceed to AQ-02, AQ-03, AQ-04 in sequence (each depends on previous).

---

## 📞 Questions During Implementation

If you get stuck:

1. Check the full spec: `specs/features/amazon-q-integration.md`
2. Look at existing code: How does Copilot/Gemini detection work?
3. Review the roadmap: `agent-docs/tasks/amazon-q-integration-roadmap.md`
4. Check this context: Each task has subtasks and criteria

---

## 🎯 Final Checklist Before Merge

When all 10 tasks complete:

- [ ] Phase 1 complete: Core integration (4 tasks)

- [ ] Phase 2 complete: Advanced features (3 tasks)

- [ ] Phase 3 complete: Documentation (3 tasks)

- [ ] All tests passing: `pytest tests/ --cov` >80%

- [ ] All linting passing: `black`, `ruff`, `isort`, `mypy`

- [ ] No breaking changes to existing agents

- [ ] PR created with description linking to roadmap

- [ ] Documentation updated and cross-linked

---

## 🎬 Ready to Begin

**Current State**:

- ✅ Branch created: `feature/amazon-q-integration`

- ✅ All documentation merged to `main`

- ✅ Specifications complete and accessible

- ✅ Task roadmap detailed with subtasks

- ✅ Quality standards defined

- ✅ Success criteria clear

**You're ready to execute immediately. Start with Task AQ-01.**

---

**Created**: November 4, 2025  
**Ready for Jules**: ✅ YES - ALL SYSTEMS GO

