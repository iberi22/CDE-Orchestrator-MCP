import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar

from cde_orchestrator.infrastructure.logging import get_logger, set_correlation_id

logger = get_logger(__name__)

T = TypeVar("T")


def log_metric(
    name: str,
    value: float,
    unit: str = "count",
    tags: Optional[Dict[str, str]] = None,
) -> None:
    """
    Log a metric in a structured format.
    """
    metric_data = {
        "metric_name": name,
        "metric_value": value,
        "metric_unit": unit,
    }
    if tags:
        metric_data.update(tags)

    logger.info(
        f"Metric: {name}={value}{unit}", extra={"context": {"metric": metric_data}}
    )


def trace_execution(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to trace function execution.
    - Sets a correlation ID if not present.
    - Logs start and end of execution with timing.
    - Handles async and sync functions.
    """

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        correlation_id = set_correlation_id()
        start_time = time.perf_counter()
        func_name = func.__name__

        logger.info(
            f"Starting execution of {func_name}",
            extra={"context": {"args": str(args), "kwargs": str(kwargs)}},
        )

        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(
                f"Error in {func_name}: {e}",
                exc_info=True,
                extra={"context": {"correlation_id": correlation_id}},
            )
            raise
        finally:
            duration = time.perf_counter() - start_time
            log_metric(
                "execution_time",
                duration,
                "s",
                {"function": func_name, "correlation_id": correlation_id},
            )
            logger.info(
                f"Finished execution of {func_name}",
                extra={"context": {"duration_seconds": duration}},
            )

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        correlation_id = set_correlation_id()
        start_time = time.perf_counter()
        func_name = func.__name__

        logger.info(
            f"Starting execution of {func_name}",
            extra={"context": {"args": str(args), "kwargs": str(kwargs)}},
        )

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(
                f"Error in {func_name}: {e}",
                exc_info=True,
                extra={"context": {"correlation_id": correlation_id}},
            )
            raise
        finally:
            duration = time.perf_counter() - start_time
            log_metric(
                "execution_time",
                duration,
                "s",
                {"function": func_name, "correlation_id": correlation_id},
            )
            logger.info(
                f"Finished execution of {func_name}",
                extra={"context": {"duration_seconds": duration}},
            )

    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
