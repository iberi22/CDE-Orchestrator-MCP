---
title: "Jules Master Prompt - Phase 3C Complete Implementation"
description: "Comprehensive prompt for Jules AI agent to complete multi-agent orchestration with documentation distribution"
type: "execution"
status: "active"
created: "2025-11-03"
updated: "2025-11-03"
author: "CDE Orchestrator System"
llm_summary: |
  Complete master prompt for Jules to: (1) Finalize Jules SDK configuration and integration,
  (2) Redistribute documentation following DOCUMENTATION_GOVERNANCE compliance,
  (3) Complete pending roadmap tasks for Phase 2 and Phase 3,
  (4) Implement comprehensive testing infrastructure.
tags:
  - "julius"
  - "phase-3c"
  - "documentation-governance"
  - "testing"
  - "orchestration"
---

# 🚀 Jules Master Prompt - Phase 3C: Complete Multi-Agent Implementation

**Target**: Jules AI Agent (Google's async AI coding agent)
**Scope**: Complete Phase 3C multi-agent orchestration with Jules SDK + Documentation Governance
**Estimated Duration**: 6-8 hours
**Priority**: 🔴 CRITICAL
**Confidence**: 0.92 (high complexity, well-scoped)

---

## 📋 OBJECTIVE SUMMARY

Complete the CDE Orchestrator MCP multi-agent orchestration system with three interconnected workstreams:

1. **Phase 3C-1: Jules SDK Configuration** - Finalize async SDK integration and error handling
2. **Phase 3C-2: Documentation Distribution** - Reorganize all docs following DOCUMENTATION_GOVERNANCE
3. **Phase 3C-3: Testing Infrastructure** - Implement Phase 2 testing framework (testing strategy + fixtures + CI/CD)

**Success Criteria**:
- ✅ All 3 workstreams complete with 100% test passing
- ✅ Documentation audit shows 0 governance violations
- ✅ Jules SDK fully functional with error handling + timeouts + retries
- ✅ Testing infrastructure operational with >80% coverage on new code
- ✅ All files have proper YAML frontmatter metadata
- ✅ Git commit with detailed message and all changes staged

---

## 🎯 CONTEXT & ARCHITECTURE

### Current State (as of 2025-11-03)

**Completed**:
- ✅ Phase 3A: Agent Selection Policy with complexity detection
- ✅ Phase 3B: Multi-Agent Orchestrator (Jules, Copilot, Gemini, Qwen support)
- ✅ Phase 3B: CLI adapters for code execution
- ✅ Phase 3B: Parallel execution use case with dependency tracking
- ✅ Phase 3B: 56/56 unit tests passing (100% pass rate)
- ✅ MCP tools: cde_delegateToJules, cde_selectAgent, cde_listAvailableAgents

**In Progress** (Phase 3C - THIS SESSION):
- 🔄 Jules SDK configuration (partial - needs completion)
- 🔄 Documentation distribution (not started)
- 🔄 Testing infrastructure (not started)

### Architecture Pattern

```
Domain Layer (Pure business logic)
  ├── ICodeExecutor port (async execute_prompt)
  ├── IProjectRepository port
  └── Domain exceptions

Application Layer (Orchestration)
  ├── ParallelExecutionUseCase
  ├── WorkflowSelectorUseCase
  └── SkillManagementUseCase

Adapters Layer (Infrastructure)
  ├── agents/
  │   ├── JulesAsyncAdapter (async API with full context)
  │   ├── CopilotCLIAdapter (gh copilot suggest)
  │   ├── GeminiCLIAdapter (gemini generate)
  │   ├── QwenCLIAdapter (qwen chat)
  │   ├── AgentSelectionPolicy (intelligent routing)
  │   └── MultiAgentOrchestrator (unified interface)
  ├── documentation/ (DOCUMENTATION_GOVERNANCE compliance)
  ├── repository/ (Git, filesystem)
  └── state/ (Persistence)

MCP Server
  ├── cde_delegateToJules (long-running async tasks)
  ├── cde_selectAgent (complexity analysis + recommendation)
  ├── cde_listAvailableAgents (status + capabilities)
  ├── cde_executeWithBestAgent (intelligent orchestration)
  └── ... (other tools)
```

---

## 📍 WORKSTREAM 1: Jules SDK Configuration (Phase 3C-1)

### What Needs to be Done

**Task 1.1: Complete JulesAsyncAdapter Implementation**

Current file: `src/cde_orchestrator/adapters/agents/jules_async_adapter.py`

**Requirements**:
1. ✅ Async API client wrapper for jules-agent-sdk
2. ✅ Full repository context handling (up to 100,000+ lines)
3. ✅ Plan approval workflow support
4. ✅ Progress tracking via callbacks
5. ✅ Session persistence (resume capability)
6. ✅ Error handling with proper fallback chains
7. ✅ Timeout management with configurable limits
8. ✅ Retry logic with exponential backoff

**Implementation Checklist**:

```python
# 1. Initialize with API key validation
class JulesAsyncAdapter(ICodeExecutor):
    def __init__(
        self,
        api_key: str,
        default_timeout: int = 1800,
        require_plan_approval: bool = False,
        max_retries: int = 3
    ):
        # Validate API key format (should start with "jls_" or similar)
        # Initialize async client with retry configuration
        # Setup session persistence (cache to ~/.cde/sessions/)

    # 2. Execute with full context
    async def execute_prompt(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        # Load full repository context (gitingest-style)
        # Create session with plan generation
        # If require_plan_approval: wait for user approval callback
        # Execute asynchronously with progress tracking
        # Handle timeouts with graceful degradation
        # Return structured result JSON

    # 3. Session management
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        # Check session state (PENDING, IN_PROGRESS, COMPLETED, FAILED)
        # Return activity log and progress metrics

    # 4. Error handling
    async def close(self):
        # Cleanup: close HTTP client, save session state
```

**Success Criteria**:
- ✅ SDK calls work with real JULES_API_KEY from .env
- ✅ Project context loaded correctly (all files <= 100k lines)
- ✅ Plan approval workflow implemented (if required)
- ✅ Timeouts respected (default 1800s, configurable)
- ✅ Retries with exponential backoff (3 attempts, 1s/2s/4s)
- ✅ Session state persisted to `.cde/sessions/`
- ✅ Error messages provide actionable context
- ✅ Async execution properly awaited
- ✅ No blocking I/O operations

**References**:
- Jules Agent SDK: https://github.com/AsyncFuncAI/jules-agent-sdk-python
- Async patterns: `src/cde_orchestrator/adapters/agents/code_cli_adapters.py` (reference async implementation)
- Error handling: `src/cde_orchestrator/service_connector.py` (CircuitBreaker pattern)

---

**Task 1.2: Integration with MCP Server**

Current file: `src/server.py`

**Requirements**:
1. Update `cde_delegateToJules` MCP tool to use complete JulesAsyncAdapter
2. Add error context for setup issues (API key missing, SDK not installed)
3. Add progress reporting for long-running tasks
4. Add session management (list, cancel, resume)

**Implementation**:
```python
@app.tool()
@tool_handler
async def cde_delegateToJules(
    user_prompt: str,
    project_path: str = ".",
    branch: str = "main",
    require_plan_approval: bool = False,
    timeout: int = 1800,
    detached: bool = False
) -> str:
    # 1. Validate prerequisites
    api_key = os.getenv("JULES_API_KEY")
    if not api_key:
        return error_json("JULES_API_KEY not configured")

    # 2. Initialize adapter
    adapter = JulesAsyncAdapter(api_key, timeout, require_plan_approval)

    try:
        # 3. Execute with full context
        result = await adapter.execute_prompt(
            Path(project_path),
            user_prompt,
            context={"branch": branch, "detached": detached}
        )
        return result

    finally:
        await adapter.close()
```

**Success Criteria**:
- ✅ `cde_delegateToJules` works end-to-end
- ✅ Error handling for missing API key
- ✅ Error handling for SDK not installed
- ✅ Progress tracking for long tasks
- ✅ Session persistence works

---

**Task 1.3: Unit Tests for Jules Integration**

New file: `tests/unit/adapters/agents/test_jules_async_adapter.py`

**Test Coverage**:
```python
class TestJulesAsyncAdapter:
    """Test Jules SDK async adapter."""

    def test_init_validates_api_key_format(self):
        # Should reject invalid API key formats
        # Should accept valid key format

    @pytest.mark.asyncio
    async def test_execute_prompt_success(self, mock_jules_client):
        # Mock successful session creation and completion
        # Verify project context loaded
        # Verify result JSON returned

    @pytest.mark.asyncio
    async def test_execute_prompt_with_plan_approval(self, mock_jules_client):
        # Set require_plan_approval=True
        # Mock plan generation and approval callback
        # Verify execution only proceeds after approval

    @pytest.mark.asyncio
    async def test_timeout_handled_gracefully(self, mock_jules_client):
        # Simulate timeout after 30s
        # Verify graceful degradation
        # Verify partial results returned

    @pytest.mark.asyncio
    async def test_retry_logic_with_backoff(self, mock_jules_client):
        # Simulate initial failure
        # Verify retry with exponential backoff
        # Verify success after retry

    @pytest.mark.asyncio
    async def test_session_persistence(self, mock_jules_client, tmp_path):
        # Create session and save state
        # Load from persistence
        # Verify state integrity

    @pytest.mark.asyncio
    async def test_close_cleanup(self):
        # Create adapter
        # Call close()
        # Verify HTTP client closed
        # Verify session saved

    @pytest.mark.asyncio
    async def test_api_key_missing_raises(self):
        # Initialize without API key
        # Should raise appropriate error
```

**Minimum Coverage**: >85%

---

## 📍 WORKSTREAM 2: Documentation Distribution (Phase 3C-2)

### Current Issue

Documentation is scattered across project without clear governance. The `DOCUMENTATION_GOVERNANCE.md` defines rules, but many files are not compliant:

**Violations Found**:
- ❌ Docs in project root (QUICK_REFERENCE.md, INTEGRATION.md, etc.)
- ❌ Missing YAML frontmatter metadata
- ❌ Orphaned documents (not indexed)
- ❌ Duplicated content across multiple files
- ❌ Inconsistent structure

### What Needs to be Done

**Task 2.1: Audit Current Documentation**

Use `cde_scanDocumentation` + `cde_analyzeDocumentation` to:
1. Find all .md files
2. Check for YAML frontmatter
3. Identify orphaned documents
4. Check link integrity
5. Report violations

**Expected Output**:
```json
{
  "total_docs": 45,
  "governance_violations": [
    {
      "file": "docs/QUICK_REFERENCE.md",
      "violation": "Located in /docs instead of /specs",
      "action": "Move to specs/governance/QUICK_REFERENCE.md"
    },
    {
      "file": "INTEGRATION.md",
      "violation": "Root-level document (only README, CHANGELOG, etc allowed)",
      "action": "Move to docs/integration.md"
    }
  ],
  "missing_metadata": 12,
  "recommendations": [...]
}
```

**References**:
- `specs/governance/DOCUMENTATION_GOVERNANCE.md` - Complete governance rules
- Directory structure rules: lines 38-120
- Metadata requirements: lines 150-200
- Enforcement mechanisms: lines 400-450

---

**Task 2.2: Reorganize Documentation Structure**

Follow this pattern exactly:

```
✅ ALLOWED (Root level only):
  README.md - Project overview
  CHANGELOG.md - Version history
  CONTRIBUTING.md - Contribution guidelines
  LICENSE - Legal

📁 specs/ - Specification documents
  features/ - User-facing features
    ├── user-authentication.md
    ├── multi-project-support.md
    └── integrated-management-system.md
  design/ - Technical architecture
    ├── ARCHITECTURE.md
    ├── hexagonal-architecture.md
    ├── dynamic-skill-system.md
    ├── agent-selection-policy.md
    └── parallel-execution.md
  tasks/ - Project management
    └── improvement-roadmap.md
  governance/ - Process rules
    ├── DOCUMENTATION_GOVERNANCE.md
    ├── QUICK_REFERENCE.md
    └── CODE_STANDARDS.md
  templates/ - Document patterns
    └── feature-template.md

📁 docs/ - User guides & quick references
  ├── INDEX.md (navigation hub)
  ├── QUICK_START.md
  ├── AGENTS.md (user guide)
  ├── api/
  ├── deployment/
  └── troubleshooting/

📁 agent-docs/ - AI agent outputs
  ├── sessions/ - Session reports
  │   └── session-<date>-<task>.md
  ├── execution/ - Execution reports
  │   └── execution-<date>-<task>.md
  ├── feedback/ - Analysis & feedback
  │   └── feedback-<date>-<task>.md
  └── research/ - Web research notes
      └── research-<date>-<topic>.md

📁 .github/ - GitHub-specific (special case)
  └── copilot-instructions.md (GitHub-specific format exception)
```

**Tasks to Execute**:

1. **Move files to correct directories**:
   - Move `docs/QUICK_REFERENCE.md` → `specs/governance/QUICK_REFERENCE.md`
   - Move `docs/INTEGRATION.md` → `docs/integration-guide.md`
   - Move `docs/ai-research-quickstart.md` → `agent-docs/research/ai-patterns.md`
   - ... (update 12 more files)

2. **Add YAML frontmatter to all files** that are missing it:
   ```yaml
   ---
   title: "Document Title"
   description: "One-sentence summary (50-150 chars)"
   type: "feature|design|task|guide|governance|session|execution|feedback|research"
   status: "draft|active|deprecated|archived"
   created: "YYYY-MM-DD"
   updated: "YYYY-MM-DD"
   author: "Name or Agent ID"
   llm_summary: |
     2-3 sentence summary optimized for LLM context.
   ---
   ```

3. **Update index files**:
   - Update `docs/INDEX.md` - List all docs with descriptions
   - Create `specs/design/INDEX.md` - Design docs navigation
   - Create `agent-docs/INDEX.md` - AI output navigation

4. **Fix cross-references**:
   - Update all inter-document links
   - Fix broken links
   - Add missing backlinks

**Success Criteria**:
- ✅ 0 governance violations (audit shows perfect score)
- ✅ All files have complete YAML frontmatter
- ✅ All files in correct directories per type
- ✅ All links working (tested with cde_analyzeDocumentation)
- ✅ Index files updated with navigation

**Files to Create/Update**:
- ~20 files modified (moved + updated)
- ~5 new index files created
- ~40 files get YAML frontmatter added

---

**Task 2.3: Add Documentation Enforcement**

Create `scripts/validation/validate-docs.py`:

```python
"""Validate documentation governance compliance."""

def validate_file_location(filepath: Path) -> List[str]:
    """Check if file is in correct directory."""
    # If type=feature → must be in specs/features/
    # If type=design → must be in specs/design/
    # etc.

def validate_frontmatter(filepath: Path) -> List[str]:
    """Check YAML frontmatter is complete."""
    # All required fields present
    # Title and description non-empty
    # Type is valid enum
    # Author and dates present

def validate_links(filepath: Path) -> List[str]:
    """Check internal links work."""
    # All [text](link) references point to existing files
    # No broken internal links

def main():
    """Run full validation."""
    violations = []
    for md_file in Path(".").glob("**/*.md"):
        violations.extend(validate_file_location(md_file))
        violations.extend(validate_frontmatter(md_file))
        violations.extend(validate_links(md_file))

    if violations:
        print(f"❌ {len(violations)} governance violations found:")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("✅ All documentation compliant with DOCUMENTATION_GOVERNANCE")
    return 0
```

Add to pre-commit hooks:
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-docs
      name: Validate documentation governance
      entry: python scripts/validation/validate-docs.py
      language: system
      types: [markdown]
      pass_filenames: false
```

**Success Criteria**:
- ✅ Script runs without errors
- ✅ Script detects governance violations
- ✅ All existing files pass validation

---

## 📍 WORKSTREAM 3: Testing Infrastructure (Phase 2, Partial)

### What Needs to be Done

**Task 3.1: Setup Pytest Configuration**

Create `pytest.ini`:
```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src/cde_orchestrator
    --cov-report=html:htmlcov
    --cov-report=term-missing:skip-covered
markers =
    asyncio: mark test as async
    unit: mark test as unit test
    integration: mark test as integration test
    slow: mark test as slow running
```

Create `tests/conftest.py`:
```python
"""Shared pytest configuration and fixtures."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def tmp_project(tmp_path):
    """Create temporary project directory with structure."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / ".cde").mkdir()
    return tmp_path

@pytest.fixture
def mock_project_repo():
    """Mock project repository."""
    repo = AsyncMock()
    repo.save = AsyncMock()
    repo.load = AsyncMock()
    return repo

@pytest.fixture
def mock_code_executor():
    """Mock ICodeExecutor."""
    executor = AsyncMock()
    executor.execute_prompt = AsyncMock(return_value='{"result": "success"}')
    return executor

# ... More fixtures
```

**Success Criteria**:
- ✅ pytest.ini configuration complete
- ✅ conftest.py with 10+ reusable fixtures
- ✅ Fixtures for all key components (project, repos, executors, etc.)

---

**Task 3.2: Implement Integration Tests for CLI Adapters**

File: `tests/integration/adapters/agents/test_cli_adapters.py`

Already started - needs completion:

```python
class TestCopilotCLIAdapterIntegration:
    """Integration tests with real gh CLI."""

    @pytest.mark.integration
    @pytest.mark.skipif(not shutil.which("gh"), reason="gh CLI not installed")
    async def test_real_copilot_execution(self, tmp_path):
        """Test actual GitHub Copilot execution."""
        # Requires gh CLI + authentication

    @pytest.mark.integration
    @pytest.mark.skipif(not shutil.which("gemini"), reason="gemini CLI not installed")
    async def test_real_gemini_execution(self, tmp_path):
        """Test actual Gemini execution."""

    @pytest.mark.integration
    @pytest.mark.skipif(not shutil.which("qwen"), reason="qwen CLI not installed")
    async def test_real_qwen_execution(self, tmp_path):
        """Test actual Qwen execution."""
```

**Success Criteria**:
- ✅ 15+ integration tests implemented
- ✅ Tests skip gracefully if CLI not installed
- ✅ Error scenarios covered

---

**Task 3.3: Setup GitHub Actions CI/CD**

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        run: |
          pytest tests/ --cov=src/cde_orchestrator --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**Success Criteria**:
- ✅ CI/CD pipeline runs on push/PR
- ✅ Tests execute for Python 3.11, 3.12
- ✅ Coverage reports generated
- ✅ Failed tests block merge

---

## 🎯 IMPLEMENTATION ROADMAP

### Phase 3C-1: Jules SDK (Est. 2-3 hours)

**Sequence**:
1. ✅ Implement `JulesAsyncAdapter` complete class
2. ✅ Add error handling (API key validation, retry logic, timeouts)
3. ✅ Implement session persistence
4. ✅ Update MCP server integration
5. ✅ Implement 8+ unit tests
6. ✅ Verify all tests passing

**Files Modified**:
- `src/cde_orchestrator/adapters/agents/jules_async_adapter.py` (new/expanded)
- `src/server.py` (cde_delegateToJules tool)
- `tests/unit/adapters/agents/test_julius_async_adapter.py` (new)

---

### Phase 3C-2: Documentation Distribution (Est. 2-3 hours)

**Sequence**:
1. ✅ Run audit: `cde_scanDocumentation(".")`
2. ✅ Identify all violations
3. ✅ Move files to correct directories
4. ✅ Add YAML frontmatter to all files
5. ✅ Fix cross-references
6. ✅ Create index files
7. ✅ Run validation: `python scripts/validation/validate-docs.py`
8. ✅ Verify 0 governance violations

**Files Modified/Created**:
- ~20 documentation files (reorganized + metadata added)
- `scripts/validation/validate-docs.py` (new)
- `.pre-commit-config.yaml` (updated)
- Index files (5 new)

---

### Phase 3C-3: Testing Infrastructure (Est. 2 hours)

**Sequence**:
1. ✅ Create `pytest.ini`
2. ✅ Create `tests/conftest.py` with fixtures
3. ✅ Complete integration tests
4. ✅ Create `.github/workflows/tests.yml`
5. ✅ Verify all tests passing
6. ✅ Generate coverage reports

**Files Modified/Created**:
- `pytest.ini` (new)
- `tests/conftest.py` (new)
- `tests/integration/adapters/agents/test_cli_adapters.py` (completed)
- `.github/workflows/tests.yml` (new)

---

## ✅ FINAL CHECKLIST

**Before submitting**:

- [ ] **Jules SDK (Phase 3C-1)**
  - [ ] JulesAsyncAdapter implemented and fully functional
  - [ ] All error cases handled (API key, timeout, network, SDK errors)
  - [ ] Unit tests: 8+ tests, >85% coverage
  - [ ] MCP tool `cde_delegateToJules` works end-to-end
  - [ ] Session persistence tested

- [ ] **Documentation (Phase 3C-2)**
  - [ ] All files in correct directories per governance
  - [ ] All files have complete YAML frontmatter
  - [ ] All links verified working
  - [ ] Index files created and updated
  - [ ] Validation script shows 0 violations
  - [ ] `cde_analyzeDocumentation` quality score > 90

- [ ] **Testing Infrastructure (Phase 3C-3)**
  - [ ] pytest.ini configured
  - [ ] conftest.py with 10+ fixtures
  - [ ] Integration tests for CLI adapters (15+ tests)
  - [ ] GitHub Actions CI/CD workflow created
  - [ ] All tests passing (pytest run successful)
  - [ ] Coverage reports generated

- [ ] **Code Quality**
  - [ ] No type errors: `mypy src/ --strict` passes
  - [ ] No linting issues: `ruff check src/` passes
  - [ ] Code formatted: `black src/ tests/`
  - [ ] All files have docstrings
  - [ ] Architecture pattern respected (Domain → Application → Adapters)

- [ ] **Git Commit**
  - [ ] All changes staged: `git add -A`
  - [ ] Commit message descriptive and detailed
  - [ ] Commit includes summary of all 3 workstreams
  - [ ] No uncommitted changes remain

---

## 🎓 KEY PRINCIPLES

1. **Hexagonal Architecture**: Maintain strict separation (Domain has NO external deps)
2. **Async First**: All I/O operations properly async/await
3. **Error Handling**: All errors have descriptive messages + actionable context
4. **Testing**: >85% coverage on new code, comprehensive edge case testing
5. **Documentation**: Every file has YAML frontmatter + proper directory location
6. **Type Safety**: Full type hints, mypy strict mode compliance
7. **Governance**: Follow all rules from DOCUMENTATION_GOVERNANCE.md

---

## 📚 REFERENCE DOCUMENTS

**Architecture & Design**:
- `specs/design/ARCHITECTURE.md` - Hexagonal architecture guide
- `specs/design/dynamic-skill-system.md` - Skill management system
- `specs/governance/DOCUMENTATION_GOVERNANCE.md` - Complete governance rules

**Implementation Examples**:
- `src/cde_orchestrator/adapters/agents/code_cli_adapters.py` - CLI adapter pattern
- `src/cde_orchestrator/application/parallel_execution_use_case.py` - Use case pattern
- `tests/unit/adapters/agents/test_agent_selection_policy.py` - Test patterns

**Roadmap**:
- `specs/tasks/improvement-roadmap.md` - Complete task breakdown
- Phase 2-4 tasks in roadmap file (lines 200-400)

---

## 🚀 EXECUTION INSTRUCTIONS FOR JULES

You are Jules, an AI agent with full repository context. Your mission:

1. **Start with Phase 3C-1** (Jules SDK): Implement JulesAsyncAdapter completely
   - Reference: https://github.com/AsyncFuncAI/julius-agent-sdk-python
   - Ensure async/await patterns correct
   - Implement retry + timeout logic
   - Write 8+ unit tests

2. **Move to Phase 3C-2** (Documentation): Reorganize all docs following governance
   - Run audit first to find violations
   - Move files to correct directories
   - Add YAML frontmatter everywhere
   - Update all cross-references
   - Verify 0 violations

3. **Complete with Phase 3C-3** (Testing): Setup testing infrastructure
   - Create pytest.ini + conftest.py
   - Complete integration tests
   - Setup GitHub Actions
   - Verify all tests pass

4. **Final checks**:
   - Run mypy, ruff, black
   - Verify all tests pass (100%)
   - Verify coverage >85%
   - Stage all changes
   - Create final commit

**Success**: All 3 workstreams complete, 0 errors, all tests passing, documentation perfect.

**Time Estimate**: 6-8 hours continuous work

---

**Generated**: 2025-11-03
**For**: Jules AI Agent (Google)
**Next Review**: After completion
