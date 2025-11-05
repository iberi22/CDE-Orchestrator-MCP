# tests/unit/domain/services/test_recipe_service.py
import pytest
from typing import List

from src.cde_orchestrator.domain.entities import Recipe
from src.cde_orchestrator.domain.services.recipe_service import RecipeService

@pytest.fixture
def recipes():
    return [
        Recipe(id="ai-engineer", name="AI Engineer", category="engineering", description="For AI engineering tasks.", file_path="", tools=[], providers={}, topology=""),
        Recipe(id="sprint-prioritizer", name="Sprint Prioritizer", category="product", description="For sprint planning.", file_path="", tools=[], providers={}, topology=""),
        Recipe(id="studio-producer", name="Studio Producer", category="project-management", description="For project management.", file_path="", tools=[], providers={}, topology=""),
    ]

@pytest.fixture
def recipe_service():
    return RecipeService()

def test_suggest_recipe_by_content(recipe_service: RecipeService, recipes: List[Recipe]):
    """Should suggest 'ai-engineer' for AI-related prompts."""
    prompt = "I want to build a machine learning model."
    suggestion = recipe_service.suggest_recipe(prompt, "implement", recipes)
    assert suggestion is not None
    assert suggestion.recipe.id == "ai-engineer"
    assert suggestion.confidence == 0.8

def test_suggest_recipe_by_phase(recipe_service: RecipeService, recipes: List[Recipe]):
    """Should suggest 'sprint-prioritizer' for the define phase."""
    prompt = "I want to plan the next sprint."
    suggestion = recipe_service.suggest_recipe(prompt, "define", recipes)
    assert suggestion is not None
    assert suggestion.recipe.id == "sprint-prioritizer"
    assert suggestion.confidence == 0.8

def test_suggest_recipe_fallback(recipe_service: RecipeService, recipes: List[Recipe]):
    """Should fallback to the first recipe if no other suggestion is found."""
    prompt = "I want to write some documentation."
    suggestion = recipe_service.suggest_recipe(prompt, "documentation", recipes)
    assert suggestion is not None
    assert suggestion.recipe.id == "ai-engineer" # The first recipe in the list
    assert suggestion.confidence == pytest.approx(0.2)
