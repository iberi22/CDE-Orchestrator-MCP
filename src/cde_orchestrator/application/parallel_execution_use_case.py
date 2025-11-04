"""
Parallel Execution Use Case - Execute multiple tasks concurrently.

This module enables concurrent execution of independent tasks with
dependency tracking and result aggregation.

Architecture: Application Layer (Use Cases)
"""

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Coroutine
from enum import Enum

__all__ = [
    "TaskStatus",
    "TaskResult",
    "Task",
    "ParallelExecutionUseCase",
]

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskResult:
    """
    Result of task execution.

    Attributes:
        task_id: Unique task identifier
        status: Final status of task
        output: Task output (or None if failed)
        error: Error message (if failed)
        duration_seconds: Execution time in seconds
    """
    task_id: str
    status: TaskStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0

    def is_success(self) -> bool:
        """Check if task succeeded."""
        return self.status == TaskStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if task failed."""
        return self.status == TaskStatus.FAILED


@dataclass
class Task:
    """
    Executable task in parallel execution.

    Attributes:
        task_id: Unique task identifier
        coro: Coroutine to execute
        dependencies: List of task IDs this task depends on
        metadata: Additional task metadata
    """
    task_id: str
    coro: Coroutine
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_dependencies(self) -> bool:
        """Check if task has dependencies."""
        return len(self.dependencies) > 0


class DependencyGraph:
    """
    Task dependency graph for parallel execution.

    Manages task dependencies and ensures tasks execute in correct order.
    """

    def __init__(self):
        """Initialize empty dependency graph."""
        self._tasks: Dict[str, Task] = {}
        self._results: Dict[str, TaskResult] = {}

    def add_task(self, task: Task) -> None:
        """
        Add task to graph.

        Args:
            task: Task to add

        Raises:
            ValueError: If task_id already exists or dependency not found
        """
        if task.task_id in self._tasks:
            raise ValueError(f"Task {task.task_id} already exists")

        # Validate dependencies
        for dep_id in task.dependencies:
            if dep_id not in self._tasks:
                raise ValueError(
                    f"Task {task.task_id} depends on unknown task {dep_id}"
                )

        self._tasks[task.task_id] = task
        logger.info(f"Added task: {task.task_id}")

    def get_ready_tasks(self) -> List[Task]:
        """
        Get tasks ready to execute (all dependencies completed).

        Returns:
            List of tasks with completed dependencies
        """
        ready = []
        for task_id, task in self._tasks.items():
            # Skip already executed
            if task_id in self._results:
                continue

            # Check if all dependencies are done
            if not task.has_dependencies():
                ready.append(task)
            else:
                all_deps_done = all(
                    dep_id in self._results
                    for dep_id in task.dependencies
                )
                if all_deps_done:
                    # Check if any dependency failed
                    any_dep_failed = any(
                        self._results[dep_id].is_failed()
                        for dep_id in task.dependencies
                    )
                    if any_dep_failed:
                        # Mark as skipped
                        self._results[task_id] = TaskResult(
                            task_id=task_id,
                            status=TaskStatus.SKIPPED,
                            error="Dependency failed",
                        )
                    else:
                        ready.append(task)

        return ready

    def add_result(self, result: TaskResult) -> None:
        """
        Record task result.

        Args:
            result: TaskResult to record
        """
        self._results[result.task_id] = result

    def get_results(self) -> Dict[str, TaskResult]:
        """
        Get all task results.

        Returns:
            Dictionary mapping task ID to result
        """
        return dict(self._results)

    def is_complete(self) -> bool:
        """Check if all tasks are done."""
        return len(self._results) == len(self._tasks)

    def has_failures(self) -> bool:
        """Check if any task failed."""
        return any(r.is_failed() for r in self._results.values())


class ParallelExecutionUseCase:
    """
    Parallel execution orchestrator.

    Executes multiple tasks concurrently with dependency management,
    error handling, and result aggregation.

    Example:
        >>> async def task_one():
        ...     return "Result 1"
        ...
        >>> async def task_two():
        ...     return "Result 2"
        ...
        >>> executor = ParallelExecutionUseCase(max_concurrent=2)
        >>> executor.add_task(Task(
        ...     task_id="task-1",
        ...     coro=task_one()
        ... ))
        >>> executor.add_task(Task(
        ...     task_id="task-2",
        ...     coro=task_two(),
        ...     dependencies=["task-1"]  # Wait for task-1
        ... ))
        >>> results = await executor.execute()
    """

    def __init__(self, max_concurrent: int = 3):
        """
        Initialize parallel execution use case.

        Args:
            max_concurrent: Maximum concurrent tasks (default: 3)
        """
        self.max_concurrent = max_concurrent
        self.graph = DependencyGraph()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._progress_callback: Optional[Callable[[str, TaskStatus], None]] = None

    def set_progress_callback(
        self,
        callback: Callable[[str, TaskStatus], None]
    ) -> None:
        """
        Set callback for progress updates.

        Args:
            callback: Callable that takes (task_id, status)
        """
        self._progress_callback = callback

    def add_task(
        self,
        task_id: str,
        coro: Coroutine,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add task to execution plan.

        Args:
            task_id: Unique task identifier
            coro: Coroutine to execute
            dependencies: List of task IDs to wait for
            metadata: Additional task metadata
        """
        task = Task(
            task_id=task_id,
            coro=coro,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )
        self.graph.add_task(task)

    async def execute(self) -> Dict[str, TaskResult]:
        """
        Execute all tasks with dependency management.

        Returns:
            Dictionary mapping task_id to TaskResult

        Raises:
            RuntimeError: If any task execution fails (unless continue_on_error=True)
        """
        logger.info(f"Starting parallel execution with {len(self.graph._tasks)} tasks")

        while not self.graph.is_complete():
            # Get ready tasks
            ready_tasks = self.graph.get_ready_tasks()

            if not ready_tasks:
                logger.warning("No ready tasks but execution not complete")
                break

            logger.info(f"Executing {len(ready_tasks)} tasks concurrently")

            # Execute ready tasks concurrently
            execute_tasks = [
                self._execute_with_semaphore(task)
                for task in ready_tasks
            ]

            # Wait for all to complete
            results = await asyncio.gather(
                *execute_tasks,
                return_exceptions=False,
            )

            # Record results
            for result in results:
                self.graph.add_result(result)
                if self._progress_callback:
                    self._progress_callback(result.task_id, result.status)

        logger.info("Parallel execution complete")
        return self.graph.get_results()

    async def _execute_with_semaphore(self, task: Task) -> TaskResult:
        """
        Execute single task with concurrency limit.

        Args:
            task: Task to execute

        Returns:
            TaskResult with execution outcome
        """
        async with self._semaphore:
            return await self._execute_task(task)

    async def _execute_task(self, task: Task) -> TaskResult:
        """
        Execute single task and capture result.

        Args:
            task: Task to execute

        Returns:
            TaskResult with execution outcome
        """
        import time

        task_id = task.task_id
        start_time = time.time()

        try:
            logger.info(f"Starting task: {task_id}")
            if self._progress_callback:
                self._progress_callback(task_id, TaskStatus.RUNNING)

            # Execute coroutine
            output = await task.coro

            duration = time.time() - start_time
            logger.info(f"Task {task_id} completed in {duration:.2f}s")

            return TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                output=output,
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Task {task_id} failed after {duration:.2f}s: {e}",
                exc_info=True,
            )

            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                duration_seconds=duration,
            )

    def get_summary(self) -> Dict[str, Any]:
        """
        Get execution summary.

        Returns:
            Summary with statistics
        """
        results = self.graph.get_results()
        completed = sum(1 for r in results.values() if r.is_success())
        failed = sum(1 for r in results.values() if r.is_failed())
        skipped = sum(
            1 for r in results.values()
            if r.status == TaskStatus.SKIPPED
        )
        total_duration = sum(r.duration_seconds for r in results.values())

        return {
            "total_tasks": len(self.graph._tasks),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "total_duration_seconds": total_duration,
            "success_rate": (
                completed / len(self.graph._tasks) * 100
                if self.graph._tasks else 0
            ),
        }
