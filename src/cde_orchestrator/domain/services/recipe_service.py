# src/cde_orchestrator/domain/services/recipe_service.py
from typing import List, Optional

from ..entities import Recipe, RecipeSuggestion


class RecipeService:
    """
    Domain service for recipe-related business logic.
    """

    def suggest_recipe(
        self, user_prompt: str, phase_id: str, recipes: List[Recipe]
    ) -> Optional[RecipeSuggestion]:
        """
        Suggests the best recipe based on a scoring system.

        The suggestion logic is as follows:
        1.  **Keyword Matching (High Confidence):** The user's prompt is checked for specific
            keywords. If a keyword matches a recipe's theme, that recipe is suggested
            with high confidence (0.8).
        2.  **Phase-Based Matching (Medium Confidence):** If no keywords match, the current
            workflow phase is used to suggest a relevant recipe. This suggestion has
            medium confidence (0.6).
        3.  **Fallback (Low Confidence):** If no recipe is found through keyword or phase
            matching, the first recipe in the provided list is returned as a fallback
            suggestion with low confidence (0.2).
        4.  **No Recipes:** If the list of recipes is empty, no suggestion is made (returns None).
        """
        if not recipes:
            return None

        prompt_lower = user_prompt.lower()

        # 1. Keyword-based suggestions (High Confidence)
        keyword_map = {
            "ai-engineer": ["ai", "ml", "machine learning", "algorithm"],
            "sprint-prioritizer": ["sprint", "prioritize", "backlog", "feature"],
            "studio-producer": ["team", "coordinate", "manage", "workflow"],
        }

        for recipe_id, keywords in keyword_map.items():
            if any(keyword in prompt_lower for keyword in keywords):
                for recipe in recipes:
                    if recipe.id == recipe_id:
                        return RecipeSuggestion(recipe=recipe, confidence=0.8)

        # 2. Phase-based suggestions (Medium Confidence)
        phase_map = {
            "define": "sprint-prioritizer",
            "decompose": "studio-producer",
            "design": "ai-engineer",
            "implement": "ai-engineer",
            "test": "ai-engineer",
            "review": "studio-producer",
        }

        suggested_recipe_id = phase_map.get(phase_id)
        if suggested_recipe_id:
            for recipe in recipes:
                if recipe.id == suggested_recipe_id:
                    return RecipeSuggestion(recipe=recipe, confidence=0.6)

        # 3. Fallback to the first recipe
        return RecipeSuggestion(recipe=recipes[0], confidence=0.2)
