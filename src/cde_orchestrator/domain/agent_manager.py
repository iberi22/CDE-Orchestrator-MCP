"""
Agent Manager - CEO Orchestration Layer

This module implements the high-level orchestration for managing multiple
AI coding agents in parallel, ensuring non-blocking task execution.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Status of an agent task."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Types of available agents."""

    COPILOT = "copilot"
    GEMINI = "gemini"
    QWEN = "qwen"
    JULES = "jules"
    DEEPAGENTS = "deepagents"
    CODEX = "codex"
    ROVO = "rovo"


@dataclass
class AgentTask:
    """Represents a task to be executed by an agent."""

    task_id: str
    task_type: str
    description: str
    project_path: Path
    context: Dict[str, Any] = field(default_factory=dict)
    preferred_agent: Optional[AgentType] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.QUEUED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentWorker:
    """Represents a worker that executes agent tasks."""

    worker_id: str
    current_task: Optional[AgentTask] = None
    is_busy: bool = False
    tasks_completed: int = 0
    tasks_failed: int = 0


class AgentManager:
    """
    CEO Agent Manager - Orchestrates parallel agent execution.

    Features:
    - Non-blocking task execution via asyncio.Queue
    - Worker pool pattern for concurrent agents
    - Shared context store for agent communication
    - Rust-optimized process spawning
    """

    def __init__(self, max_workers: int = 3):
        """
        Initialize Agent Manager.

        Args:
            max_workers: Maximum number of concurrent agent workers
        """
        self.max_workers = max_workers
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.workers: List[AgentWorker] = []
        self.active_tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: Dict[str, AgentTask] = {}
        self._shutdown = False
        self._worker_tasks: List[asyncio.Task] = []

        logger.info(f"AgentManager initialized with {max_workers} workers")

    async def start(self) -> None:
        """Start worker pool."""
        for i in range(self.max_workers):
            worker = AgentWorker(worker_id=f"worker-{i}")
            self.workers.append(worker)

            # Start worker coroutine
            task = asyncio.create_task(self._worker_loop(worker))
            self._worker_tasks.append(task)

        logger.info(f"Started {self.max_workers} agent workers")

    async def stop(self) -> None:
        """Stop worker pool gracefully."""
        self._shutdown = True

        # Wait for workers to finish current tasks
        for task in self._worker_tasks:
            task.cancel()

        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        logger.info("AgentManager stopped")

    async def delegate_task(
        self,
        task_type: str,
        description: str,
        project_path: Path | str,
        context: Optional[Dict[str, Any]] = None,
        preferred_agent: Optional[AgentType] = None,
    ) -> str:
        """
        Delegate task to next available worker (non-blocking).

        Args:
            task_type: Type of task (e.g., "code_generation", "testing")
            description: Natural language task description
            project_path: Path to project
            context: Additional context for the task
            preferred_agent: Preferred agent to use

        Returns:
            task_id: UUID of the queued task
        """
        task_id = str(uuid.uuid4())

        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            project_path=Path(project_path),
            context=context or {},
            preferred_agent=preferred_agent,
        )

        # Add to queue
        await self.task_queue.put(task)
        self.active_tasks[task_id] = task

        logger.info(f"Task {task_id} queued: {task_type} - {description[:50]}...")

        return task_id

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a task.

        Args:
            task_id: Task UUID

        Returns:
            Dict with task status, result, and metadata
        """
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": (
                    task.completed_at.isoformat() if task.completed_at else None
                ),
                "result": task.result,
                "error": task.error,
            }

        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": (
                    task.completed_at.isoformat() if task.completed_at else None
                ),
                "result": task.result,
                "error": task.error,
            }

        return {"task_id": task_id, "status": "not_found", "error": "Task not found"}

    async def list_active_tasks(self) -> List[Dict[str, Any]]:
        """List all active tasks."""
        return [
            {
                "task_id": task.task_id,
                "status": task.status.value,
                "description": task.description,
                "created_at": task.created_at.isoformat(),
            }
            for task in self.active_tasks.values()
        ]

    async def get_worker_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all workers."""
        return [
            {
                "worker_id": worker.worker_id,
                "is_busy": worker.is_busy,
                "current_task": (
                    worker.current_task.task_id if worker.current_task else None
                ),
                "tasks_completed": worker.tasks_completed,
                "tasks_failed": worker.tasks_failed,
            }
            for worker in self.workers
        ]

    async def _worker_loop(self, worker: AgentWorker) -> None:
        """
        Worker loop - continuously processes tasks from queue.

        Args:
            worker: Worker instance
        """
        logger.info(f"Worker {worker.worker_id} started")

        while not self._shutdown:
            try:
                # Wait for task (timeout to check shutdown flag)
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)

                worker.is_busy = True
                worker.current_task = task
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now(timezone.utc)

                logger.info(f"Worker {worker.worker_id} executing task {task.task_id}")

                # Execute task
                try:
                    result = await self._execute_task(task)
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    worker.tasks_completed += 1

                    logger.info(f"Task {task.task_id} completed by {worker.worker_id}")

                except Exception as e:
                    task.error = str(e)
                    task.status = TaskStatus.FAILED
                    worker.tasks_failed += 1

                    logger.error(f"Task {task.task_id} failed: {e}", exc_info=True)

                finally:
                    task.completed_at = datetime.now(timezone.utc)
                    worker.is_busy = False
                    worker.current_task = None

                    # Move to completed
                    self.completed_tasks[task.task_id] = task
                    del self.active_tasks[task.task_id]

                    self.task_queue.task_done()

            except asyncio.TimeoutError:
                # No task available, continue loop
                continue
            except asyncio.CancelledError:
                logger.info(f"Worker {worker.worker_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker.worker_id} error: {e}", exc_info=True)

    async def _execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task using the appropriate agent.

        This will be replaced with actual agent execution logic.

        Args:
            task: Task to execute

        Returns:
            Dict with execution result
        """
        # Import here to avoid circular dependency
        from cde_orchestrator.adapters.agents import MultiAgentOrchestrator

        # Create orchestrator with available agents
        orchestrator = MultiAgentOrchestrator()

        # Register available agents (this will be enhanced)
        # For now, use the existing CLI adapters
        try:
            from cde_orchestrator.adapters.agents.agent_selection_policy import (
                AgentType as PolicyAgentType,
            )
            from cde_orchestrator.adapters.agents.code_cli_adapters import (
                CopilotCLIAdapter,
                GeminiCLIAdapter,
                QwenCLIAdapter,
            )

            # Register CLI adapters
            cli_adapters = {
                PolicyAgentType.COPILOT: CopilotCLIAdapter,
                PolicyAgentType.GEMINI: GeminiCLIAdapter,
                PolicyAgentType.QWEN: QwenCLIAdapter,
            }

            for agent_type, adapter_class in cli_adapters.items():
                adapter = adapter_class()
                if adapter.is_available():
                    orchestrator.register_agent(agent_type, adapter)

        except ImportError as e:
            logger.warning(f"Could not import CLI adapters: {e}")

        # Execute with orchestrator
        result = await orchestrator.execute_prompt(
            project_path=task.project_path,
            prompt=task.description,
            context=task.context,
        )

        return {"output": result, "agent_used": "multi_agent_orchestrator"}


# Global instance (singleton pattern)
_agent_manager: Optional[AgentManager] = None


def get_agent_manager(max_workers: int = 3) -> AgentManager:
    """
    Get global AgentManager instance (singleton).

    Args:
        max_workers: Number of concurrent workers (only used on first call)

    Returns:
        AgentManager instance
    """
    global _agent_manager

    if _agent_manager is None:
        _agent_manager = AgentManager(max_workers=max_workers)

    return _agent_manager
