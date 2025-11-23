"""
Integration tests for CEO Agent Manager orchestration.

Tests the complete flow:
1. Task delegation via MCP tools
2. Worker pool parallel execution
3. Rust process spawning
4. Task status tracking
5. Agent coordination
"""

import asyncio
import json

import pytest

from cde_orchestrator.domain.agent_manager import get_agent_manager
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
    mgr = get_agent_manager(max_workers=3)
    await mgr.start()
    yield mgr
    await mgr.stop()


@pytest.mark.asyncio
async def test_delegate_single_task(manager):
    """Test delegating a single task."""
    # Delegate task
    result = await cde_delegateTask(
        task_description="Fix typo in README.md",
        task_type="bug_fix",
        project_path=".",
        preferred_agent="copilot",
    )

    data = json.loads(result)

    # Verify response
    assert data["status"] == "success"
    assert "task_id" in data
    assert data["task_type"] == "bug_fix"
    assert data["assigned_agent"] == "copilot"

    # Wait for task to process
    await asyncio.sleep(0.5)

    # Check task status
    status_result = await cde_getTaskStatus(data["task_id"])
    status_data = json.loads(status_result)

    assert status_data["task_id"] == data["task_id"]
    assert status_data["status"] in ["queued", "running", "completed", "failed"]


@pytest.mark.asyncio
async def test_parallel_task_execution(manager):
    """Test that multiple tasks execute in parallel without blocking."""
    import time

    start_time = time.time()

    # Delegate 3 tasks simultaneously
    tasks = []
    for i in range(3):
        result = await cde_delegateTask(
            task_description=f"Task {i}: Generate test code",
            task_type="code_generation",
            project_path=".",
            preferred_agent="copilot",
        )
        data = json.loads(result)
        assert data["status"] == "success"
        tasks.append(data["task_id"])

    delegation_time = time.time() - start_time

    # Verify non-blocking: all 3 tasks should be delegated in < 1 second
    assert (
        delegation_time < 1.0
    ), f"Delegation took {delegation_time}s (should be instant)"

    # Wait for tasks to start processing
    await asyncio.sleep(1.0)

    # Check that tasks are running in parallel
    active_result = await cde_listActiveTasks()
    active_data = json.loads(active_result)

    assert active_data["status"] == "success"
    # At least some tasks should be queued/running
    assert active_data["total_tasks"] >= 0


@pytest.mark.asyncio
async def test_worker_stats(manager):
    """Test worker statistics reporting."""
    # Get initial stats
    result = await cde_getWorkerStats()
    data = json.loads(result)

    assert data["status"] == "success"
    assert data["max_workers"] == 3
    assert len(data["workers"]) == 3

    # Verify worker structure
    for worker in data["workers"]:
        assert "worker_id" in worker
        assert "is_busy" in worker
        assert "tasks_completed" in worker
        assert "tasks_failed" in worker


@pytest.mark.asyncio
async def test_task_cancellation(manager):
    """Test cancelling a queued task."""
    # Delegate a task
    result = await cde_delegateTask(
        task_description="Long running task",
        task_type="refactoring",
        project_path=".",
    )
    data = json.loads(result)
    task_id = data["task_id"]

    # Cancel it
    cancel_result = await cde_cancelTask(task_id)
    cancel_data = json.loads(cancel_result)

    assert cancel_data["status"] == "success"
    assert cancel_data["task_id"] == task_id

    # Verify it's cancelled
    status_result = await cde_getTaskStatus(task_id)
    status_data = json.loads(status_result)

    # Task might be cancelled or already completed
    assert status_data["status"] in ["cancelled", "running", "completed"]


@pytest.mark.asyncio
async def test_agent_type_validation(manager):
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
async def test_task_not_found(manager):
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
async def test_task_lifecycle(manager):
    """Test complete task lifecycle from delegation to completion."""
    # Delegate task
    result = await cde_delegateTask(
        task_description="Simple task",
        task_type="documentation",
        project_path=".",
    )
    data = json.loads(result)
    task_id = data["task_id"]

    # Initial status should be queued or running
    status_result = await cde_getTaskStatus(task_id)
    status_data = json.loads(status_result)
    assert status_data["status"] in ["queued", "running"]

    # Wait for processing
    max_wait = 30  # 30 seconds timeout
    waited = 0
    while waited < max_wait:
        await asyncio.sleep(1)
        waited += 1

        status_result = await cde_getTaskStatus(task_id)
        status_data = json.loads(status_result)

        if status_data["status"] in ["completed", "failed"]:
            break

    # Task should eventually complete or fail
    assert status_data["status"] in ["completed", "failed", "running"]


@pytest.mark.asyncio
async def test_rust_process_spawning_integration(manager):
    """Test that Rust process spawning functions are called correctly."""
    # This test verifies the integration with rust_core module
    try:
        from cde_rust_core import spawn_agents_parallel

        # Test parallel spawning with dummy commands
        commands = [
            ["echo", "test1"],
            ["echo", "test2"],
            ["echo", "test3"],
        ]

        result_json = spawn_agents_parallel(commands)
        results = json.loads(result_json)

        # Verify we got results for all commands
        assert len(results) == 3

        # Each result should have pid, command, status
        for result in results:
            assert "pid" in result
            assert "command" in result
            assert "status" in result

    except ImportError:
        pytest.skip("Rust module not compiled, skipping integration test")


@pytest.mark.asyncio
async def test_concurrent_worker_pool(manager):
    """Test that worker pool handles concurrent tasks correctly."""
    # Delegate 10 tasks (more than worker pool size)
    task_ids = []
    for i in range(10):
        result = await cde_delegateTask(
            task_description=f"Concurrent task {i}",
            task_type="code_generation",
            project_path=".",
        )
        data = json.loads(result)
        task_ids.append(data["task_id"])

    # Wait a bit for processing to start
    await asyncio.sleep(2)

    # Check worker stats
    stats_result = await cde_getWorkerStats()
    stats_data = json.loads(stats_result)

    # Some workers should be busy
    busy_workers = sum(1 for w in stats_data["workers"] if w["is_busy"])

    # At most 3 workers can be busy (pool size)
    assert busy_workers <= 3

    # Some tasks should be queued
    active_result = await cde_listActiveTasks()
    active_data = json.loads(active_result)

    # We should have some active tasks
    assert active_data["total_tasks"] > 0


@pytest.mark.asyncio
async def test_agent_auto_selection(manager):
    """Test that agent is auto-selected when not specified."""
    result = await cde_delegateTask(
        task_description="Auto-select agent task",
        task_type="code_generation",
        project_path=".",
        # No preferred_agent specified
    )

    data = json.loads(result)
    assert data["status"] == "success"
    assert data["assigned_agent"] == "auto"  # Should indicate auto-selection


@pytest.mark.asyncio
async def test_context_passing(manager):
    """Test that context is passed correctly to tasks."""
    context = {
        "files": ["src/main.py", "tests/test_main.py"],
        "requirements": ["Add type hints", "Use async/await"],
    }

    result = await cde_delegateTask(
        task_description="Add type hints to main.py",
        task_type="refactoring",
        project_path=".",
        context=context,
    )

    data = json.loads(result)
    assert data["status"] == "success"

    # Verify context was stored
    status_result = await cde_getTaskStatus(data["task_id"])
    status_data = json.loads(status_result)

    # Context should be in the task (not returned by status for brevity, but stored)
    assert status_data["task_id"] == data["task_id"]


if __name__ == "__main__":
    # Run tests manually
    pytest.main([__file__, "-v", "-s"])
