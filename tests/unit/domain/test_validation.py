# tests/unit/domain/test_validation.py
"""
Unit tests for domain validation module.
"""


import pytest

from cde_orchestrator.domain.validation import (
    StartFeatureInput,
    sanitize_string,
    validate_file_path,
    validate_input,
)


class TestSanitizeString:
    """Test string sanitization functionality."""

    def test_sanitize_normal_string(self):
        """Test sanitizing a normal string."""
        result = sanitize_string("Hello World")
        assert result == "Hello World"

    def test_sanitize_string_with_control_chars(self):
        """Test sanitizing string with control characters."""
        # String with null byte and other control chars
        dirty_string = "Hello\x00World\x01Test"
        result = sanitize_string(dirty_string)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "HelloWorldTest" == result

    def test_sanitize_string_max_length(self):
        """Test string length limiting."""
        long_string = "A" * 20000
        result = sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_string_preserves_whitespace(self):
        """Test that normal whitespace is preserved."""
        text = "Hello\nWorld\tTest\r\n"
        result = sanitize_string(text)
        assert result == text


class TestValidateFilePath:
    """Test file path validation."""

    def test_validate_normal_path(self):
        """Test validating a normal file path."""
        result = validate_file_path("docs/readme.md")
        assert result is True

    def test_validate_path_traversal_attack(self):
        """Test that path traversal attacks are blocked."""
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            validate_file_path("../../../etc/passwd")

    def test_validate_absolute_path_attack(self):
        """Test that absolute paths are blocked."""
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            validate_file_path("/etc/passwd")

    def test_validate_allowed_extensions(self):
        """Test file extension validation."""
        # Should pass with allowed extension
        result = validate_file_path("test.md", allowed_extensions=[".md", ".txt"])
        assert result is True

        # Should fail with disallowed extension
        with pytest.raises(ValueError, match="Invalid file extension"):
            validate_file_path("test.exe", allowed_extensions=[".md", ".txt"])


class TestValidateInput:
    """Test input validation decorator."""

    def test_validate_input_decorator_success(self):
        """Test that valid input passes validation."""

        @validate_input(StartFeatureInput)
        def test_func(user_prompt: str) -> str:
            return f"Processed: {user_prompt}"

        result = test_func(user_prompt="This is a valid prompt that is long enough")
        assert "Processed:" in result

    def test_validate_input_decorator_failure(self):
        """Test that invalid input returns error JSON."""

        @validate_input(StartFeatureInput)
        def test_func(user_prompt: str) -> str:
            return f"Processed: {user_prompt}"

        # Too short prompt should fail
        result = test_func(user_prompt="short")
        assert "validation_error" in result

    def test_validate_input_decorator_missing_param(self):
        """Test that missing required parameter returns error."""

        @validate_input(StartFeatureInput)
        def test_func(user_prompt: str) -> str:
            return f"Processed: {user_prompt}"

        # Missing user_prompt should fail
        result = test_func()
        assert "validation_error" in result
