"""
Unit Tests for Specification Entity.

Tests business rules and domain logic for documentation specifications.
NO infrastructure dependencies - pure domain tests.

Coverage:
    - Factory method creation
    - Status transitions (draft → active → deprecated → archived)
    - Semantic linking
    - Tag management
    - Content updates
    - Business rule validation
"""

import pytest
from datetime import datetime, timezone

from cde_orchestrator.domain.documentation.entities import (
    Specification,
    SpecificationId,
    DocumentType,
    DocumentStatus,
    SemanticLink,
    LinkRelationship,
)

from cde_orchestrator.domain.documentation.exceptions import (
    InvalidStatusTransitionError,
    InvalidLinkError,
    SpecificationValidationError,
)


# ============================================================================
# FACTORY TESTS
# ============================================================================


def test_create_specification_with_minimal_fields():
    """Test creating specification with only required fields."""
    spec = Specification.create(
        title="Test Feature",
        type=DocumentType.FEATURE,
        author="Alice",
    )

    assert spec.id is not None
    assert spec.title == "Test Feature"
    assert spec.type == DocumentType.FEATURE
    assert spec.status == DocumentStatus.DRAFT
    assert spec.author == "Alice"
    assert spec.content == ""
    assert spec.tags == []
    assert spec.links == []
    assert spec.llm_summary is None


def test_create_specification_with_all_fields():
    """Test creating specification with all optional fields."""
    spec = Specification.create(
        title="Authentication System",
        type=DocumentType.FEATURE,
        author="Alice",
        content="This feature implements authentication...",
        tags=["security", "auth"],
        llm_summary="Authentication system using OAuth2 flow.",
    )

    assert spec.title == "Authentication System"
    assert spec.content == "This feature implements authentication..."
    assert "security" in spec.tags
    assert "auth" in spec.tags
    assert spec.llm_summary == "Authentication system using OAuth2 flow."


def test_create_specification_normalizes_tags():
    """Test that tags are normalized to lowercase."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        tags=["Security", "AUTH", "  backend  "],
    )

    assert spec.tags == ["security", "auth", "backend"]


def test_create_specification_validates_title_length():
    """Test that title must be at least 3 characters."""
    with pytest.raises(SpecificationValidationError) as exc_info:
        Specification.create(
            title="AB",  # Too short
            type=DocumentType.FEATURE,
            author="Alice",
        )

    assert "Title must be at least 3 characters" in str(exc_info.value)


def test_create_specification_validates_llm_summary_length():
    """Test that LLM summary must be concise."""
    long_summary = " ".join(["word"] * 150)  # 150 words

    with pytest.raises(SpecificationValidationError) as exc_info:
        Specification.create(
            title="Test",
            type=DocumentType.FEATURE,
            author="Alice",
            llm_summary=long_summary,
        )

    assert "LLM summary must be concise" in str(exc_info.value)


# ============================================================================
# STATUS TRANSITION TESTS
# ============================================================================


def test_activate_specification_from_draft():
    """Test activating a draft specification."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test summary",
    )

    assert spec.status == DocumentStatus.DRAFT

    spec.activate()

    assert spec.status == DocumentStatus.ACTIVE


def test_activate_requires_llm_summary():
    """Test that activation requires LLM summary."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        # No llm_summary
    )

    with pytest.raises(SpecificationValidationError) as exc_info:
        spec.activate()

    assert "Active specifications must have LLM summary" in str(exc_info.value)


def test_deprecate_active_specification():
    """Test deprecating an active specification."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()

    successor_id = SpecificationId("new-spec-id")
    spec.deprecate(reason="Replaced by v2", successor_id=successor_id)

    assert spec.status == DocumentStatus.DEPRECATED
    assert spec.metadata["deprecation_reason"] == "Replaced by v2"
    assert spec.metadata["successor_id"] == successor_id


def test_cannot_deprecate_draft():
    """Test that draft specs cannot be deprecated."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
    )

    with pytest.raises(InvalidStatusTransitionError) as exc_info:
        spec.deprecate(reason="test")

    assert "Can only deprecate ACTIVE specifications" in str(exc_info.value)


def test_archive_active_specification():
    """Test archiving an active specification."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()

    spec.archive()

    assert spec.status == DocumentStatus.ARCHIVED


def test_cannot_archive_draft():
    """Test that draft specs cannot be archived directly."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
    )

    with pytest.raises(InvalidStatusTransitionError) as exc_info:
        spec.archive()

    assert "Can only archive ACTIVE or DEPRECATED" in str(exc_info.value)


def test_archived_is_terminal_state():
    """Test that archived specs cannot transition to any other state."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()
    spec.archive()

    # Cannot activate archived spec
    assert not spec.status.can_transition_to(DocumentStatus.ACTIVE)
    assert not spec.status.can_transition_to(DocumentStatus.DEPRECATED)


# ============================================================================
# SEMANTIC LINK TESTS
# ============================================================================


def test_establish_link_to_other_specification():
    """Test creating semantic link between specifications."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()

    target_id = SpecificationId("target-spec-id")

    spec.establish_link(
        target_id=target_id,
        relationship=LinkRelationship.IMPLEMENTS,
    )

    assert len(spec.links) == 1
    assert spec.links[0].target_id == target_id
    assert spec.links[0].relationship == LinkRelationship.IMPLEMENTS


def test_establish_link_with_metadata():
    """Test creating link with additional metadata."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()

    target_id = SpecificationId("target-spec-id")

    spec.establish_link(
        target_id=target_id,
        relationship=LinkRelationship.REFERENCES,
        metadata={"line_number": 42, "quote": "See architecture doc"},
    )

    assert spec.links[0].metadata["line_number"] == 42
    assert spec.links[0].metadata["quote"] == "See architecture doc"


def test_cannot_link_archived_specification():
    """Test that archived specs cannot create links."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()
    spec.archive()

    target_id = SpecificationId("target-spec-id")

    with pytest.raises(InvalidLinkError) as exc_info:
        spec.establish_link(
            target_id=target_id,
            relationship=LinkRelationship.IMPLEMENTS,
        )

    assert "Cannot link archived specifications" in str(exc_info.value)


def test_cannot_create_duplicate_links():
    """Test that duplicate links to same target with same relationship are prevented."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()

    target_id = SpecificationId("target-spec-id")

    # First link succeeds
    spec.establish_link(target_id=target_id, relationship=LinkRelationship.IMPLEMENTS)

    # Duplicate link fails
    with pytest.raises(InvalidLinkError) as exc_info:
        spec.establish_link(target_id=target_id, relationship=LinkRelationship.IMPLEMENTS)

    assert "Link with relationship 'implements' already exists" in str(exc_info.value)


def test_can_create_multiple_links_with_different_relationships():
    """Test that same target can have multiple relationships."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()

    target_id = SpecificationId("target-spec-id")

    spec.establish_link(target_id=target_id, relationship=LinkRelationship.IMPLEMENTS)
    spec.establish_link(target_id=target_id, relationship=LinkRelationship.EXTENDS)

    assert len(spec.links) == 2


def test_has_link_to():
    """Test checking if link exists to target."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()

    target_id = SpecificationId("target-spec-id")
    other_id = SpecificationId("other-spec-id")

    spec.establish_link(target_id=target_id, relationship=LinkRelationship.IMPLEMENTS)

    assert spec.has_link_to(target_id)
    assert not spec.has_link_to(other_id)


def test_get_related_spec_ids():
    """Test getting all related specification IDs."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )
    spec.activate()

    target1 = SpecificationId("target1")
    target2 = SpecificationId("target2")

    spec.establish_link(target1, LinkRelationship.IMPLEMENTS)
    spec.establish_link(target2, LinkRelationship.REFERENCES)

    related_ids = spec.get_related_spec_ids()

    assert target1 in related_ids
    assert target2 in related_ids
    assert len(related_ids) == 2


# ============================================================================
# TAG MANAGEMENT TESTS
# ============================================================================


def test_add_tag():
    """Test adding tag to specification."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
    )

    spec.add_tag("security")

    assert "security" in spec.tags


def test_add_tag_normalizes_to_lowercase():
    """Test that tags are normalized when added."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
    )

    spec.add_tag("Security")

    assert "security" in spec.tags
    assert "Security" not in spec.tags


def test_add_duplicate_tag_is_ignored():
    """Test that adding duplicate tag has no effect."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
    )

    spec.add_tag("security")
    spec.add_tag("security")

    assert spec.tags.count("security") == 1


def test_remove_tag():
    """Test removing tag from specification."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        tags=["security", "auth"],
    )

    spec.remove_tag("security")

    assert "security" not in spec.tags
    assert "auth" in spec.tags


def test_remove_nonexistent_tag_is_ignored():
    """Test that removing nonexistent tag has no effect."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        tags=["security"],
    )

    spec.remove_tag("nonexistent")  # Should not raise

    assert "security" in spec.tags


# ============================================================================
# CONTENT UPDATE TESTS
# ============================================================================


def test_update_content():
    """Test updating specification content."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        content="Original content",
    )

    spec.update_content("Updated content")

    assert spec.content == "Updated content"


def test_cannot_update_archived_content():
    """Test that archived specs cannot be updated."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
        content="Original",
    )
    spec.activate()
    spec.archive()

    with pytest.raises(InvalidStatusTransitionError) as exc_info:
        spec.update_content("New content")

    assert "Cannot update archived specifications" in str(exc_info.value)


def test_update_llm_summary():
    """Test updating LLM summary."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Original summary",
    )

    spec.update_llm_summary("Updated summary with more detail.")

    assert spec.llm_summary == "Updated summary with more detail."


def test_update_llm_summary_validates_length():
    """Test that LLM summary update validates length."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Original",
    )

    long_summary = " ".join(["word"] * 150)

    with pytest.raises(SpecificationValidationError) as exc_info:
        spec.update_llm_summary(long_summary)

    assert "LLM summary must be concise" in str(exc_info.value)


# ============================================================================
# TIMESTAMP TESTS
# ============================================================================


def test_create_sets_timestamps():
    """Test that creation sets created_at and updated_at."""
    before = datetime.now(timezone.utc)

    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
    )

    after = datetime.now(timezone.utc)

    assert before <= spec.created_at <= after
    assert before <= spec.updated_at <= after
    assert spec.created_at == spec.updated_at


def test_updates_modify_updated_at():
    """Test that updates modify updated_at but not created_at."""
    spec = Specification.create(
        title="Test",
        type=DocumentType.FEATURE,
        author="Alice",
        llm_summary="Test",
    )

    original_created = spec.created_at
    original_updated = spec.updated_at

    # Small delay to ensure timestamp difference
    import time
    time.sleep(0.01)

    spec.activate()

    assert spec.created_at == original_created
    assert spec.updated_at > original_updated


# ============================================================================
# DOCUMENT TYPE TESTS
# ============================================================================


def test_document_type_get_directory_path():
    """Test that document types map to correct directories."""
    assert DocumentType.FEATURE.get_directory_path() == "specs/features"
    assert DocumentType.DESIGN.get_directory_path() == "specs/design"
    assert DocumentType.TASK.get_directory_path() == "specs/tasks"
    assert DocumentType.GUIDE.get_directory_path() == "docs"
    assert DocumentType.GOVERNANCE.get_directory_path() == "specs/governance"
    assert DocumentType.SESSION.get_directory_path() == "agent-docs/sessions"
    assert DocumentType.EXECUTION.get_directory_path() == "agent-docs/execution"
    assert DocumentType.FEEDBACK.get_directory_path() == "agent-docs/feedback"
    assert DocumentType.RESEARCH.get_directory_path() == "agent-docs/research"


# ============================================================================
# REPR TESTS
# ============================================================================


def test_specification_repr():
    """Test string representation of specification."""
    spec = Specification.create(
        title="Test Feature",
        type=DocumentType.FEATURE,
        author="Alice",
    )

    repr_str = repr(spec)

    assert "Specification" in repr_str
    assert "Test Feature" in repr_str
    assert "feature" in repr_str
    assert "draft" in repr_str
