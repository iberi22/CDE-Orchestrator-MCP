# src/cde_orchestrator/application/use_cases/manage_recipes.py
from typing import List, Optional

from ...domain.entities import Recipe, RecipeSuggestion
from ...domain.ports import IRecipeRepository
from ...domain.services.recipe_service import RecipeService


class ManageRecipesUseCase:
    """
    Use case for managing and suggesting recipes.
    """

    def __init__(self, recipe_repository: IRecipeRepository, recipe_service: RecipeService):
        self._recipe_repository = recipe_repository
        self._recipe_service = recipe_service
        self._recipes: Optional[List[Recipe]] = None

    def _load_recipes_if_needed(self):
        if self._recipes is None:
            self._recipes = self._recipe_repository.list_all()

    def list_all_recipes(self) -> List[Recipe]:
        self._load_recipes_if_needed()
        return self._recipes

    def suggest_recipe(self, user_prompt: str, phase_id: str) -> Optional[RecipeSuggestion]:
        self._load_recipes_if_needed()
        return self._recipe_service.suggest_recipe(user_prompt, phase_id, self._recipes)
