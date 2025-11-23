"""
Unit tests for rate limiter infrastructure.

Tests cover:
- Token bucket algorithm correctness
- Rate limiting behavior
- Burst allowance
- Metrics tracking
- Async safety
- Decorator pattern

Author: CDE Orchestrator Team
Created: 2025-11-22
"""

import asyncio
import time

import pytest

from src.cde_orchestrator.infrastructure.rate_limiter import (
    RateLimitConfig,
    RateLimiter,
    TokenBucket,
    get_rate_limiter,
    rate_limited,
)


class TestRateLimitConfig:
    """Test rate limit configuration."""

    def test_valid_config(self):
        """Test creating valid configuration."""
        config = RateLimitConfig(
            max_tokens=100,
            refill_rate=1.0,
            burst_allowance=10,
        )

        assert config.max_tokens == 100
        assert config.refill_rate == 1.0
        assert config.burst_allowance == 10

    def test_invalid_max_tokens(self):
        """Test validation of max_tokens."""
        with pytest.raises(ValueError, match="max_tokens must be positive"):
            RateLimitConfig(max_tokens=0, refill_rate=1.0)

    def test_invalid_refill_rate(self):
        """Test validation of refill_rate."""
        with pytest.raises(ValueError, match="refill_rate must be positive"):
            RateLimitConfig(max_tokens=100, refill_rate=0)

    def test_invalid_burst_allowance(self):
        """Test validation of burst_allowance."""
        with pytest.raises(ValueError, match="burst_allowance cannot be negative"):
            RateLimitConfig(max_tokens=100, refill_rate=1.0, burst_allowance=-1)


class TestTokenBucket:
    """Test token bucket rate limiter."""

    @pytest.mark.asyncio
    async def test_basic_acquire(self):
        """Test basic token acquisition."""
        config = RateLimitConfig(max_tokens=10, refill_rate=1.0)
        bucket = TokenBucket(config)

        # Should acquire immediately (bucket starts full)
        result = await bucket.acquire(1)
        assert result is True

        metrics = bucket.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["rejected_requests"] == 0

    @pytest.mark.asyncio
    async def test_acquire_multiple_tokens(self):
        """Test acquiring multiple tokens at once."""
        config = RateLimitConfig(max_tokens=10, refill_rate=1.0)
        bucket = TokenBucket(config)

        # Acquire 5 tokens
        result = await bucket.acquire(5)
        assert result is True

        # Should have ~5 tokens left
        metrics = bucket.get_metrics()
        assert 4 <= metrics["current_tokens"] <= 6

    @pytest.mark.asyncio
    async def test_try_acquire_success(self):
        """Test try_acquire when tokens available."""
        config = RateLimitConfig(max_tokens=10, refill_rate=1.0)
        bucket = TokenBucket(config)

        result = await bucket.try_acquire(1)
        assert result is True

    @pytest.mark.asyncio
    async def test_try_acquire_failure(self):
        """Test try_acquire when insufficient tokens."""
        config = RateLimitConfig(max_tokens=5, refill_rate=0.1)
        bucket = TokenBucket(config)

        # Exhaust tokens
        await bucket.acquire(5)

        # Try to acquire more (should fail immediately)
        result = await bucket.try_acquire(1)
        assert result is False

        metrics = bucket.get_metrics()
        assert metrics["rejected_requests"] == 1

    @pytest.mark.asyncio
    async def test_refill_over_time(self):
        """Test token refill over time."""
        config = RateLimitConfig(max_tokens=10, refill_rate=10.0)  # 10 tokens/sec
        bucket = TokenBucket(config)

        # Exhaust tokens
        await bucket.acquire(10)

        # Wait for refill (100ms = 1 token at 10/sec)
        await asyncio.sleep(0.1)

        # Should be able to acquire 1 token
        result = await bucket.try_acquire(1)
        assert result is True

    @pytest.mark.asyncio
    async def test_burst_allowance(self):
        """Test burst allowance allows extra tokens."""
        config = RateLimitConfig(
            max_tokens=10,
            refill_rate=1.0,
            burst_allowance=5,
        )
        bucket = TokenBucket(config)

        # Should be able to acquire 15 tokens (10 + 5 burst)
        result = await bucket.acquire(15)
        assert result is True

    @pytest.mark.asyncio
    async def test_wait_for_tokens(self):
        """Test waiting for tokens to refill."""
        config = RateLimitConfig(max_tokens=5, refill_rate=10.0)  # Fast refill
        bucket = TokenBucket(config)

        # Exhaust tokens
        await bucket.acquire(5)

        # Acquire with wait (should wait for refill)
        start = time.monotonic()
        result = await bucket.acquire(2, wait=True)
        elapsed = time.monotonic() - start

        assert result is True
        assert elapsed >= 0.1  # Should wait ~200ms for 2 tokens at 10/sec

    @pytest.mark.asyncio
    async def test_metrics_tracking(self):
        """Test metrics are tracked correctly."""
        config = RateLimitConfig(max_tokens=10, refill_rate=1.0)
        bucket = TokenBucket(config)

        # Make some requests
        await bucket.acquire(1)
        await bucket.acquire(2)
        await bucket.try_acquire(100)  # Should be rejected

        metrics = bucket.get_metrics()
        assert metrics["total_requests"] == 3
        assert metrics["rejected_requests"] == 1
        assert metrics["rejection_rate"] == 1 / 3

    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test thread-safe concurrent access."""
        config = RateLimitConfig(max_tokens=100, refill_rate=10.0)
        bucket = TokenBucket(config)

        # Simulate 50 concurrent requests
        tasks = [bucket.acquire(1) for _ in range(50)]
        results = await asyncio.gather(*tasks)

        # All should succeed (100 tokens available)
        assert all(results)

        metrics = bucket.get_metrics()
        assert metrics["total_requests"] == 50


class TestRateLimiter:
    """Test global rate limiter manager."""

    @pytest.mark.asyncio
    async def test_get_limiter(self):
        """Test getting a rate limiter for a service."""
        limiter = RateLimiter()

        bucket = await limiter.get_limiter("github_api")
        assert isinstance(bucket, TokenBucket)

    @pytest.mark.asyncio
    async def test_get_limiter_caching(self):
        """Test limiters are cached per service."""
        limiter = RateLimiter()

        bucket1 = await limiter.get_limiter("github_api")
        bucket2 = await limiter.get_limiter("github_api")

        # Should be the same instance
        assert bucket1 is bucket2

    @pytest.mark.asyncio
    async def test_get_limiter_unknown_service(self):
        """Test error on unknown service."""
        limiter = RateLimiter()

        with pytest.raises(ValueError, match="Unknown service"):
            await limiter.get_limiter("unknown_service")

    @pytest.mark.asyncio
    async def test_limit_context_manager(self):
        """Test rate limiting with context manager."""
        limiter = RateLimiter()

        # Should succeed
        async with limiter.limit("mcp_tools"):
            pass  # Operation would go here

    @pytest.mark.asyncio
    async def test_limit_context_manager_exceeded(self):
        """Test rate limit exceeded with wait=False."""
        limiter = RateLimiter()

        # Exhaust tokens
        bucket = await limiter.get_limiter("mcp_tools")
        await bucket.acquire(70)  # 60 + 10 burst

        # Should raise error
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            async with limiter.limit("mcp_tools", wait=False):
                pass

    @pytest.mark.asyncio
    async def test_get_all_metrics(self):
        """Test getting metrics for all limiters."""
        limiter = RateLimiter()

        # Use some limiters
        async with limiter.limit("github_api"):
            pass
        async with limiter.limit("web_research"):
            pass

        metrics = await limiter.get_all_metrics()

        assert "github_api" in metrics
        assert "web_research" in metrics
        assert metrics["github_api"]["total_requests"] == 1
        assert metrics["web_research"]["total_requests"] == 1


class TestRateLimitedDecorator:
    """Test rate_limited decorator."""

    @pytest.mark.asyncio
    async def test_decorator_basic(self):
        """Test basic decorator usage."""
        call_count = 0

        @rate_limited("filesystem")
        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await test_func()

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_decorator_with_args(self):
        """Test decorator with function arguments."""

        @rate_limited("filesystem")
        async def test_func(x: int, y: int) -> int:
            return x + y

        result = await test_func(2, 3)
        assert result == 5

    @pytest.mark.asyncio
    async def test_decorator_rate_limiting(self):
        """Test decorator actually rate limits."""
        limiter = get_rate_limiter()

        @rate_limited("mcp_tools", tokens=10)
        async def test_func():
            return "success"

        # First call should succeed
        await test_func()

        # Check metrics
        metrics = await limiter.get_all_metrics()
        assert metrics["mcp_tools"]["total_requests"] >= 1


class TestGlobalSingleton:
    """Test global rate limiter singleton."""

    def test_get_rate_limiter_singleton(self):
        """Test get_rate_limiter returns singleton."""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()

        assert limiter1 is limiter2


class TestPredefinedConfigs:
    """Test predefined service configurations."""

    def test_all_configs_valid(self):
        """Test all predefined configs are valid."""
        limiter = RateLimiter()

        for service, config in limiter.CONFIGS.items():
            assert config.max_tokens > 0
            assert config.refill_rate > 0
            assert config.burst_allowance >= 0

    def test_github_api_config(self):
        """Test GitHub API has appropriate limits."""
        limiter = RateLimiter()
        config = limiter.CONFIGS["github_api"]

        # Should be conservative (GitHub has 5000/hour limit)
        assert config.max_tokens <= 100
        assert config.refill_rate <= 2.0

    def test_filesystem_config(self):
        """Test filesystem has generous limits."""
        limiter = RateLimiter()
        config = limiter.CONFIGS["filesystem"]

        # Should be generous (local operations)
        assert config.max_tokens >= 100
        assert config.refill_rate >= 2.0
