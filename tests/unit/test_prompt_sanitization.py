import pytest

from cde_orchestrator.adapters.prompt import PromptAdapter, PromptValidationError


def test_prompt_manager_sanitizes_context(tmp_path):
    poml_file = tmp_path / "sanitized.poml"
    poml_file.write_text("Value: {{USER_PROMPT}}", encoding="utf-8")

    manager = PromptAdapter(allowed_placeholders={"USER_PROMPT"})
    result = manager.load_and_prepare(
        poml_file,
        {"USER_PROMPT": "<script>alert('x')</script>"},
    )

    assert "&lt;script&gt;" in result
    assert "alert" in result


def test_missing_context_key_raises(tmp_path):
    poml_file = tmp_path / "missing.poml"
    poml_file.write_text("Value: {{USER_PROMPT}}", encoding="utf-8")

    manager = PromptAdapter(allowed_placeholders={"USER_PROMPT"})
    with pytest.raises(PromptValidationError):
        manager.load_and_prepare(poml_file, {})


def test_disallowed_placeholder_rejected(tmp_path):
    poml_file = tmp_path / "disallowed.poml"
    poml_file.write_text("Value: {{UNSAFE}}", encoding="utf-8")

    manager = PromptAdapter(allowed_placeholders={"USER_PROMPT"})
    with pytest.raises(PromptValidationError):
        manager.load_and_prepare(poml_file, {"UNSAFE": "value"})
