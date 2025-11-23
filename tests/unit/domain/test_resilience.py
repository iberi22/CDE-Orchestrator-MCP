# tests/unit/domain/test_resilience.py
"""
Unit tests for domain resilience module.
Tests retry decorators and error recovery logic.
"""


import pytest

from cde_orchestrator.domain.resilience import (
    retry_async_operation,
    retry_fs_operation,
    retry_network_operation,
    retry_operation,
)


class TestRetryOperation:
    """Test suite for retry_operation decorator."""

    def test_successful_operation_no_retry(self):
        """Test that successful operations don't retry."""
        call_count = 0

        @retry_operation(max_attempts=3)
        def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_func()

        assert result == "success"
        assert call_count == 1  # Should only be called once

    def test_retry_on_transient_failure(self):
        """Test that transient failures are retried."""
        call_count = 0

        @retry_operation(max_attempts=3, retry_on=(ValueError,))
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient error")
            return "success"

        result = flaky_func()

        assert result == "success"
        assert call_count == 3  # Should retry twice, succeed on third

    def test_max_attempts_exceeded(self):
        """Test that max attempts are respected."""
        call_count = 0

        @retry_operation(max_attempts=3, retry_on=(ValueError,))
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")

        with pytest.raises(ValueError, match="Persistent error"):
            always_fails()

        assert call_count == 3  # Should try exactly 3 times

    def test_fallback_value_on_failure(self):
        """Test that fallback value is returned on failure."""

        @retry_operation(
            max_attempts=2, retry_on=(ValueError,), fallback_value="fallback"
        )
        def always_fails():
            raise ValueError("Error")

        result = always_fails()

        assert result == "fallback"

    def test_non_retryable_exception(self):
        """Test that non-retryable exceptions are not retried."""
        call_count = 0

        @retry_operation(max_attempts=3, retry_on=(IOError,))
        def raises_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("Not retryable")

        with pytest.raises(TypeError):
            raises_type_error()

        assert call_count == 1  # Should not retry

    def test_retry_fs_operation_predefined(self):
        """Test predefined retry_fs_operation decorator."""
        call_count = 0

        @retry_fs_operation
        def read_file():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise IOError("File locked")
            return "file content"

        result = read_file()

        assert result == "file content"
        assert call_count == 2

    def test_retry_network_operation_predefined(self):
        """Test predefined retry_network_operation decorator."""
        call_count = 0

        @retry_network_operation
        def fetch_data():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Network timeout")
            return {"data": "value"}

        result = fetch_data()

        assert result == {"data": "value"}
        assert call_count == 3


class TestRetryAsyncOperation:
    """Test suite for retry_async_operation decorator."""

    @pytest.mark.asyncio
    async def test_successful_async_operation(self):
        """Test that successful async operations don't retry."""
        call_count = 0

        @retry_async_operation(max_attempts=3)
        async def successful_async_func():
            nonlocal call_count
            call_count += 1
            return "async success"

        result = await successful_async_func()

        assert result == "async success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_async_on_failure(self):
        """Test that async transient failures are retried."""
        call_count = 0

        @retry_async_operation(max_attempts=3, retry_on=(ValueError,))
        async def flaky_async_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Async transient error")
            return "async success"

        result = await flaky_async_func()

        assert result == "async success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_max_attempts_exceeded(self):
        """Test that async max attempts are respected."""
        call_count = 0

        @retry_async_operation(max_attempts=3, retry_on=(ValueError,))
        async def always_fails_async():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent async error")

        with pytest.raises(ValueError, match="Persistent async error"):
            await always_fails_async()

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_fallback_value(self):
        """Test that async fallback value is returned on failure."""

        @retry_async_operation(
            max_attempts=2, retry_on=(ValueError,), fallback_value="async fallback"
        )
        async def always_fails_async():
            raise ValueError("Async error")

        result = await always_fails_async()

        assert result == "async fallback"


class TestRetryIntegration:
    """Integration tests for retry logic with real-world scenarios."""

    def test_file_operation_with_permission_error(self):
        """Test retry behavior with file permission errors."""
        attempts = []

        @retry_fs_operation
        def write_file():
            attempts.append(1)
            if len(attempts) < 2:
                raise PermissionError("File locked by another process")
            return True

        result = write_file()

        assert result is True
        assert len(attempts) == 2

    def test_network_operation_with_timeout(self):
        """Test retry behavior with network timeouts."""
        attempts = []

        @retry_network_operation
        def api_call():
            attempts.append(1)
            if len(attempts) < 4:
                raise TimeoutError("Request timed out")
            return {"status": "ok"}

        result = api_call()

        assert result == {"status": "ok"}
        assert len(attempts) == 4
