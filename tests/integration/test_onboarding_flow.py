import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)
from cde_orchestrator.application.onboarding.project_setup_use_case import (
    ProjectSetupUseCase,
)
from cde_orchestrator.application.onboarding.publishing_use_case import (
    PublishingUseCase,
)


@pytest.fixture
def temp_project_for_onboarding() -> Generator[Path, None, None]:
    """
    Creates a temporary project for onboarding tests.
    """
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir)

    # Simulate a Python project
    (project_path / "pyproject.toml").write_text("[tool.poetry]")
    (project_path / "package.json").write_text(
        "{}"
    )  # Add package.json to test Node logic
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").write_text("print('hello')")

    # Initialize Git (mocking .git dir is enough for analysis usually,
    # but let's make a real one if needed, or just the dir)
    (project_path / ".git").mkdir()

    yield project_path

    shutil.rmtree(temp_dir)


def test_onboarding_analysis(temp_project_for_onboarding: Path):
    """
    Test that ProjectAnalysisUseCase correctly analyzes a project.
    """
    analyzer = ProjectAnalysisUseCase()
    result = analyzer.execute(str(temp_project_for_onboarding))

    assert result["status"] == "Analysis complete"
    assert ".py" in result["language_stats"]
    assert "pyproject.toml" in result["dependency_files"]


def test_onboarding_publishing(temp_project_for_onboarding: Path):
    """
    Test that PublishingUseCase correctly writes files.
    """
    publisher = PublishingUseCase()

    documents = {
        "AGENTS.md": "# Agents Guide",
        "specs/features/test-feature.md": "# Test Feature",
    }

    result = publisher.execute(str(temp_project_for_onboarding), documents)

    assert result["status"] == "success"
    assert (temp_project_for_onboarding / "AGENTS.md").exists()
    assert (temp_project_for_onboarding / "specs/features/test-feature.md").exists()


def test_onboarding_governance_violation(temp_project_for_onboarding: Path):
    """
    Test that PublishingUseCase blocks disallowed root files.
    """
    publisher = PublishingUseCase()

    documents = {"REPORT_2025.md": "# Bad Report"}

    # Depending on implementation, it might raise error or return partial success
    # Let's check the implementation behavior via test
    try:
        result = publisher.execute(str(temp_project_for_onboarding), documents)
        # If it doesn't raise, check if file was NOT created
        assert not (temp_project_for_onboarding / "REPORT_2025.md").exists()
        # And maybe check result for errors
        if "errors" in result:
            assert len(result["errors"]) > 0
    except ValueError as e:
        assert "Governance violation" in str(e) or "not allowed" in str(e)


def test_project_setup(temp_project_for_onboarding: Path):
    """
    Test that ProjectSetupUseCase correctly generates config files.
    """
    analysis_use_case = ProjectAnalysisUseCase()
    publishing_use_case = PublishingUseCase()
    setup_use_case = ProjectSetupUseCase(analysis_use_case, publishing_use_case)

    result = setup_use_case.execute(str(temp_project_for_onboarding), force=True)

    assert result["status"] == "success"
    assert "AGENTS.md" in result["files_written"]
    assert ".gitignore" in result["files_written"]

    # Verify content
    gitignore_content = (temp_project_for_onboarding / ".gitignore").read_text()
    assert "node_modules/" in gitignore_content  # Because we added package.json
    assert ".pytest_cache/" in gitignore_content  # Because we have .py files (main.py)
