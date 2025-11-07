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
    DocumentStatus,
    DocumentType,
    LinkRelationship,
    SemanticLink,
    Specification,
    SpecificationId,
)
from .exceptions import (
    InvalidLinkError,
    InvalidStatusTransitionError,
    SpecificationError,
    SpecificationNotFoundError,
    SpecificationValidationError,
)
from .ports import (
    IDocumentationRenderer,
    ILLMSummaryGenerator,
    ISemanticContext,
    ISpecificationRepository,
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
