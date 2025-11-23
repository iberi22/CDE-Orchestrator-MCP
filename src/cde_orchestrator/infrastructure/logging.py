import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Optional

# Context variable to store correlation ID
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set the correlation ID for the current context.
    If none provided, generates a new UUID.
    Returns the set correlation ID.
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_ctx.set(correlation_id)
    return correlation_id


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for production logging.
    Includes correlation_id if present in context.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if present
        correlation_id = get_correlation_id()
        if correlation_id:
            log_record["correlation_id"] = correlation_id

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record (context)
        # We look for 'context' attribute or extra dict
        if hasattr(record, "context"):
            log_record["context"] = record.context
        elif hasattr(record, "extra"):
            log_record["context"] = record.extra

        return json.dumps(log_record)


def configure_logging(level: str = "INFO", json_format: bool = True) -> None:
    """
    Configure root logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON formatting (default: True for prod)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)

    if json_format:
        handler.setFormatter(JsonFormatter())
    else:
        # Also add correlation ID to text format if possible, but JSON is priority
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s"
            )
        )
        # Note: standard formatter won't automatically pick up contextvar without a filter
        # For now, we focus on JSON format which explicitly calls get_correlation_id()

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
