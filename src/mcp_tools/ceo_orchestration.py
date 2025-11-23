"""
MCP Tools for CEO Agent Orchestration

Provides tools for task delegation to AI coding agents through the AgentManager.
"""

import json
from typing import Any, Dict, Optional

from cde_orchestrator.domain.agent_manager import (
    AgentManager,
    AgentType,
    TaskStatus,
    get_agent_manager,
)

# Global instance
_agent_manager: Optional[AgentManager] = None


def get_manager() -> AgentManager:
    """Get or create the global AgentManager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = get_agent_manager()
    return _agent_manager


async def cde_delegateTask(
    task_description: str,
    task_type: str = "code_generation",
    project_path: str = ".",
    context: Optional[Dict[str, Any]] = None,
    preferred_agent: Optional[str] = None,
) -> str:
    """
    Delegate a coding task to the CEO Agent Manager.

    This tool enables non-blocking task delegation to AI coding agents
    (Copilot CLI, Gemini, Qwen, Jules) managed by the Nexus AI orchestrator.

    Args:
        task_description: Natural language description of the task
            Examples:
            - "Fix bug in authentication module"
            - "Add Redis caching to user profile API"
            - "Refactor database models to async/await"

        task_type: Type of task (default: "code_generation")
            Options:
            - "code_generation": Write new code
            - "refactoring": Improve existing code
            - "bug_fix": Fix identified issues
            - "documentation": Write/update docs
            - "testing": Create/fix tests

        project_path: Path to project directory (default: current directory)

        context: Additional context for the agent (optional)
            Examples:
            - {"files": ["src/auth.py", "tests/test_auth.py"]}
            - {"requirements": ["Use async/await", "Add type hints"]}
            - {"related_tasks": ["task-123", "task-456"]}

        preferred_agent: Preferred agent name (optional)
            Options: "jules", "copilot", "gemini", "qwen"
            If None, AgentManager selects best available agent

    Returns:
        JSON string with task details:
        {
            "status": "success",
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "message": "Task delegated successfully",
            "assigned_agent": "jules",
            "estimated_duration": "5-10 minutes"
        }

    Examples:
        >>> await cde_delegateTask(
        ...     task_description="Add error handling to API endpoints",
        ...     task_type="code_generation",
        ...     project_path="E:\\\\MyProject",
        ...     context={"files": ["src/api/*.py"]}
        ... )
        {
            "status": "success",
            "task_id": "abc-123",
            "assigned_agent": "copilot"
        }

    Note:
        - Tasks execute asynchronously in the background
        - Use `cde_getTaskStatus` to poll task progress
        - CEO orchestrator ensures agents don't block each other
    """
    manager = get_manager()

    try:
        # Convert string to AgentType if provided
        agent_type = None
        if preferred_agent:
            try:
                agent_type = AgentType(preferred_agent.lower())
            except ValueError:
                return json.dumps(
                    {
                        "status": "error",
                        "message": f"Invalid agent type: {preferred_agent}. Valid options: jules, copilot, gemini, qwen",
                    }
                )

        # Delegate task (non-blocking)
        task_id = await manager.delegate_task(
            task_type=task_type,
            description=task_description,
            project_path=project_path,
            context=context or {},
            preferred_agent=agent_type,
        )

        # Get task details for response
        task = manager.active_tasks.get(task_id)
        if not task:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Task created but not found in active tasks",
                    "task_id": task_id,
                }
            )

        return json.dumps(
            {
                "status": "success",
                "task_id": task_id,
                "message": "Task delegated successfully",
                "assigned_agent": (
                    task.preferred_agent.value if task.preferred_agent else "auto"
                ),
                "task_type": task_type,
                "estimated_duration": "5-10 minutes",  # TODO: Add duration estimation
            }
        )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


async def cde_getTaskStatus(task_id: str) -> str:
    """
    Get the current status of a delegated task.

    Poll this tool to check task progress after using `cde_delegateTask`.

    Args:
        task_id: Task UUID returned by `cde_delegateTask`

    Returns:
        JSON string with task status:
        {
            "status": "running",
            "task_id": "abc-123",
            "task_type": "code_generation",
            "description": "Add error handling...",
            "assigned_agent": "copilot",
            "created_at": "2025-11-23T10:30:00",
            "updated_at": "2025-11-23T10:35:00",
            "result": null  # or result data if completed
        }

    Status Values:
        - "queued": Task waiting for available worker
        - "running": Agent currently executing task
        - "completed": Task finished successfully
        - "failed": Task execution failed (check result for error)
        - "cancelled": Task was cancelled

    Examples:
        >>> await cde_getTaskStatus("abc-123")
        {
            "status": "completed",
            "task_id": "abc-123",
            "result": {
                "files_modified": ["src/api/auth.py"],
                "summary": "Added try-except blocks..."
            }
        }
    """
    manager = get_manager()

    try:
        task = manager.active_tasks.get(task_id)
        if not task:
            return json.dumps(
                {
                    "status": "not_found",
                    "task_id": task_id,
                    "message": "Task not found. It may have been completed and cleaned up.",
                }
            )

        return json.dumps(
            {
                "status": task.status.value,
                "task_id": task.task_id,
                "task_type": task.task_type,
                "description": task.description,
                "preferred_agent": (
                    task.preferred_agent.value if task.preferred_agent else None
                ),
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": (
                    task.completed_at.isoformat() if task.completed_at else None
                ),
                "result": task.result,
                "error": task.error,
            }
        )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


async def cde_listActiveTasks() -> str:
    """
    List all currently active tasks managed by the CEO orchestrator.

    Returns:
        JSON string with list of active tasks:
        {
            "status": "success",
            "total_tasks": 5,
            "tasks": [
                {
                    "task_id": "abc-123",
                    "status": "running",
                    "description": "Add error handling...",
                    "preferred_agent": "copilot"
                },
                ...
            ]
        }

    Examples:
        >>> await cde_listActiveTasks()
        {
            "status": "success",
            "total_tasks": 2,
            "tasks": [...]
        }
    """
    manager = get_manager()

    try:
        # list_active_tasks returns a coroutine, need to await it
        active_tasks_list = await manager.list_active_tasks()

        return json.dumps(
            {
                "status": "success",
                "total_tasks": len(active_tasks_list),
                "tasks": [
                    {
                        "task_id": task["task_id"],
                        "status": task["status"],
                        "task_type": task["task_type"],
                        "description": task["description"][:100]
                        + ("..." if len(task["description"]) > 100 else ""),
                        "preferred_agent": task.get("preferred_agent"),
                        "created_at": task["created_at"],
                    }
                    for task in active_tasks_list
                ],
            }
        )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


async def cde_getWorkerStats() -> str:
    """
    Get statistics about the CEO worker pool.

    Returns:
        JSON string with worker stats:
        {
            "status": "success",
            "max_workers": 3,
            "active_workers": 2,
            "total_tasks_queued": 1,
            "total_tasks_processed": 45,
            "workers": [
                {
                    "worker_id": "worker-1",
                    "is_busy": true,
                    "current_task": "abc-123",
                    "tasks_completed": 15
                },
                ...
            ]
        }

    Examples:
        >>> await cde_getWorkerStats()
        {
            "status": "success",
            "max_workers": 3,
            "active_workers": 2
        }
    """
    manager = get_manager()

    try:
        # get_worker_stats returns a coroutine, need to await it
        stats_list = await manager.get_worker_stats()

        # Calculate total completed tasks
        total_completed = sum(w["tasks_completed"] for w in stats_list)

        return json.dumps(
            {
                "status": "success",
                "max_workers": manager.max_workers,
                "active_workers": len(manager.workers),
                "total_tasks_queued": manager.task_queue.qsize(),
                "total_tasks_processed": total_completed,
                "workers": stats_list,
            }
        )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


async def cde_cancelTask(task_id: str) -> str:
    """
    Cancel a queued or running task.

    Note: Cancellation is best-effort. Running tasks may not stop immediately.

    Args:
        task_id: Task UUID to cancel

    Returns:
        JSON string:
        {
            "status": "success",
            "task_id": "abc-123",
            "message": "Task cancelled successfully"
        }

    Examples:
        >>> await cde_cancelTask("abc-123")
        {"status": "success", "message": "Task cancelled"}
    """
    manager = get_manager()

    try:
        task = manager.active_tasks.get(task_id)
        if not task:
            return json.dumps(
                {
                    "status": "error",
                    "task_id": task_id,
                    "message": "Task not found",
                }
            )

        # Mark task as cancelled
        task.status = TaskStatus.CANCELLED
        task.error = "Task cancelled by user"

        return json.dumps(
            {
                "status": "success",
                "task_id": task_id,
                "message": "Task cancelled successfully",
            }
        )

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
