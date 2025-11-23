import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from cde_orchestrator.adapters.prompt.prompt_adapter import (
    PromptAdapter,
    PromptValidationError,
)


@pytest.fixture
def temp_cde_env() -> Generator[Path, None, None]:
    """
    Creates a temporary CDE environment with prompts.
    """
    temp_dir = tempfile.mkdtemp()
    cde_path = Path(temp_dir) / ".cde"
    prompts_path = cde_path / "prompts"
    prompts_path.mkdir(parents=True)

    # Create a valid test POML
    (prompts_path / "test.poml").write_text(
        "Project: {{PROJECT_NAME}}\nTask: {{USER_PROMPT}}"
    )

    # Create an invalid test POML (bad placeholder)
    (prompts_path / "invalid.poml").write_text("This has a bad key: {{BAD_KEY}}")

    yield Path(temp_dir)

    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_prompt_adapter_rendering(temp_cde_env: Path):
    """
    Test that PromptAdapter correctly renders a valid POML.
    """
    adapter = PromptAdapter(prompt_dir=temp_cde_env / ".cde" / "prompts")
    poml_path = temp_cde_env / ".cde" / "prompts" / "test.poml"

    context = {"PROJECT_NAME": "Test Project", "USER_PROMPT": "Do something cool"}

    result = await adapter.load_and_prepare(poml_path, context)

    assert "Project: Test Project" in result
    assert "Task: Do something cool" in result


@pytest.mark.asyncio
async def test_prompt_adapter_validation_error(temp_cde_env: Path):
    """
    Test that PromptAdapter raises error for disallowed placeholders.
    """
    adapter = PromptAdapter(prompt_dir=temp_cde_env / ".cde" / "prompts")
    poml_path = temp_cde_env / ".cde" / "prompts" / "invalid.poml"

    context = {"BAD_KEY": "value"}

    with pytest.raises(PromptValidationError) as excinfo:
        await adapter.load_and_prepare(poml_path, context)

    assert "Found placeholders not in whitelist" in str(excinfo.value)


@pytest.mark.asyncio
async def test_prompt_adapter_missing_context(temp_cde_env: Path):
    """
    Test that PromptAdapter raises error for missing context keys.
    """
    adapter = PromptAdapter(prompt_dir=temp_cde_env / ".cde" / "prompts")
    poml_path = temp_cde_env / ".cde" / "prompts" / "test.poml"

    # Missing USER_PROMPT
    context = {"PROJECT_NAME": "Test Project"}

    with pytest.raises(PromptValidationError) as excinfo:
        await adapter.load_and_prepare(poml_path, context)

    assert "requires context keys" in str(excinfo.value)
    assert "USER_PROMPT" in str(excinfo.value)
