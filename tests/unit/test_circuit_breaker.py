import asyncio
import pytest
from cde_orchestrator.infrastructure.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
    circuit_breaker,
)


class TestException(Exception):
    """Test exception for circuit breaker."""

    pass


@pytest.mark.asyncio
async def test_circuit_breaker_closed_state():
    """Test circuit breaker in CLOSED state (normal operation)."""
    breaker = CircuitBreaker(
        name="test",
        failure_threshold=3,
        timeout=1.0,
        expected_exception=TestException,
    )

    call_count = 0

    async def successful_call():
        nonlocal call_count
        call_count += 1
        return "success"

    # Should allow calls in CLOSED state
    result = await breaker.call(successful_call)
    assert result == "success"
    assert call_count == 1
    assert breaker.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_threshold():
    """Test circuit breaker opens after failure threshold."""
    breaker = CircuitBreaker(
        name="test",
        failure_threshold=3,
        timeout=1.0,
        expected_exception=TestException,
    )

    async def failing_call():
        raise TestException("Service unavailable")

    # Fail 3 times to reach threshold
    for i in range(3):
        with pytest.raises(TestException):
            await breaker.call(failing_call)

    # Circuit should now be OPEN
    assert breaker.state == CircuitState.OPEN

    # Further calls should fail immediately with CircuitBreakerError
    with pytest.raises(CircuitBreakerError) as exc_info:
        await breaker.call(failing_call)

    assert "Circuit breaker 'test' is OPEN" in str(exc_info.value)


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_recovery():
    """Test circuit breaker transitions to HALF_OPEN and recovers."""
    breaker = CircuitBreaker(
        name="test",
        failure_threshold=2,
        timeout=0.1,  # Short timeout for testing
        expected_exception=TestException,
    )

    async def failing_call():
        raise TestException("Service unavailable")

    async def successful_call():
        return "recovered"

    # Open the circuit
    for i in range(2):
        with pytest.raises(TestException):
            await breaker.call(failing_call)

    assert breaker.state == CircuitState.OPEN

    # Wait for timeout
    await asyncio.sleep(0.15)

    # Next call should enter HALF_OPEN
    result = await breaker.call(successful_call)
    assert result == "recovered"
    assert breaker.state == CircuitState.CLOSED  # Should close after success


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_fails_again():
    """Test circuit breaker reopens if HALF_OPEN call fails."""
    breaker = CircuitBreaker(
        name="test",
        failure_threshold=2,
        timeout=0.1,
        expected_exception=TestException,
    )

    async def failing_call():
        raise TestException("Still failing")

    # Open the circuit
    for i in range(2):
        with pytest.raises(TestException):
            await breaker.call(failing_call)

    assert breaker.state == CircuitState.OPEN

    # Wait for timeout
    await asyncio.sleep(0.15)

    # HALF_OPEN call fails
    with pytest.raises(TestException):
        await breaker.call(failing_call)

    # Should still be OPEN (failure count increased)
    assert breaker.state == CircuitState.OPEN


@pytest.mark.asyncio
async def test_circuit_breaker_decorator():
    """Test circuit breaker decorator."""
    call_count = 0

    @circuit_breaker("test_decorator", failure_threshold=2, timeout=0.1)
    async def decorated_function(should_fail: bool = False):
        nonlocal call_count
        call_count += 1
        if should_fail:
            raise TestException("Failed")
        return "success"

    # Successful calls
    result = await decorated_function(should_fail=False)
    assert result == "success"
    assert call_count == 1

    # Fail to open circuit
    for i in range(2):
        with pytest.raises(TestException):
            await decorated_function(should_fail=True)

    # Circuit should be open
    assert decorated_function._circuit_breaker.state == CircuitState.OPEN

    # Should block further calls
    with pytest.raises(CircuitBreakerError):
        await decorated_function(should_fail=False)


@pytest.mark.asyncio
async def test_circuit_breaker_stats():
    """Test circuit breaker statistics."""
    breaker = CircuitBreaker(
        name="test",
        failure_threshold=3,
        timeout=1.0,
        expected_exception=TestException,
    )

    async def successful_call():
        return "success"

    async def failing_call():
        raise TestException("Failed")

    # Some successful calls
    await breaker.call(successful_call)
    await breaker.call(successful_call)

    # Some failures
    with pytest.raises(TestException):
        await breaker.call(failing_call)

    stats = breaker.get_stats()
    assert stats["name"] == "test"
    assert stats["state"] == "closed"
    assert stats["success_count"] == 2
    assert stats["failure_count"] == 1
    assert stats["failure_threshold"] == 3


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_max_calls():
    """Test circuit breaker limits concurrent calls in HALF_OPEN state."""
    breaker = CircuitBreaker(
        name="test",
        failure_threshold=2,
        timeout=0.1,
        expected_exception=TestException,
        half_open_max_calls=1,
    )

    async def slow_call():
        await asyncio.sleep(0.2)
        return "success"

    async def failing_call():
        raise TestException("Failed")

    # Open the circuit
    for i in range(2):
        with pytest.raises(TestException):
            await breaker.call(failing_call)

    # Wait for timeout
    await asyncio.sleep(0.15)

    # Start first HALF_OPEN call (slow)
    task1 = asyncio.create_task(breaker.call(slow_call))
    await asyncio.sleep(0.05)  # Let it start

    # Second call should be blocked (max_calls=1)
    with pytest.raises(CircuitBreakerError) as exc_info:
        await breaker.call(slow_call)

    assert "HALF_OPEN" in str(exc_info.value)

    # Wait for first call to complete
    result = await task1
    assert result == "success"
    assert breaker.state == CircuitState.CLOSED
