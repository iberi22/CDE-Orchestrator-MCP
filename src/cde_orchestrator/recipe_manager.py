# src/cde_orchestrator/recipe_manager.py
import re
from pathlib import Path
from typing import Dict, List, Optional

from .models import Recipe


class RecipeManager:
    """Manages POML recipes and their selection based on context."""

    def __init__(self, recipes_dir: Path):
        self.recipes_dir = recipes_dir
        self.recipes: Dict[str, Recipe] = {}
        self._load_recipes()

    def _load_recipes(self):
        """Load all POML recipes from the recipes directory."""
        if not self.recipes_dir.exists():
            return

        for poml_file in self.recipes_dir.rglob("*.poml"):
            try:
                recipe = self._parse_recipe(poml_file)
                self.recipes[recipe.id] = recipe
            except Exception as e:
                print(f"Warning: Failed to load recipe {poml_file}: {e}")

    def _parse_recipe(self, poml_file: Path) -> Recipe:
        """Parse a POML file and extract recipe metadata."""
        with open(poml_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract metadata from POML <let> blocks
        recipe_id = poml_file.stem
        category = poml_file.parent.name

        # Parse tools
        tools_match = re.search(r'<let name="tools">\s*\[(.*?)\]', content, re.DOTALL)
        tools = []
        if tools_match:
            tools_str = tools_match.group(1)
            tools = [
                tool.strip().strip('"') for tool in tools_str.split(",") if tool.strip()
            ]

        # Parse providers
        providers_match = re.search(
            r'<let name="providers">\s*\{(.*?)\}', content, re.DOTALL
        )
        providers = {}
        if providers_match:
            # Simple parsing - in production you'd want proper JSON parsing
            providers_str = providers_match.group(1)
            if "openai" in providers_str:
                providers["openai"] = {"model": "gpt-5", "temperature": 0.2}
            if "gemini" in providers_str:
                providers["gemini"] = {"model": "gemini-2.5-pro", "temperature": 0.2}
            if "qwen" in providers_str:
                providers["qwen"] = {"model": "Qwen2.5-Coder", "temperature": 0.1}

        # Parse topology
        topology_match = re.search(r'<let name="topology">(.*?)</let>', content)
        topology = topology_match.group(1).strip() if topology_match else "solo"

        # Extract description from role section
        role_match = re.search(r"<role>(.*?)</role>", content, re.DOTALL)
        description = "AI Agent Recipe"
        if role_match:
            role_text = role_match.group(1).strip()
            # Take first sentence as description
            first_sentence = role_text.split(".")[0]
            if len(first_sentence) < 200:
                description = first_sentence + "."

        return Recipe(
            id=recipe_id,
            name=recipe_id.replace("-", " ").title(),
            category=category,
            description=description,
            file_path=str(poml_file),
            tools=tools,
            providers=providers,
            topology=topology,
        )

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID."""
        return self.recipes.get(recipe_id)

    def get_recipes_by_category(self, category: str) -> List[Recipe]:
        """Get all recipes in a specific category."""
        return [
            recipe for recipe in self.recipes.values() if recipe.category == category
        ]

    def suggest_recipe(self, user_prompt: str, phase_id: str) -> Optional[Recipe]:
        """Suggest the best recipe based on user prompt and current phase."""
        prompt_lower = user_prompt.lower()

        # Phase-specific recipe suggestions
        phase_recipes = {
            "define": ["sprint-prioritizer", "studio-producer"],
            "decompose": ["studio-producer", "sprint-prioritizer"],
            "design": ["ai-engineer", "studio-producer"],
            "implement": ["ai-engineer"],
            "test": ["ai-engineer"],
            "review": ["studio-producer", "ai-engineer"],
        }

        # Content-based suggestions
        if any(
            keyword in prompt_lower
            for keyword in ["ai", "ml", "machine learning", "algorithm"]
        ):
            return self.get_recipe("ai-engineer")
        elif any(
            keyword in prompt_lower
            for keyword in ["sprint", "prioritize", "backlog", "feature"]
        ):
            return self.get_recipe("sprint-prioritizer")
        elif any(
            keyword in prompt_lower
            for keyword in ["team", "coordinate", "manage", "workflow"]
        ):
            return self.get_recipe("studio-producer")

        # Default to phase-based suggestion
        suggested_recipes = phase_recipes.get(phase_id, ["ai-engineer"])
        for recipe_id in suggested_recipes:
            recipe = self.get_recipe(recipe_id)
            if recipe:
                return recipe

        # Fallback to first available recipe
        if self.recipes:
            return list(self.recipes.values())[0]

        return None

    def load_recipe_content(self, recipe_id: str, context: Dict[str, str]) -> str:
        """Load and prepare a recipe with context injection."""
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe '{recipe_id}' not found")

        with open(recipe.file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Inject context variables
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))

        return content

    def list_recipes(self) -> Dict[str, List[str]]:
        """List all available recipes grouped by category."""
        result = {}
        for recipe in self.recipes.values():
            if recipe.category not in result:
                result[recipe.category] = []
            result[recipe.category].append(recipe.id)
        return result
