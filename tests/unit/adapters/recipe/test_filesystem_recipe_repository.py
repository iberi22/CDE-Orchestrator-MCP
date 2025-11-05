# tests/unit/adapters/recipe/test_filesystem_recipe_repository.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.cde_orchestrator.domain.entities import Recipe
from src.cde_orchestrator.adapters.recipe.filesystem_recipe_repository import FileSystemRecipeRepository

@pytest.fixture
def mock_poml_content(request):
    """Provides POML content for mock files."""
    if request.param == "valid":
        return '<let name="tools">["tool1"]</let><role>A valid recipe.</role>'
    if request.param == "invalid":
        return '<let name="tools">["tool1"]</let><role>An invalid recipe.'
    return ''

@patch('pathlib.Path')
def test_list_all_recipes(MockPath):
    """Should load all valid recipes from the recipes directory."""
    mock_dir = MagicMock()
    mock_dir.exists.return_value = True

    mock_file1 = MagicMock()
    mock_file1.stem = 'recipe1'
    mock_file1.parent.name = 'category1'
    mock_file1.is_file.return_value = True

    mock_file2 = MagicMock()
    mock_file2.stem = 'recipe2'
    mock_file2.parent.name = 'category2'
    mock_file2.is_file.return_value = True

    mock_dir.rglob.return_value = [mock_file1, mock_file2]

    # We need to mock the context manager for open
    mock_open_func = patch('builtins.open', MagicMock())
    mock_open = mock_open_func.start()
    mock_open.return_value.__enter__.return_value.read.return_value = '<let name="tools">[]</let><role>Test recipe.</role>'

    MockPath.return_value = mock_dir
    repository = FileSystemRecipeRepository(recipes_dir=Path("dummy"))
    recipes = repository.list_all()

    assert len(recipes) == 2
    assert recipes[0].id == 'recipe1'
    assert recipes[1].category == 'category2'

    mock_open_func.stop()

@patch('pathlib.Path')
def test_list_all_handles_parsing_errors(MockPath):
    """Should skip recipes that fail to parse."""
    mock_dir = MagicMock()
    mock_dir.exists.return_value = True

    mock_file = MagicMock()
    mock_dir.rglob.return_value = [mock_file]

    mock_open_func = patch('builtins.open', MagicMock())
    mock_open = mock_open_func.start()
    mock_open.return_value.__enter__.return_value.read.side_effect = Exception("Parsing failed")

    MockPath.return_value = mock_dir
    repository = FileSystemRecipeRepository(recipes_dir=Path("dummy"))
    recipes = repository.list_all()

    assert len(recipes) == 0
    mock_open_func.stop()
