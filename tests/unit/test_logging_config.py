# tests/unit/test_logging_config.py
import io
import json
import logging

from cde_orchestrator.infrastructure.logging import (
    JsonFormatter,
    configure_logging,
    get_logger,
)


def test_json_formatter():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="test message",
        args=(),
        exc_info=None,
    )
    record.context = {"user_id": "123"}

    output = formatter.format(record)
    data = json.loads(output)

    assert data["message"] == "test message"
    assert data["level"] == "INFO"
    assert data["context"]["user_id"] == "123"
    assert "timestamp" in data


def test_configure_logging():
    # Capture stdout
    from unittest.mock import patch

    with patch("sys.stdout", new=io.StringIO()) as fake_out:
        configure_logging(level="INFO", json_format=True)
        logger = get_logger("test_config")
        logger.info("hello world")

        output = fake_out.getvalue()
        data = json.loads(output)
        assert data["message"] == "hello world"
