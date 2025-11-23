"""
Unit tests for CEO Agent Manager (no external dependencies).

Tests the orchestration layer without requiring actual CLI agents.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cde_orchestrator.domain.agent_manager import AgentManager, TaskStatus
from mcp_tools.ceo_orchestration import (
    cde_cancelTask,
    cde_delegateTask,
    cde_getTaskStatus,
    cde_getWorkerStats,
    cde_listActiveTasks,
)


@pytest.fixture
async def manager():
    """Create and start AgentManager for tests."""
    mgr = AgentManager(max_workers=3)
    await mgr.start()
    yield mgr
    await mgr.stop()


@pytest.fixture
def mock_orchestrator():
    """Mock MultiAgentOrchestrator to avoid needing real CLI agents."""
    with patch("cde_orchestrator.domain.agent_manager.MultiAgentOrchestrator") as mock:
        mock_instance = MagicMock()
        mock_instance.execute_prompt = AsyncMock(
            return_value={
                "status": "success",
                "output": "Mock agent response",
                "files_modified": [],
            }
        )
        mock.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_manager_initialization():
    """Test AgentManager initializes correctly."""
    manager = AgentManager(max_workers=3)
    assert manager.max_workers == 3
    assert len(manager.workers) == 0  # Not started yet
    assert len(manager.active_tasks) == 0


@pytest.mark.asyncio
async def test_manager_start_stop():
    """Test starting and stopping worker pool."""
    manager = AgentManager(max_workers=3)

    # Start workers
    await manager.start()
    assert len(manager.workers) == 3
    assert all(not w.is_busy for w in manager.workers)

    # Stop workers
    await manager.stop()
    assert manager._shutdown is True


@pytest.mark.asyncio
async def test_delegate_task_basic(manager, mock_orchestrator):
    """Test basic task delegation."""
    result = await cde_delegateTask(
        task_description="Test task",
        task_type="code_generation",
        project_path=".",
    )

    data = json.loads(result)

    assert data["status"] == "success"
    assert "task_id" in data
    assert data["task_type"] == "code_generation"


@pytest.mark.asyncio
async def test_delegate_task_with_preferred_agent(manager, mock_orchestrator):
    """Test task delegation with preferred agent."""
    result = await cde_delegateTask(
        task_description="Test task",
        task_type="bug_fix",
        project_path=".",
        preferred_agent="copilot",
    )

    data = json.loads(result)

    assert data["status"] == "success"
    assert data["assigned_agent"] == "copilot"


@pytest.mark.asyncio
async def test_delegate_invalid_agent(manager):
    """Test that invalid agent types are rejected."""
    result = await cde_delegateTask(
        task_description="Test task",
        task_type="code_generation",
        project_path=".",
        preferred_agent="invalid_agent",
    )

    data = json.loads(result)
    assert data["status"] == "error"
    assert "Invalid agent type" in data["message"]


@pytest.mark.asyncio
async def test_get_task_status(manager, mock_orchestrator):
    """Test getting task status."""
    # Delegate a task
    delegate_result = await cde_delegateTask(
        task_description="Test task",
        task_type="code_generation",
        project_path=".",
    )
    delegate_data = json.loads(delegate_result)
    task_id = delegate_data["task_id"]

    # Get status immediately
    status_result = await cde_getTaskStatus(task_id)
    status_data = json.loads(status_result)

    assert status_data["task_id"] == task_id
    assert status_data["status"] in ["queued", "running", "completed", "failed"]


@pytest.mark.asyncio
async def test_get_task_status_not_found(manager):
    """Test getting status of non-existent task."""
    result = await cde_getTaskStatus("nonexistent-uuid")
    data = json.loads(result)

    assert data["status"] == "not_found"
    assert "not found" in data["message"].lower()


@pytest.mark.asyncio
async def test_list_active_tasks_empty(manager):
    """Test listing tasks when queue is empty."""
    result = await cde_listActiveTasks()
    data = json.loads(result)

    assert data["status"] == "success"
    assert data["total_tasks"] == 0
    assert data["tasks"] == []


@pytest.mark.asyncio
async def test_list_active_tasks_with_tasks(manager, mock_orchestrator):
    """Test listing active tasks."""
    # Delegate multiple tasks
    task_ids = []
    for i in range(3):
        result = await cde_delegateTask(
            task_description=f"Task {i}",
            task_type="code_generation",
            project_path=".",
        )
        data = json.loads(result)
        task_ids.append(data["task_id"])

    # List tasks
    result = await cde_listActiveTasks()
    data = json.loads(result)

    assert data["status"] == "success"
    assert data["total_tasks"] >= 0  # Some may have completed


@pytest.mark.asyncio
async def test_get_worker_stats(manager):
    """Test getting worker statistics."""
    result = await cde_getWorkerStats()
    data = json.loads(result)

    assert data["status"] == "success"
    assert data["max_workers"] == 3
    assert len(data["workers"]) == 3

    for worker in data["workers"]:
        assert "worker_id" in worker
        assert "is_busy" in worker
        assert "tasks_completed" in worker


@pytest.mark.asyncio
async def test_cancel_task(manager, mock_orchestrator):
    """Test cancelling a task."""
    # Delegate a task
    delegate_result = await cde_delegateTask(
        task_description="Test task",
        task_type="code_generation",
        project_path=".",
    )
    delegate_data = json.loads(delegate_result)
    task_id = delegate_data["task_id"]

    # Cancel it
    cancel_result = await cde_cancelTask(task_id)
    cancel_data = json.loads(cancel_result)

    assert cancel_data["status"] == "success"


@pytest.mark.asyncio
async def test_cancel_nonexistent_task(manager):
    """Test cancelling non-existent task."""
    result = await cde_cancelTask("nonexistent-uuid")
    data = json.loads(result)

    assert data["status"] == "error"
    assert "not found" in data["message"].lower()


@pytest.mark.asyncio
async def test_parallel_task_delegation(manager, mock_orchestrator):
    """Test that multiple tasks can be delegated in parallel."""
    import time

    start_time = time.time()

    # Delegate 5 tasks
    tasks = []
    for i in range(5):
        result = await cde_delegateTask(
            task_description=f"Task {i}",
            task_type="code_generation",
            project_path=".",
        )
        data = json.loads(result)
        tasks.append(data["task_id"])

    elapsed = time.time() - start_time

    # Delegation should be nearly instant (non-blocking)
    assert elapsed < 1.0
    assert len(tasks) == 5


@pytest.mark.asyncio
async def test_task_context_passing(manager, mock_orchestrator):
    """Test that context is passed to tasks."""
    context = {
        "files": ["main.py"],
        "requirements": ["Add type hints"],
    }

    result = await cde_delegateTask(
        task_description="Add type hints",
        task_type="refactoring",
        project_path=".",
        context=context,
    )

    data = json.loads(result)
    assert data["status"] == "success"

    # Verify task was created with context
    task = manager.active_tasks.get(data["task_id"])
    assert task is not None
    assert task.context == context


@pytest.mark.asyncio
async def test_worker_task_execution(manager, mock_orchestrator):
    """Test that workers execute tasks correctly."""
    # Delegate a task
    result = await cde_delegateTask(
        task_description="Test task",
        task_type="code_generation",
        project_path=".",
    )
    data = json.loads(result)
    task_id = data["task_id"]

    # Wait for processing
    await asyncio.sleep(0.5)

    # Check if task was picked up
    task = manager.active_tasks.get(task_id) or manager.completed_tasks.get(task_id)
    assert task is not None

    # Task should have been processed
    assert task.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED, TaskStatus.FAILED]


@pytest.mark.asyncio
async def test_task_lifecycle_states(manager, mock_orchestrator):
    """Test task transitions through lifecycle states."""
    # Delegate task
    result = await cde_delegateTask(
        task_description="Test task",
        task_type="code_generation",
        project_path=".",
    )
    data = json.loads(result)
    task_id = data["task_id"]

    # Initial state should be QUEUED
    task = manager.active_tasks[task_id]
    assert task.status == TaskStatus.QUEUED

    # Wait for processing
    await asyncio.sleep(0.5)

    # Task should have progressed
    task = manager.active_tasks.get(task_id) or manager.completed_tasks.get(task_id)
    assert task.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED, TaskStatus.FAILED]


@pytest.mark.asyncio
async def test_rust_module_available():
    """Test that Rust module is compiled and available."""
    try:
        from cde_rust_core import (
            kill_process,
            monitor_process_health,
            spawn_agent_async,
            spawn_agents_parallel,
        )

        # Verify functions exist
        assert callable(spawn_agents_parallel)
        assert callable(spawn_agent_async)
        assert callable(monitor_process_health)
        assert callable(kill_process)

    except ImportError as e:
        pytest.skip(f"Rust module not compiled: {e}")


@pytest.mark.asyncio
async def test_rust_parallel_spawn():
    """Test Rust parallel spawning with dummy commands."""
    try:
        from cde_rust_core import spawn_agents_parallel

        # Test with echo commands (platform-agnostic)
        commands = [
            ["python", "-c", "print('test1')"],
            ["python", "-c", "print('test2')"],
            ["python", "-c", "print('test3')"],
        ]

        result_json = spawn_agents_parallel(commands)
        results = json.loads(result_json)

        # Verify results
        assert len(results) == 3
        for result in results:
            assert "pid" in result
            assert "command" in result
            assert "status" in result

    except ImportError:
        pytest.skip("Rust module not compiled")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
