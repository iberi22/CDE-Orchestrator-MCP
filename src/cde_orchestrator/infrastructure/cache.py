# src/cde_orchestrator/infrastructure/cache.py
import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from diskcache import Cache

class CacheManager:
    """Manages a persistent cache for project analysis results."""

    def __init__(
        self,
        cache_dir: str = ".cde/cache",
        size_limit: int = 50 * 1024 * 1024,  # 50MB
        eviction_policy: str = "least-recently-used",
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = Cache(
            self.cache_dir.as_posix(),
            size_limit=size_limit,
            eviction_policy=eviction_policy,
            statistics=True,
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves an item from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached item, or None if the key is not found.
        """
        return self.cache.get(key)

    def set(self, key: str, value: Any, expire: int = 3600):
        """
        Adds an item to the cache.

        Args:
            key: The cache key.
            value: The value to cache.
            expire: Time-to-live in seconds (default is 1 hour).
        """
        self.cache.set(key, value, expire=expire)

    def invalidate(self, key: str):
        """
        Removes an item from the cache.

        Args:
            key: The cache key to invalidate.
        """
        if key in self.cache:
            del self.cache[key]

    def generate_cache_key(
        self, project_path: str, watch_files: List[str]
    ) -> str:
        """
        Generates a cache key based on the project path and modification times of key files.

        Args:
            project_path: The absolute path to the project.
            watch_files: A list of file names to monitor for changes.

        Returns:
            A unique SHA256 hash representing the state of the project.
        """
        hasher = hashlib.sha256()
        hasher.update(project_path.encode())

        for file_name in sorted(watch_files):
            file_path = Path(project_path) / file_name
            if file_path.exists():
                mtime = os.path.getmtime(file_path)
                hasher.update(str(mtime).encode())

        return hasher.hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """
        Retrieves cache statistics.

        Returns:
            A dictionary with cache statistics (hits, misses, size).
        """
        hits, misses = self.cache.stats()

        # Calculate hit rate, avoiding division by zero
        total = hits + misses
        hit_rate = (hits / total) * 100 if total > 0 else 0

        return {
            "hits": hits,
            "misses": misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "size": self.cache.volume(),
        }

    def clear(self):
        """Clears the entire cache."""
        self.cache.clear()
