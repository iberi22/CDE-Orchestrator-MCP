"""
Unit tests for graceful shutdown infrastructure.

Tests cover:
- Signal handling
- Request tracking and completion
- Cleanup task execution
- Timeout handling
- Shutdown sequence coordination

Author: CDE Orchestrator Team
Created: 2025-11-23
"""

import asyncio
import signal

import pytest

from cde_orchestrator.infrastructure.graceful_shutdown import (
    ShutdownConfig,
    ShutdownManager,
    get_shutdown_manager,
    track_request,
)


class TestShutdownConfig:
    """Test shutdown configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ShutdownConfig()

        assert config.request_timeout == 30.0
        assert config.cleanup_timeout == 10.0
        assert config.force_after_timeout is True
        assert signal.SIGTERM in config.signals
        assert signal.SIGINT in config.signals

    def test_custom_config(self):
        """Test custom configuration."""
        config = ShutdownConfig(
            request_timeout=60.0,
            cleanup_timeout=20.0,
            force_after_timeout=False,
            signals=[signal.SIGTERM],
        )

        assert config.request_timeout == 60.0
        assert config.cleanup_timeout == 20.0
        assert config.force_after_timeout is False
        assert config.signals == [signal.SIGTERM]


class TestShutdownManager:
    """Test shutdown manager."""

    def test_initialization(self):
        """Test manager initialization."""
        manager = ShutdownManager()

        assert manager.config is not None
        assert not manager.is_shutting_down()
        assert manager.get_shutdown_stats()["shutdown_initiated"] is False

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = ShutdownConfig(request_timeout=60.0)
        manager = ShutdownManager(config)

        assert manager.config.request_timeout == 60.0

    @pytest.mark.asyncio
    async def test_register_cleanup(self):
        """Test registering cleanup tasks."""
        manager = ShutdownManager()

        cleanup_called = False

        def cleanup():
            nonlocal cleanup_called
            cleanup_called = True

        manager.register_cleanup(cleanup)

        stats = manager.get_shutdown_stats()
        assert stats["cleanup_tasks_registered"] == 1

    @pytest.mark.asyncio
    async def test_shutdown_with_no_requests(self):
        """Test shutdown with no active requests."""
        manager = ShutdownManager()

        # Initiate shutdown
        await manager.shutdown()

        assert manager.is_shutting_down()
        stats = manager.get_shutdown_stats()
        assert stats["shutdown_initiated"] is True

    @pytest.mark.asyncio
    async def test_shutdown_with_cleanup_tasks(self):
        """Test shutdown executes cleanup tasks."""
        manager = ShutdownManager()

        cleanup1_called = False
        cleanup2_called = False

        def cleanup1():
            nonlocal cleanup1_called
            cleanup1_called = True

        async def cleanup2():
            nonlocal cleanup2_called
            cleanup2_called = True

        manager.register_cleanup(cleanup1)
        manager.register_cleanup(cleanup2)

        await manager.shutdown()

        assert cleanup1_called
        assert cleanup2_called

    @pytest.mark.asyncio
    async def test_shutdown_with_active_requests(self):
        """Test shutdown waits for active requests."""
        config = ShutdownConfig(request_timeout=1.0)
        manager = ShutdownManager(config)

        request_completed = False

        async def mock_request():
            nonlocal request_completed
            await asyncio.sleep(0.1)
            request_completed = True

        # Create and track task
        task = asyncio.create_task(mock_request())
        manager.track_request(task)

        # Shutdown should wait for request
        await manager.shutdown()

        assert request_completed
        assert manager.is_shutting_down()

    @pytest.mark.asyncio
    async def test_shutdown_timeout_with_slow_request(self):
        """Test shutdown timeout with slow request."""
        config = ShutdownConfig(request_timeout=0.1, force_after_timeout=True)
        manager = ShutdownManager(config)

        async def slow_request():
            await asyncio.sleep(10)  # Will timeout

        # Create and track task
        task = asyncio.create_task(slow_request())
        manager.track_request(task)

        # Shutdown should timeout and force
        await manager.shutdown()

        assert manager.is_shutting_down()
        assert task.cancelled()

    @pytest.mark.asyncio
    async def test_cleanup_task_timeout(self):
        """Test cleanup task timeout handling."""
        config = ShutdownConfig(cleanup_timeout=0.1)
        manager = ShutdownManager(config)

        async def slow_cleanup():
            await asyncio.sleep(10)  # Will timeout

        manager.register_cleanup(slow_cleanup)

        # Should complete despite timeout
        await manager.shutdown()

        assert manager.is_shutting_down()

    @pytest.mark.asyncio
    async def test_cleanup_task_error_handling(self):
        """Test cleanup task error handling."""
        manager = ShutdownManager()

        def failing_cleanup():
            raise ValueError("Cleanup failed")

        manager.register_cleanup(failing_cleanup)

        # Should complete despite error
        await manager.shutdown()

        assert manager.is_shutting_down()

    @pytest.mark.asyncio
    async def test_duplicate_shutdown_ignored(self):
        """Test duplicate shutdown calls are ignored."""
        manager = ShutdownManager()

        # First shutdown
        await manager.shutdown()

        # Second shutdown should be ignored
        await manager.shutdown()

        assert manager.is_shutting_down()

    @pytest.mark.asyncio
    async def test_wait_for_shutdown(self):
        """Test waiting for shutdown signal."""
        manager = ShutdownManager()

        # Simulate signal in background
        async def trigger_shutdown():
            await asyncio.sleep(0.1)
            manager._shutdown_event.set()

        asyncio.create_task(trigger_shutdown())

        # Should wait until signal
        await manager.wait_for_shutdown()

        # Shutdown event should be set
        assert manager._shutdown_event.is_set()

    def test_signal_handler_installation(self):
        """Test signal handler installation."""
        manager = ShutdownManager()

        # Install handlers (may not work in all test environments)
        try:
            manager.install_signal_handlers()
            # If successful, handlers are installed
            assert True
        except (OSError, ValueError):
            # Some platforms don't support signal handling
            pytest.skip("Signal handling not supported on this platform")

    @pytest.mark.asyncio
    async def test_track_request_removes_on_completion(self):
        """Test request tracking removes task on completion."""
        manager = ShutdownManager()

        async def mock_request():
            await asyncio.sleep(0.01)

        task = asyncio.create_task(mock_request())
        manager.track_request(task)

        # Initially tracked
        assert len(manager._active_requests) == 1

        # Wait for completion
        await task
        await asyncio.sleep(0.01)  # Give callback time to execute

        # Should be removed
        assert len(manager._active_requests) == 0

    @pytest.mark.asyncio
    async def test_shutdown_stats(self):
        """Test shutdown statistics."""
        manager = ShutdownManager()

        # Before shutdown
        stats = manager.get_shutdown_stats()
        assert stats["shutdown_initiated"] is False
        assert stats["shutdown_duration"] is None

        # After shutdown
        await manager.shutdown()

        stats = manager.get_shutdown_stats()
        assert stats["shutdown_initiated"] is True
        assert stats["shutdown_duration"] is not None
        assert stats["shutdown_duration"] > 0


class TestGlobalShutdownManager:
    """Test global shutdown manager singleton."""

    def test_get_shutdown_manager_singleton(self):
        """Test get_shutdown_manager returns singleton."""
        # Reset global
        import cde_orchestrator.infrastructure.graceful_shutdown as module

        module._shutdown_manager = None

        manager1 = get_shutdown_manager()
        manager2 = get_shutdown_manager()

        assert manager1 is manager2

    def test_get_shutdown_manager_with_config(self):
        """Test get_shutdown_manager with config on first call."""
        # Reset global
        import cde_orchestrator.infrastructure.graceful_shutdown as module

        module._shutdown_manager = None

        config = ShutdownConfig(request_timeout=60.0)
        manager = get_shutdown_manager(config)

        assert manager.config.request_timeout == 60.0


class TestTrackRequestDecorator:
    """Test track_request decorator."""

    @pytest.mark.asyncio
    async def test_decorator_tracks_request(self):
        """Test decorator tracks request."""
        # Reset global
        import cde_orchestrator.infrastructure.graceful_shutdown as module

        module._shutdown_manager = None

        @track_request
        async def test_func():
            await asyncio.sleep(0.01)
            return "success"

        # Execute function
        result = await test_func()

        assert result == "success"

    @pytest.mark.asyncio
    async def test_decorator_rejects_during_shutdown(self):
        """Test decorator rejects requests during shutdown."""
        # Reset global
        import cde_orchestrator.infrastructure.graceful_shutdown as module

        module._shutdown_manager = None

        manager = get_shutdown_manager()
        manager._shutdown_initiated = True

        @track_request
        async def test_func():
            return "success"

        # Should raise error
        with pytest.raises(RuntimeError, match="Server is shutting down"):
            await test_func()


class TestShutdownSequence:
    """Test complete shutdown sequence."""

    @pytest.mark.asyncio
    async def test_complete_shutdown_sequence(self):
        """Test complete shutdown sequence with all components."""
        config = ShutdownConfig(request_timeout=1.0, cleanup_timeout=1.0)
        manager = ShutdownManager(config)

        # Track execution order
        execution_order = []

        # Mock request
        async def mock_request():
            execution_order.append("request_start")
            await asyncio.sleep(0.1)
            execution_order.append("request_end")

        # Mock cleanup
        async def mock_cleanup():
            execution_order.append("cleanup")

        # Setup
        task = asyncio.create_task(mock_request())
        manager.track_request(task)
        manager.register_cleanup(mock_cleanup)

        # Execute shutdown
        await manager.shutdown()

        # Verify sequence
        assert "request_start" in execution_order
        assert "request_end" in execution_order
        assert "cleanup" in execution_order

        # Request should complete before cleanup
        request_end_idx = execution_order.index("request_end")
        cleanup_idx = execution_order.index("cleanup")
        assert request_end_idx < cleanup_idx

    @pytest.mark.asyncio
    async def test_shutdown_with_multiple_requests_and_cleanups(self):
        """Test shutdown with multiple concurrent requests and cleanups."""
        manager = ShutdownManager()

        completed_requests = []
        completed_cleanups = []

        async def mock_request(request_id):
            await asyncio.sleep(0.05)
            completed_requests.append(request_id)

        async def mock_cleanup(cleanup_id):
            completed_cleanups.append(cleanup_id)

        # Create multiple requests
        for i in range(5):
            task = asyncio.create_task(mock_request(i))
            manager.track_request(task)

        # Register multiple cleanups (create proper async wrappers)
        for i in range(3):

            async def cleanup_wrapper(idx=i):
                await mock_cleanup(idx)

            manager.register_cleanup(cleanup_wrapper)

        # Execute shutdown
        await manager.shutdown()

        # All requests should complete
        assert len(completed_requests) == 5

        # All cleanups should execute
        assert len(completed_cleanups) == 3
