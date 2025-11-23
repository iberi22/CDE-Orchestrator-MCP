"""
Tests for Error Recovery Strategies.

Tests:
- Dead Letter Queue operations
- Compensating Transactions
- Recovery logging
- Integration with other resilience components
"""

import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cde_orchestrator.infrastructure.error_recovery import (
    CompensatingTransaction,
    CompensationManager,
    DeadLetterQueue,
    FailedOperation,
    OperationStatus,
    get_compensation_manager,
    get_dlq,
)


class TestFailedOperation:
    """Tests for FailedOperation dataclass."""

    def test_can_retry_initial(self):
        """Test that new operation can be retried."""
        op = FailedOperation(
            operation_id="test-1",
            operation_type="test",
            timestamp=datetime.now(),
            error="Test error",
            error_type="TestError",
            context={},
            max_retries=3,
        )

        assert op.can_retry()
        assert op.retry_count == 0

    def test_can_retry_max_retries_reached(self):
        """Test that operation cannot be retried after max retries."""
        op = FailedOperation(
            operation_id="test-1",
            operation_type="test",
            timestamp=datetime.now(),
            error="Test error",
            error_type="TestError",
            context={},
            max_retries=3,
            retry_count=3,
        )

        assert not op.can_retry()

    def test_can_retry_next_retry_not_reached(self):
        """Test that operation cannot be retried before next_retry time."""
        op = FailedOperation(
            operation_id="test-1",
            operation_type="test",
            timestamp=datetime.now(),
            error="Test error",
            error_type="TestError",
            context={},
            max_retries=3,
            next_retry=datetime.now() + timedelta(hours=1),
        )

        assert not op.can_retry()

    def test_schedule_retry_exponential_backoff(self):
        """Test exponential backoff for retries."""
        op = FailedOperation(
            operation_id="test-1",
            operation_type="test",
            timestamp=datetime.now(),
            error="Test error",
            error_type="TestError",
            context={},
            max_retries=3,
        )

        # First retry: 60 seconds
        op.schedule_retry(backoff_seconds=60)
        assert op.retry_count == 1
        assert op.status == OperationStatus.RETRYING
        first_retry = op.next_retry

        # Second retry: 120 seconds (2^1 * 60)
        op.schedule_retry(backoff_seconds=60)
        assert op.retry_count == 2
        second_retry = op.next_retry

        # Verify exponential backoff
        assert second_retry > first_retry


class TestDeadLetterQueue:
    """Tests for Dead Letter Queue."""

    def test_add_operation(self):
        """Test adding operation to DLQ."""
        dlq = DeadLetterQueue(max_size=100)

        error = ValueError("Test error")
        op = dlq.add(
            operation_id="test-1",
            operation_type="skill_sourcing",
            error=error,
            context={"skill": "test-skill"},
            max_retries=3,
        )

        assert op.operation_id == "test-1"
        assert op.operation_type == "skill_sourcing"
        assert op.error == "Test error"
        assert op.error_type == "ValueError"
        assert op.context == {"skill": "test-skill"}
        assert op.max_retries == 3

        stats = dlq.get_statistics()
        assert stats["total_failed"] == 1
        assert stats["total_dlq"] == 1
        assert stats["current_size"] == 1

    def test_max_size_enforcement(self):
        """Test that DLQ enforces max size."""
        dlq = DeadLetterQueue(max_size=3)

        # Add 5 operations
        for i in range(5):
            dlq.add(
                operation_id=f"test-{i}",
                operation_type="test",
                error=ValueError(f"Error {i}"),
                context={},
            )

        # Only last 3 should remain
        stats = dlq.get_statistics()
        assert stats["current_size"] == 3
        assert stats["total_failed"] == 5

    def test_get_retryable_operations(self):
        """Test getting retryable operations."""
        dlq = DeadLetterQueue()

        # Add operation that can be retried
        dlq.add(
            operation_id="test-1",
            operation_type="test",
            error=ValueError("Error 1"),
            context={},
            max_retries=3,
        )

        # Add operation that cannot be retried (max retries reached)
        op2 = dlq.add(
            operation_id="test-2",
            operation_type="test",
            error=ValueError("Error 2"),
            context={},
            max_retries=1,
        )
        op2.retry_count = 1

        retryable = dlq.get_retryable_operations()
        assert len(retryable) == 1
        assert retryable[0].operation_id == "test-1"

    def test_statistics_by_type(self):
        """Test statistics grouped by operation type."""
        dlq = DeadLetterQueue()

        dlq.add("test-1", "skill_sourcing", ValueError("Error 1"), {})
        dlq.add("test-2", "skill_sourcing", ValueError("Error 2"), {})
        dlq.add("test-3", "web_research", ValueError("Error 3"), {})

        stats = dlq.get_statistics()
        assert stats["by_type"]["skill_sourcing"] == 2
        assert stats["by_type"]["web_research"] == 1

    def test_statistics_by_status(self):
        """Test statistics grouped by status."""
        dlq = DeadLetterQueue()

        op1 = dlq.add("test-1", "test", ValueError("Error 1"), {})
        op2 = dlq.add("test-2", "test", ValueError("Error 2"), {})

        op2.schedule_retry()

        stats = dlq.get_statistics()
        assert stats["by_status"]["failed"] == 1
        assert stats["by_status"]["retrying"] == 1

    @pytest.mark.asyncio
    async def test_auto_retry_start_stop(self):
        """Test starting and stopping auto-retry."""
        dlq = DeadLetterQueue(retry_interval=1)

        await dlq.start_auto_retry()
        assert dlq._running
        assert dlq._retry_task is not None

        await dlq.stop_auto_retry()
        assert not dlq._running

    @pytest.mark.asyncio
    async def test_auto_retry_loop(self):
        """Test auto-retry loop processes retryable operations."""
        dlq = DeadLetterQueue(retry_interval=1)

        # Add retryable operation
        dlq.add(
            operation_id="test-1",
            operation_type="test",
            error=ValueError("Error"),
            context={},
            max_retries=3,
        )

        await dlq.start_auto_retry()

        # Wait for retry loop to process
        await asyncio.sleep(2)

        stats = dlq.get_statistics()
        assert stats["total_retried"] > 0

        await dlq.stop_auto_retry()

    def test_persistence_to_disk(self):
        """Test persisting DLQ to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence_path = Path(tmpdir) / "dlq.json"
            dlq = DeadLetterQueue(persistence_path=persistence_path)

            # Add operations
            dlq.add("test-1", "test", ValueError("Error 1"), {"key": "value"})
            dlq.add("test-2", "test", ValueError("Error 2"), {})

            # Verify file was created
            assert persistence_path.exists()

            # Verify content
            data = json.loads(persistence_path.read_text())
            assert len(data["operations"]) == 2
            assert data["operations"][0]["operation_id"] == "test-1"
            assert data["operations"][0]["context"] == {"key": "value"}

    def test_load_from_disk(self):
        """Test loading DLQ from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence_path = Path(tmpdir) / "dlq.json"

            # Create DLQ and add operations
            dlq1 = DeadLetterQueue(persistence_path=persistence_path)
            dlq1.add("test-1", "test", ValueError("Error 1"), {})
            dlq1.add("test-2", "test", ValueError("Error 2"), {})

            # Create new DLQ and load from disk
            dlq2 = DeadLetterQueue(persistence_path=persistence_path)

            stats = dlq2.get_statistics()
            assert stats["current_size"] == 2


class TestCompensatingTransaction:
    """Tests for Compensating Transaction."""

    @pytest.mark.asyncio
    async def test_execute_sync_function(self):
        """Test executing synchronous compensation function."""
        executed = []

        def compensation_func(value):
            executed.append(value)

        transaction = CompensatingTransaction(
            transaction_id="tx-1",
            operation_id="op-1",
            compensation_func=compensation_func,
            compensation_args=("test",),
        )

        success = await transaction.execute()

        assert success
        assert transaction.executed
        assert transaction.success
        assert executed == ["test"]

    @pytest.mark.asyncio
    async def test_execute_async_function(self):
        """Test executing asynchronous compensation function."""
        executed = []

        async def compensation_func(value):
            executed.append(value)

        transaction = CompensatingTransaction(
            transaction_id="tx-1",
            operation_id="op-1",
            compensation_func=compensation_func,
            compensation_args=("test",),
        )

        success = await transaction.execute()

        assert success
        assert transaction.executed
        assert transaction.success
        assert executed == ["test"]

    @pytest.mark.asyncio
    async def test_execute_with_error(self):
        """Test compensation function that raises error."""

        def compensation_func():
            raise ValueError("Compensation failed")

        transaction = CompensatingTransaction(
            transaction_id="tx-1",
            operation_id="op-1",
            compensation_func=compensation_func,
        )

        success = await transaction.execute()

        assert not success
        assert transaction.executed
        assert not transaction.success
        assert transaction.error == "Compensation failed"

    @pytest.mark.asyncio
    async def test_execute_idempotent(self):
        """Test that transaction can only be executed once."""
        executed_count = []

        def compensation_func():
            executed_count.append(1)

        transaction = CompensatingTransaction(
            transaction_id="tx-1",
            operation_id="op-1",
            compensation_func=compensation_func,
        )

        # Execute twice
        await transaction.execute()
        await transaction.execute()

        # Should only execute once
        assert len(executed_count) == 1


class TestCompensationManager:
    """Tests for Compensation Manager."""

    def test_register_transaction(self):
        """Test registering compensating transaction."""
        manager = CompensationManager()

        def compensation_func():
            pass

        tx_id = manager.register("op-1", compensation_func)

        assert tx_id.startswith("op-1_compensation_")

        stats = manager.get_statistics()
        assert stats["total_registered"] == 1
        assert stats["pending_operations"] == 1
        assert stats["pending_transactions"] == 1

    def test_register_multiple_transactions(self):
        """Test registering multiple transactions for same operation."""
        manager = CompensationManager()

        def compensation_func():
            pass

        tx_id1 = manager.register("op-1", compensation_func)
        tx_id2 = manager.register("op-1", compensation_func)

        assert tx_id1 != tx_id2

        stats = manager.get_statistics()
        assert stats["total_registered"] == 2
        assert stats["pending_operations"] == 1
        assert stats["pending_transactions"] == 2

    @pytest.mark.asyncio
    async def test_compensate_lifo_order(self):
        """Test that compensations execute in LIFO order."""
        manager = CompensationManager()
        execution_order = []

        def compensation1():
            execution_order.append(1)

        def compensation2():
            execution_order.append(2)

        def compensation3():
            execution_order.append(3)

        # Register in order 1, 2, 3
        manager.register("op-1", compensation1)
        manager.register("op-1", compensation2)
        manager.register("op-1", compensation3)

        # Execute compensations
        await manager.compensate("op-1")

        # Should execute in reverse order: 3, 2, 1
        assert execution_order == [3, 2, 1]

    @pytest.mark.asyncio
    async def test_compensate_all_success(self):
        """Test compensation when all transactions succeed."""
        manager = CompensationManager()

        def compensation():
            pass

        manager.register("op-1", compensation)
        manager.register("op-1", compensation)

        success = await manager.compensate("op-1")

        assert success

        stats = manager.get_statistics()
        assert stats["total_executed"] == 2
        assert stats["total_successful"] == 2
        assert stats["total_failed"] == 0
        assert stats["pending_operations"] == 0

    @pytest.mark.asyncio
    async def test_compensate_with_failure(self):
        """Test compensation when some transactions fail."""
        manager = CompensationManager()

        def compensation_success():
            pass

        def compensation_failure():
            raise ValueError("Compensation failed")

        manager.register("op-1", compensation_success)
        manager.register("op-1", compensation_failure)

        success = await manager.compensate("op-1")

        assert not success

        stats = manager.get_statistics()
        assert stats["total_executed"] == 2
        assert stats["total_successful"] == 1
        assert stats["total_failed"] == 1

    @pytest.mark.asyncio
    async def test_compensate_no_transactions(self):
        """Test compensating operation with no registered transactions."""
        manager = CompensationManager()

        success = await manager.compensate("op-1")

        assert success


class TestGlobalInstances:
    """Tests for global singleton instances."""

    def test_get_dlq_singleton(self):
        """Test that get_dlq returns singleton instance."""
        dlq1 = get_dlq()
        dlq2 = get_dlq()

        assert dlq1 is dlq2

    def test_get_compensation_manager_singleton(self):
        """Test that get_compensation_manager returns singleton instance."""
        mgr1 = get_compensation_manager()
        mgr2 = get_compensation_manager()

        assert mgr1 is mgr2


class TestIntegrationScenarios:
    """Integration tests for error recovery scenarios."""

    @pytest.mark.asyncio
    async def test_failed_operation_with_compensation(self):
        """Test complete flow: operation fails, compensates, goes to DLQ."""
        dlq = DeadLetterQueue()
        manager = CompensationManager()

        # Simulate operation with compensation
        operation_id = "op-1"
        compensated = []

        def cleanup_resource():
            compensated.append("cleaned")

        manager.register(operation_id, cleanup_resource)

        # Operation fails
        error = ValueError("Operation failed")
        dlq.add(operation_id, "test_operation", error, {})

        # Compensate
        success = await manager.compensate(operation_id)

        assert success
        assert compensated == ["cleaned"]

        # Verify in DLQ
        stats = dlq.get_statistics()
        assert stats["total_failed"] == 1

    @pytest.mark.asyncio
    async def test_retry_with_eventual_success(self):
        """Test retry logic with eventual success."""
        dlq = DeadLetterQueue()

        # Add operation with max_retries=3
        op = dlq.add("op-1", "test", ValueError("Temporary error"), {}, max_retries=3)

        # Verify initial state
        assert op.retry_count == 0
        assert op.can_retry()

        # First retry
        op.schedule_retry(backoff_seconds=1)
        assert op.retry_count == 1
        assert op.status == OperationStatus.RETRYING

        # Simulate time passing by clearing next_retry
        op.next_retry = None
        assert op.can_retry()

        # Second retry
        op.schedule_retry(backoff_seconds=1)
        assert op.retry_count == 2

        # Third retry
        op.next_retry = None
        op.schedule_retry(backoff_seconds=1)
        assert op.retry_count == 3

        # After 3 retries, cannot retry anymore (max reached)
        assert not op.can_retry()
        assert op.status == OperationStatus.RETRYING
