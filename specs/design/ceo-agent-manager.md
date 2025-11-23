---
title: "Design: CEO Agent Manager"
description: "Architecture for the Agent Manager component that orchestrates CLI-based AI agents in Windows local environment with Rust optimization."
type: design
status: active
created: "2025-11-23"
updated: "2025-11-23"
author: "Nexus AI Architect"
llm_summary: |
  Design document for the CEO Agent Manager.
  Handles parallel agent execution, process management, and context sharing on Windows.
  Uses Rust for CPU-intensive operations (process monitoring, log parsing, context serialization).
---

# CEO Agent Manager Design

## Vision

The **Agent Manager** is the core component that transforms Nexus AI into a true "CEO". It manages a pool of AI coding agents (employees), delegates tasks intelligently, and ensures high availability without blocking.

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    Nexus AI (CEO)                       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │            AgentManager (Python)                  │ │
│  │  - Task Queue (asyncio.Queue)                    │ │
│  │  - Agent Registry (Available agents)             │ │
│  │  - Context Sharing (Shared state)                │ │
│  └───────────────────────────────────────────────────┘ │
│           │           │           │                     │
│           ▼           ▼           ▼                     │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│    │ Worker 1 │ │ Worker 2 │ │ Worker 3 │             │
│    │  (Pool)  │ │  (Pool)  │ │  (Pool)  │             │
│    └──────────┘ └──────────┘ └──────────┘             │
│           │           │           │                     │
│           ▼           ▼           ▼                     │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│    │ Copilot  │ │  Gemini  │ │   Qwen   │             │
│    │   CLI    │ │   CLI    │ │   CLI    │             │
│    └──────────┘ └──────────┘ └──────────┘             │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │        RustProcessManager (FFI)                   │ │
│  │  - Parallel subprocess spawning (Rayon)          │ │
│  │  - Log streaming (async tokio)                   │ │
│  │  - Process health monitoring                     │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Non-Blocking Task Execution

**Problem**: When one agent runs a 5-minute test suite, other agents should not wait.

**Solution**: Asyncio task queue + worker pool pattern.

```python
# src/cde_orchestrator/domain/agent_manager.py
class AgentManager:
    def __init__(self, max_workers: int = 3):
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.workers: List[AgentWorker] = []
        self.active_tasks: Dict[str, TaskStatus] = {}

    async def delegate_task(self, task: AgentTask) -> str:
        """
        Delegate task to next available worker.
        Returns task_id immediately (non-blocking).
        """
        task_id = str(uuid.uuid4())
        await self.task_queue.put((task_id, task))

        self.active_tasks[task_id] = TaskStatus.QUEUED
        return task_id

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Poll task status."""
        return {
            "task_id": task_id,
            "status": self.active_tasks[task_id],
            "result": self.results.get(task_id)
        }
```

### 2. Context Sharing

**Problem**: Agents need shared context (project state, previous results).

**Solution**: Shared memory store with Rust-optimized serialization.

```python
# Uses Rust FFI for fast JSON serialization
class ContextStore:
    def __init__(self):
        self._store: Dict[str, Any] = {}

    def set_context(self, key: str, value: Any):
        """Serialize with Rust (faster than pickle)."""
        serialized = rust_utils.serialize_json(value)
        self._store[key] = serialized

    def get_context(self, key: str) -> Any:
        """Deserialize with Rust."""
        return rust_utils.deserialize_json(self._store[key])
```

### 3. Process Management (Rust)

**Why Rust?**
- **Parallel Subprocess Spawning**: `rayon` for spawning multiple CLI agents simultaneously.
- **Log Streaming**: `tokio` async I/O for real-time log capture without blocking.
- **Process Health Monitoring**: Efficient polling of process status (CPU, memory).

```rust
// rust_core/src/process_manager.rs
use std::process::{Command, Stdio};
use tokio::io::{AsyncBufReadExt, BufReader};
use rayon::prelude::*;

/// Spawn multiple CLI agents in parallel
pub fn spawn_agents_parallel(commands: Vec<Vec<String>>) -> Vec<AgentProcess> {
    commands.par_iter()
        .map(|cmd| spawn_agent(cmd))
        .collect()
}

/// Spawn single agent with async log streaming
async fn spawn_agent(cmd: &[String]) -> AgentProcess {
    let mut child = Command::new(&cmd[0])
        .args(&cmd[1..])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("Failed to spawn agent");

    let stdout = child.stdout.take().unwrap();
    let stderr = child.stderr.take().unwrap();

    // Stream logs asynchronously
    tokio::spawn(stream_logs(stdout, stderr));

    AgentProcess {
        pid: child.id(),
        handle: child,
    }
}
```

## Rust Optimization Opportunities

### CPU-Intensive Operations (Use Rust)

| Operation | Why Rust | Current Python | Speedup |
|-----------|----------|----------------|---------|
| **Process Spawning** | Parallel spawning with Rayon | `subprocess.run` (sequential) | 3-5x |
| **Log Parsing** | Regex + streaming with `tokio` | `readline()` loop | 10-20x |
| **Context Serialization** | `serde_json` (zero-copy) | `json.dumps` | 5-10x |
| **Health Monitoring** | Async polling (tokio) | Blocking `psutil` | 2-3x |

### I/O-Bound Operations (Keep Python)

| Operation | Why Python | Reason |
|-----------|------------|--------|
| **MCP Tool Dispatch** | FastMCP framework | Better async ecosystem |
| **Workflow Orchestration** | High-level logic | Easier to maintain |
| **Error Handling** | Rich exceptions | Better debugging |

## Implementation Plan

### Phase 1.1: Python Agent Manager (Current)

- [x] Basic CLI adapters exist (`CopilotCLIAdapter`, `GeminiCLIAdapter`, etc.)
- [ ] Create `AgentManager` class with task queue
- [ ] Implement worker pool pattern
- [ ] Add task status tracking (queued → running → completed)

### Phase 1.2: Rust Process Manager

- [ ] Create `rust_core/src/process_manager.rs`
- [ ] Implement `spawn_agents_parallel` (Rayon)
- [ ] Implement `stream_logs_async` (Tokio)
- [ ] Add health monitoring (CPU/memory usage)
- [ ] Expose to Python via PyO3

### Phase 1.3: Context Store (Rust-Optimized)

- [ ] Create `rust_core/src/context_store.rs`
- [ ] Fast JSON serialization with `serde_json`
- [ ] Shared memory store (concurrent HashMap)
- [ ] Expose to Python

### Phase 1.4: Integration Testing

- [ ] Test parallel agent execution (3 agents simultaneously)
- [ ] Verify non-blocking behavior
- [ ] Benchmark Rust vs Python performance

## Example Usage

### Python API

```python
# In MCP tool
@tool_handler
async def cde_delegateTaskToCEO(task_description: str) -> str:
    """Delegate task to CEO Agent Manager."""
    manager = get_agent_manager()

    task = AgentTask(
        type="code_generation",
        description=task_description,
        context={"project_path": "."}
    )

    task_id = await manager.delegate_task(task)

    return json.dumps({
        "task_id": task_id,
        "status": "queued",
        "message": "Task delegated to agent worker"
    })

@tool_handler
async def cde_getTaskStatus(task_id: str) -> str:
    """Get task execution status."""
    manager = get_agent_manager()
    status = await manager.get_task_status(task_id)
    return json.dumps(status)
```

### Rust FFI

```python
# Python calling Rust
from cde_orchestrator import rust_utils

# Spawn 3 agents in parallel
commands = [
    ["gh", "copilot", "suggest", "create auth"],
    ["gemini", "generate", "add tests"],
    ["qwen", "chat", "review code"]
]

processes = rust_utils.spawn_agents_parallel(commands)
# Returns immediately, agents run in background
```

## Windows Compatibility

### Path Handling

- Use `pathlib.Path` in Python (cross-platform)
- Use `std::path::PathBuf` in Rust

### Subprocess

- Windows uses `cmd.exe` by default
- Rust: `Command::new("cmd").arg("/C").arg("gh copilot...")`
- Python: `subprocess.run(["cmd", "/C", "gh", "copilot", ...])`

### Process Monitoring

- Windows: Use `psutil` (Python) or `sysinfo` crate (Rust)
- Both support Windows process APIs

## Next Steps

1. **Create Rust module**: `rust_core/src/process_manager.rs`
2. **Expose to Python**: Add PyO3 bindings in `rust_core/src/lib.rs`
3. **Implement AgentManager**: Python orchestration layer
4. **Add MCP tools**: `cde_delegateTask`, `cde_getTaskStatus`
5. **Integration tests**: Verify parallel execution on Windows

---

**See Also**:
- `specs/tasks/roadmap-ceo.md` - Full roadmap
- `src/cde_orchestrator/adapters/agents/` - Existing CLI adapters
- `rust_core/src/` - Rust optimization modules
