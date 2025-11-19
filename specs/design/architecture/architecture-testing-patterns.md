---
title: "CDE Orchestrator MCP - Testing Strategy & LLM Patterns"
description: "Testing approach and LLM interaction patterns for hexagonal architecture"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Orchestrator Team"
tags:
  - "architecture"
  - "testing"
  - "llm-optimization"
  - "context-management"
llm_summary: |
  Testing strategy (unit/integration/E2E) for hexagonal architecture plus LLM
  optimization patterns (progressive disclosure, context budgets, token efficiency).
  Covers test organization, mocking, and context management.
---

# Testing Strategy & LLM Patterns

> **Part of**: [Architecture Documentation](README.md)
> **Purpose**: Testing approach + LLM optimization guidelines

## Part 1: Testing Strategy

### Testing Pyramid

```
        /\
       /E2E\         <- Few, expensive, full system
      /------\
     /  INT   \      <- Moderate, with real I/O
    /----------\
   /   UNIT     \    <- Many, fast, isolated
  /--------------\
```

**Distribution**:
- 70% Unit Tests (domain logic)
- 20% Integration Tests (adapters)
- 10% End-to-End Tests (full workflows)

---

### Unit Tests (Domain Layer)

**Purpose**: Test business logic in isolation

**Characteristics**:
- ✅ No I/O
- ✅ No external dependencies
- ✅ Fast execution (<1ms per test)
- ✅ Deterministic

```python
# tests/unit/domain/test_project.py

from cde_orchestrator.domain.entities import Project, ProjectStatus
from cde_orchestrator.domain.exceptions import InvalidStateTransitionError
import pytest

class TestProject:
    def test_create_project_initializes_correctly(self):
        """Project creation sets proper defaults."""
        project = Project.create(name="Test", path="/tmp/test")

        assert project.name == "Test"
        assert project.path == "/tmp/test"
        assert project.status == ProjectStatus.CREATED
        assert len(project.features) == 0

    def test_activate_project_changes_status(self):
        """Activation transitions from CREATED to ACTIVE."""
        project = Project.create("Test", "/tmp/test")

        project.activate()

        assert project.status == ProjectStatus.ACTIVE

    def test_start_feature_requires_active_project(self):
        """Cannot start feature on non-active project."""
        project = Project.create("Test", "/tmp/test")
        # Project is CREATED, not ACTIVE

        with pytest.raises(InvalidStateTransitionError):
            project.start_feature("Add login")

    def test_start_feature_creates_feature_entity(self):
        """Starting feature creates Feature entity."""
        project = Project.create("Test", "/tmp/test")
        project.activate()

        feature = project.start_feature("Add login")

        assert feature.prompt == "Add login"
        assert len(project.features) == 1
        assert project.features[0] == feature
```

---

### Integration Tests (Adapters)

**Purpose**: Test adapters with real I/O

**Characteristics**:
- ✅ Uses real filesystem/network
- ✅ Tests adapter implementation
- ✅ Slower than unit tests (~10-100ms)
- ✅ May require setup/teardown

```python
# tests/integration/adapters/test_filesystem_repo.py

from cde_orchestrator.adapters.filesystem_project_repository import FileSystemProjectRepository
from cde_orchestrator.domain.entities import Project
import tempfile
import shutil
from pathlib import Path

class TestFileSystemProjectRepository:
    def setup_method(self):
        """Create temporary directory for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.repo = FileSystemProjectRepository(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_save_creates_state_file(self):
        """Saving project creates .cde/state.json."""
        project = Project.create("TestProject", str(self.temp_dir / "project"))

        self.repo.save(project)

        state_file = self.temp_dir / "project" / ".cde" / "state.json"
        assert state_file.exists()

    def test_save_and_load_round_trip(self):
        """Saved project can be loaded correctly."""
        original = Project.create("TestProject", str(self.temp_dir / "project"))
        original.activate()
        original.start_feature("Add login")

        self.repo.save(original)
        loaded = self.repo.get_by_path(str(self.temp_dir / "project"))

        assert loaded.name == original.name
        assert loaded.status == original.status
        assert len(loaded.features) == len(original.features)

    def test_list_all_returns_multiple_projects(self):
        """List all finds multiple saved projects."""
        proj1 = Project.create("Proj1", str(self.temp_dir / "proj1"))
        proj2 = Project.create("Proj2", str(self.temp_dir / "proj2"))

        self.repo.save(proj1)
        self.repo.save(proj2)

        all_projects = self.repo.list_all()

        assert len(all_projects) == 2
        assert {p.name for p in all_projects} == {"Proj1", "Proj2"}
```

---

### End-to-End Tests (Use Cases)

**Purpose**: Test complete workflows

**Characteristics**:
- ✅ Full system integration
- ✅ Tests use cases with real adapters
- ✅ Slowest tests (~100ms-1s)
- ✅ Validates entire flow

```python
# tests/integration/test_workflow.py

from cde_orchestrator.infrastructure.di_container import DIContainer
import tempfile
import shutil
from pathlib import Path

class TestCompleteWorkflow:
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.container = DIContainer.create_default(registry_path=self.temp_dir)

    def teardown_method(self):
        """Cleanup."""
        shutil.rmtree(self.temp_dir)

    async def test_complete_feature_workflow(self):
        """End-to-end workflow: start → define → decompose → implement."""
        # 1. Create project
        manage_use_case = self.container.get_manage_project_use_case()
        project_result = manage_use_case.create_project(
            name="TestProject",
            path=str(self.temp_dir / "project")
        )
        project_id = project_result["project_id"]

        # 2. Start feature
        start_use_case = self.container.get_start_feature_use_case()
        feature_result = start_use_case.execute(project_id, "Add user authentication")

        assert feature_result["status"] == "success"
        assert feature_result["phase"] == "define"
        feature_id = feature_result["feature_id"]

        # 3. Submit define phase
        submit_use_case = self.container.get_submit_work_use_case()
        define_result = submit_use_case.execute(
            project_id=project_id,
            feature_id=feature_id,
            phase_id="define",
            results={"specification": "# Auth Spec..."}
        )

        assert define_result["phase"] == "decompose"

        # 4. Submit decompose phase
        decompose_result = submit_use_case.execute(
            project_id=project_id,
            feature_id=feature_id,
            phase_id="decompose",
            results={"tasks": ["Task 1", "Task 2"]}
        )

        assert decompose_result["phase"] == "design"
```

---

### Test Organization

```
tests/
├── unit/                       # Domain logic (no I/O)
│   ├── domain/
│   │   ├── test_project.py
│   │   ├── test_feature.py
│   │   └── test_value_objects.py
│   └── application/
│       └── test_use_cases.py   # With mocked ports
│
├── integration/                # With real adapters
│   ├── adapters/
│   │   ├── test_filesystem_repo.py
│   │   ├── test_yaml_workflow_engine.py
│   │   └── test_copilot_cli_adapter.py
│   └── test_workflow.py        # E2E with real components
│
└── mocks/                      # Mock implementations
    ├── mock_repository.py
    ├── mock_executor.py
    └── mock_workflow_engine.py
```

---

### Mocking Strategy

```python
# tests/mocks/mock_repository.py

from cde_orchestrator.domain.ports import IProjectRepository
from cde_orchestrator.domain.entities import Project
from typing import List, Optional

class MockProjectRepository(IProjectRepository):
    """In-memory project repository for testing."""

    def __init__(self):
        self._projects = {}

    def save(self, project: Project):
        self._projects[project.id] = project

    def get_by_id(self, project_id: str) -> Optional[Project]:
        return self._projects.get(project_id)

    def get_by_path(self, path: str) -> Optional[Project]:
        for p in self._projects.values():
            if p.path == path:
                return p
        return None

    def list_all(self) -> List[Project]:
        return list(self._projects.values())

    def delete(self, project_id: str):
        if project_id in self._projects:
            del self._projects[project_id]
```

---

## Part 2: LLM Interaction Patterns

### Pattern 1: Progressive Disclosure

**Problem**: Loading all project contexts consumes millions of tokens

**Solution**: Load details on-demand with `detail_level` parameter

```python
# Example: Scanning 1000 projects

# Step 1: Get names only (~390 bytes for 1000 projects)
all_projects = cde_listProjects(detail_level="name_only")
# Returns: ["CDE Orchestrator", "MyWebApp", ...]

# Step 2: Filter with summary (~15KB for 1000 projects)
summaries = cde_listProjects(detail_level="summary")
auth_projects = [p for p in summaries if "auth" in p["name"].lower()]

# Step 3: Full detail ONLY for active project
full_project = cde_getProjectInfo(
    project_path="E:\\scripts-python\\CDE",
    detail_level="full"
)
```

**Token Savings**:
- Traditional: 1000 projects × 40KB = 40MB
- Progressive: 390B + 15KB + 40KB = ~55KB
- **Reduction: 99.86%**

---

### Pattern 2: Context Budget Management

**Problem**: LLM context windows limited (100K-200K tokens)

**Solution**: Strict token budgets per operation

```python
# Token allocation strategy

CONTEXT_BUDGET = {
    "system_prompt": 2000,       # Instructions
    "user_request": 1000,        # Current request
    "workflow_state": 5000,      # Feature/phase context
    "code_context": 50000,       # Relevant source code
    "documentation": 10000,      # Specs/design docs
    "examples": 5000,            # Code examples
    "buffer": 27000              # Safety margin
}

# Total: 100,000 tokens (Claude Sonnet limit)
```

**Implementation**:

```python
def prepare_prompt(user_request: str, feature: Feature) -> str:
    """Build prompt within token budget."""
    components = []

    # System prompt (fixed)
    components.append(load_system_prompt())  # 2000 tokens

    # User request
    components.append(f"User request: {user_request}")  # ~1000 tokens

    # Workflow state
    components.append(feature.to_context_string())  # ~5000 tokens

    # Code context (selective)
    relevant_files = find_relevant_files(user_request)
    code_context = load_code_context(relevant_files[:10])  # Limit to 10 files
    components.append(code_context)  # ~50000 tokens

    # Check budget
    total_tokens = estimate_tokens("\n".join(components))
    if total_tokens > 100000:
        # Trim code context
        code_context = load_code_context(relevant_files[:5])
        components[-1] = code_context

    return "\n".join(components)
```

---

### Pattern 3: Stateless Operations

**Problem**: Maintaining state across multi-project workflows is expensive

**Solution**: Stateless design where agent provides context

```python
# ✅ CORRECT: Stateless (agent knows context)
cde_startFeature(
    project_path="E:\\scripts-python\\CDE",  # Agent specifies
    user_prompt="Add authentication"
)

# ❌ WRONG: Stateful (MCP tracks "current project")
cde_setCurrentProject("CDE")
cde_startFeature("Add authentication")  # Implicit project
```

**Benefits**:
- No state synchronization issues
- Works with multiple projects simultaneously
- Simpler MCP server implementation

---

### Testing with Token Budgets

```python
# tests/test_context_management.py

def test_prompt_stays_within_budget():
    """Generated prompts don't exceed token limit."""
    user_request = "Implement OAuth2 authentication"
    feature = create_test_feature()

    prompt = prepare_prompt(user_request, feature)
    token_count = estimate_tokens(prompt)

    assert token_count < 100000, f"Prompt too large: {token_count} tokens"

def test_progressive_disclosure_reduces_tokens():
    """Progressive loading saves tokens."""
    # Full load
    full_data = cde_scanDocumentation(".", detail_level="full")
    full_tokens = estimate_tokens(json.dumps(full_data))

    # Name only
    names_data = cde_scanDocumentation(".", detail_level="name_only")
    names_tokens = estimate_tokens(json.dumps(names_data))

    reduction = (full_tokens - names_tokens) / full_tokens
    assert reduction > 0.90, f"Expected 90%+ reduction, got {reduction:.1%}"
```

---

## Next Steps

- **Review Architecture**: See [Architecture Overview](architecture-overview.md)
- **Understand Domain**: See [Domain Layer](architecture-domain-layer.md)
- **Learn Use Cases**: See [Use Cases](architecture-use-cases.md)

---

*This document is part of the modular architecture documentation. See [README](README.md) for full navigation.*
