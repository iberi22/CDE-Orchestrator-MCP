# src/cde_orchestrator/infrastructure/logging.py
import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for production logging.
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


def configure_logging(level: str = "INFO", json_format: bool = True):
    """
    Configure root logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON formatting (default: True for prod)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)

    if json_format:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
