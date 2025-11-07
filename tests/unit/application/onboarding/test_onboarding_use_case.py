# tests/unit/application/onboarding/test_onboarding_use_case.py

from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from cde_orchestrator.application.onboarding.onboarding_use_case import (
    OnboardingUseCase,
)
from cde_orchestrator.domain.git import Commit
from cde_orchestrator.domain.ports import IGitAdapter


async def mock_commits_async_generator():
    yield Commit(
        hash="abcdef123",
        author="Test Author",
        date=datetime.now(),
        message="Test commit message",
    )


@pytest.mark.asyncio
async def test_onboarding_plan_uses_git_adapter():
    """Tests that generate_onboarding_plan uses the GitAdapter."""
    mock_adapter = AsyncMock(spec=IGitAdapter)
    mock_adapter.traverse_commits.return_value = mock_commits_async_generator()

    use_case = OnboardingUseCase(Path("."), git_adapter=mock_adapter)
    plan = await use_case.generate_onboarding_plan()

    mock_adapter.traverse_commits.assert_called_once()
    assert plan is not None
