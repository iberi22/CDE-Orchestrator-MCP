"""
Graceful Shutdown Infrastructure

Handles clean shutdown of the CDE Orchestrator MCP server:
- Signal handling (SIGTERM, SIGINT, SIGHUP)
- Request completion with timeout
- Resource cleanup (cache, logs, metrics)
- Coordinated shutdown sequence

Author: CDE Orchestrator Team
Created: 2025-11-23
"""

import asyncio
import signal
import sys
import time
from typing import Callable, List, Optional, Set
from dataclasses import dataclass, field

from cde_orchestrator.infrastructure.logging import get_logger, get_correlation_id

logger = get_logger(__name__)


@dataclass
class ShutdownConfig:
    """Configuration for graceful shutdown."""

    # Maximum time to wait for in-progress requests (seconds)
    request_timeout: float = 30.0

    # Maximum time to wait for cleanup tasks (seconds)
    cleanup_timeout: float = 10.0

    # Whether to force shutdown after timeout
    force_after_timeout: bool = True

    # Signals to handle
    signals: List[signal.Signals] = field(default_factory=lambda: [
        signal.SIGTERM,  # Graceful shutdown (Docker, Kubernetes)
        signal.SIGINT,   # Ctrl+C
    ])


class ShutdownManager:
    """
    Manages graceful shutdown of the application.

    Coordinates:
    1. Signal handling
    2. Request completion
    3. Resource cleanup
    4. Orderly shutdown sequence

    Usage:
        shutdown_manager = ShutdownManager()

        # Register cleanup tasks
        shutdown_manager.register_cleanup(cache.flush)
        shutdown_manager.register_cleanup(db.close)

        # Install signal handlers
        shutdown_manager.install_signal_handlers()

        # Wait for shutdown signal
        await shutdown_manager.wait_for_shutdown()
    """

    def __init__(self, config: Optional[ShutdownConfig] = None):
        """
        Initialize shutdown manager.

        Args:
            config: Shutdown configuration (uses defaults if None)
        """
        self.config = config or ShutdownConfig()
        self._shutdown_event = asyncio.Event()
        self._cleanup_tasks: List[Callable] = []
        self._active_requests: Set[asyncio.Task] = set()
        self._shutdown_initiated = False
        self._shutdown_start_time: Optional[float] = None

        logger.info(
            "ShutdownManager initialized",
            extra={
                "correlation_id": get_correlation_id(),
                "request_timeout": self.config.request_timeout,
                "cleanup_timeout": self.config.cleanup_timeout,
            }
        )

    def install_signal_handlers(self) -> None:
        """
        Install signal handlers for graceful shutdown.

        Handles:
        - SIGTERM: Graceful shutdown (sent by Docker/Kubernetes)
        - SIGINT: Interrupt (Ctrl+C)
        """
        for sig in self.config.signals:
            try:
                signal.signal(sig, self._signal_handler)
                logger.info(
                    f"Installed signal handler for {sig.name}",
                    extra={"correlation_id": get_correlation_id()}
                )
            except (OSError, ValueError) as e:
                # Some signals may not be available on all platforms
                logger.warning(
                    f"Could not install handler for {sig.name}: {e}",
                    extra={"correlation_id": get_correlation_id()}
                )

    def _signal_handler(self, signum: int, frame) -> None:
        """
        Handle shutdown signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        sig_name = signal.Signals(signum).name
        logger.info(
            f"Received signal {sig_name}, initiating graceful shutdown",
            extra={
                "correlation_id": get_correlation_id(),
                "signal": sig_name,
                "signal_number": signum,
            }
        )

        # Set shutdown event (will be picked up by wait_for_shutdown)
        self._shutdown_event.set()

    def register_cleanup(self, cleanup_func: Callable) -> None:
        """
        Register a cleanup function to be called during shutdown.

        Cleanup functions can be sync or async.

        Args:
            cleanup_func: Function to call during cleanup

        Example:
            shutdown_manager.register_cleanup(cache.flush)
            shutdown_manager.register_cleanup(lambda: print("Goodbye!"))
        """
        self._cleanup_tasks.append(cleanup_func)
        logger.debug(
            f"Registered cleanup task: {cleanup_func.__name__}",
            extra={"correlation_id": get_correlation_id()}
        )

    def track_request(self, task: asyncio.Task) -> None:
        """
        Track an active request.

        Args:
            task: Async task representing the request
        """
        self._active_requests.add(task)
        task.add_done_callback(self._active_requests.discard)

    async def wait_for_shutdown(self) -> None:
        """
        Wait for shutdown signal.

        This is a blocking call that waits until a shutdown signal is received.
        Use this in your main server loop.

        Example:
            async def main():
                shutdown_manager = ShutdownManager()
                shutdown_manager.install_signal_handlers()

                # Start server
                server = await start_server()

                # Wait for shutdown
                await shutdown_manager.wait_for_shutdown()

                # Cleanup
                await shutdown_manager.shutdown()
        """
        await self._shutdown_event.wait()
        logger.info(
            "Shutdown signal received",
            extra={"correlation_id": get_correlation_id()}
        )

    async def shutdown(self) -> None:
        """
        Execute graceful shutdown sequence.

        Steps:
        1. Stop accepting new requests
        2. Wait for active requests to complete (with timeout)
        3. Run cleanup tasks
        4. Flush logs and metrics

        This should be called after wait_for_shutdown() returns.
        """
        if self._shutdown_initiated:
            logger.warning(
                "Shutdown already initiated, ignoring duplicate call",
                extra={"correlation_id": get_correlation_id()}
            )
            return

        self._shutdown_initiated = True
        self._shutdown_start_time = time.time()

        logger.info(
            "Starting graceful shutdown sequence",
            extra={
                "correlation_id": get_correlation_id(),
                "active_requests": len(self._active_requests),
                "cleanup_tasks": len(self._cleanup_tasks),
            }
        )

        # Step 1: Stop accepting new requests (handled by caller)
        logger.info("Step 1: Stopped accepting new requests")

        # Step 2: Wait for active requests to complete
        await self._wait_for_active_requests()

        # Step 3: Run cleanup tasks
        await self._run_cleanup_tasks()

        # Step 4: Final logging
        shutdown_duration = time.time() - self._shutdown_start_time
        logger.info(
            "Graceful shutdown completed",
            extra={
                "correlation_id": get_correlation_id(),
                "shutdown_duration_seconds": shutdown_duration,
            }
        )

    async def _wait_for_active_requests(self) -> None:
        """Wait for active requests to complete with timeout."""
        if not self._active_requests:
            logger.info("No active requests to wait for")
            return

        logger.info(
            f"Waiting for {len(self._active_requests)} active requests to complete",
            extra={
                "correlation_id": get_correlation_id(),
                "timeout": self.config.request_timeout,
            }
        )

        try:
            # Wait for all active requests with timeout
            await asyncio.wait_for(
                asyncio.gather(*self._active_requests, return_exceptions=True),
                timeout=self.config.request_timeout
            )
            logger.info("All active requests completed successfully")
        except asyncio.TimeoutError:
            remaining = len(self._active_requests)
            logger.warning(
                f"Timeout waiting for requests, {remaining} still active",
                extra={
                    "correlation_id": get_correlation_id(),
                    "remaining_requests": remaining,
                }
            )

            if self.config.force_after_timeout:
                logger.warning("Forcing shutdown despite active requests")
                # Cancel remaining tasks
                for task in self._active_requests:
                    if not task.done():
                        task.cancel()

    async def _run_cleanup_tasks(self) -> None:
        """Run all registered cleanup tasks."""
        if not self._cleanup_tasks:
            logger.info("No cleanup tasks to run")
            return

        logger.info(
            f"Running {len(self._cleanup_tasks)} cleanup tasks",
            extra={"correlation_id": get_correlation_id()}
        )

        for i, cleanup_func in enumerate(self._cleanup_tasks, 1):
            try:
                logger.debug(
                    f"Running cleanup task {i}/{len(self._cleanup_tasks)}: {cleanup_func.__name__}"
                )

                # Run cleanup (handle both sync and async)
                if asyncio.iscoroutinefunction(cleanup_func):
                    await asyncio.wait_for(
                        cleanup_func(),
                        timeout=self.config.cleanup_timeout
                    )
                else:
                    cleanup_func()

                logger.debug(f"Cleanup task {cleanup_func.__name__} completed")
            except asyncio.TimeoutError:
                logger.error(
                    f"Cleanup task {cleanup_func.__name__} timed out",
                    extra={"correlation_id": get_correlation_id()}
                )
            except Exception as e:
                logger.error(
                    f"Error in cleanup task {cleanup_func.__name__}: {e}",
                    exc_info=True,
                    extra={"correlation_id": get_correlation_id()}
                )

        logger.info("All cleanup tasks completed")

    def is_shutting_down(self) -> bool:
        """
        Check if shutdown has been initiated.

        Returns:
            True if shutdown is in progress
        """
        return self._shutdown_initiated

    def get_shutdown_stats(self) -> dict:
        """
        Get shutdown statistics.

        Returns:
            Dictionary with shutdown stats
        """
        return {
            "shutdown_initiated": self._shutdown_initiated,
            "active_requests": len(self._active_requests),
            "cleanup_tasks_registered": len(self._cleanup_tasks),
            "shutdown_duration": (
                time.time() - self._shutdown_start_time
                if self._shutdown_start_time
                else None
            ),
        }


# Global singleton instance
_shutdown_manager: Optional[ShutdownManager] = None


def get_shutdown_manager(config: Optional[ShutdownConfig] = None) -> ShutdownManager:
    """
    Get the global shutdown manager instance.

    Args:
        config: Optional configuration (only used on first call)

    Returns:
        Global ShutdownManager singleton
    """
    global _shutdown_manager
    if _shutdown_manager is None:
        _shutdown_manager = ShutdownManager(config)
    return _shutdown_manager


# Decorator for tracking requests
def track_request(func):
    """
    Decorator to track async requests during shutdown.

    Usage:
        @track_request
        async def handle_request():
            # Request is automatically tracked
            pass
    """
    async def wrapper(*args, **kwargs):
        shutdown_manager = get_shutdown_manager()

        # Don't accept new requests if shutting down
        if shutdown_manager.is_shutting_down():
            raise RuntimeError("Server is shutting down, not accepting new requests")

        # Create task and track it
        task = asyncio.current_task()
        if task:
            shutdown_manager.track_request(task)

        try:
            return await func(*args, **kwargs)
        finally:
            # Task is automatically removed via callback
            pass

    return wrapper
