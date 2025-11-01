import sys
import types

import pytest

from cde_orchestrator.service_connector import CircuitBreaker, GitHubConnector


class DummyTimeout(Exception):
    """Simulated timeout exception."""


class DummyConnectionError(Exception):
    """Simulated connection error."""


class DummyHTTPError(Exception):
    """Simulated HTTP error."""


class DummyResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {"id": 123}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise DummyHTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def _stub_requests(behavior):
    """Create a stubbed requests module with controllable post behavior."""
    module = types.SimpleNamespace()
    module.exceptions = types.SimpleNamespace(
        Timeout=DummyTimeout,
        ConnectionError=DummyConnectionError,
        HTTPError=DummyHTTPError,
        RequestException=Exception,
    )
    module.post = behavior
    return module


def _connector_with_stub(monkeypatch, behavior, failure_threshold: int = 2) -> GitHubConnector:
    """Helper to build a GitHubConnector with a stubbed requests module."""
    stub = _stub_requests(behavior)
    monkeypatch.setitem(sys.modules, "requests", stub)

    breaker = CircuitBreaker(failure_threshold=failure_threshold, recovery_timeout=1)
    connector = GitHubConnector(
        circuit_breaker=breaker,
        default_timeout=1,
        retry_attempts=1,
    )
    connector.mcp_available = False
    connector.token = "token"
    return connector


def test_github_connector_timeout_fallback(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise DummyTimeout("request timed out")

    connector = _connector_with_stub(monkeypatch, raise_timeout)
    result = connector.create_issue("owner", "repo", "title", "body")

    assert result["method"] == "local"
    assert result["fallback_reason"] == "timeout"
    assert connector.circuit_breaker.failure_count == 1


def test_circuit_breaker_opens_after_consecutive_failures(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise DummyTimeout("timeout")

    connector = _connector_with_stub(monkeypatch, raise_timeout, failure_threshold=2)

    # First call increments failure count
    connector.create_issue("owner", "repo", "title", "body")
    assert connector.circuit_breaker.failure_count == 1
    assert connector.circuit_breaker.state == "closed"

    # Second failure should open the circuit
    connector.create_issue("owner", "repo", "title", "body")
    assert connector.circuit_breaker.state == "open"

    # Subsequent calls should short-circuit to local fallback
    result = connector.create_issue("owner", "repo", "title", "body")
    assert result["fallback_reason"] == "circuit_open"
    assert connector.circuit_breaker.state == "open"


def test_success_resets_circuit_breaker(monkeypatch):
    calls = {"count": 0}

    def flaky_post(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise DummyConnectionError("transient network issue")
        return DummyResponse(payload={"id": 456})

    connector = _connector_with_stub(monkeypatch, flaky_post, failure_threshold=3)
    connector.retry_attempts = 2  # allow a retry within the same call

    result = connector.create_issue("owner", "repo", "title", "body")

    assert result == {"id": 456}
    assert connector.circuit_breaker.failure_count == 0
    assert connector.circuit_breaker.state == "closed"
