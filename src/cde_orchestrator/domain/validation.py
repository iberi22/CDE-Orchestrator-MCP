# src/cde_orchestrator/domain/validation.py
"""
Domain Validation - Input validation decorators and utilities for MCP tools.
Provides Pydantic-based validation to prevent invalid inputs.
"""
import json
from functools import wraps
from typing import Any, Callable, Type

from pydantic import BaseModel, ValidationError


def validate_input(model: Type[BaseModel]) -> Callable:
    """
    Decorator to validate tool inputs using Pydantic models.

    Usage:
        class MyToolInput(BaseModel):
            param1: str
            param2: int = Field(gt=0)

        @validate_input(MyToolInput)
        def my_tool(param1: str, param2: int) -> str:
            # params are already validated here
            return f"Processed {param1} with {param2}"

    Args:
        model: Pydantic model class for validation

    Returns:
        Decorator function that validates inputs
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Validate kwargs against model
                validated = model(**kwargs)
                # Replace kwargs with validated data
                return func(*args, **validated.model_dump())
            except ValidationError as e:
                # Return structured error for AI agent
                return json.dumps(
                    {
                        "error": "validation_error",
                        "message": "Invalid input parameters",
                        "details": e.errors(),
                        "tool": func.__name__,
                    },
                    indent=2,
                )
            except Exception as e:
                # Catch any other validation-related errors
                return json.dumps(
                    {
                        "error": "validation_error",
                        "message": str(e),
                        "tool": func.__name__,
                    },
                    indent=2,
                )

        return wrapper

    return decorator


def sanitize_string(value: str, max_length: int = 10000) -> str:
    """
    Sanitize string input by removing dangerous characters and limiting length.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)

    # Trim to max length
    sanitized = value[:max_length]

    # Remove null bytes and other control characters
    sanitized = "".join(
        char for char in sanitized if ord(char) >= 32 or char in "\n\r\t"
    )

    return sanitized


def validate_file_path(path: str, allowed_extensions: list = None) -> bool:
    """
    Validate file path for safety.

    Args:
        path: File path to validate
        allowed_extensions: Optional list of allowed file extensions

    Returns:
        True if path is valid

    Raises:
        ValueError: If path is invalid or dangerous
    """
    from pathlib import Path

    # Check for path traversal attacks
    if ".." in path or path.startswith("/"):
        raise ValueError(f"Invalid path: {path}. Path traversal not allowed.")

    # Check extension if specified
    if allowed_extensions:
        path_obj = Path(path)
        if path_obj.suffix not in allowed_extensions:
            raise ValueError(f"Invalid file extension. Allowed: {allowed_extensions}")

    return True


# Common validation models for CDE tools
from pydantic import ConfigDict


class StartFeatureInput(BaseModel):
    """Validation model for cde_startFeature."""

    user_prompt: str

    model_config = ConfigDict(str_min_length=10, str_max_length=5000)


class SubmitWorkInput(BaseModel):
    """Validation model for cde_submitWork."""

    feature_id: str
    phase_id: str
    results: dict

    model_config = ConfigDict(str_min_length=1, str_max_length=100)


class CreateBranchInput(BaseModel):
    """Validation model for cde_createGitBranch."""

    feature_id: str
    branch_name: str
    base_branch: str = "main"

    model_config = ConfigDict(str_min_length=1, str_max_length=200)


class CreateIssueInput(BaseModel):
    """Validation model for cde_createGitHubIssue."""

    feature_id: str
    title: str
    description: str
    labels: list = []

    model_config = ConfigDict(str_min_length=1, str_max_length=1000)
