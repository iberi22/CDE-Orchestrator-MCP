from unittest.mock import AsyncMock
import pytest
import httpx
from cde_orchestrator.adapters.service.service_adapter import (
    CircuitBreaker,
    GitHubConnector,
)

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


class DummyResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {"id": 123}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(f"HTTP {self.status_code}", request=None, response=self)

    def json(self):
        return self._payload


def _connector_with_stub(
    monkeypatch, behavior, failure_threshold: int = 2
) -> GitHubConnector:
    """Helper to build a GitHubConnector with a stubbed httpx client."""
    mock_async_client = AsyncMock()

    # The behavior is the side_effect for the 'post' method
    mock_async_client.post = AsyncMock(side_effect=behavior)

    # We patch the class to return an instance of our mock client
    monkeypatch.setattr("httpx.AsyncClient", lambda: mock_async_client)

    breaker = CircuitBreaker(failure_threshold=failure_threshold, recovery_timeout=1)
    connector = GitHubConnector(
        circuit_breaker=breaker,
        default_timeout=1,
        retry_attempts=1,
    )
    connector.mcp_available = False
    connector.token = "token"
    return connector


async def test_github_connector_timeout_fallback(monkeypatch):
    connector = _connector_with_stub(monkeypatch, httpx.TimeoutException("request timed out"))
    result = await connector.create_issue("owner", "repo", "title", "body")

    assert result["method"] == "local"
    assert result["fallback_reason"] == "timeout"
    assert connector.circuit_breaker.failure_count == 1


async def test_circuit_breaker_opens_after_consecutive_failures(monkeypatch):
    connector = _connector_with_stub(
        monkeypatch, httpx.TimeoutException("timeout"), failure_threshold=2
    )

    # First call increments failure count
    await connector.create_issue("owner", "repo", "title", "body")
    assert connector.circuit_breaker.failure_count == 1
    assert connector.circuit_breaker.state == "closed"

    # Second failure should open the circuit
    await connector.create_issue("owner", "repo", "title", "body")
    assert connector.circuit_breaker.state == "open"

    # Subsequent calls should short-circuit to local fallback
    result = await connector.create_issue("owner", "repo", "title", "body")
    assert result["fallback_reason"] == "circuit_open"
    assert connector.circuit_breaker.state == "open"


async def test_success_resets_circuit_breaker(monkeypatch):
    calls = {"count": 0}

    def flaky_post(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.ConnectError("transient network issue")
        return DummyResponse(payload={"id": 456})

    connector = _connector_with_stub(monkeypatch, flaky_post, failure_threshold=3)
    connector.retry_attempts = 2  # allow a retry within the same call

    result = await connector.create_issue("owner", "repo", "title", "body")

    assert result == {"id": 456}
    assert connector.circuit_breaker.failure_count == 0
    assert connector.circuit_breaker.state == "closed"
