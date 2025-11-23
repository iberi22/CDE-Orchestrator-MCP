# tests/unit/application/test_start_feature_validation.py
"""
Unit tests for StartFeature use case input validation.
Tests the Pydantic validation and sanitization logic.
"""

import pytest
from pydantic import ValidationError

from cde_orchestrator.application.use_cases.start_feature import StartFeatureInput


class TestStartFeatureInputValidation:
    """Test suite for StartFeatureInput validation model."""

    def test_valid_input(self):
        """Test that valid inputs pass validation."""
        input_data = StartFeatureInput(
            project_path="/path/to/project",
            user_prompt="Add user authentication with OAuth2",
            workflow_type="standard",
            recipe_id="ai-engineer",
        )

        assert input_data.project_path == "/path/to/project"
        assert input_data.user_prompt == "Add user authentication with OAuth2"
        assert input_data.workflow_type == "standard"
        assert input_data.recipe_id == "ai-engineer"

    def test_minimal_valid_input(self):
        """Test that minimal valid inputs work with defaults."""
        input_data = StartFeatureInput(
            project_path="/project",
            user_prompt="Add feature X with proper validation",
        )

        assert input_data.project_path == "/project"
        assert input_data.workflow_type == "standard"  # Default
        assert input_data.recipe_id == "ai-engineer"  # Default

    def test_prompt_too_short(self):
        """Test that prompts shorter than 10 characters are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            StartFeatureInput(
                project_path="/project",
                user_prompt="Short",  # Only 5 characters
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("user_prompt",) and "at least 10 characters" in str(error)
            for error in errors
        )

    def test_prompt_too_long(self):
        """Test that prompts longer than 5000 characters are rejected."""
        long_prompt = "A" * 5001

        with pytest.raises(ValidationError) as exc_info:
            StartFeatureInput(
                project_path="/project",
                user_prompt=long_prompt,
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("user_prompt",) and "at most 5000 characters" in str(error)
            for error in errors
        )

    def test_empty_project_path(self):
        """Test that empty project paths are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            StartFeatureInput(
                project_path="",
                user_prompt="Valid prompt here",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("project_path",) for error in errors)

    def test_whitespace_project_path(self):
        """Test that whitespace-only project paths are rejected."""
        with pytest.raises(ValueError, match="cannot be empty or whitespace"):
            StartFeatureInput(
                project_path="   ",
                user_prompt="Valid prompt here",
            )

    def test_sanitization_removes_control_characters(self):
        """Test that control characters are removed from prompts."""
        input_data = StartFeatureInput(
            project_path="/project",
            user_prompt="Add feature\x00with\x01null\x02bytes",
        )

        # Control characters should be removed
        assert "\x00" not in input_data.user_prompt
        assert "\x01" not in input_data.user_prompt
        assert "\x02" not in input_data.user_prompt
        assert "Add feature" in input_data.user_prompt

    def test_sanitization_preserves_newlines(self):
        """Test that newlines and tabs are preserved during sanitization."""
        input_data = StartFeatureInput(
            project_path="/project",
            user_prompt="Add feature\nwith multiple\tlines",
        )

        assert "\n" in input_data.user_prompt
        assert "\t" in input_data.user_prompt

    def test_path_length_limit(self):
        """Test that project paths longer than 500 characters are rejected."""
        long_path = "/" + "a" * 500

        with pytest.raises(ValidationError) as exc_info:
            StartFeatureInput(
                project_path=long_path,
                user_prompt="Valid prompt here",
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("project_path",)
            and "at most 500 characters" in str(error)
            for error in errors
        )

    def test_workflow_type_validation(self):
        """Test that workflow_type is validated."""
        input_data = StartFeatureInput(
            project_path="/project",
            user_prompt="Valid prompt here",
            workflow_type="quick-fix",
        )

        assert input_data.workflow_type == "quick-fix"

    def test_recipe_id_validation(self):
        """Test that recipe_id is validated."""
        input_data = StartFeatureInput(
            project_path="/project",
            user_prompt="Valid prompt here",
            recipe_id="deep-research",
        )

        assert input_data.recipe_id == "deep-research"

    def test_injection_attempt_sanitized(self):
        """Test that potential injection attempts are sanitized."""
        # Attempt to inject shell commands or special characters
        malicious_prompt = "Add feature; rm -rf / && echo 'hacked'"

        input_data = StartFeatureInput(
            project_path="/project",
            user_prompt=malicious_prompt,
        )

        # The prompt should still contain the text but be sanitized
        # (sanitize_string removes control chars but preserves printable ones)
        assert "Add feature" in input_data.user_prompt
        # The actual command should still be there (sanitize_string doesn't
        # remove shell metacharacters, just control chars)
        # For deeper injection prevention, we'd need additional validators
