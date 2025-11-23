"""
Unit tests for the FileSystemRecipeRepository.
"""

from pathlib import Path

import pytest

from cde_orchestrator.adapters.recipe.filesystem_recipe_repository import (
    FileSystemRecipeRepository,
)


@pytest.fixture
def recipe_dir(tmp_path):
    """Creates a temporary recipe directory with sample recipes."""
    recipes_path = tmp_path / "recipes"
    engineering_path = recipes_path / "engineering"
    engineering_path.mkdir(parents=True)

    # Sample ai-engineer recipe
    (engineering_path / "ai-engineer.poml").write_text(
        """
    <poml>
        <let name="tools">["file", "shell"]</let>
        <let name="providers">{ "openai": { "model": "gpt-5" } }</let>
        <role>You are an AI engineer.</role>
    </poml>
    """
    )

    # Sample sprint-prioritizer recipe
    (recipes_path / "planning").mkdir()
    (recipes_path / "planning" / "sprint-prioritizer.poml").write_text(
        """
    <poml>
        <let name="tools">["jira"]</let>
        <role>You prioritize sprints.</role>
    </poml>
    """
    )

    return recipes_path


@pytest.mark.asyncio
async def test_list_all_recipes(recipe_dir):
    """Tests that all recipes are loaded and parsed correctly."""
    repo = FileSystemRecipeRepository(recipes_dir=recipe_dir)
    recipes = await repo.list_all()

    assert len(recipes) == 2

    recipe_ids = {recipe.id for recipe in recipes}
    assert "ai-engineer" in recipe_ids
    assert "sprint-prioritizer" in recipe_ids


@pytest.mark.asyncio
async def test_empty_recipe_dir():
    """Tests that an empty list is returned for a non-existent directory."""
    repo = FileSystemRecipeRepository(recipes_dir=Path("non_existent_dir"))
    recipes = await repo.list_all()
    assert len(recipes) == 0


@pytest.mark.asyncio
async def test_parsing_logic(recipe_dir):
    """Tests the parsing logic for a single recipe."""
    repo = FileSystemRecipeRepository(recipes_dir=recipe_dir)
    recipes = await repo.list_all()

    ai_engineer = next((r for r in recipes if r.id == "ai-engineer"), None)
    assert ai_engineer is not None
    assert ai_engineer.category == "engineering"
    assert "file" in ai_engineer.tools
    assert "openai" in ai_engineer.providers
