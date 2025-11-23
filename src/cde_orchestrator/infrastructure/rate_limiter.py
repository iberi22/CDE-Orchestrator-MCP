"""
Rate Limiting Infrastructure - Token Bucket Algorithm

Implements rate limiting to protect the system from overload:
- Token bucket algorithm for smooth rate limiting
- Per-service and global limits
- Async-safe with thread-safe token management
- Integration with telemetry for monitoring

Author: CDE Orchestrator Team
Created: 2025-11-22
"""

import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Dict, Optional

from cde_orchestrator.infrastructure.logging import get_correlation_id, get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for a rate limiter."""

    max_tokens: int  # Maximum tokens in bucket
    refill_rate: float  # Tokens added per second
    burst_allowance: int = 0  # Extra tokens for bursts (default: 0)

    def __post_init__(self):
        """Validate configuration."""
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if self.refill_rate <= 0:
            raise ValueError("refill_rate must be positive")
        if self.burst_allowance < 0:
            raise ValueError("burst_allowance cannot be negative")


class TokenBucket:
    """
    Token bucket rate limiter implementation.

    Thread-safe, async-compatible token bucket for rate limiting.
    Tokens are refilled continuously at a configured rate.
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize token bucket.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self._tokens = float(config.max_tokens + config.burst_allowance)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

        # Metrics
        self._total_requests = 0
        self._rejected_requests = 0
        self._total_wait_time = 0.0

        logger.info(
            "TokenBucket initialized",
            extra={
                "correlation_id": get_correlation_id(),
                "max_tokens": config.max_tokens,
                "refill_rate": config.refill_rate,
                "burst_allowance": config.burst_allowance,
            },
        )

    async def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_refill

        # Calculate tokens to add
        tokens_to_add = elapsed * self.config.refill_rate

        # Update tokens (capped at max + burst)
        max_capacity = self.config.max_tokens + self.config.burst_allowance
        self._tokens = min(self._tokens + tokens_to_add, max_capacity)
        self._last_refill = now

    async def acquire(self, tokens: int = 1, wait: bool = True) -> bool:
        """
        Acquire tokens from the bucket.

        Args:
            tokens: Number of tokens to acquire
            wait: If True, wait for tokens to become available
                  If False, return immediately if insufficient tokens

        Returns:
            True if tokens acquired, False if rejected (when wait=False)
        """
        if tokens <= 0:
            raise ValueError("tokens must be positive")

        async with self._lock:
            self._total_requests += 1
            start_time = time.monotonic()

            while True:
                await self._refill()

                if self._tokens >= tokens:
                    # Tokens available
                    self._tokens -= tokens
                    wait_time = time.monotonic() - start_time
                    self._total_wait_time += wait_time

                    logger.debug(
                        "Tokens acquired",
                        extra={
                            "correlation_id": get_correlation_id(),
                            "tokens_requested": tokens,
                            "tokens_remaining": self._tokens,
                            "wait_time_ms": wait_time * 1000,
                        },
                    )
                    return True

                if not wait:
                    # Reject immediately
                    self._rejected_requests += 1
                    logger.warning(
                        "Rate limit exceeded - request rejected",
                        extra={
                            "correlation_id": get_correlation_id(),
                            "tokens_requested": tokens,
                            "tokens_available": self._tokens,
                            "rejection_rate": self._rejected_requests
                            / self._total_requests,
                        },
                    )
                    return False

                # Wait for next refill opportunity
                tokens_needed = tokens - self._tokens
                wait_time = tokens_needed / self.config.refill_rate
                await asyncio.sleep(min(wait_time, 0.1))  # Cap at 100ms

    async def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without waiting.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens acquired, False otherwise
        """
        return await self.acquire(tokens, wait=False)

    def get_metrics(self) -> Dict[str, float]:
        """
        Get rate limiter metrics.

        Returns:
            Dictionary with metrics
        """
        return {
            "total_requests": self._total_requests,
            "rejected_requests": self._rejected_requests,
            "rejection_rate": (
                self._rejected_requests / self._total_requests
                if self._total_requests > 0
                else 0.0
            ),
            "avg_wait_time_ms": (
                (self._total_wait_time / self._total_requests) * 1000
                if self._total_requests > 0
                else 0.0
            ),
            "current_tokens": self._tokens,
        }


class RateLimiter:
    """
    Global rate limiter manager.

    Manages multiple rate limiters for different services and operations.
    Provides a centralized interface for rate limiting across the application.
    """

    # Predefined configurations
    CONFIGS = {
        # MCP Tools - Global limit
        "mcp_tools": RateLimitConfig(
            max_tokens=60,  # 60 requests
            refill_rate=1.0,  # 1 per second = 60/min
            burst_allowance=10,  # Allow bursts of 70
        ),
        # GitHub API - Conservative (5000/hour = ~83/min)
        "github_api": RateLimitConfig(
            max_tokens=80,
            refill_rate=1.33,  # ~80/min
            burst_allowance=20,
        ),
        # Web Research - Moderate
        "web_research": RateLimitConfig(
            max_tokens=30,
            refill_rate=0.5,  # 30/min
            burst_allowance=10,
        ),
        # Skill Operations - Generous
        "skill_operations": RateLimitConfig(
            max_tokens=100,
            refill_rate=2.0,  # 120/min
            burst_allowance=20,
        ),
        # File System - Very generous (local operations)
        "filesystem": RateLimitConfig(
            max_tokens=200,
            refill_rate=5.0,  # 300/min
            burst_allowance=50,
        ),
    }

    def __init__(self):
        """Initialize rate limiter manager."""
        self._limiters: Dict[str, TokenBucket] = {}
        self._lock = asyncio.Lock()

        logger.info(
            "RateLimiter initialized",
            extra={
                "correlation_id": get_correlation_id(),
                "available_limiters": list(self.CONFIGS.keys()),
            },
        )

    async def get_limiter(self, service: str) -> TokenBucket:
        """
        Get or create a rate limiter for a service.

        Args:
            service: Service name (must be in CONFIGS)

        Returns:
            TokenBucket for the service
        """
        if service not in self.CONFIGS:
            raise ValueError(
                f"Unknown service: {service}. "
                f"Available: {list(self.CONFIGS.keys())}"
            )

        async with self._lock:
            if service not in self._limiters:
                config = self.CONFIGS[service]
                self._limiters[service] = TokenBucket(config)
                logger.info(
                    f"Created rate limiter for {service}",
                    extra={
                        "correlation_id": get_correlation_id(),
                        "service": service,
                        "config": {
                            "max_tokens": config.max_tokens,
                            "refill_rate": config.refill_rate,
                        },
                    },
                )

            return self._limiters[service]

    @asynccontextmanager
    async def limit(self, service: str, tokens: int = 1, wait: bool = True):
        """
        Context manager for rate-limited operations.

        Usage:
            async with rate_limiter.limit("github_api"):
                # Make API call
                result = await github_api.fetch()

        Args:
            service: Service name
            tokens: Number of tokens to acquire
            wait: Whether to wait for tokens

        Raises:
            RuntimeError: If rate limit exceeded and wait=False
        """
        limiter = await self.get_limiter(service)
        acquired = await limiter.acquire(tokens, wait=wait)

        if not acquired:
            raise RuntimeError(f"Rate limit exceeded for {service}")

        try:
            yield
        finally:
            pass  # Tokens already consumed

    async def get_all_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Get metrics for all active rate limiters.

        Returns:
            Dictionary mapping service names to their metrics
        """
        async with self._lock:
            return {
                service: limiter.get_metrics()
                for service, limiter in self._limiters.items()
            }


# Global singleton instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Get the global rate limiter instance.

    Returns:
        Global RateLimiter singleton
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# Convenience decorator
def rate_limited(service: str, tokens: int = 1):
    """
    Decorator for rate-limited async functions.

    Usage:
        @rate_limited("github_api")
        async def fetch_recipe():
            # Function is automatically rate-limited
            pass

    Args:
        service: Service name for rate limiting
        tokens: Number of tokens to acquire
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()
            async with limiter.limit(service, tokens):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
