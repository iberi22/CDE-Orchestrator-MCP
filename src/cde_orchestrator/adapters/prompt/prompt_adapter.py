# src/cde_orchestrator/adapters/prompt/prompt_adapter.py
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Set

from markupsafe import escape


class PromptValidationError(ValueError):
    """Raised when a prompt template fails validation or sanitization."""


class PromptAdapter:
    """Loads POML recipes and injects sanitized context."""

    PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
    DEFAULT_ALLOWED_PLACEHOLDERS: Set[str] = {
        "USER_PROMPT",
        "FEATURE_SPEC",
        "TASK_BREAKDOWN",
        "DESIGN_DOCUMENT",
        "PROJECT_ANALYSIS",
        "GIT_INSIGHTS",
        "MISSING_STRUCTURE",
        "TECH_STACK",
        "REPO_DIGEST",
        "REPO_SYNTHESIS",
        "CLEANUP_RECOMMENDATIONS",
        "MANAGEMENT_PRINCIPLES",
    }

    def __init__(
        self,
        prompt_dir: Optional[Path] = None,
        allowed_placeholders: Optional[Iterable[str]] = None,
    ):
        self.prompt_dir = prompt_dir or (Path(".cde") / "prompts")
        self.allowed_placeholders: Set[str] = set(
            allowed_placeholders or self.DEFAULT_ALLOWED_PLACEHOLDERS
        )

    def load_and_prepare(self, poml_path: Path, context: Dict[str, Any]) -> str:
        """
        Reads a POML file, validates placeholders, and replaces them with sanitized values.

        Args:
            poml_path: Path to the POML file.
            context: Mapping of placeholder -> value.

        Returns:
            Sanitized prompt content ready for downstream consumption.
        """
        if not poml_path.exists():
            raise FileNotFoundError(f"POML recipe not found at {poml_path}")

        content = poml_path.read_text(encoding="utf-8")

        placeholders = set(self.PLACEHOLDER_PATTERN.findall(content))
        if not placeholders:
            return content

        self._validate_placeholders(placeholders)
        self._validate_context(placeholders, context, poml_path)

        sanitized_content = content
        for key in placeholders:
            sanitized_value = self._sanitize_value(context[key])
            sanitized_content = sanitized_content.replace(
                f"{{{{{key}}}}}", sanitized_value
            )

        unresolved = set(self.PLACEHOLDER_PATTERN.findall(sanitized_content))
        if unresolved:
            unresolved_list = ", ".join(sorted(unresolved))
            raise PromptValidationError(
                f"Unresolved placeholders after substitution: {unresolved_list}"
            )

        return sanitized_content

    # --- Internal helpers -------------------------------------------------

    def _validate_placeholders(self, placeholders: Set[str]) -> None:
        """Ensure all placeholders belong to the allowed whitelist."""
        disallowed = placeholders - self.allowed_placeholders
        if disallowed:
            disallowed_list = ", ".join(sorted(disallowed))
            raise PromptValidationError(
                f"Found placeholders not in whitelist: {disallowed_list}"
            )

    def _validate_context(
        self,
        placeholders: Set[str],
        context: Dict[str, Any],
        poml_path: Path,
    ) -> None:
        """Ensure required placeholders are present in the context mapping."""
        missing = placeholders - set(context.keys())
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise PromptValidationError(
                f"POML template {poml_path} requires context keys: {missing_list}"
            )

    @staticmethod
    def _sanitize_value(value: Any) -> str:
        """Convert context values to safe strings for prompt injection."""
        if isinstance(value, (dict, list)):
            serialized = json.dumps(value, indent=2)
        else:
            serialized = str(value)

        # Escape to mitigate prompt/markup injection vectors.
        return str(escape(serialized))
