# tests/integration/test_cached_analysis.py
import asyncio
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)
from cde_orchestrator.infrastructure.cache import CacheManager


class TestCachedAnalysis(unittest.TestCase):
    def setUp(self):
        self.project_path = Path("./test_project")
        self.project_path.mkdir(exist_ok=True)
        (self.project_path / "pyproject.toml").touch()

        self.analysis_use_case = ProjectAnalysisUseCase()
        self.analysis_use_case.cache_manager = CacheManager(cache_dir=".cde_test/cache")
        self.analysis_use_case.cache_manager.clear()

    def tearDown(self):
        self.analysis_use_case.cache_manager.clear()
        for f in self.project_path.glob("*"):
            f.unlink()
        self.project_path.rmdir()

    @patch(
        "cde_orchestrator.application.onboarding.project_analysis_use_case.ProjectAnalysisUseCase._execute_rust"
    )
    def test_cache_hit_and_miss(self, mock_execute_rust):
        mock_execute_rust.return_value = {"status": "Analysis complete"}

        # First run (cache miss)
        result1 = asyncio.run(self.analysis_use_case.execute(str(self.project_path)))
        self.assertEqual(result1, {"status": "Analysis complete"})
        self.assertEqual(mock_execute_rust.call_count, 1)

        # Second run (cache hit)
        result2 = asyncio.run(self.analysis_use_case.execute(str(self.project_path)))
        self.assertEqual(result2, {"status": "Analysis complete"})
        self.assertEqual(mock_execute_rust.call_count, 1)  # Should not be called again

    @patch(
        "cde_orchestrator.application.onboarding.project_analysis_use_case.ProjectAnalysisUseCase._execute_rust"
    )
    def test_cache_invalidation_on_file_change(self, mock_execute_rust):
        mock_execute_rust.return_value = {"status": "Analysis complete"}

        # First run
        asyncio.run(self.analysis_use_case.execute(str(self.project_path)))
        self.assertEqual(mock_execute_rust.call_count, 1)

        # Modify a watched file
        (self.project_path / "pyproject.toml").touch()

        # Second run (should be a cache miss)
        asyncio.run(self.analysis_use_case.execute(str(self.project_path)))
        self.assertEqual(mock_execute_rust.call_count, 2)


if __name__ == "__main__":
    unittest.main()
