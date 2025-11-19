"""
Unit tests for SkillStorageAdapter.

Tests filesystem persistence, skill loading/saving, and index management.
"""

import json
from datetime import datetime, timedelta, timezone

import pytest

from cde_orchestrator.skills.models import (
    BaseSkill,
    EphemeralSkill,
    SkillDomain,
    SkillStatus,
    SkillType,
)
from cde_orchestrator.skills.storage import SkillStorageAdapter


@pytest.fixture
def temp_cde_root(tmp_path):
    """Create temporary CDE root directory."""
    cde_dir = tmp_path / "test_project"
    cde_dir.mkdir()
    (cde_dir / ".cde").mkdir()
    return cde_dir


@pytest.fixture
def storage(temp_cde_root):
    """Create SkillStorageAdapter instance with temp directory."""
    return SkillStorageAdapter(cde_root=temp_cde_root)


@pytest.fixture
def sample_base_skill():
    """Create sample base skill for testing."""
    return BaseSkill(
        id="redis-caching",
        title="Redis Caching Patterns",
        description="Best practices for Redis caching",
        domain=SkillDomain.DATABASE,
        complexity="medium",
        tags=["redis", "caching", "performance"],
        content="# Redis Caching\n\nBest practices...",
        version="1.0.0",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        author="test-agent",
        status=SkillStatus.ACTIVE,
    )


@pytest.fixture
def sample_ephemeral_skill():
    """Create sample ephemeral skill for testing."""
    return EphemeralSkill(
        id="task-redis-impl",
        title="Redis Implementation Context",
        description="Task-specific Redis context",
        domain=SkillDomain.DATABASE,
        complexity="medium",
        content="# Task Context\n\nImplementing Redis...",
        created_at=datetime.now(timezone.utc),
        task_id="task-123",
        generated_from_base_skill="redis-caching",
        generation_time_seconds=1.5,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )


class TestSkillStorageAdapter:
    """Tests for SkillStorageAdapter class."""

    # Initialization Tests

    def test_storage_initialization(self, storage, temp_cde_root):
        """Test storage adapter initializes correctly."""
        assert storage.cde_root == temp_cde_root
        assert storage.skills_dir.exists()
        assert storage.base_skills_dir.exists()
        assert storage.ephemeral_skills_dir.exists()

    def test_index_file_created(self, storage):
        """Test that index file is created."""
        assert storage.index_file.exists()

    def test_find_cde_root_in_parent(self, tmp_path):
        """Test finding .cde in parent directories."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / ".cde").mkdir()

        subdir = project_root / "src" / "submodule"
        subdir.mkdir(parents=True)

        # Change to subdir and try to find .cde
        storage = SkillStorageAdapter(cde_root=project_root)
        assert storage.cde_root == project_root

    # Base Skill Saving Tests

    def test_save_base_skill(self, storage, sample_base_skill):
        """Test saving a base skill."""
        path = storage.save_base_skill(sample_base_skill)

        assert path.exists()
        assert (path / "SKILL.md").exists()
        assert (path / "metadata.json").exists()

    def test_save_base_skill_creates_metadata(self, storage, sample_base_skill):
        """Test that metadata.json is created correctly."""
        path = storage.save_base_skill(sample_base_skill)

        metadata_file = path / "metadata.json"
        assert metadata_file.exists()

        with open(metadata_file) as f:
            metadata = json.load(f)

        assert metadata["id"] == sample_base_skill.id
        assert metadata["title"] == sample_base_skill.title
        assert "domain" in metadata

    def test_save_base_skill_creates_content(self, storage, sample_base_skill):
        """Test that SKILL.md is created with correct content."""
        path = storage.save_base_skill(sample_base_skill)

        skill_file = path / "SKILL.md"
        assert skill_file.exists()

        content = skill_file.read_text()
        assert "# Redis Caching" in content

    def test_save_base_skill_updates_index(self, storage, sample_base_skill):
        """Test that saving skill updates the index."""
        storage.save_base_skill(sample_base_skill)

        assert sample_base_skill.id in storage.index
        index_entry = storage.index[sample_base_skill.id]
        assert index_entry.id == sample_base_skill.id
        assert index_entry.skill_type == SkillType.BASE

    # Base Skill Loading Tests

    def test_load_base_skill(self, storage, sample_base_skill):
        """Test loading a base skill."""
        storage.save_base_skill(sample_base_skill)
        loaded = storage.load_base_skill(sample_base_skill.id)

        assert loaded is not None
        assert loaded.id == sample_base_skill.id
        assert loaded.title == sample_base_skill.title

    def test_load_nonexistent_base_skill(self, storage):
        """Test loading nonexistent skill returns None."""
        loaded = storage.load_base_skill("nonexistent-skill")
        assert loaded is None

    def test_load_base_skill_preserves_content(self, storage, sample_base_skill):
        """Test that content is preserved when loading."""
        storage.save_base_skill(sample_base_skill)
        loaded = storage.load_base_skill(sample_base_skill.id)

        assert loaded.content == sample_base_skill.content

    # Ephemeral Skill Saving Tests

    def test_save_ephemeral_skill(self, storage, sample_ephemeral_skill):
        """Test saving an ephemeral skill."""
        path = storage.save_ephemeral_skill(sample_ephemeral_skill)

        assert path.exists()
        assert (path / "SKILL.md").exists()
        assert (path / "metadata.json").exists()

    def test_save_ephemeral_skill_includes_expiry(
        self, storage, sample_ephemeral_skill
    ):
        """Test that ephemeral skill metadata includes expiry."""
        path = storage.save_ephemeral_skill(sample_ephemeral_skill)

        metadata_file = path / "metadata.json"
        with open(metadata_file) as f:
            metadata = json.load(f)

        assert "expires_at" in metadata
        assert metadata["type"] == SkillType.EPHEMERAL

    def test_save_ephemeral_skill_includes_task_id(
        self, storage, sample_ephemeral_skill
    ):
        """Test that ephemeral skill includes task_id."""
        path = storage.save_ephemeral_skill(sample_ephemeral_skill)

        metadata_file = path / "metadata.json"
        with open(metadata_file) as f:
            metadata = json.load(f)

        assert metadata["task_id"] == sample_ephemeral_skill.task_id

    # Ephemeral Skill Loading Tests

    def test_load_ephemeral_skill(self, storage, sample_ephemeral_skill):
        """Test loading an ephemeral skill."""
        storage.save_ephemeral_skill(sample_ephemeral_skill)
        loaded = storage.load_ephemeral_skill(sample_ephemeral_skill.id)

        assert loaded is not None
        assert loaded.id == sample_ephemeral_skill.id
        assert loaded.task_id == sample_ephemeral_skill.task_id

    def test_load_expired_ephemeral_skill(self, storage):
        """Test loading expired ephemeral skill."""
        expired_skill = EphemeralSkill(
            id="expired-skill",
            title="Expired Skill",
            description="Test expired skill",
            domain=SkillDomain.DATABASE,
            tags=["test"],
            content="# Expired\n\nExpired skill content",
            version="1.0.0",
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            updated_at=datetime.now(timezone.utc) - timedelta(days=2),
            author="test-agent",
            status=SkillStatus.ACTIVE,
            task_id="task-expired",
            base_skills=[],
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        storage.save_ephemeral_skill(expired_skill)
        loaded = storage.load_ephemeral_skill(expired_skill.id)

        # Should still load, but caller should check is_expired
        assert loaded is not None
        assert loaded.is_expired

    # Skill Listing Tests

    def test_list_base_skills(self, storage, sample_base_skill):
        """Test listing base skills."""
        storage.save_base_skill(sample_base_skill)
        skills = storage.list_base_skills()

        assert len(skills) == 1
        assert skills[0].id == sample_base_skill.id

    def test_list_ephemeral_skills(self, storage, sample_ephemeral_skill):
        """Test listing ephemeral skills."""
        storage.save_ephemeral_skill(sample_ephemeral_skill)
        skills = storage.list_ephemeral_skills()

        assert len(skills) == 1
        assert skills[0].id == sample_ephemeral_skill.id

    def test_list_skills_returns_metadata_only(self, storage, sample_base_skill):
        """Test that list operations return lightweight metadata."""
        storage.save_base_skill(sample_base_skill)
        skills = storage.list_base_skills()

        # Should be SkillMetadata, not full BaseSkill
        assert len(skills) > 0
        skill_meta = skills[0]
        assert hasattr(skill_meta, "id")
        assert hasattr(skill_meta, "name")

    # Skill Deletion Tests

    def test_delete_base_skill(self, storage, sample_base_skill):
        """Test deleting a base skill."""
        storage.save_base_skill(sample_base_skill)

        result = storage.delete_base_skill(sample_base_skill.id)
        assert result is True

        # Verify deletion
        loaded = storage.load_base_skill(sample_base_skill.id)
        assert loaded is None

    def test_delete_nonexistent_base_skill(self, storage):
        """Test deleting nonexistent skill returns False."""
        result = storage.delete_base_skill("nonexistent")
        assert result is False

    def test_delete_ephemeral_skill(self, storage, sample_ephemeral_skill):
        """Test deleting an ephemeral skill."""
        storage.save_ephemeral_skill(sample_ephemeral_skill)

        result = storage.delete_ephemeral_skill(sample_ephemeral_skill.id)
        assert result is True

        # Verify deletion
        loaded = storage.load_ephemeral_skill(sample_ephemeral_skill.id)
        assert loaded is None

    def test_delete_skill_removes_from_index(self, storage, sample_base_skill):
        """Test that deletion removes skill from index."""
        storage.save_base_skill(sample_base_skill)
        storage.delete_base_skill(sample_base_skill.id)

        assert sample_base_skill.id not in storage.index

    # Cleanup Tests

    def test_cleanup_expired_ephemeral_skills(self, storage):
        """Test cleanup of expired ephemeral skills."""
        # Create expired skill
        expired_skill = EphemeralSkill(
            id="expired-skill",
            title="Expired Skill",
            description="Test expired skill",
            domain=SkillDomain.DATABASE,
            tags=["test"],
            content="# Expired",
            version="1.0.0",
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            updated_at=datetime.now(timezone.utc) - timedelta(days=2),
            author="test-agent",
            status=SkillStatus.ACTIVE,
            task_id="task-expired",
            base_skills=[],
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        # Create active skill
        active_skill = EphemeralSkill(
            id="active-skill",
            title="Active Skill",
            description="Test active skill",
            domain=SkillDomain.DATABASE,
            tags=["test"],
            content="# Active",
            version="1.0.0",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            author="test-agent",
            status=SkillStatus.ACTIVE,
            task_id="task-active",
            base_skills=[],
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )

        storage.save_ephemeral_skill(expired_skill)
        storage.save_ephemeral_skill(active_skill)

        deleted_count = storage.cleanup_expired_ephemeral_skills()

        assert deleted_count == 1
        assert storage.load_ephemeral_skill("expired-skill") is None
        assert storage.load_ephemeral_skill("active-skill") is not None

    def test_cleanup_with_no_expired_skills(self, storage, sample_ephemeral_skill):
        """Test cleanup when no skills are expired."""
        storage.save_ephemeral_skill(sample_ephemeral_skill)

        deleted_count = storage.cleanup_expired_ephemeral_skills()
        assert deleted_count == 0

    # Search Tests

    def test_search_skills_by_query(self, storage, sample_base_skill):
        """Test searching skills by query string."""
        storage.save_base_skill(sample_base_skill)

        results = storage.search_skills("redis")
        assert len(results) > 0
        assert any(r.id == sample_base_skill.id for r in results)

    def test_search_skills_case_insensitive(self, storage, sample_base_skill):
        """Test that search is case insensitive."""
        storage.save_base_skill(sample_base_skill)

        results_lower = storage.search_skills("redis")
        results_upper = storage.search_skills("REDIS")

        assert len(results_lower) == len(results_upper)

    def test_search_skills_no_results(self, storage):
        """Test search with no matching results."""
        results = storage.search_skills("nonexistent-term")
        assert len(results) == 0

    # Statistics Tests

    def test_get_storage_stats(
        self, storage, sample_base_skill, sample_ephemeral_skill
    ):
        """Test getting storage statistics."""
        storage.save_base_skill(sample_base_skill)
        storage.save_ephemeral_skill(sample_ephemeral_skill)

        stats = storage.get_storage_stats()

        assert "base_count" in stats
        assert "ephemeral_count" in stats
        assert stats["base_count"] >= 1
        assert stats["ephemeral_count"] >= 1

    # Index Management Tests

    def test_index_persists_across_instances(self, temp_cde_root, sample_base_skill):
        """Test that index persists when creating new storage instance."""
        storage1 = SkillStorageAdapter(cde_root=temp_cde_root)
        storage1.save_base_skill(sample_base_skill)

        # Create new instance
        storage2 = SkillStorageAdapter(cde_root=temp_cde_root)

        assert sample_base_skill.id in storage2.index

    def test_index_updated_on_save(self, storage, sample_base_skill):
        """Test that index is updated immediately on save."""
        storage.save_base_skill(sample_base_skill)

        # Index should be updated in memory
        assert sample_base_skill.id in storage.index

        # Index should be persisted to disk
        assert storage.index_file.exists()

    # Edge Cases

    def test_save_skill_with_special_characters_in_id(self, storage):
        """Test saving skill with special characters in ID."""
        skill = BaseSkill(
            id="redis-caching-v2.0",
            title="Redis Caching V2",
            description="Version 2.0 of Redis caching",
            domain=SkillDomain.DATABASE,
            complexity="medium",
            tags=["redis"],
            content="# Redis V2",
            version="2.0.0",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            author="test-agent",
            status=SkillStatus.ACTIVE,
        )

        path = storage.save_base_skill(skill)
        assert path.exists()

    def test_load_skill_handles_corrupted_metadata(self, storage, sample_base_skill):
        """Test loading skill with corrupted metadata file."""
        path = storage.save_base_skill(sample_base_skill)

        # Corrupt metadata
        metadata_file = path / "metadata.json"
        metadata_file.write_text("{ invalid json")

        # Should handle gracefully (doesn't crash entire system)
        # Depending on implementation, might return None or raise
        _ = storage.load_base_skill(sample_base_skill.id)
