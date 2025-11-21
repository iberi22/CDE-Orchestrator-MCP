# src/cde_orchestrator/infrastructure/error_handling.py
import functools
import inspect
import logging
import traceback
from typing import Any, Callable, Dict, Union, cast

from cde_orchestrator.domain.exceptions import CDEError

logger = logging.getLogger(__name__)


def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to handle exceptions in MCP tools and return user-friendly errors.

    Wraps tool execution to catch CDEError (domain errors) and generic Exceptions,
    formatting them into a standardized JSON response structure.
    Supports both synchronous and asynchronous functions.
    """
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(
            *args: Any, **kwargs: Any
        ) -> Union[Dict[str, Any], str]:
            try:
                return cast(Union[Dict[str, Any], str], await func(*args, **kwargs))
            except CDEError as e:
                # Domain error - expected business logic failure
                logger.error(
                    f"Domain error in {func.__name__}: {e.message}",
                    exc_info=True,
                    extra={"code": e.code, "context": e.context},
                )
                return {
                    "status": "error",
                    "error_type": e.__class__.__name__,
                    "error_code": e.code,
                    "message": e.message,
                    "recoverable": e.recoverable,
                    "details": e.context,
                }
            except Exception as e:
                # Unexpected system error
                logger.error(
                    f"System error in {func.__name__}: {str(e)}", exc_info=True
                )
                return {
                    "status": "error",
                    "error_type": "SystemError",
                    "error_code": "E999",
                    "message": f"An unexpected error occurred: {str(e)}",
                    "recoverable": False,
                    "details": {"traceback": traceback.format_exc()},
                }

        return async_wrapper

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[Dict[str, Any], str]:
        try:
            return cast(Union[Dict[str, Any], str], func(*args, **kwargs))
        except CDEError as e:
            # Domain error - expected business logic failure
            logger.error(
                f"Domain error in {func.__name__}: {e.message}",
                exc_info=True,
                extra={"code": e.code, "context": e.context},
            )
            return {
                "status": "error",
                "error_type": e.__class__.__name__,
                "error_code": e.code,
                "message": e.message,
                "recoverable": e.recoverable,
                "details": e.context,
            }
        except Exception as e:
            # Unexpected system error
            logger.error(f"System error in {func.__name__}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error_type": "SystemError",
                "error_code": "E999",
                "message": f"An unexpected error occurred: {str(e)}",
                "recoverable": False,
                "details": {"traceback": traceback.format_exc()},
            }

    return wrapper
