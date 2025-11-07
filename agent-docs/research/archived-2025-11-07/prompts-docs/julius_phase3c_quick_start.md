---
title: "Jules Phase 3C - Quick Start Guide"
description: "Quick execution guide for Jules AI agent - what to do right now"
type: "execution"
status: "active"
created: "2025-11-03"
updated: "2025-11-03"
author: "CDE System"
llm_summary: |
  Quick action guide for Jules AI agent. Complete 3 workstreams: (1) Jules SDK,
  (2) Documentation governance, (3) Testing infrastructure. Full instructions in master prompt.
---

# ⚡ Jules Phase 3C - Quick Start (TL;DR)

**Target**: You (Jules AI Agent)  
**Current Time**: Estimated 6-8 hours of work  
**Success Criteria**: All tests pass, 0 doc violations, full SDK working

---

## 🎯 Your Mission (3 Workstreams)

### PART 1️⃣: Jules SDK Configuration (2-3 hours)

**What**: Complete implementation of `JulesAsyncAdapter` for async agent task execution

**Files to Create/Modify**:
- ✏️ `src/cde_orchestrator/adapters/agents/julius_async_adapter.py` - Expand implementation
- ✏️ `src/server.py` - Update `cde_delegateToJules` MCP tool
- ✨ `tests/unit/adapters/agents/test_julius_async_adapter.py` - Add 8+ tests

**Key Requirements**:
- Async/await pattern (reference: `code_cli_adapters.py`)
- Error handling: API key validation, timeouts, retries with exponential backoff
- Session persistence to `.cde/sessions/`
- Plan approval workflow support
- Full repository context handling (100k+ lines)

**How to Know It's Done**:
- All 8+ tests pass with >85% coverage
- `pytest tests/unit/adapters/agents/test_julius_async_adapter.py -v` succeeds
- `mypy src/cde_orchestrator/adapters/agents/ --strict` passes
- MCP tool `cde_delegateToJules` works end-to-end

**Reference**:
- Jules SDK: https://github.com/AsyncFuncAI/julius-agent-sdk-python
- Full details: `agent-docs/prompts/JULES_MASTER_PROMPT_PHASE3C.md` lines 108-267

---

### PART 2️⃣: Documentation Distribution (2-3 hours)

**What**: Reorganize all docs following `DOCUMENTATION_GOVERNANCE.md` - ZERO violations!

**Files to Audit/Reorganize**:
- ~20 documentation files need movement + metadata
- Create 5 new index files
- Fix ~30 broken cross-references

**Target Structure**:
```
✅ ALLOWED (root): README.md, CHANGELOG.md, CONTRIBUTING.md, LICENSE, AGENTS.md

📁 specs/features/ - Features
📁 specs/design/ - Architecture  
📁 specs/tasks/ - Roadmap
📁 specs/governance/ - Rules
📁 docs/ - User guides
📁 agent-docs/ - AI outputs (sessions, execution, feedback, research)
```

**Step-by-Step**:
1. **Find violations**: Run `cde_scanDocumentation(".")` to audit
2. **Move files**: Use `git mv` to reorganize  
3. **Add metadata**: Every .md file needs YAML frontmatter
4. **Fix links**: Update all cross-references
5. **Validate**: Run `python scripts/validation/validate-docs.py` - must show 0 violations

**How to Know It's Done**:
- `cde_analyzeDocumentation(".")` returns quality_score >= 95
- Script shows "✅ All documentation compliant"
- All 45+ docs have YAML frontmatter
- No broken links (cde_analyzeDocumentation reports 0 broken)

**Reference**: `specs/governance/DOCUMENTATION_GOVERNANCE.md` + `agent-docs/prompts/JULES_MASTER_PROMPT_PHASE3C.md` lines 268-480

---

### PART 3️⃣: Testing Infrastructure (2 hours)

**What**: Setup pytest + CI/CD pipeline for automated testing

**Files to Create**:
- ✨ `pytest.ini` - Test configuration
- ✨ `tests/conftest.py` - Shared fixtures (10+ fixtures)
- ✏️ `tests/integration/adapters/agents/test_cli_adapters.py` - Complete existing tests
- ✨ `.github/workflows/tests.yml` - GitHub Actions CI/CD

**Quick Checklist**:
- [ ] pytest.ini created with coverage config
- [ ] conftest.py has fixtures for: tmp_project, mock_repo, mock_executor, etc.
- [ ] Integration tests for CLI adapters completed (15+ tests)
- [ ] GitHub Actions workflow tests Python 3.11 + 3.12
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage >85%: `pytest tests/ --cov=src/cde_orchestrator --cov-report=term-missing`

**How to Know It's Done**:
- `pytest tests/` returns "XXX passed" (all tests green)
- Coverage report shows >85% for new code
- GitHub Actions workflow runs successfully on push

**Reference**: `agent-docs/prompts/JULES_MASTER_PROMPT_PHASE3C.md` lines 481-600

---

## 📋 Order of Execution

**SEQUENTIAL** (do in this order):

1. **Phase 3C-1 FIRST** (2-3 hours)
   - Implement JulesAsyncAdapter
   - Add tests
   - Verify all pass
   - COMMIT: "feat: Complete Jules SDK async adapter integration"

2. **Phase 3C-2 SECOND** (2-3 hours)
   - Audit docs
   - Reorganize files
   - Add metadata
   - Create validation script
   - COMMIT: "docs: Reorganize documentation following DOCUMENTATION_GOVERNANCE"

3. **Phase 3C-3 LAST** (2 hours)
   - Create pytest.ini
   - Create conftest.py
   - Complete integration tests
   - Create GitHub Actions workflow
   - COMMIT: "test: Setup testing infrastructure with pytest + CI/CD"

4. **Final Commit**:
   ```bash
   git add -A
   git commit -m "feat: Phase 3C complete - Jules SDK + Doc Governance + Testing

   - ✅ Phase 3C-1: Jules SDK complete with async/await + error handling + tests
   - ✅ Phase 3C-2: Documentation reorganized, 0 governance violations
   - ✅ Phase 3C-3: Testing infrastructure with pytest + GitHub Actions
   - All tests passing (100%), coverage >85%, code quality verified"
   ```

---

## 🔍 Quick Verification

After completing each phase, run:

```bash
# Phase 1 verification
pytest tests/unit/adapters/agents/test_julius_async_adapter.py -v

# Phase 2 verification
python scripts/validation/validate-docs.py  # Should show "✅ All documentation compliant"
cde_analyzeDocumentation(".")  # Should show quality_score >= 95

# Phase 3 verification
pytest tests/ -v --cov=src/cde_orchestrator --cov-report=term-missing

# Full verification
mypy src/ --strict
ruff check src/
black src/ tests/ --check
```

---

## 📚 Key Files You'll Need

**Read FIRST**:
- `agent-docs/prompts/JULIUS_MASTER_PROMPT_PHASE3C.md` (full 600-line prompt with all details)
- `specs/governance/DOCUMENTATION_GOVERNANCE.md` (documentation rules)
- `specs/design/ARCHITECTURE.md` (hexagonal pattern)

**Reference During Work**:
- `src/cde_orchestrator/adapters/agents/code_cli_adapters.py` (async patterns)
- `src/cde_orchestrator/service_connector.py` (error handling patterns)
- `tests/unit/adapters/agents/test_agent_selection_policy.py` (test patterns)
- `specs/tasks/improvement-roadmap.md` (roadmap context)

---

## 🎓 Remember These Principles

1. **Architecture**: Domain has NO external dependencies. Everything points inward.
2. **Async**: All I/O is async/await. No blocking operations in adapters.
3. **Testing**: >85% coverage. Test error cases, not just happy path.
4. **Documentation**: Every file has YAML frontmatter + correct directory location.
5. **Error Handling**: Descriptive errors with actionable context (not just stack traces).
6. **Type Safety**: Full type hints. `mypy --strict` must pass.

---

## ✅ Final Checklist Before "DONE"

- [ ] **Phase 3C-1**: JulesAsyncAdapter complete, 8+ tests passing, >85% coverage
- [ ] **Phase 3C-2**: All docs reorganized, 0 governance violations, quality_score >=95
- [ ] **Phase 3C-3**: pytest.ini + conftest.py + integration tests + GitHub Actions working
- [ ] **Code Quality**: `mypy src/ --strict` ✅ passes
- [ ] **Code Quality**: `ruff check src/` ✅ passes  
- [ ] **Code Quality**: `black src/ tests/` ✅ formatted
- [ ] **All Tests**: `pytest tests/` ✅ 100% passing
- [ ] **Git**: All changes staged and committed with detailed message
- [ ] **No uncommitted changes**: `git status` shows clean working directory

---

## 🚀 You Got This!

Full instructions in: `agent-docs/prompts/JULIUS_MASTER_PROMPT_PHASE3C.md`

**Time**: 6-8 hours continuous work  
**Outcome**: Production-ready multi-agent orchestrator with perfect documentation  
**Next**: Phase 3D+ from roadmap (if needed)

Go build! 💪

