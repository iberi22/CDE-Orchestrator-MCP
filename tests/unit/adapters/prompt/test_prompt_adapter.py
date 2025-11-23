"""
Unit tests for the PromptAdapter.
"""

from pathlib import Path

import pytest

from cde_orchestrator.adapters.prompt.prompt_adapter import (
    PromptAdapter,
    PromptValidationError,
)


@pytest.fixture
def prompt_dir(tmp_path):
    """Creates a temporary prompt directory for tests."""
    (tmp_path / "prompts").mkdir()
    return tmp_path / "prompts"


@pytest.mark.asyncio
async def test_load_and_prepare_success(prompt_dir):
    """Tests successful loading and preparation of a simple prompt."""
    poml_content = "Hello, {{USER_PROMPT}}!"
    poml_path = prompt_dir / "hello.poml"
    poml_path.write_text(poml_content)

    adapter = PromptAdapter(prompt_dir=prompt_dir)
    context = {"USER_PROMPT": "World"}

    result = await adapter.load_and_prepare(poml_path, context)
    assert result == "Hello, World!"


@pytest.mark.asyncio
async def test_sanitize_value(prompt_dir):
    """Tests that context values are properly sanitized."""
    poml_content = "Data: {{USER_PROMPT}}"
    poml_path = prompt_dir / "sanitize.poml"
    poml_path.write_text(poml_content)

    adapter = PromptAdapter(prompt_dir=prompt_dir)
    context = {"USER_PROMPT": "<script>alert('xss')</script>"}

    result = await adapter.load_and_prepare(poml_path, context)
    assert "<script>" not in result
    assert "&lt;script&gt;" in result


@pytest.mark.asyncio
async def test_disallowed_placeholder_raises_error(prompt_dir):
    """Tests that a prompt with a disallowed placeholder raises an error."""
    poml_content = "Secret: {{SECRET_KEY}}"
    poml_path = prompt_dir / "disallowed.poml"
    poml_path.write_text(poml_content)

    adapter = PromptAdapter(prompt_dir=prompt_dir)
    context = {"SECRET_KEY": "12345"}

    with pytest.raises(
        PromptValidationError, match="Found placeholders not in whitelist"
    ):
        await adapter.load_and_prepare(poml_path, context)


@pytest.mark.asyncio
async def test_missing_context_key_raises_error(prompt_dir):
    """Tests that a missing context key raises an error."""
    poml_content = "Hello, {{USER_PROMPT}}!"
    poml_path = prompt_dir / "missing.poml"
    poml_path.write_text(poml_content)

    adapter = PromptAdapter(prompt_dir=prompt_dir)
    context = {"WRONG_KEY": "World"}

    with pytest.raises(PromptValidationError, match="requires context keys"):
        await adapter.load_and_prepare(poml_path, context)


@pytest.mark.asyncio
async def test_prompt_file_not_found_raises_error(prompt_dir):
    """Tests that a non-existent prompt file raises an error."""
    adapter = PromptAdapter(prompt_dir=prompt_dir)
    with pytest.raises(FileNotFoundError):
        await adapter.load_and_prepare(Path("nonexistent.poml"), {})
