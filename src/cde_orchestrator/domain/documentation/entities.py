"""
Documentation Domain Entities.

Core business objects representing documentation specifications.
These entities contain ONLY business logic - no infrastructure dependencies.

Key Entities:
    - Specification: Core documentation entity with lifecycle
    - SemanticLink: Relationship between specifications
    - DocumentType: Classification of documents
    - DocumentStatus: Lifecycle state

Design Principles:
    - Rich domain models (behavior, not just data)
    - Immutable value objects where possible
    - Self-validating entities
    - LLM-first metadata
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, NewType, Optional

from .exceptions import (
    InvalidLinkError,
    InvalidStatusTransitionError,
    SpecificationValidationError,
)

# Type aliases for clarity
SpecificationId = NewType("SpecificationId", str)


class DocumentType(str, Enum):
    """
    Classification of documentation types.

    Maps to Spec-Kit structure:
        - FEATURE: specs/features/
        - DESIGN: specs/design/
        - TASK: specs/tasks/
        - GUIDE: docs/
        - GOVERNANCE: specs/governance/
        - SESSION: agent-docs/sessions/
        - EXECUTION: agent-docs/execution/
        - FEEDBACK: agent-docs/feedback/
        - RESEARCH: agent-docs/research/
    """

    FEATURE = "feature"
    DESIGN = "design"
    TASK = "task"
    GUIDE = "guide"
    GOVERNANCE = "governance"
    SESSION = "session"
    EXECUTION = "execution"
    FEEDBACK = "feedback"
    RESEARCH = "research"

    def get_directory_path(self) -> str:
        """Get standard directory path for this document type."""
        mapping = {
            DocumentType.FEATURE: "specs/features",
            DocumentType.DESIGN: "specs/design",
            DocumentType.TASK: "specs/tasks",
            DocumentType.GUIDE: "docs",
            DocumentType.GOVERNANCE: "specs/governance",
            DocumentType.SESSION: "agent-docs/sessions",
            DocumentType.EXECUTION: "agent-docs/execution",
            DocumentType.FEEDBACK: "agent-docs/feedback",
            DocumentType.RESEARCH: "agent-docs/research",
        }
        return mapping[self]


class DocumentStatus(str, Enum):
    """
    Lifecycle status of specification.

    State Machine:
        DRAFT → ACTIVE → DEPRECATED → ARCHIVED
                  ↓
                ACTIVE (can return from deprecated)

    Business Rules:
        - DRAFT: Can be edited freely, not indexed
        - ACTIVE: Published, indexed, linked
        - DEPRECATED: Marked obsolete, show warnings
        - ARCHIVED: No longer used, preserved for history
    """

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

    def can_transition_to(self, target: "DocumentStatus") -> bool:
        """Validate if transition to target status is allowed."""
        allowed_transitions = {
            DocumentStatus.DRAFT: [DocumentStatus.ACTIVE],
            DocumentStatus.ACTIVE: [
                DocumentStatus.DEPRECATED,
                DocumentStatus.ARCHIVED,
            ],
            DocumentStatus.DEPRECATED: [
                DocumentStatus.ACTIVE,
                DocumentStatus.ARCHIVED,
            ],
            DocumentStatus.ARCHIVED: [],  # Terminal state
        }
        return target in allowed_transitions.get(self, [])


class LinkRelationship(str, Enum):
    """
    Semantic relationships between specifications.

    Used for:
        - Dependency tracking
        - Navigation
        - Impact analysis
        - LLM context building
    """

    REFERENCES = "references"  # General reference
    IMPLEMENTS = "implements"  # Implements design/spec
    SUPERSEDES = "supersedes"  # Replaces older doc
    DEPENDS_ON = "depends_on"  # Requires other spec
    RELATED_TO = "related_to"  # Loosely related
    CONTRADICTS = "contradicts"  # Conflicting specs (flag)
    EXTENDS = "extends"  # Builds upon


@dataclass(frozen=True)
class SemanticLink:
    """
    Immutable value object representing a semantic link between specifications.

    Attributes:
        target_id: ID of target specification
        relationship: Type of relationship
        created_at: When link was established
        metadata: Additional context (e.g., line numbers, quote)
    """

    target_id: SpecificationId
    relationship: LinkRelationship
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate link on creation."""
        if not self.target_id:
            raise InvalidLinkError("", str(self.target_id), "Target ID cannot be empty")


@dataclass
class Specification:
    """
    Core domain entity representing a documentation specification.

    This is a RICH domain model with business logic, not just a data bag.

    Business Rules:
        - Title must be unique within document type
        - Cannot link archived specifications
        - Status transitions follow state machine
        - LLM summary required for active specs
        - Tags normalized to lowercase

    Attributes:
        id: Unique identifier (UUID)
        title: Human-readable title (unique per type)
        type: Document classification
        status: Lifecycle status
        content: Domain content (NOT markdown - that's adapter concern)
        author: Original author
        created_at: Creation timestamp
        updated_at: Last modification timestamp
        tags: Categorization tags (lowercase)
        links: Semantic links to other specifications
        llm_summary: 2-3 sentence AI-optimized summary
        metadata: Extensible metadata dict
    """

    id: SpecificationId
    title: str
    type: DocumentType
    status: DocumentStatus
    content: str
    author: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = field(default_factory=list)
    links: List[SemanticLink] = field(default_factory=list)
    llm_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        title: str,
        type: DocumentType,
        author: str,
        content: str = "",
        tags: Optional[List[str]] = None,
        llm_summary: Optional[str] = None,
    ) -> "Specification":
        """
        Factory method to create new specification in DRAFT status.

        Args:
            title: Specification title (must be unique per type)
            type: Document type
            author: Author name
            content: Initial content
            tags: Optional categorization tags
            llm_summary: Optional LLM summary

        Returns:
            New Specification instance

        Raises:
            SpecificationValidationError: If validation fails

        Examples:
            >>> spec = Specification.create(
            ...     title="Authentication System",
            ...     type=DocumentType.FEATURE,
            ...     author="Alice"
            ... )
            >>> spec.status
            <DocumentStatus.DRAFT: 'draft'>
        """
        # Validation
        if not title or len(title) < 3:
            raise SpecificationValidationError(
                "title", title, "Title must be at least 3 characters"
            )

        if llm_summary and len(llm_summary.split()) > 100:
            raise SpecificationValidationError(
                "llm_summary",
                llm_summary[:50] + "...",
                "LLM summary must be concise (< 100 words)",
            )

        now = datetime.now(timezone.utc)
        spec_id = SpecificationId(str(uuid.uuid4()))

        # Normalize tags
        normalized_tags = [tag.lower().strip() for tag in (tags or [])]

        return cls(
            id=spec_id,
            title=title,
            type=type,
            status=DocumentStatus.DRAFT,
            content=content,
            author=author,
            created_at=now,
            updated_at=now,
            tags=normalized_tags,
            links=[],
            llm_summary=llm_summary,
            metadata={},
        )

    def activate(self) -> None:
        """
        Transition specification to ACTIVE status.

        Makes specification publicly available, indexed, and linkable.

        Raises:
            InvalidStatusTransitionError: If current status doesn't allow activation
            SpecificationValidationError: If required fields missing
        """
        if not self.status.can_transition_to(DocumentStatus.ACTIVE):
            raise InvalidStatusTransitionError(
                self.status.value,
                DocumentStatus.ACTIVE.value,
                "Can only activate from DRAFT or DEPRECATED status",
            )

        # Business rule: Active specs must have LLM summary
        if not self.llm_summary:
            raise SpecificationValidationError(
                "llm_summary",
                "",
                "Active specifications must have LLM summary for discoverability",
            )

        self.status = DocumentStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)

    def deprecate(
        self, reason: str, successor_id: Optional[SpecificationId] = None
    ) -> None:
        """
        Mark specification as deprecated.

        Args:
            reason: Why this spec is deprecated
            successor_id: ID of specification that supersedes this one

        Raises:
            InvalidStatusTransitionError: If transition not allowed
        """
        if not self.status.can_transition_to(DocumentStatus.DEPRECATED):
            raise InvalidStatusTransitionError(
                self.status.value,
                DocumentStatus.DEPRECATED.value,
                "Can only deprecate ACTIVE specifications",
            )

        self.status = DocumentStatus.DEPRECATED
        self.updated_at = datetime.now(timezone.utc)
        self.metadata["deprecation_reason"] = reason
        if successor_id:
            self.metadata["successor_id"] = successor_id

    def archive(self) -> None:
        """
        Archive specification (terminal state).

        Archived specs preserved for history but no longer active.

        Raises:
            InvalidStatusTransitionError: If transition not allowed
        """
        if not self.status.can_transition_to(DocumentStatus.ARCHIVED):
            raise InvalidStatusTransitionError(
                self.status.value,
                DocumentStatus.ARCHIVED.value,
                "Can only archive ACTIVE or DEPRECATED specifications",
            )

        self.status = DocumentStatus.ARCHIVED
        self.updated_at = datetime.now(timezone.utc)

    def establish_link(
        self,
        target_id: SpecificationId,
        relationship: LinkRelationship,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Create semantic link to another specification.

        Args:
            target_id: Target specification ID
            relationship: Type of relationship
            metadata: Optional link metadata

        Raises:
            InvalidLinkError: If link violates business rules

        Examples:
            >>> spec.establish_link(
            ...     target_id=SpecificationId("other-spec"),
            ...     relationship=LinkRelationship.IMPLEMENTS
            ... )
        """
        # Business rule: Cannot link archived specs
        if self.status == DocumentStatus.ARCHIVED:
            raise InvalidLinkError(
                str(self.id),
                str(target_id),
                "Cannot link archived specifications",
            )

        # Business rule: Prevent duplicate links
        if any(
            link.target_id == target_id and link.relationship == relationship
            for link in self.links
        ):
            raise InvalidLinkError(
                str(self.id),
                str(target_id),
                f"Link with relationship '{relationship.value}' already exists",
            )

        link = SemanticLink(
            target_id=target_id,
            relationship=relationship,
            metadata=metadata or {},
        )
        self.links.append(link)
        self.updated_at = datetime.now(timezone.utc)

    def add_tag(self, tag: str) -> None:
        """
        Add categorization tag.

        Tags normalized to lowercase.

        Args:
            tag: Tag to add
        """
        normalized = tag.lower().strip()
        if normalized and normalized not in self.tags:
            self.tags.append(normalized)
            self.updated_at = datetime.now(timezone.utc)

    def remove_tag(self, tag: str) -> None:
        """Remove tag if exists."""
        normalized = tag.lower().strip()
        if normalized in self.tags:
            self.tags.remove(normalized)
            self.updated_at = datetime.now(timezone.utc)

    def update_content(self, content: str) -> None:
        """
        Update specification content.

        Args:
            content: New content

        Raises:
            InvalidStatusTransitionError: If specification is archived
        """
        if self.status == DocumentStatus.ARCHIVED:
            raise InvalidStatusTransitionError(
                self.status.value,
                "",
                "Cannot update archived specifications",
            )

        self.content = content
        self.updated_at = datetime.now(timezone.utc)

    def update_llm_summary(self, summary: str) -> None:
        """
        Update LLM-optimized summary.

        Args:
            summary: New summary (2-3 sentences, < 100 words)

        Raises:
            SpecificationValidationError: If summary too long
        """
        if len(summary.split()) > 100:
            raise SpecificationValidationError(
                "llm_summary",
                summary[:50] + "...",
                "LLM summary must be concise (< 100 words)",
            )

        self.llm_summary = summary
        self.updated_at = datetime.now(timezone.utc)

    def get_related_spec_ids(self) -> List[SpecificationId]:
        """Get IDs of all linked specifications."""
        return [link.target_id for link in self.links]

    def has_link_to(self, target_id: SpecificationId) -> bool:
        """Check if link exists to target specification."""
        return any(link.target_id == target_id for link in self.links)

    def __repr__(self) -> str:
        return (
            f"Specification(id={self.id}, title='{self.title}', "
            f"type={self.type.value}, status={self.status.value})"
        )
