# src/cde_orchestrator/prompt_manager.py
from pathlib import Path


class PromptManager:
    """Loads POML recipes and injects dynamic context."""

    @staticmethod
    def load_and_prepare(poml_path: Path, context: dict) -> str:
        """
        Reads a POML file and replaces placeholders with values from the context dict.
        Placeholders are in the format {{KEY}}.
        """
        if not poml_path.exists():
            raise FileNotFoundError(f"POML recipe not found at {poml_path}")

        with open(poml_path, 'r') as f:
            content = f.read()

        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        return content
