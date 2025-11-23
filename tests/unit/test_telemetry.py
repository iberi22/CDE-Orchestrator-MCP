import asyncio
import json
import logging
from io import StringIO

import pytest

from cde_orchestrator.infrastructure.logging import (
    get_correlation_id,
)
from cde_orchestrator.infrastructure.telemetry import trace_execution


@pytest.mark.asyncio
async def test_trace_execution_async():
    # Capture logs
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    @trace_execution
    async def async_func(x):
        await asyncio.sleep(0.01)
        return x * 2

    # Run function
    result = await async_func(5)
    assert result == 10

    # Check logs
    logs = stream.getvalue()
    assert "Starting execution of async_func" in logs
    assert "Finished execution of async_func" in logs

    # Verify correlation ID was set (we can't easily check the value in the log string with simple formatter,
    # but we can check if get_correlation_id returns something inside the function if we modified the test)


@pytest.mark.asyncio
async def test_correlation_id_propagation():
    # We need to use the JsonFormatter to see the correlation ID in the output
    from cde_orchestrator.infrastructure.logging import JsonFormatter

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = []  # Clear existing
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    @trace_execution
    async def traced_func():
        cid = get_correlation_id()
        logging.getLogger().info("Inside function")
        return cid

    cid = await traced_func()
    assert cid is not None

    logs = stream.getvalue()
    log_lines = [json.loads(line) for line in logs.strip().split("\n")]

    # Check start log
    assert log_lines[0]["message"] == "Starting execution of traced_func"
    assert log_lines[0]["correlation_id"] == cid

    # Check inside log
    assert log_lines[1]["message"] == "Inside function"
    assert log_lines[1]["correlation_id"] == cid

    # Check metric log (added by trace_execution)
    assert log_lines[2]["message"].startswith("Metric: execution_time=")
    assert log_lines[2]["correlation_id"] == cid

    # Check end log
    assert log_lines[3]["message"] == "Finished execution of traced_func"
    assert log_lines[3]["correlation_id"] == cid


def test_trace_execution_sync():
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    @trace_execution
    def sync_func(x):
        return x + 1

    result = sync_func(10)
    assert result == 11

    logs = stream.getvalue()
    assert "Starting execution of sync_func" in logs
    assert "Finished execution of sync_func" in logs
