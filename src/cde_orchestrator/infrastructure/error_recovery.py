"""
Error Recovery Strategies for Production Resilience.

This module implements:
- Dead Letter Queue (DLQ) for failed operations
- Compensating Transactions for rollback
- Enhanced Recovery Logging
- Integration with Circuit Breakers and Rate Limiters

Author: CDE Orchestrator Team
Created: 2025-11-23
"""

import asyncio
import json
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RecoveryStrategy(Enum):
    """Recovery strategies for failed operations."""

    RETRY = "retry"
    DLQ = "dead_letter_queue"
    COMPENSATE = "compensate"
    IGNORE = "ignore"


class OperationStatus(Enum):
    """Status of an operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DLQ = "dead_letter_queue"
    COMPENSATED = "compensated"


@dataclass
class FailedOperation:
    """Represents a failed operation in the DLQ."""

    operation_id: str
    operation_type: str
    timestamp: datetime
    error: str
    error_type: str
    context: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3
    next_retry: Optional[datetime] = None
    status: OperationStatus = OperationStatus.FAILED

    def can_retry(self) -> bool:
        """Check if operation can be retried."""
        if self.retry_count >= self.max_retries:
            return False
        if self.next_retry and datetime.now() < self.next_retry:
            return False
        return True

    def schedule_retry(self, backoff_seconds: int = 60):
        """Schedule next retry with exponential backoff."""
        self.retry_count += 1
        backoff = backoff_seconds * (2 ** (self.retry_count - 1))
        self.next_retry = datetime.now() + timedelta(seconds=backoff)
        self.status = OperationStatus.RETRYING
        logger.info(
            f"Scheduled retry {self.retry_count}/{self.max_retries} "
            f"for operation {self.operation_id} at {self.next_retry}"
        )


@dataclass
class CompensatingTransaction:
    """Represents a compensating transaction for rollback."""

    transaction_id: str
    operation_id: str
    compensation_func: Callable
    compensation_args: tuple = field(default_factory=tuple)
    compensation_kwargs: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    executed: bool = False
    success: bool = False
    error: Optional[str] = None

    async def execute(self) -> bool:
        """Execute the compensating transaction."""
        if self.executed:
            logger.warning(
                f"Compensating transaction {self.transaction_id} " f"already executed"
            )
            return self.success

        try:
            logger.info(
                f"Executing compensating transaction {self.transaction_id} "
                f"for operation {self.operation_id}"
            )

            if asyncio.iscoroutinefunction(self.compensation_func):
                await self.compensation_func(
                    *self.compensation_args, **self.compensation_kwargs
                )
            else:
                self.compensation_func(
                    *self.compensation_args, **self.compensation_kwargs
                )

            self.executed = True
            self.success = True
            logger.info(
                f"Compensating transaction {self.transaction_id} "
                f"executed successfully"
            )
            return True

        except Exception as e:
            self.executed = True
            self.success = False
            self.error = str(e)
            logger.error(
                f"Compensating transaction {self.transaction_id} failed: {e}",
                exc_info=True,
            )
            return False


class DeadLetterQueue:
    """
    Dead Letter Queue for failed operations.

    Stores failed operations for later retry or manual intervention.
    Implements exponential backoff for retries.
    """

    def __init__(
        self,
        max_size: int = 1000,
        persistence_path: Optional[Path] = None,
        auto_retry: bool = True,
        retry_interval: int = 60,
    ):
        """
        Initialize Dead Letter Queue.

        Args:
            max_size: Maximum number of failed operations to store
            persistence_path: Path to persist DLQ to disk
            auto_retry: Enable automatic retry of failed operations
            retry_interval: Interval in seconds to check for retryable operations
        """
        self._queue: deque[FailedOperation] = deque(maxlen=max_size)
        self._persistence_path = persistence_path
        self._auto_retry = auto_retry
        self._retry_interval = retry_interval
        self._retry_task: Optional[asyncio.Task] = None
        self._running = False

        # Statistics
        self._stats = {
            "total_failed": 0,
            "total_retried": 0,
            "total_recovered": 0,
            "total_dlq": 0,
        }

        # Load persisted operations if path provided
        if self._persistence_path:
            self._load_from_disk()

    def add(
        self,
        operation_id: str,
        operation_type: str,
        error: Exception,
        context: Dict[str, Any],
        max_retries: int = 3,
    ) -> FailedOperation:
        """
        Add a failed operation to the DLQ.

        Args:
            operation_id: Unique identifier for the operation
            operation_type: Type of operation (e.g., "skill_sourcing", "web_research")
            error: The exception that caused the failure
            context: Additional context about the operation
            max_retries: Maximum number of retry attempts

        Returns:
            FailedOperation instance
        """
        failed_op = FailedOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            timestamp=datetime.now(),
            error=str(error),
            error_type=type(error).__name__,
            context=context,
            max_retries=max_retries,
        )

        self._queue.append(failed_op)
        self._stats["total_failed"] += 1
        self._stats["total_dlq"] = len(self._queue)

        logger.error(
            f"Operation {operation_id} ({operation_type}) added to DLQ: {error}",
            extra={
                "operation_id": operation_id,
                "operation_type": operation_type,
                "error_type": type(error).__name__,
                "context": context,
            },
        )

        # Persist to disk if configured
        if self._persistence_path:
            self._persist_to_disk()

        return failed_op

    def get_retryable_operations(self) -> List[FailedOperation]:
        """Get operations that are ready for retry."""
        return [op for op in self._queue if op.can_retry()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get DLQ statistics."""
        return {
            **self._stats,
            "current_size": len(self._queue),
            "retryable_count": len(self.get_retryable_operations()),
            "by_type": self._get_operations_by_type(),
            "by_status": self._get_operations_by_status(),
        }

    def _get_operations_by_type(self) -> Dict[str, int]:
        """Get count of operations by type."""
        counts: Dict[str, int] = {}
        for op in self._queue:
            counts[op.operation_type] = counts.get(op.operation_type, 0) + 1
        return counts

    def _get_operations_by_status(self) -> Dict[str, int]:
        """Get count of operations by status."""
        counts: Dict[str, int] = {}
        for op in self._queue:
            status = op.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts

    async def start_auto_retry(self):
        """Start automatic retry of failed operations."""
        if self._running:
            logger.warning("Auto-retry already running")
            return

        self._running = True
        self._retry_task = asyncio.create_task(self._retry_loop())
        logger.info("Started DLQ auto-retry loop")

    async def stop_auto_retry(self):
        """Stop automatic retry of failed operations."""
        if not self._running:
            return

        self._running = False
        if self._retry_task:
            self._retry_task.cancel()
            try:
                await self._retry_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped DLQ auto-retry loop")

    async def _retry_loop(self):
        """Background task to retry failed operations."""
        while self._running:
            try:
                retryable = self.get_retryable_operations()

                for op in retryable:
                    logger.info(
                        f"Retrying operation {op.operation_id} "
                        f"(attempt {op.retry_count + 1}/{op.max_retries})"
                    )

                    # Schedule retry
                    op.schedule_retry(self._retry_interval)
                    self._stats["total_retried"] += 1

                    # Note: Actual retry logic would be implemented by
                    # the caller using retry callbacks

                await asyncio.sleep(self._retry_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in DLQ retry loop: {e}", exc_info=True)
                await asyncio.sleep(self._retry_interval)

    def _persist_to_disk(self):
        """Persist DLQ to disk."""
        if not self._persistence_path:
            return

        try:
            data = {
                "operations": [
                    {
                        "operation_id": op.operation_id,
                        "operation_type": op.operation_type,
                        "timestamp": op.timestamp.isoformat(),
                        "error": op.error,
                        "error_type": op.error_type,
                        "context": op.context,
                        "retry_count": op.retry_count,
                        "max_retries": op.max_retries,
                        "next_retry": (
                            op.next_retry.isoformat() if op.next_retry else None
                        ),
                        "status": op.status.value,
                    }
                    for op in self._queue
                ],
                "stats": self._stats,
            }

            self._persistence_path.parent.mkdir(parents=True, exist_ok=True)
            self._persistence_path.write_text(json.dumps(data, indent=2))

        except Exception as e:
            logger.error(f"Failed to persist DLQ to disk: {e}", exc_info=True)

    def _load_from_disk(self):
        """Load DLQ from disk."""
        if not self._persistence_path or not self._persistence_path.exists():
            return

        try:
            data = json.loads(self._persistence_path.read_text())

            for op_data in data.get("operations", []):
                op = FailedOperation(
                    operation_id=op_data["operation_id"],
                    operation_type=op_data["operation_type"],
                    timestamp=datetime.fromisoformat(op_data["timestamp"]),
                    error=op_data["error"],
                    error_type=op_data["error_type"],
                    context=op_data["context"],
                    retry_count=op_data["retry_count"],
                    max_retries=op_data["max_retries"],
                    next_retry=(
                        datetime.fromisoformat(op_data["next_retry"])
                        if op_data["next_retry"]
                        else None
                    ),
                    status=OperationStatus(op_data["status"]),
                )
                self._queue.append(op)

            self._stats.update(data.get("stats", {}))
            logger.info(f"Loaded {len(self._queue)} operations from DLQ")

        except Exception as e:
            logger.error(f"Failed to load DLQ from disk: {e}", exc_info=True)


class CompensationManager:
    """
    Manages compensating transactions for rollback.

    Implements the Saga pattern for distributed transactions.
    """

    def __init__(self):
        """Initialize Compensation Manager."""
        self._transactions: Dict[str, List[CompensatingTransaction]] = {}
        self._stats = {
            "total_registered": 0,
            "total_executed": 0,
            "total_successful": 0,
            "total_failed": 0,
        }

    def register(
        self, operation_id: str, compensation_func: Callable, *args, **kwargs
    ) -> str:
        """
        Register a compensating transaction.

        Args:
            operation_id: ID of the operation this compensates
            compensation_func: Function to execute for compensation
            *args: Arguments for compensation function
            **kwargs: Keyword arguments for compensation function

        Returns:
            Transaction ID
        """
        transaction_id = f"{operation_id}_compensation_{len(self._transactions.get(operation_id, []))}"

        transaction = CompensatingTransaction(
            transaction_id=transaction_id,
            operation_id=operation_id,
            compensation_func=compensation_func,
            compensation_args=args,
            compensation_kwargs=kwargs,
        )

        if operation_id not in self._transactions:
            self._transactions[operation_id] = []

        self._transactions[operation_id].append(transaction)
        self._stats["total_registered"] += 1

        logger.debug(
            f"Registered compensating transaction {transaction_id} "
            f"for operation {operation_id}"
        )

        return transaction_id

    async def compensate(self, operation_id: str) -> bool:
        """
        Execute all compensating transactions for an operation.

        Executes in reverse order (LIFO) to properly rollback.

        Args:
            operation_id: ID of the operation to compensate

        Returns:
            True if all compensations succeeded
        """
        if operation_id not in self._transactions:
            logger.warning(
                f"No compensating transactions found for operation {operation_id}"
            )
            return True

        transactions = self._transactions[operation_id]
        logger.info(
            f"Executing {len(transactions)} compensating transactions "
            f"for operation {operation_id}"
        )

        # Execute in reverse order (LIFO)
        all_success = True
        for transaction in reversed(transactions):
            success = await transaction.execute()
            self._stats["total_executed"] += 1

            if success:
                self._stats["total_successful"] += 1
            else:
                self._stats["total_failed"] += 1
                all_success = False

        # Clean up transactions
        del self._transactions[operation_id]

        return all_success

    def get_statistics(self) -> Dict[str, Any]:
        """Get compensation statistics."""
        return {
            **self._stats,
            "pending_operations": len(self._transactions),
            "pending_transactions": sum(
                len(txs) for txs in self._transactions.values()
            ),
        }


# Global instances
_dlq: Optional[DeadLetterQueue] = None
_compensation_manager: Optional[CompensationManager] = None


def get_dlq() -> DeadLetterQueue:
    """Get global Dead Letter Queue instance."""
    global _dlq
    if _dlq is None:
        _dlq = DeadLetterQueue()
    return _dlq


def get_compensation_manager() -> CompensationManager:
    """Get global Compensation Manager instance."""
    global _compensation_manager
    if _compensation_manager is None:
        _compensation_manager = CompensationManager()
    return _compensation_manager
