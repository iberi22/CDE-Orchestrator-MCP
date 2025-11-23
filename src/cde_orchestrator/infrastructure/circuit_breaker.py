"""
Circuit Breaker Pattern Implementation.

Prevents cascading failures by monitoring external service health
and temporarily blocking requests when a service is failing.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service is failing, requests fail immediately
- HALF_OPEN: Testing if service has recovered

Example:
    >>> breaker = CircuitBreaker(
    ...     failure_threshold=5,
    ...     timeout=60,
    ...     expected_exception=aiohttp.ClientError
    ... )
    >>>
    >>> @breaker
    ... async def call_external_api():
    ...     async with aiohttp.ClientSession() as session:
    ...         async with session.get("https://api.example.com") as resp:
    ...             return await resp.json()
"""

import asyncio
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar

from cde_orchestrator.infrastructure.logging import get_logger
from cde_orchestrator.infrastructure.telemetry import log_metric

logger = get_logger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, block requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """
    Circuit breaker for external service calls.

    Monitors failure rate and opens circuit when threshold is exceeded.
    After timeout, enters half-open state to test recovery.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
        half_open_max_calls: int = 1,
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Identifier for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery (half-open)
            expected_exception: Exception type that counts as failure
            half_open_max_calls: Max calls allowed in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Async function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original exception from func if circuit allows
        """
        async with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    logger.info(
                        f"Circuit breaker '{self.name}' entering HALF_OPEN state"
                    )
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                else:
                    log_metric(
                        "circuit_breaker_blocked",
                        1,
                        "count",
                        {"circuit": self.name, "state": "open"},
                    )
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Service unavailable. Retry after {self.timeout}s."
                    )

            # Check if we've exceeded half-open call limit
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    log_metric(
                        "circuit_breaker_blocked",
                        1,
                        "count",
                        {"circuit": self.name, "state": "half_open_limit"},
                    )
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is HALF_OPEN. "
                        f"Max concurrent calls ({self.half_open_max_calls}) reached."
                    )
                self._half_open_calls += 1

        # Execute the function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception:
            await self._on_failure()
            raise
        finally:
            if self._state == CircuitState.HALF_OPEN:
                async with self._lock:
                    self._half_open_calls -= 1

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return False
        return (time.time() - self._last_failure_time) >= self.timeout

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            self._failure_count = 0
            self._success_count += 1

            if self._state == CircuitState.HALF_OPEN:
                logger.info(
                    f"Circuit breaker '{self.name}' closing (service recovered)"
                )
                self._state = CircuitState.CLOSED
                log_metric(
                    "circuit_breaker_closed",
                    1,
                    "count",
                    {"circuit": self.name},
                )

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            logger.warning(
                f"Circuit breaker '{self.name}' failure "
                f"({self._failure_count}/{self.failure_threshold})"
            )

            if self._failure_count >= self.failure_threshold:
                if self._state != CircuitState.OPEN:
                    logger.error(
                        f"Circuit breaker '{self.name}' opening "
                        f"(threshold {self.failure_threshold} exceeded)"
                    )
                    self._state = CircuitState.OPEN
                    log_metric(
                        "circuit_breaker_opened",
                        1,
                        "count",
                        {"circuit": self.name, "failures": self._failure_count},
                    )

    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "last_failure_time": self._last_failure_time,
        }


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for applying circuit breaker to async functions.

    Args:
        name: Circuit breaker identifier
        failure_threshold: Failures before opening
        timeout: Seconds before attempting recovery
        expected_exception: Exception type that triggers circuit

    Example:
        >>> @circuit_breaker("github_api", failure_threshold=3, timeout=30)
        >>> async def fetch_from_github():
        ...     # API call here
        ...     pass
    """
    breaker = CircuitBreaker(
        name=name,
        failure_threshold=failure_threshold,
        timeout=timeout,
        expected_exception=expected_exception,
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await breaker.call(func, *args, **kwargs)

        # Attach breaker instance for testing/monitoring
        wrapper._circuit_breaker = breaker  # type: ignore
        return wrapper

    return decorator


class CircuitBreakerRegistry:
    """Registry to track all circuit breakers for monitoring."""

    def __init__(self) -> None:
        self._breakers: Dict[str, CircuitBreaker] = {}

    def register(self, breaker: CircuitBreaker) -> None:
        """Register a circuit breaker."""
        self._breakers[breaker.name] = breaker

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name."""
        return self._breakers.get(name)

    def get_all_metrics(self) -> Dict[str, dict]:
        """Get metrics for all registered circuit breakers."""
        return {name: breaker.get_stats() for name, breaker in self._breakers.items()}


# Global registry instance
_global_registry: Optional[CircuitBreakerRegistry] = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get global circuit breaker registry (lazy initialization)."""
    global _global_registry
    if _global_registry is None:
        _global_registry = CircuitBreakerRegistry()
    return _global_registry
