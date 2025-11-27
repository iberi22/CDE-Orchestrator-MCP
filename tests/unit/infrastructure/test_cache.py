# tests/unit/infrastructure/test_cache.py
import unittest
from pathlib import Path
from unittest.mock import patch

from cde_orchestrator.infrastructure.cache import CacheManager


import shutil

class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.cache_dir = Path(".cde_test/cache")
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
        self.cache_manager = CacheManager(cache_dir=self.cache_dir.as_posix())

    def tearDown(self):
        self.cache_manager.clear()

    def test_set_and_get(self):
        self.cache_manager.set("key1", "value1")
        self.assertEqual(self.cache_manager.get("key1"), "value1")

    def test_get_nonexistent_key(self):
        self.assertIsNone(self.cache_manager.get("nonexistent"))

    def test_invalidate(self):
        self.cache_manager.set("key2", "value2")
        self.cache_manager.invalidate("key2")
        self.assertIsNone(self.cache_manager.get("key2"))

    def test_generate_cache_key(self):
        project_path = "/tmp/project"
        watch_files = ["file1.txt", "file2.txt"]

        with patch("os.path.getmtime") as mock_getmtime:
            mock_getmtime.return_value = 1234567890.0

            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = True

                key1 = self.cache_manager.generate_cache_key(project_path, watch_files)
                key2 = self.cache_manager.generate_cache_key(project_path, watch_files)
                self.assertEqual(key1, key2)

    def test_cache_stats(self):
        self.cache_manager.set("key3", "value3")
        self.cache_manager.get("key3")  # Hit
        self.cache_manager.get("nonexistent")  # Miss

        stats = self.cache_manager.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hit_rate"], "50.00%")


if __name__ == "__main__":
    unittest.main()
