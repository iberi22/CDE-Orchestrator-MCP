# src/cde_orchestrator/domain/resilience.py
"""
Domain Resilience - Retry logic and error recovery for CDE operations.

Provides decorators and utilities for handling transient failures in:
- File system operations
- Network calls
- External service integrations
"""

import logging
from functools import wraps
from typing import Any, Callable, Optional, Type, Tuple

from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    RetryError,
)

logger = logging.getLogger(__name__)


def retry_operation(
    max_attempts: int = 3,
    wait_multiplier: float = 1.0,
    wait_min: float = 1.0,
    wait_max: float = 10.0,
    retry_on: Tuple[Type[Exception], ...] = (IOError, OSError, ConnectionError),
    fallback_value: Optional[Any] = None,
) -> Callable:
    """
    Decorator to retry operations with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        wait_multiplier: Multiplier for exponential backoff
        wait_min: Minimum wait time between retries (seconds)
        wait_max: Maximum wait time between retries (seconds)
        retry_on: Tuple of exception types to retry on
        fallback_value: Value to return if all retries fail (if None, re-raises)

    Usage:
        @retry_operation(max_attempts=5, retry_on=(FileNotFoundError,))
        def read_config_file(path: str) -> dict:
            with open(path) as f:
                return json.load(f)

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retrying = Retrying(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(
                    multiplier=wait_multiplier,
                    min=wait_min,
                    max=wait_max,
                ),
                retry=retry_if_exception_type(retry_on),
                reraise=True,
            )

            try:
                for attempt in retrying:
                    with attempt:
                        result = func(*args, **kwargs)
                        logger.debug(
                            "Operation %s succeeded on attempt %d",
                            func.__name__,
                            attempt.retry_state.attempt_number,
                        )
                        return result
            except Exception as e:
                # When reraise=True, tenacity raises the original exception
                # Check if it's one of the retry_on exceptions that exhausted retries
                if isinstance(e, retry_on):
                    logger.error(
                        "Operation %s failed after %d attempts: %s",
                        func.__name__,
                        max_attempts,
                        e,
                    )
                    if fallback_value is not None:
                        logger.warning(
                            "Returning fallback value for %s: %s",
                            func.__name__,
                            fallback_value,
                        )
                        return fallback_value
                raise

        return wrapper

    return decorator


def retry_async_operation(
    max_attempts: int = 3,
    wait_multiplier: float = 1.0,
    wait_min: float = 1.0,
    wait_max: float = 10.0,
    retry_on: Tuple[Type[Exception], ...] = (IOError, OSError, ConnectionError),
    fallback_value: Optional[Any] = None,
) -> Callable:
    """
    Decorator to retry async operations with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        wait_multiplier: Multiplier for exponential backoff
        wait_min: Minimum wait time between retries (seconds)
        wait_max: Maximum wait time between retries (seconds)
        retry_on: Tuple of exception types to retry on
        fallback_value: Value to return if all retries fail (if None, re-raises)

    Usage:
        @retry_async_operation(max_attempts=5)
        async def fetch_remote_data(url: str) -> dict:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()

    Returns:
        Decorated async function with retry logic
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            from tenacity import AsyncRetrying

            retrying = AsyncRetrying(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(
                    multiplier=wait_multiplier,
                    min=wait_min,
                    max=wait_max,
                ),
                retry=retry_if_exception_type(retry_on),
                reraise=True,
            )

            try:
                async for attempt in retrying:
                    with attempt:
                        result = await func(*args, **kwargs)
                        logger.debug(
                            "Async operation %s succeeded on attempt %d",
                            func.__name__,
                            attempt.retry_state.attempt_number,
                        )
                        return result
            except Exception as e:
                # When reraise=True, tenacity raises the original exception
                if isinstance(e, retry_on):
                    logger.error(
                        "Async operation %s failed after %d attempts: %s",
                        func.__name__,
                        max_attempts,
                        e,
                    )
                    if fallback_value is not None:
                        logger.warning(
                            "Returning fallback value for %s: %s",
                            func.__name__,
                            fallback_value,
                        )
                        return fallback_value
                raise

        return wrapper

    return decorator


# Predefined retry configurations for common scenarios

# File system operations (quick retries)
retry_fs_operation = retry_operation(
    max_attempts=3,
    wait_multiplier=0.5,
    wait_min=0.5,
    wait_max=2.0,
    retry_on=(IOError, OSError, PermissionError),
)

# Network operations (longer backoff)
retry_network_operation = retry_operation(
    max_attempts=5,
    wait_multiplier=1.0,
    wait_min=1.0,
    wait_max=30.0,
    retry_on=(ConnectionError, TimeoutError),
)

# External API calls (moderate retries)
retry_api_call = retry_operation(
    max_attempts=3,
    wait_multiplier=1.0,
    wait_min=1.0,
    wait_max=10.0,
    retry_on=(ConnectionError, TimeoutError),
)
