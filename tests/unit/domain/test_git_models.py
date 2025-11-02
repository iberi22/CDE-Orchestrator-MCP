# tests/unit/domain/test_git_models.py

from datetime import datetime
from pathlib import Path

from cde_orchestrator.domain.git import Commit, Modification

def test_commit_model_creation():
    """Tests that the Commit model can be instantiated correctly."""
    now = datetime.now()
    commit = Commit(
        hash="abcdef123",
        author="Test Author",
        date=now,
        message="Test commit message",
    )
    assert commit.hash == "abcdef123"
    assert commit.author == "Test Author"
    assert commit.date == now
    assert commit.message == "Test commit message"
    assert commit.modifications == []

def test_modification_model_creation():
    """Tests that the Modification model can be instantiated correctly."""
    modification = Modification(
        change_type="A",
        old_path=Path(""),
        new_path=Path("src/main.py"),
    )
    assert modification.change_type == "A"
    assert modification.old_path == Path("")
    assert modification.new_path == Path("src/main.py")
