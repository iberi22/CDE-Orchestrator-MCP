# src/cde_orchestrator/adapters/recipe/filesystem_recipe_repository.py
import re
from pathlib import Path
from typing import List
import aiofiles

from ...domain.entities import Recipe
from ...domain.ports import IRecipeRepository


class FileSystemRecipeRepository(IRecipeRepository):
    """
    Loads recipe definitions from POML files on the filesystem.
    """

    def __init__(self, recipes_dir: Path):
        self._recipes_dir = recipes_dir

    async def list_all(self) -> List[Recipe]:
        """Load all POML recipes from the recipes directory."""
        if not self._recipes_dir.exists():
            return []

        recipes = []
        # rglob is synchronous but fast for directory listing.
        # Reading files will be async.
        for poml_file in self._recipes_dir.rglob("*.poml"):
            try:
                recipe = await self._parse_recipe(poml_file)
                recipes.append(recipe)
            except Exception as e:
                print(f"Warning: Failed to load recipe {poml_file}: {e}")
        return recipes

    async def _parse_recipe(self, poml_file: Path) -> Recipe:
        """Parse a POML file and extract recipe metadata."""
        async with aiofiles.open(poml_file, "r", encoding="utf-8") as f:
            content = await f.read()

        recipe_id = poml_file.stem
        category = poml_file.parent.name

        tools_match = re.search(r'<let name="tools">\s*\[(.*?)\]', content, re.DOTALL)
        tools = []
        if tools_match:
            tools_str = tools_match.group(1)
            tools = [
                tool.strip().strip('"') for tool in tools_str.split(",") if tool.strip()
            ]

        providers_match = re.search(
            r'<let name="providers">\s*\{(.*?)\}', content, re.DOTALL
        )
        providers = {}
        if providers_match:
            providers_str = providers_match.group(1)
            if "openai" in providers_str:
                providers["openai"] = {"model": "gpt-5", "temperature": 0.2}
            if "gemini" in providers_str:
                providers["gemini"] = {"model": "gemini-2.5-pro", "temperature": 0.2}
            if "qwen" in providers_str:
                providers["qwen"] = {"model": "Qwen2.5-Coder", "temperature": 0.1}

        topology_match = re.search(r'<let name="topology">(.*?)</let>', content)
        topology = topology_match.group(1).strip() if topology_match else "solo"

        role_match = re.search(r"<role>(.*?)</role>", content, re.DOTALL)
        description = "AI Agent Recipe"
        if role_match:
            role_text = role_match.group(1).strip()
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
