---
title: "Onboarding Enhancement Implementation Plan"
description: "A granular, task-based plan for the high-performance refactoring of the onboarding tool."
type: "task"
status: "draft"
created: "2025-11-02"
updated: "2025-11-02"
author: "Gemini"
tags:
  - "planning"
  - "onboarding"
  - "performance"
llm_summary: |
  This document provides a detailed, step-by-step task plan for implementing the onboarding performance enhancement. It breaks the refactoring effort into four main phases: creating a new Git Adapter, defining domain models, refactoring the core use case, and testing. Each task is granular and actionable.
---

# Onboarding Enhancement Implementation Plan

This document breaks down the work required to implement the feature described in `specs/features/onboarding-performance-enhancement.md`.

## Phase 1: Build the Core `GitAdapter`

**Goal:** Create a new, efficient, and asynchronous adapter for all Git operations.

---

### TASK-01: Create `GitAdapter` Structure
**Priority:** 🔴 CRITICAL | **Effort:** <1 hour | **Status:** ✅ COMPLETED

**Description:**
Create the basic file and class structure for the new `GitAdapter`.

**Implementation:**
- [ ] Create a new file: `src/cde_orchestrator/adapters/repository/git_adapter.py`.
- [ ] Define the `GitAdapter` class within this file.
- [ ] The constructor should accept a `project_root: Path`.

**Files Modified:**
- `src/cde_orchestrator/adapters/repository/git_adapter.py` (new file)

**Tests:**
- N/A (structure only)

**Acceptance Criteria:**
```python
# The following code should be possible
from src.cde_orchestrator.adapters.repository.git_adapter import GitAdapter
from pathlib import Path

adapter = GitAdapter(Path("."))
assert adapter is not None
```

---

### TASK-02: Implement Async Commit Iterator
**Priority:** 🔴 CRITICAL | **Effort:** 3 hours | **Status:** ✅ COMPLETED

**Description:**
Implement the `traverse_commits` async generator to efficiently stream the Git log.

**Implementation:**
- [ ] Create a private `_run_git_stream` method that uses `asyncio.create_subprocess_exec` to run a git command and yields lines from stdout.
- [ ] Create the public `async def traverse_commits(self) -> AsyncGenerator[Commit, None]:` method.
- [ ] This method will call `_run_git_stream` with `git log` and a specific `--pretty=format` string to easily parse commit metadata.
- [ ] For each line of output, parse it, create a `Commit` domain object (to be defined in Phase 2), and `yield` it.

**Files Modified:**
- `src/cde_orchestrator/adapters/repository/git_adapter.py`

**Tests:**
- `tests/integration/adapters/test_git_adapter.py` (new file)

**Acceptance Criteria:**
```python
# Test against a real Git repository fixture
async def test_traverse_commits_returns_commits():
    adapter = GitAdapter(Path("path/to/test/repo"))
    commits = [commit async for commit in adapter.traverse_commits()]
    assert len(commits) > 0
    assert isinstance(commits[0], Commit)
```

---

## Phase 2: Define Domain Models

**Goal:** Create clean, decoupled data structures for Git concepts.

---

### TASK-03: Create `Commit` and `Modification` Models
**Priority:** 🔴 CRITICAL | **Effort:** 1 hour | **Status:** ✅ COMPLETED

**Description:**
Define the `Commit` and `Modification` dataclasses in the domain layer.

**Implementation:**
- [ ] Create a new file: `src/cde_orchestrator/domain/git.py`.
- [ ] Define a `Modification` dataclass with fields like `change_type: str`, `old_path: Path`, `new_path: Path`.
- [ ] Define a `Commit` dataclass with fields like `hash: str`, `author: str`, `date: datetime`, `message: str`.
- [ ] The `Commit` class should also have a placeholder for modifications: `modifications: List[Modification] = field(default_factory=list)`.

**Files Modified:**
- `src/cde_orchestrator/domain/git.py` (new file)

**Tests:**
- `tests/unit/domain/test_git_models.py` (new file)

**Acceptance Criteria:**
```python
# Test the creation and properties of the models
def test_commit_model_creation():
    commit = Commit(
        hash="abcdef",
        author="Test Author",
        date=datetime.now(),
        message="Test commit"
    )
    assert commit.hash == "abcdef"
```

---

## Phase 3: Refactor the Onboarding Use Case

**Goal:** Simplify `OnboardingUseCase` to use the new adapter and models, removing old, slow logic.

---

### TASK-04: Integrate `GitAdapter` into `OnboardingUseCase`
**Priority:** 🟡 HIGH | **Effort:** 4 hours | **Status:** ✅ COMPLETED

**Description:**
Refactor `OnboardingUseCase` to replace its internal Git analysis with calls to the new `GitAdapter`.

**Implementation:**
- [ ] Modify the `OnboardingUseCase` constructor to accept an `IGitAdapter` port (create this new port interface in `domain/ports.py`).
- [ ] Remove the private `_analyze_git_history` method.
- [ ] In `needs_onboarding` and `generate_onboarding_plan`, use `git_adapter.traverse_commits()` to get the project history.
- [ ] Remove the `_synthesize_repository` method. The tech stack and file structure analysis should now be derived from the files listed in the latest commit from the `GitAdapter`, not from a full `rglob` scan.

**Files Modified:**
- `src/cde_orchestrator/application/onboarding/onboarding_use_case.py`
- `src/cde_orchestrator/domain/ports.py`

**Tests:**
- `tests/unit/application/onboarding/test_onboarding_use_case.py` (refactor existing tests)

**Acceptance Criteria:**
```python
# Test that the use case correctly uses the adapter
@pytest.mark.asyncio
async def test_onboarding_plan_uses_git_adapter():
    mock_adapter = Mock(spec=IGitAdapter)
    mock_adapter.traverse_commits.return_value = mock_commits_async_generator()

    use_case = OnboardingUseCase(Path("."), git_adapter=mock_adapter)
    plan = await use_case.generate_onboarding_plan()

    mock_adapter.traverse_commits.assert_called_once()
```

---

### TASK-05: Implement Lazy Loading for Modifications
**Priority:** 🟡 HIGH | **Effort:** 2 hours | **Status:** ✅ COMPLETED

**Description:**
Add the lazy-loading logic for commit modifications to the `GitAdapter`.

**Implementation:**
- [ ] Add a new method to `GitAdapter`: `async def get_modifications(self, commit_hash: str) -> List[Modification]:`.
- [ ] This method will use `_run_git_stream` to execute `git show --name-status <commit_hash>`.
- [ ] It will parse the output to create a list of `Modification` objects.
- [ ] The `Commit` domain model will *not* call this automatically. The use case will call it only when modification details are needed.

**Files Modified:**
- `src/cde_orchestrator/adapters/repository/git_adapter.py`

**Tests:**
- `tests/integration/adapters/test_git_adapter.py`

**Acceptance Criteria:**
```python
# Test that modifications are loaded correctly
async def test_get_modifications_returns_modifications():
    adapter = GitAdapter(Path("path/to/test/repo"))
    # Get a known commit hash from the test repo
    commit_hash = "..."
    modifications = await adapter.get_modifications(commit_hash)
    assert len(modifications) > 0
    assert isinstance(modifications[0], Modification)
```

---

## Phase 4: Cleanup and Finalization

**Goal:** Remove old code and ensure the new implementation is fully integrated.

---

### TASK-06: Deprecate and Remove `RepoIngestor`
**Priority:** 🟢 MEDIUM | **Effort:** 1 hour | **Status:** ✅ COMPLETED

**Description:**
With the new `GitAdapter`, the old `RepoIngestor` is no longer needed.

**Implementation:**
- [ ] Remove the `RepoIngestor` class from `src/cde_orchestrator/adapters/repository/repository_adapter.py`.
- [ ] Remove the call to `RepoIngestor` from the `cde_onboardingProject` tool in `src/server.py`.
- [ ] Ensure the `repo_digest` context variable is now populated with data from the `GitAdapter` instead.

**Files Modified:**
- `src/cde_orchestrator/adapters/repository/repository_adapter.py`
- `src/server.py`

**Tests:**
- N/A (removal of code)

**Acceptance Criteria:**
- The `cde_onboardingProject` tool must function correctly without `RepoIngestor`.
- A code search for `RepoIngestor` should yield no results.

---
