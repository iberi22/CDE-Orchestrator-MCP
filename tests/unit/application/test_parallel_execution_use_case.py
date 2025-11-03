"""
Unit tests for ParallelExecutionUseCase.

Tests concurrent task execution with dependency management.
"""

import pytest
import asyncio
from cde_orchestrator.application.parallel_execution_use_case import (
    ParallelExecutionUseCase,
    DependencyGraph,
    Task,
    TaskResult,
    TaskStatus,
)


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.SKIPPED.value == "skipped"


class TestTaskResult:
    """Test TaskResult dataclass."""

    def test_create_success_result(self):
        """Test creating success result."""
        result = TaskResult(
            task_id="task-1",
            status=TaskStatus.COMPLETED,
            output="Success",
            duration_seconds=1.5,
        )

        assert result.task_id == "task-1"
        assert result.is_success() is True
        assert result.is_failed() is False

    def test_create_failure_result(self):
        """Test creating failure result."""
        result = TaskResult(
            task_id="task-1",
            status=TaskStatus.FAILED,
            error="Something failed",
            duration_seconds=0.5,
        )

        assert result.is_failed() is True
        assert result.is_success() is False


class TestTask:
    """Test Task dataclass."""

    @pytest.mark.asyncio
    async def test_task_without_dependencies(self):
        """Test task with no dependencies."""
        async def dummy_coro():
            return "result"

        task = Task(
            task_id="task-1",
            coro=dummy_coro(),
            dependencies=[],
        )

        assert task.task_id == "task-1"
        assert task.has_dependencies() is False

    @pytest.mark.asyncio
    async def test_task_with_dependencies(self):
        """Test task with dependencies."""
        async def dummy_coro():
            return "result"

        task = Task(
            task_id="task-2",
            coro=dummy_coro(),
            dependencies=["task-1"],
        )

        assert task.has_dependencies() is True
        assert "task-1" in task.dependencies


class TestDependencyGraph:
    """Test DependencyGraph."""

    @pytest.mark.asyncio
    async def test_add_and_get_tasks(self):
        """Test adding and retrieving tasks."""
        async def dummy_coro():
            return "result"

        graph = DependencyGraph()
        task = Task(
            task_id="task-1",
            coro=dummy_coro(),
            dependencies=[],
        )

        graph.add_task(task)

        # Verify task was added by checking graph state
        assert len(graph._tasks) == 1

    def test_add_result(self):
        """Test adding task result."""
        graph = DependencyGraph()
        result = TaskResult(
            task_id="task-1",
            status=TaskStatus.COMPLETED,
            output="Result",
        )

        graph.add_result(result)

        results = graph.get_results()
        assert "task-1" in results
        assert results["task-1"].status == TaskStatus.COMPLETED

    def test_is_complete(self):
        """Test completion check."""
        async def dummy_coro():
            return "result"

        graph = DependencyGraph()
        task = Task(task_id="task-1", coro=dummy_coro(), dependencies=[])
        graph.add_task(task)

        assert graph.is_complete() is False

        result = TaskResult(
            task_id="task-1",
            status=TaskStatus.COMPLETED,
        )
        graph.add_result(result)

        assert graph.is_complete() is True

    def test_has_failures(self):
        """Test failure detection."""
        graph = DependencyGraph()

        success = TaskResult(
            task_id="task-1",
            status=TaskStatus.COMPLETED,
        )
        graph.add_result(success)

        assert graph.has_failures() is False

        failure = TaskResult(
            task_id="task-2",
            status=TaskStatus.FAILED,
            error="Failed",
        )
        graph.add_result(failure)

        assert graph.has_failures() is True

    @pytest.mark.asyncio
    async def test_get_ready_tasks(self):
        """Test getting ready tasks."""
        async def dummy_coro():
            return "result"

        graph = DependencyGraph()
        task1 = Task(task_id="task-1", coro=dummy_coro(), dependencies=[])
        task2 = Task(
            task_id="task-2",
            coro=dummy_coro(),
            dependencies=["task-1"],
        )

        graph.add_task(task1)
        graph.add_task(task2)

        # Only task1 should be ready
        ready = graph.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].task_id == "task-1"

        # After task1 completes, task2 should be ready
        result1 = TaskResult(
            task_id="task-1",
            status=TaskStatus.COMPLETED,
        )
        graph.add_result(result1)

        ready = graph.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].task_id == "task-2"


class TestParallelExecutionUseCase:
    """Test ParallelExecutionUseCase."""

    @pytest.mark.asyncio
    async def test_execute_single_task(self):
        """Test executing single task."""
        async def task_coro():
            return "result"

        use_case = ParallelExecutionUseCase(max_concurrent=1)

        use_case.add_task(task_id="task-1", coro=task_coro())

        results = await use_case.execute()

        assert len(results) == 1
        assert "task-1" in results
        assert results["task-1"].status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_summary(self):
        """Test summary generation."""
        async def success_task():
            await asyncio.sleep(0.01)
            return "success"

        async def fail_task():
            await asyncio.sleep(0.01)
            raise ValueError("Failed")

        use_case = ParallelExecutionUseCase()

        use_case.add_task(task_id="task-1", coro=success_task())
        use_case.add_task(task_id="task-2", coro=success_task())
        use_case.add_task(task_id="task-3", coro=fail_task())

        await use_case.execute()

        summary = use_case.get_summary()

        assert summary["total_tasks"] == 3
        assert summary["completed"] == 2
        assert summary["failed"] == 1

    @pytest.mark.asyncio
    async def test_max_concurrent_limit(self):
        """Test concurrent execution limit."""
        concurrent_count = 0
        max_observed = 0

        async def task_coro():
            nonlocal concurrent_count, max_observed
            concurrent_count += 1
            max_observed = max(max_observed, concurrent_count)
            await asyncio.sleep(0.01)
            concurrent_count -= 1

        use_case = ParallelExecutionUseCase(max_concurrent=2)

        for i in range(5):
            use_case.add_task(task_id=f"task-{i}", coro=task_coro())

        await use_case.execute()

        # Should never exceed max_concurrent
        assert max_observed <= 2
