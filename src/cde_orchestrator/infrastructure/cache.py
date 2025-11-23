"""
Intelligent Caching System for CDE Orchestrator.

Provides:
- TTL (Time-To-Live) caching for configurations
- LRU (Least Recently Used) caching for recipes
- File-based invalidation (detect changes)
- Async-first design
- Metrics tracking (hit/miss rates)

Design Philosophy:
- Zero-config defaults (works out of the box)
- Explicit invalidation (no surprises)
- Observable (metrics for monitoring)
- Type-safe (full type hints)

Examples:
    >>> # Automatic caching with decorator
    >>> @cached(ttl=300)  # 5 minutes
    >>> async def load_recipe(name: str) -> dict:
    ...     return await expensive_operation(name)

    >>> # Manual cache management
    >>> cache = CacheManager()
    >>> await cache.set("key", value, ttl=60)
    >>> result = await cache.get("key")

    >>> # File-based invalidation
    >>> @cached(file_path="config.yml")
    >>> async def load_config() -> dict:
    ...     # Cache invalidates when config.yml changes
    ...     return await read_config()
"""

import asyncio
import hashlib
import logging
import time
from collections import OrderedDict
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from cde_orchestrator.infrastructure.telemetry import log_metric

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheEntry:
    """Single cache entry with metadata."""

    def __init__(
        self,
        value: Any,
        ttl: Optional[float] = None,
        file_path: Optional[Path] = None,
    ):
        """
        Initialize cache entry.

        Args:
            value: Cached value
            ttl: Time-to-live in seconds (None = no expiration)
            file_path: File to watch for changes (None = no file tracking)
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.file_path = file_path
        self.file_mtime: Optional[float] = None
        self.access_count = 0
        self.last_accessed = self.created_at

        # Track file modification time if file_path provided
        if file_path and file_path.exists():
            self.file_mtime = file_path.stat().st_mtime

    def is_expired(self) -> bool:
        """Check if entry has expired (TTL or file changed)."""
        # Check TTL expiration
        if self.ttl is not None:
            age = time.time() - self.created_at
            if age > self.ttl:
                return True

        # Check file modification
        if self.file_path and self.file_path.exists():
            current_mtime = self.file_path.stat().st_mtime
            if self.file_mtime is None or current_mtime > self.file_mtime:
                return True

        return False

    def access(self) -> Any:
        """Mark entry as accessed and return value."""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value


class CacheMetrics:
    """Track cache performance metrics."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.invalidations = 0

    @property
    def total_requests(self) -> int:
        """Total cache requests."""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 to 1.0)."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    def record_hit(self) -> None:
        """Record cache hit."""
        self.hits += 1
        log_metric("cache_hit", 1, "count")

    def record_miss(self) -> None:
        """Record cache miss."""
        self.misses += 1
        log_metric("cache_miss", 1, "count")

    def record_eviction(self) -> None:
        """Record cache eviction."""
        self.evictions += 1

    def record_invalidation(self) -> None:
        """Record cache invalidation."""
        self.invalidations += 1

    def to_dict(self) -> Dict[str, Union[int, float]]:
        """Export metrics as dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "invalidations": self.invalidations,
            "total_requests": self.total_requests,
            "hit_rate": self.hit_rate,
        }


class CacheManager:
    """
    Async cache manager with TTL, LRU, and file-based invalidation.

    Features:
    - TTL expiration (time-based)
    - LRU eviction (size-based)
    - File modification tracking
    - Metrics tracking
    - Thread-safe (async locks)

    Examples:
        >>> cache = CacheManager(max_size=100, default_ttl=300)
        >>> await cache.set("config", {"key": "value"}, ttl=60)
        >>> result = await cache.get("config")
        >>> metrics = cache.get_metrics()
        >>> print(f"Hit rate: {metrics['hit_rate']:.2%}")
    """

    def __init__(
        self,
        max_size: int = 100,
        default_ttl: Optional[float] = None,
    ):
        """
        Initialize cache manager.

        Args:
            max_size: Maximum number of entries (LRU eviction)
            default_ttl: Default TTL in seconds (None = no expiration)
        """
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._metrics = CacheMetrics()
        self._lock = asyncio.Lock()
        self._logger = logger

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and valid, None otherwise

        Side Effects:
            - Updates access time
            - Increments hit/miss counter
            - Removes expired entries
        """
        async with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._metrics.record_miss()
                self._logger.debug(f"Cache MISS: {key}")
                return None

            # Check expiration
            if entry.is_expired():
                self._logger.debug(f"Cache EXPIRED: {key}")
                del self._cache[key]
                self._metrics.record_invalidation()
                self._metrics.record_miss()
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)

            self._metrics.record_hit()
            self._logger.debug(
                f"Cache HIT: {key} (age: {time.time() - entry.created_at:.1f}s)"
            )
            return entry.access()

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        file_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
            file_path: File to track for changes (None = no tracking)

        Side Effects:
            - May evict LRU entry if cache is full
            - Creates new CacheEntry
        """
        async with self._lock:
            # Use default TTL if not specified
            effective_ttl = ttl if ttl is not None else self._default_ttl

            # Convert file_path to Path if string
            path_obj = Path(file_path) if file_path else None

            # Create entry
            entry = CacheEntry(value, ttl=effective_ttl, file_path=path_obj)

            # Evict LRU if at capacity
            if len(self._cache) >= self._max_size and key not in self._cache:
                evicted_key, _ = self._cache.popitem(last=False)
                self._metrics.record_eviction()
                self._logger.debug(f"Cache EVICT: {evicted_key} (LRU)")

            # Store entry (move to end if exists)
            self._cache[key] = entry
            self._cache.move_to_end(key)

            self._logger.debug(
                f"Cache SET: {key} (ttl: {effective_ttl}, file: {path_obj})"
            )

    async def invalidate(self, key: str) -> bool:
        """
        Remove entry from cache.

        Args:
            key: Cache key

        Returns:
            True if entry was removed, False if not found
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._metrics.record_invalidation()
                self._logger.debug(f"Cache INVALIDATE: {key}")
                return True
            return False

    async def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._logger.info(f"Cache CLEAR: {count} entries removed")
            return count

    async def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed

        Note:
            This is called automatically on get(), but can be
            called manually for periodic cleanup.
        """
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]
                self._metrics.record_invalidation()

            if expired_keys:
                self._logger.info(f"Cache CLEANUP: {len(expired_keys)} expired entries")

            return len(expired_keys)

    def get_metrics(self) -> Dict[str, Union[int, float]]:
        """
        Get cache performance metrics.

        Returns:
            Dictionary with hits, misses, hit_rate, etc.
        """
        return self._metrics.to_dict()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get detailed cache statistics.

        Returns:
            Dictionary with size, metrics, and entry details
        """
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "default_ttl": self._default_ttl,
            "metrics": self.get_metrics(),
            "entries": [
                {
                    "key": key,
                    "age": time.time() - entry.created_at,
                    "ttl": entry.ttl,
                    "access_count": entry.access_count,
                    "file_path": str(entry.file_path) if entry.file_path else None,
                }
                for key, entry in list(self._cache.items())[:10]  # Top 10
            ],
        }


# Global cache instance (singleton pattern)
_global_cache: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """
    Get global cache instance (lazy initialization).

    Returns:
        Global CacheManager instance

    Examples:
        >>> cache = get_cache()
        >>> await cache.set("key", "value")
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager(
            max_size=100,  # 100 entries
            default_ttl=300,  # 5 minutes
        )
    return _global_cache


def cached(
    ttl: Optional[float] = None,
    file_path: Optional[Union[str, Path]] = None,
    key_prefix: str = "",
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for automatic caching of async functions.

    Args:
        ttl: Time-to-live in seconds (None = use cache default)
        file_path: File to track for changes (None = no tracking)
        key_prefix: Prefix for cache keys (default: function name)

    Returns:
        Decorated function with caching

    Examples:
        >>> @cached(ttl=300)  # 5 minutes
        >>> async def load_recipe(name: str) -> dict:
        ...     return await expensive_operation(name)

        >>> @cached(file_path="config.yml")
        >>> async def load_config() -> dict:
        ...     # Invalidates when config.yml changes
        ...     return await read_config()

        >>> # Custom key prefix
        >>> @cached(ttl=60, key_prefix="user")
        >>> async def get_user(user_id: int) -> dict:
        ...     return await db.get_user(user_id)

    Note:
        - Cache key is generated from function name + args + kwargs
        - Only works with async functions
        - Arguments must be hashable (str, int, tuple, etc.)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            cache = get_cache()

            # Generate cache key from function name + args
            prefix = key_prefix or func.__name__
            key_parts = [prefix] + [str(arg) for arg in args]
            key_parts += [f"{k}={v}" for k, v in sorted(kwargs.items())]
            key_str = ":".join(key_parts)

            # Hash key if too long
            if len(key_str) > 200:
                key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]
                cache_key = f"{prefix}:{key_hash}"
            else:
                cache_key = key_str

            # Try cache first
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value  # type: ignore

            # Cache miss - call function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl=ttl, file_path=file_path)

            return result

        return wrapper  # type: ignore

    return decorator
