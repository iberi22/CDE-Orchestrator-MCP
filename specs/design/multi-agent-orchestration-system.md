---
title: Multi-Agent Orchestration System - Jules & CLI Agents Integration
description: Comprehensive design for orchestrating multiple AI coding agents (Jules async, Gemini CLI, Qwen CLI, Copilot CLI) with dynamic task allocation and workflow management
type: design
status: active
created: 2025-11-03
updated: 2025-11-03
author: AI Architecture Team
tags:
  - architecture
  - jules
  - multi-agent
  - orchestration
  - cli-agents
  - async
  - workflow
llm_summary: |
  Architecture design for multi-agent orchestration system integrating Jules (async API),
  Gemini CLI, Qwen CLI, and Copilot CLI for intelligent task delegation and parallel execution.
  Implements hexagonal architecture with ICodeExecutor port for unified agent interface.
---

# Multi-Agent Orchestration System - Jules & CLI Agents Integration

> **Status**: Active Design
> **Priority**: 🔴 CRITICAL
> **Target**: Phase 3 Implementation
> **Architecture**: Hexagonal (Ports & Adapters)

---

## 📋 Executive Summary

### Objective

Create a robust, professional multi-agent orchestration system that:
1. **Integrates Jules** as an async AI agent via Python SDK
2. **Unifies CLI agents** (Gemini, Qwen, Copilot) under common interface
3. **Enables intelligent task delegation** based on agent capabilities
4. **Supports parallel execution** for independent tasks
5. **Provides failover mechanisms** when agents are unavailable

### Key Innovation

**Hexagonal Architecture + Agent Polymorphism**
- Single `ICodeExecutor` port → Multiple agent adapters
- CDE orchestrates agents without knowing implementation details
- Easy to add new agents (just implement the port)

---

## 🏗️ Architecture Overview

### Current State (Baseline)

```
CDE Orchestrator MCP
├── ICodeExecutor Port (domain/ports.py)
│   └── execute_prompt(project_path, prompt, context) -> str
│
└── Adapters (partially implemented)
    ├── CopilotCLIAdapter ✅ (specs only, not implemented)
    ├── GeminiCLIAdapter ✅ (llm_cli_adapter.py)
    ├── QwenCLIAdapter ✅ (llm_cli_adapter.py)
    └── MultiProviderLLMCLIAdapter ✅ (llm_cli_adapter.py)
```

### Target State (Phase 3)

```
CDE Orchestrator MCP
├── Domain Layer
│   ├── ICodeExecutor Port (unified interface)
│   └── AgentCapability Enum (task type routing)
│
├── Application Layer
│   ├── AgentOrchestratorUseCase (intelligent task delegation)
│   └── ParallelExecutionUseCase (concurrent task execution)
│
└── Adapters Layer
    ├── Jules Adapter (async API)
    │   ├── JulesAsyncAdapter(ICodeExecutor)
    │   └── SDK: jules-agent-sdk-python
    │
    ├── CLI Adapters (sync/async)
    │   ├── CopilotCLIAdapter(ICodeExecutor)
    │   ├── GeminiCLIAdapter(ICodeExecutor)
    │   ├── QwenCLIAdapter(ICodeExecutor)
    │   └── MultiAgentCLIAdapter (unified facade)
    │
    └── Fallback Strategy
        └── AgentSelectionPolicy (capability-based routing)
```

---

## 🎯 Design Principles

### 1. Hexagonal Architecture

**Core Tenet**: Business logic (domain) must not depend on infrastructure (adapters).

```python
# ✅ CORRECT: Domain defines interface
class ICodeExecutor(ABC):
    @abstractmethod
    async def execute_prompt(
        self, project_path: Path, prompt: str, context: Dict[str, Any]
    ) -> ExecutionResult:
        pass

# ✅ CORRECT: Adapter implements interface
class JulesAsyncAdapter(ICodeExecutor):
    async def execute_prompt(self, project_path, prompt, context):
        # Jules-specific implementation
        session = await self.client.sessions.create(...)
        return ExecutionResult(...)
```

### 2. Agent Capability Model

Each agent has strengths and weaknesses:

| Agent | Type | Strengths | Limitations | Use Case |
|-------|------|-----------|-------------|----------|
| **Jules** | Async API | Full repo context, long-running tasks, plan approval | API key required, cloud-only | Complex features, refactoring |
| **Copilot CLI** | Sync CLI | GitHub integration, code suggestions | Limited context window | Quick fixes, code generation |
| **Gemini CLI** | Sync CLI | Fast responses, code understanding | No plan approval | Documentation, analysis |
| **Qwen CLI** | Sync CLI | Alternative fallback | Less accurate | Backup option |

### 3. Task Delegation Strategy

```python
class TaskComplexity(Enum):
    TRIVIAL = "trivial"       # < 5 min → Copilot/Gemini CLI
    SIMPLE = "simple"         # 15-30 min → Copilot/Gemini CLI
    MODERATE = "moderate"     # 1-2 hours → Jules or CLI with supervision
    COMPLEX = "complex"       # 4-8 hours → Jules (async, long-running)
    EPIC = "epic"             # 2-5 days → Jules (plan approval required)

class AgentCapability(Enum):
    QUICK_FIX = "quick_fix"           # CLI agents preferred
    CODE_GENERATION = "code_gen"      # CLI agents sufficient
    REFACTORING = "refactor"          # Jules preferred (full context)
    FEATURE_DEVELOPMENT = "feature"   # Jules preferred (complex logic)
    DOCUMENTATION = "docs"            # CLI agents sufficient
```

---

## 📐 Detailed Design

### Phase 3A: Jules Async Adapter

#### Jules Adapter Implementation

```python
# src/cde_orchestrator/adapters/agents/jules_async_adapter.py

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

from jules_agent_sdk import AsyncJulesClient
from jules_agent_sdk.models import SessionState

from ...domain.ports import ICodeExecutor
from ...domain.exceptions import AgentExecutionError


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    session_id: str
    state: str
    modified_files: list[str]
    activities: list[Dict[str, Any]]
    log: str
    metadata: Dict[str, Any]


class JulesAsyncAdapter(ICodeExecutor):
    """
    Jules async agent adapter.

    Uses jules-agent-sdk-python for async task delegation.

    Features:
        - Full repository context
        - Long-running task support
        - Plan approval workflow
        - Activity monitoring
        - Session persistence

    Requirements:
        - JULES_API_KEY environment variable
        - jules-agent-sdk installed (pip install jules-agent-sdk)
        - Repository connected to Jules (sources)
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        default_timeout: int = 1800,  # 30 minutes
        require_plan_approval: bool = False
    ):
        """
        Initialize Jules adapter.

        Args:
            api_key: Jules API key (from environment)
            base_url: Optional custom API endpoint
            default_timeout: Default timeout for wait_for_completion (seconds)
            require_plan_approval: Whether to require manual plan approval
        """
        self.api_key = api_key
        self.base_url = base_url
        self.default_timeout = default_timeout
        self.require_plan_approval = require_plan_approval
        self._client: Optional[AsyncJulesClient] = None

    async def _get_client(self) -> AsyncJulesClient:
        """Get or create Jules client (lazy initialization)."""
        if self._client is None:
            self._client = AsyncJulesClient(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    async def execute_prompt(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Execute code generation with Jules.

        Workflow:
            1. Resolve project to Jules source
            2. Create Jules session
            3. Optionally approve plan
            4. Wait for completion (or return async if detached)
            5. Collect activities and results

        Args:
            project_path: Absolute path to project
            prompt: Task description
            context: Additional context
                - branch: Starting branch (default: main)
                - timeout: Override default timeout
                - detached: Don't wait for completion (default: False)
                - require_plan_approval: Override default

        Returns:
            ExecutionResult with session details and outcomes

        Raises:
            AgentExecutionError: If Jules fails or session errors
        """
        client = await self._get_client()

        try:
            # 1. Resolve source
            source_id = await self._resolve_source(client, project_path)

            # 2. Extract context
            branch = context.get("branch", "main")
            timeout = context.get("timeout", self.default_timeout)
            detached = context.get("detached", False)
            require_approval = context.get(
                "require_plan_approval",
                self.require_plan_approval
            )

            # 3. Create session
            session = await client.sessions.create(
                prompt=prompt,
                source=source_id,
                starting_branch=branch,
                require_plan_approval=require_approval
            )

            # 4. Handle plan approval if required
            if require_approval:
                session = await self._handle_plan_approval(client, session.id)

            # 5. Wait for completion (unless detached)
            if not detached:
                session = await client.sessions.wait_for_completion(
                    session.id,
                    poll_interval=5,
                    timeout=timeout
                )

            # 6. Collect activities
            activities = await client.activities.list_all(session.id)

            # 7. Extract modified files (from activities)
            modified_files = self._extract_modified_files(activities)

            return ExecutionResult(
                success=(session.state == SessionState.COMPLETED),
                session_id=session.id,
                state=session.state.value,
                modified_files=modified_files,
                activities=[self._activity_to_dict(a) for a in activities],
                log=self._format_activities_log(activities),
                metadata={
                    "session_url": session.url,
                    "prompt": prompt,
                    "source": source_id,
                    "branch": branch,
                }
            )

        except Exception as e:
            raise AgentExecutionError(
                f"Jules execution failed: {str(e)}",
                agent="jules",
                project_path=str(project_path)
            ) from e

    async def _resolve_source(
        self,
        client: AsyncJulesClient,
        project_path: Path
    ) -> str:
        """
        Resolve project path to Jules source ID.

        Logic:
            1. Check if project has .jules/source_id file (cached)
            2. Search Jules sources by GitHub repo URL
            3. Fallback: Search by project name
        """
        # Check cache
        cache_file = project_path / ".jules" / "source_id"
        if cache_file.exists():
            return cache_file.read_text().strip()

        # Get project Git remote
        git_remote = self._get_git_remote(project_path)

        # Search Jules sources
        sources = await client.sources.list_all()

        # Match by GitHub repo
        if git_remote:
            for source in sources:
                if source.github_repo:
                    repo_url = f"{source.github_repo.owner}/{source.github_repo.repo}"
                    if git_remote.endswith(repo_url):
                        # Cache for future
                        cache_file.parent.mkdir(exist_ok=True)
                        cache_file.write_text(source.name)
                        return source.name

        # Match by project name
        project_name = project_path.name
        for source in sources:
            if source.github_repo and source.github_repo.repo == project_name:
                cache_file.parent.mkdir(exist_ok=True)
                cache_file.write_text(source.name)
                return source.name

        raise AgentExecutionError(
            f"No Jules source found for project: {project_path}. "
            f"Connect the repository at https://jules.google/",
            agent="jules",
            project_path=str(project_path)
        )

    def _get_git_remote(self, project_path: Path) -> Optional[str]:
        """Extract Git remote URL from project."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    async def _handle_plan_approval(
        self,
        client: AsyncJulesClient,
        session_id: str
    ) -> Any:
        """
        Wait for plan generation and approve automatically or prompt user.

        For now: Auto-approve after plan is generated.
        Future: Interactive approval in MCP UI.
        """
        # Wait for plan to be generated
        while True:
            session = await client.sessions.get(session_id)

            if session.state == SessionState.AWAITING_PLAN_APPROVAL:
                # Auto-approve (for now)
                await client.sessions.approve_plan(session_id)
                return session

            if session.state in [SessionState.FAILED, SessionState.COMPLETED]:
                return session

            await asyncio.sleep(2)

    def _extract_modified_files(self, activities: list) -> list[str]:
        """Extract list of modified files from activities."""
        files = []
        for activity in activities:
            if activity.code_change_made:
                change = activity.code_change_made
                if "files" in change:
                    files.extend(change["files"])
        return list(set(files))

    def _activity_to_dict(self, activity) -> Dict[str, Any]:
        """Convert Activity model to dict."""
        return {
            "id": activity.id,
            "description": activity.description,
            "originator": activity.originator,
            "create_time": str(activity.create_time),
            "agent_messaged": activity.agent_messaged,
            "code_change_made": activity.code_change_made,
            "plan_generated": activity.plan_generated,
        }

    def _format_activities_log(self, activities: list) -> str:
        """Format activities into human-readable log."""
        lines = ["Jules Session Activity Log:", "=" * 50]
        for i, activity in enumerate(activities, 1):
            lines.append(f"\n{i}. {activity.description}")
            lines.append(f"   Time: {activity.create_time}")
            lines.append(f"   Originator: {activity.originator}")

            if activity.agent_messaged:
                msg = activity.agent_messaged.get("agentMessage", "")
                if msg:
                    lines.append(f"   Message: {msg[:100]}...")

        return "\n".join(lines)

    async def close(self):
        """Close Jules client connection."""
        if self._client:
            await self._client.close()
            self._client = None
```

#### Environment Setup Script

```bash
# .jules/setup.sh - Jules VM environment setup

#!/bin/bash
set -e

echo "🔧 CDE Orchestrator MCP - Jules Environment Setup"
echo "=================================================="

# 1. Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 2. Verify Python tools
echo "✅ Python environment:"
python --version
pip --version

# 3. Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# 4. Run tests to verify setup
echo "🧪 Running tests..."
pytest tests/ -v --tb=short

# 5. Check code quality
echo "🔍 Checking code quality..."
ruff check src/ --select I,E,F,B,SIM
black src/ tests/ --check

# 6. Type checking
echo "🔬 Type checking..."
mypy src/ --ignore-missing-imports

echo ""
echo "✅ Environment setup complete!"
echo "Ready for Jules execution."
```

### Phase 3B: Multi-Agent Orchestrator

#### Agent Selection Policy

```python
# src/cde_orchestrator/adapters/agents/multi_agent_orchestrator.py

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

from ...domain.ports import ICodeExecutor


class AgentType(Enum):
    JULES = "jules"
    COPILOT = "copilot"
    GEMINI = "gemini"
    QWEN = "qwen"


class TaskComplexity(Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EPIC = "epic"


@dataclass
class AgentCapabilities:
    """Agent capability matrix."""
    agent_type: AgentType
    supports_async: bool
    supports_plan_approval: bool
    max_context_lines: int
    best_for: list[str]
    requires_auth: bool


class AgentSelectionPolicy:
    """
    Intelligent agent selection based on task characteristics.

    Selection Criteria:
        1. Task complexity (trivial → epic)
        2. Required capabilities (async, plan approval, context size)
        3. Agent availability (API key, CLI installed)
        4. Fallback chain (Jules → Copilot → Gemini → Qwen)
    """

    CAPABILITIES = {
        AgentType.JULES: AgentCapabilities(
            agent_type=AgentType.JULES,
            supports_async=True,
            supports_plan_approval=True,
            max_context_lines=100000,  # Full repo
            best_for=["refactoring", "feature_development", "complex_tasks"],
            requires_auth=True
        ),
        AgentType.COPILOT: AgentCapabilities(
            agent_type=AgentType.COPILOT,
            supports_async=False,
            supports_plan_approval=False,
            max_context_lines=5000,
            best_for=["quick_fixes", "code_generation", "suggestions"],
            requires_auth=True
        ),
        AgentType.GEMINI: AgentCapabilities(
            agent_type=AgentType.GEMINI,
            supports_async=False,
            supports_plan_approval=False,
            max_context_lines=8000,
            best_for=["documentation", "analysis", "quick_fixes"],
            requires_auth=False  # CLI auth
        ),
        AgentType.QWEN: AgentCapabilities(
            agent_type=AgentType.QWEN,
            supports_async=False,
            supports_plan_approval=False,
            max_context_lines=4000,
            best_for=["fallback"],
            requires_auth=False
        ),
    }

    @classmethod
    def select_agent(
        cls,
        task_complexity: TaskComplexity,
        require_plan_approval: bool,
        context_size: int,
        available_agents: list[AgentType]
    ) -> AgentType:
        """
        Select best agent for task.

        Logic:
            1. If EPIC or COMPLEX → Prefer Jules (if available)
            2. If plan approval required → Jules only
            3. If context > 5000 lines → Jules or Gemini
            4. Otherwise → First available in [Copilot, Gemini, Qwen]
        """
        # Plan approval → Jules only
        if require_plan_approval:
            if AgentType.JULES in available_agents:
                return AgentType.JULES
            raise ValueError("Plan approval requires Jules, but Jules is not available")

        # Complex/Epic → Jules preferred
        if task_complexity in [TaskComplexity.COMPLEX, TaskComplexity.EPIC]:
            if AgentType.JULES in available_agents:
                return AgentType.JULES

        # Large context → Jules or Gemini
        if context_size > 5000:
            for agent in [AgentType.JULES, AgentType.GEMINI]:
                if agent in available_agents:
                    return agent

        # Default fallback chain
        for agent in [AgentType.COPILOT, AgentType.GEMINI, AgentType.QWEN]:
            if agent in available_agents:
                return agent

        raise ValueError("No suitable agent available for task")


class MultiAgentOrchestrator(ICodeExecutor):
    """
    Multi-agent orchestrator with intelligent delegation.

    Features:
        - Automatic agent selection
        - Fallback chain
        - Parallel execution for independent tasks
        - Unified result aggregation
    """

    def __init__(
        self,
        jules_adapter: Optional[JulesAsyncAdapter] = None,
        copilot_adapter: Optional[ICodeExecutor] = None,
        gemini_adapter: Optional[ICodeExecutor] = None,
        qwen_adapter: Optional[ICodeExecutor] = None
    ):
        """Initialize with available adapters."""
        self.adapters = {
            AgentType.JULES: jules_adapter,
            AgentType.COPILOT: copilot_adapter,
            AgentType.GEMINI: gemini_adapter,
            AgentType.QWEN: qwen_adapter,
        }
        self.policy = AgentSelectionPolicy()

    def get_available_agents(self) -> list[AgentType]:
        """List currently available agents."""
        return [
            agent_type
            for agent_type, adapter in self.adapters.items()
            if adapter is not None
        ]

    async def execute_prompt(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Execute prompt with best available agent.

        Context keys:
            - complexity: TaskComplexity enum (default: MODERATE)
            - require_plan_approval: bool (default: False)
            - context_size: int (lines of context, default: 1000)
            - preferred_agent: AgentType (optional override)
        """
        # Extract task parameters
        complexity = context.get("complexity", TaskComplexity.MODERATE)
        require_approval = context.get("require_plan_approval", False)
        context_size = context.get("context_size", 1000)
        preferred = context.get("preferred_agent")

        # Select agent
        available = self.get_available_agents()

        if preferred and preferred in available:
            selected = preferred
        else:
            selected = self.policy.select_agent(
                complexity,
                require_approval,
                context_size,
                available
            )

        # Execute with selected agent
        adapter = self.adapters[selected]
        return await adapter.execute_prompt(project_path, prompt, context)
```

---

## 🚀 Implementation Plan

### Phase 3A: Jules Integration (Week 1)

#### Tasks

**TASK-01: Install Jules SDK** 🔴 CRITICAL | 1 hour
- Add `jules-agent-sdk` to requirements.txt
- Test installation in virtual environment
- Verify API key authentication

**TASK-02: Implement JulesAsyncAdapter** 🔴 CRITICAL | 1 day
- Create `src/cde_orchestrator/adapters/agents/jules_async_adapter.py`
- Implement `ICodeExecutor` interface
- Add source resolution logic
- Add plan approval handling

**TASK-03: Jules Environment Setup Script** 🟡 HIGH | 2 hours
- Create `.jules/setup.sh`
- Test in local Jules VM
- Document setup process

**TASK-04: Unit Tests** 🟡 HIGH | 4 hours
- Test source resolution
- Test session creation
- Test wait_for_completion
- Mock Jules API responses

**TASK-05: Integration Tests** 🟢 MEDIUM | 4 hours
- End-to-end test with real Jules API
- Test plan approval flow
- Test error handling

### Phase 3B: Multi-Agent Orchestrator (Week 2)

**TASK-06: Agent Selection Policy** 🔴 CRITICAL | 1 day
- Implement `AgentSelectionPolicy`
- Define capability matrix
- Test selection logic

**TASK-07: MultiAgentOrchestrator** 🔴 CRITICAL | 1 day
- Implement orchestrator facade
- Add fallback logic
- Test with multiple adapters

**TASK-08: Parallel Execution** 🟡 HIGH | 1 day
- Implement `ParallelExecutionUseCase`
- Add task dependency graph
- Test concurrent execution

**TASK-09: MCP Tool Integration** 🟡 HIGH | 4 hours
- Add `cde_delegateToJules` MCP tool
- Add `cde_listAvailableAgents` MCP tool
- Update server.py

### Phase 3C: Documentation & Examples (Week 3)

**TASK-10: User Documentation** 🟢 MEDIUM | 1 day
- Update AGENTS.md with Jules examples
- Create Jules quickstart guide
- Document multi-agent selection

**TASK-11: Example Workflows** 🟢 MEDIUM | 1 day
- Create example: Simple task with Copilot
- Create example: Complex feature with Jules
- Create example: Parallel execution

---

## 📊 Success Criteria

### Functional Requirements

- [ ] Jules adapter can create sessions and wait for completion
- [ ] Agent selection policy chooses correct agent for task
- [ ] Multi-agent orchestrator falls back gracefully
- [ ] Parallel execution works for independent tasks
- [ ] MCP tools expose Jules functionality

### Non-Functional Requirements

- [ ] < 2s latency for agent selection
- [ ] < 5s to create Jules session
- [ ] Graceful degradation if Jules unavailable
- [ ] 80% test coverage for new code
- [ ] Zero breaking changes to existing adapters

---

## 🔧 Configuration

### Environment Variables

```bash
# .env

# Jules Configuration
JULES_API_KEY=AQ.Ab8RN6LliWPrEfS_VGB1nncm6BxVB-0JmEyAyC-5_NqVkbHW4g
JULES_BASE_URL=https://jules.googleapis.com/v1alpha  # Optional
JULES_DEFAULT_TIMEOUT=1800  # 30 minutes
JULES_REQUIRE_PLAN_APPROVAL=false

# Agent Selection
DEFAULT_AGENT_PREFERENCE=jules,copilot,gemini,qwen
ENABLE_PARALLEL_EXECUTION=true
```

### Project Configuration

```yaml
# .cde/agents.yml

agents:
  jules:
    enabled: true
    source_cache: .jules/source_id
    default_branch: main
    auto_approve_plans: false

  copilot:
    enabled: true
    cli_command: gh copilot suggest

  gemini:
    enabled: true
    cli_command: gemini generate

  qwen:
    enabled: true
    cli_command: qwen chat

selection_policy:
  trivial: [copilot, gemini]
  simple: [copilot, gemini]
  moderate: [jules, copilot]
  complex: [jules]
  epic: [jules]
```

---

## 🎯 Future Enhancements (Phase 4+)

### Advanced Features

1. **Agent Performance Tracking**
   - Log execution times, success rates
   - A/B testing different agents
   - Adaptive selection based on historical performance

2. **Interactive Plan Approval**
   - MCP UI for plan review
   - User feedback integration
   - Plan modification before approval

3. **Agent Skill Specialization**
   - Database-specific tasks → Jules
   - UI tasks → Copilot (GitHub preview)
   - Documentation → Gemini (best at markdown)

4. **Cost Optimization**
   - Track API usage costs
   - Use free CLI agents when possible
   - Cache expensive operations

5. **Agent Mesh Architecture**
   - Multiple Jules instances in parallel
   - Load balancing across agents
   - Distributed task execution

---

## 📚 References

### Documentation

- [Jules API Documentation](https://developers.google.com/jules/api)
- [Jules CLI Reference](https://jules.google/docs/cli/reference)
- [jules-agent-sdk-python](https://github.com/AsyncFuncAI/jules-agent-sdk-python)
- [CDE Architecture](./ARCHITECTURE.md)

### Related Specs

- `specs/design/architecture/README.md` - Hexagonal architecture
- `specs/design/dynamic-skill-system.md` - Skill management
- `specs/tasks/improvement-roadmap.md` - Overall roadmap

---

**Next Steps**: Implement Phase 3A (Jules Integration) starting with TASK-01.
