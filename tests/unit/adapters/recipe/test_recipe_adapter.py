"""
Unit tests for the RecipeAdapter.
"""
import pytest
from pathlib import Path
from cde_orchestrator.adapters.recipe.recipe_adapter import RecipeAdapter

@pytest.fixture
def recipe_dir(tmp_path):
    """Creates a temporary recipe directory with sample recipes."""
    recipes_path = tmp_path / "recipes"
    engineering_path = recipes_path / "engineering"
    engineering_path.mkdir(parents=True)

    # Sample ai-engineer recipe
    (engineering_path / "ai-engineer.poml").write_text("""
    <poml>
        <let name="tools">["file", "shell"]</let>
        <let name="providers">{ "openai": { "model": "gpt-5" } }</let>
        <role>You are an AI engineer.</role>
    </poml>
    """)

    # Sample sprint-prioritizer recipe
    (recipes_path / "planning").mkdir()
    (recipes_path / "planning" / "sprint-prioritizer.poml").write_text("""
    <poml>
        <let name="tools">["jira"]</let>
        <role>You prioritize sprints.</role>
    </poml>
    """)

    return recipes_path

def test_load_recipes(recipe_dir):
    """Tests that recipes are loaded and parsed correctly."""
    adapter = RecipeAdapter(recipes_dir=recipe_dir)
    assert len(adapter.recipes) == 2

    ai_engineer = adapter.get_recipe("ai-engineer")
    assert ai_engineer is not None
    assert ai_engineer.category == "engineering"
    assert "file" in ai_engineer.tools
    assert "openai" in ai_engineer.providers

def test_suggest_recipe_by_keyword(recipe_dir):
    """Tests recipe suggestion based on keywords in the user prompt."""
    adapter = RecipeAdapter(recipes_dir=recipe_dir)
    recipe = adapter.suggest_recipe("prioritize the backlog for our next sprint", "define")
    assert recipe is not None
    assert recipe.id == "sprint-prioritizer"

def test_suggest_recipe_by_phase(recipe_dir):
    """Tests recipe suggestion based on the workflow phase."""
    adapter = RecipeAdapter(recipes_dir=recipe_dir)
    recipe = adapter.suggest_recipe("a generic user prompt", "implement")
    assert recipe is not None
    assert recipe.id == "ai-engineer"

def test_list_recipes_by_category(recipe_dir):
    """Tests that recipes are correctly listed and grouped by category."""
    adapter = RecipeAdapter(recipes_dir=recipe_dir)
    categories = adapter.list_recipes()
    assert "engineering" in categories
    assert "planning" in categories
    assert "ai-engineer" in categories["engineering"]
    assert "sprint-prioritizer" in categories["planning"]

def test_empty_recipe_dir():
    """Tests that the adapter handles an empty or non-existent recipe directory gracefully."""
    adapter = RecipeAdapter(recipes_dir=Path("non_existent_dir"))
    assert len(adapter.recipes) == 0
    assert adapter.suggest_recipe("any prompt", "any_phase") is None
