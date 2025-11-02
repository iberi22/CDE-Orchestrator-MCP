"""
Documentation Domain Module.

Treats documentation as a first-class domain concern with:
- Specifications as domain entities
- Business rules for linking, deprecation, status transitions
- Semantic relationships between documents
- LLM-first metadata and context

This module follows hexagonal architecture:
- Entities: Core business objects (Specification, SemanticLink)
- Ports: Interfaces for adapters (ISpecificationRepository, etc.)
- Exceptions: Domain-specific errors

NO infrastructure dependencies - pure business logic only.
"""

from .entities import (
    Specification,
    SpecificationId,
    DocumentType,
    DocumentStatus,
    SemanticLink,
    LinkRelationship,
)

from .ports import (
    ISpecificationRepository,
    ISemanticContext,
    IDocumentationRenderer,
    ILLMSummaryGenerator,
)

from .exceptions import (
    SpecificationError,
    SpecificationNotFoundError,
    InvalidStatusTransitionError,
    InvalidLinkError,
    SpecificationValidationError,
)

__all__ = [
    # Entities
    "Specification",
    "SpecificationId",
    "DocumentType",
    "DocumentStatus",
    "SemanticLink",
    "LinkRelationship",
    # Ports
    "ISpecificationRepository",
    "ISemanticContext",
    "IDocumentationRenderer",
    "ILLMSummaryGenerator",
    # Exceptions
    "SpecificationError",
    "SpecificationNotFoundError",
    "InvalidStatusTransitionError",
    "InvalidLinkError",
    "SpecificationValidationError",
]
