"""
Unit tests for the caching infrastructure.

Tests:
- CacheEntry expiration (TTL and file-based)
- CacheManager operations (get, set, invalidate)
- LRU eviction
- Metrics tracking
- @cached decorator
- File modification detection
"""

import asyncio
import time

import pytest

from src.cde_orchestrator.infrastructure.cache import (
    CacheEntry,
    CacheManager,
    cached,
    get_cache,
)


class TestCacheEntry:
    """Test CacheEntry class."""

    def test_create_entry_no_expiration(self):
        """Test creating entry without TTL."""
        entry = CacheEntry("test_value")
        assert entry.value == "test_value"
        assert entry.ttl is None
        assert not entry.is_expired()

    def test_create_entry_with_ttl(self):
        """Test creating entry with TTL."""
        entry = CacheEntry("test_value", ttl=1.0)
        assert entry.ttl == 1.0
        assert not entry.is_expired()

        # Wait for expiration
        time.sleep(1.1)
        assert entry.is_expired()

    def test_file_based_expiration(self, tmp_path):
        """Test file modification detection."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("original")

        entry = CacheEntry("cached_value", file_path=test_file)
        assert not entry.is_expired()

        # Modify file
        time.sleep(0.1)  # Ensure mtime changes
        test_file.write_text("modified")

        assert entry.is_expired()

    def test_access_tracking(self):
        """Test access count and timestamp tracking."""
        entry = CacheEntry("value")
        assert entry.access_count == 0

        value = entry.access()
        assert value == "value"
        assert entry.access_count == 1

        entry.access()
        assert entry.access_count == 2


class TestCacheManager:
    """Test CacheManager class."""

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = CacheManager()

        await cache.set("key1", "value1")
        result = await cache.get("key1")

        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self):
        """Test getting non-existent key returns None."""
        cache = CacheManager()
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        """Test TTL-based expiration."""
        cache = CacheManager()

        await cache.set("key1", "value1", ttl=0.5)
        assert await cache.get("key1") == "value1"

        # Wait for expiration
        await asyncio.sleep(0.6)
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = CacheManager(max_size=3)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")

        # Access key1 to make it recently used
        await cache.get("key1")

        # Add key4 - should evict key2 (least recently used)
        await cache.set("key4", "value4")

        assert await cache.get("key1") == "value1"  # Still exists
        assert await cache.get("key2") is None  # Evicted
        assert await cache.get("key3") == "value3"  # Still exists
        assert await cache.get("key4") == "value4"  # Newly added

    @pytest.mark.asyncio
    async def test_invalidate(self):
        """Test manual invalidation."""
        cache = CacheManager()

        await cache.set("key1", "value1")
        assert await cache.get("key1") == "value1"

        removed = await cache.invalidate("key1")
        assert removed is True
        assert await cache.get("key1") is None

        # Invalidate non-existent key
        removed = await cache.invalidate("nonexistent")
        assert removed is False

    @pytest.mark.asyncio
    async def test_clear(self):
        """Test clearing all entries."""
        cache = CacheManager()

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")

        count = await cache.clear()
        assert count == 3

        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
        assert await cache.get("key3") is None

    @pytest.mark.asyncio
    async def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = CacheManager()

        await cache.set("key1", "value1", ttl=0.5)
        await cache.set("key2", "value2", ttl=10)
        await cache.set("key3", "value3")  # No TTL

        # Wait for key1 to expire
        await asyncio.sleep(0.6)

        count = await cache.cleanup_expired()
        assert count == 1

        assert await cache.get("key1") is None
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_file_based_invalidation(self, tmp_path):
        """Test file modification invalidation."""
        test_file = tmp_path / "config.yml"
        test_file.write_text("original")

        cache = CacheManager()
        await cache.set("config", {"key": "value"}, file_path=test_file)

        # Should be cached
        assert await cache.get("config") == {"key": "value"}

        # Modify file
        await asyncio.sleep(0.1)
        test_file.write_text("modified")

        # Should be invalidated
        assert await cache.get("config") is None

    @pytest.mark.asyncio
    async def test_metrics_tracking(self):
        """Test metrics tracking."""
        cache = CacheManager()

        # Initial metrics
        metrics = cache.get_metrics()
        assert metrics["hits"] == 0
        assert metrics["misses"] == 0
        assert metrics["hit_rate"] == 0.0

        # Set and get (hit)
        await cache.set("key1", "value1")
        await cache.get("key1")

        # Get non-existent (miss)
        await cache.get("nonexistent")

        metrics = cache.get_metrics()
        assert metrics["hits"] == 1
        assert metrics["misses"] == 1
        assert metrics["hit_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test detailed statistics."""
        cache = CacheManager(max_size=10, default_ttl=60)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2", ttl=30)

        stats = cache.get_stats()

        assert stats["size"] == 2
        assert stats["max_size"] == 10
        assert stats["default_ttl"] == 60
        assert len(stats["entries"]) == 2


class TestCachedDecorator:
    """Test @cached decorator."""

    @pytest.mark.asyncio
    async def test_basic_caching(self):
        """Test basic function caching."""
        call_count = 0

        @cached(ttl=60)
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)
            return x * 2

        # First call - cache miss
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call - cache hit
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not called again

        # Different argument - cache miss
        result3 = await expensive_function(10)
        assert result3 == 20
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_ttl_expiration_decorator(self):
        """Test TTL expiration with decorator."""
        call_count = 0

        @cached(ttl=0.5)
        async def get_data() -> str:
            nonlocal call_count
            call_count += 1
            return "data"

        # First call
        result1 = await get_data()
        assert result1 == "data"
        assert call_count == 1

        # Second call - cached
        result2 = await get_data()
        assert result2 == "data"
        assert call_count == 1

        # Wait for expiration
        await asyncio.sleep(0.6)

        # Third call - cache expired
        result3 = await get_data()
        assert result3 == "data"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_file_based_caching(self, tmp_path):
        """Test file-based invalidation with decorator."""
        config_file = tmp_path / "config.yml"
        config_file.write_text("version: 1")

        call_count = 0

        @cached(file_path=config_file)
        async def load_config() -> dict:
            nonlocal call_count
            call_count += 1
            return {"version": int(config_file.read_text().split(": ")[1])}

        # First call
        result1 = await load_config()
        assert result1 == {"version": 1}
        assert call_count == 1

        # Second call - cached
        result2 = await load_config()
        assert result2 == {"version": 1}
        assert call_count == 1

        # Modify file
        await asyncio.sleep(0.1)
        config_file.write_text("version: 2")

        # Third call - cache invalidated
        result3 = await load_config()
        assert result3 == {"version": 2}
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_multiple_arguments(self):
        """Test caching with multiple arguments."""
        call_count = 0

        @cached(ttl=60)
        async def compute(a: int, b: int, operation: str = "add") -> int:
            nonlocal call_count
            call_count += 1
            if operation == "add":
                return a + b
            elif operation == "multiply":
                return a * b
            return 0

        # Different argument combinations
        result1 = await compute(2, 3)
        assert result1 == 5
        assert call_count == 1

        result2 = await compute(2, 3)  # Cached
        assert result2 == 5
        assert call_count == 1

        result3 = await compute(2, 3, operation="multiply")  # Different kwargs
        assert result3 == 6
        assert call_count == 2

        result4 = await compute(5, 10)  # Different args
        assert result4 == 15
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_custom_key_prefix(self):
        """Test custom key prefix."""

        @cached(ttl=60, key_prefix="user")
        async def get_user(user_id: int) -> dict:
            return {"id": user_id, "name": f"User {user_id}"}

        result = await get_user(123)
        assert result == {"id": 123, "name": "User 123"}

        # Verify cache key uses prefix
        cache = get_cache()
        stats = cache.get_stats()
        assert any("user" in entry["key"] for entry in stats["entries"])


class TestGlobalCache:
    """Test global cache instance."""

    @pytest.mark.asyncio
    async def test_get_cache_singleton(self):
        """Test get_cache returns same instance."""
        cache1 = get_cache()
        cache2 = get_cache()

        assert cache1 is cache2

        # Test it works
        await cache1.set("test", "value")
        result = await cache2.get("test")
        assert result == "value"
