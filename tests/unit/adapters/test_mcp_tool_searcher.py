# tests/unit/adapters/test_mcp_tool_searcher.py
import asyncio
import unittest
from unittest.mock import MagicMock, patch

from cde_orchestrator.adapters.mcp_tool_searcher import MCPToolSearcher
from cde_orchestrator.infrastructure.cache import CacheManager


class TestMCPToolSearcher(unittest.TestCase):
    def setUp(self):
        self.mcp_tools_module = MagicMock()
        self.searcher = MCPToolSearcher(self.mcp_tools_module)
        self.searcher.cache_manager = CacheManager(cache_dir=".cde_test/cache")
        self.searcher.cache_manager.clear()

    def tearDown(self):
        self.searcher.cache_manager.clear()

    @patch("cde_orchestrator.adapters.mcp_tool_searcher.MCPToolSearcher._discover_all_tools_sync")
    def test_caching(self, mock_discover_sync):
        mock_discover_sync.return_value = [{"name": "tool1"}]

        # First call (cache miss)
        result1 = asyncio.run(self.searcher._discover_all_tools())
        self.assertEqual(result1, [{"name": "tool1"}])
        self.assertEqual(mock_discover_sync.call_count, 1)

        # Second call (cache hit)
        result2 = asyncio.run(self.searcher._discover_all_tools())
        self.assertEqual(result2, [{"name": "tool1"}])
        self.assertEqual(mock_discover_sync.call_count, 1)  # Should not be called again


if __name__ == "__main__":
    unittest.main()
