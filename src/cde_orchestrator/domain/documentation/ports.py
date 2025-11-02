"""
Documentation Domain Ports - Interface Contracts.

Ports define WHAT the domain needs from infrastructure, never HOW.
All adapters must implement these interfaces.

Key Ports:
    - ISpecificationRepository: Persistence and retrieval
    - ISemanticContext: LLM context generation
    - IDocumentationRenderer: Output formatting (Markdown, HTML, etc.)
    - ILLMSummaryGenerator: Auto-generate summaries via LLM CLI

Design for Multiple LLM Providers:
    ILLMSummaryGenerator supports headless CLI execution for:
        - Gemini (via gemini CLI)
        - Qwen (via qwen CLI)
        - GitHub Copilot (via gh copilot CLI)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator
from enum import Enum

from .entities import Specification, SpecificationId, DocumentType, DocumentStatus


# ============================================================================
# PERSISTENCE PORT
# ============================================================================


class ISpecificationRepository(ABC):
    """
    Port: Specification persistence and retrieval.

    Implementations:
        - MarkdownSpecificationRepository (Markdown files with YAML)
        - VectorDBSpecificationRepository (ChromaDB for semantic search)
        - HybridSpecificationRepository (Markdown + Vector DB)

    Responsibilities:
        - CRUD operations for specifications
        - Semantic search across specifications
        - Link resolution
        - Bulk operations for migration
    """

    @abstractmethod
    def save(self, spec: Specification) -> None:
        """
        Persist specification.

        Args:
            spec: Specification to save

        Raises:
            RepositoryError: If save fails
        """
        pass

    @abstractmethod
    def get_by_id(self, spec_id: SpecificationId) -> Optional[Specification]:
        """
        Retrieve specification by ID.

        Args:
            spec_id: Specification identifier

        Returns:
            Specification if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_title(
        self, title: str, doc_type: Optional[DocumentType] = None
    ) -> Optional[Specification]:
        """
        Find specification by title.

        Args:
            title: Specification title
            doc_type: Optional document type filter

        Returns:
            Specification if found, None otherwise
        """
        pass

    @abstractmethod
    def list_all(
        self,
        doc_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None,
        limit: Optional[int] = None,
    ) -> List[Specification]:
        """
        List specifications with optional filters.

        Args:
            doc_type: Filter by document type
            status: Filter by status
            limit: Max number of results

        Returns:
            List of specifications matching filters
        """
        pass

    @abstractmethod
    async def list_all_async(
        self,
        doc_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[Specification]:
        """
        Stream specifications asynchronously.

        Args:
            doc_type: Filter by document type
            status: Filter by status
            limit: Max number of results

        Yields:
            Specifications matching filters
        """
        pass

    @abstractmethod
    def get_related(self, spec_id: SpecificationId) -> List[Specification]:
        """
        Get all specifications linked to this one.

        Args:
            spec_id: Source specification ID

        Returns:
            List of related specifications (resolved links)
        """
        pass

    @abstractmethod
    def search_semantic(
        self, query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None
    ) -> List[Specification]:
        """
        Semantic search across specifications using vector embeddings.

        Args:
            query: Natural language query
            top_k: Number of results to return
            filters: Optional filters (type, status, tags)

        Returns:
            List of specifications ordered by relevance

        Examples:
            >>> repo.search_semantic(
            ...     "How do I add a new use case?",
            ...     top_k=5,
            ...     filters={"type": "design", "status": "active"}
            ... )
            [Specification(...), ...]
        """
        pass

    @abstractmethod
    def delete(self, spec_id: SpecificationId) -> None:
        """
        Delete specification.

        Args:
            spec_id: Specification to delete

        Raises:
            SpecificationNotFoundError: If spec doesn't exist
        """
        pass

    @abstractmethod
    def bulk_save(self, specs: List[Specification]) -> None:
        """
        Save multiple specifications efficiently.

        Used for migration operations.

        Args:
            specs: List of specifications to save
        """
        pass


# ============================================================================
# SEMANTIC CONTEXT PORT
# ============================================================================


class ISemanticContext(ABC):
    """
    Port: Generate LLM-optimized context for tasks.

    Implementations:
        - VectorDBSemanticContext (uses embeddings)
        - GraphSemanticContext (follows links)
        - HybridSemanticContext (combines both)

    Responsibilities:
        - Extract relevant specifications for task
        - Include code examples from specs
        - Extract architectural constraints
        - Format for LLM consumption
    """

    @abstractmethod
    def get_context_for_task(
        self,
        task_description: str,
        max_specs: int = 10,
        include_examples: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate context for LLM to perform task.

        Args:
            task_description: What the LLM is trying to do
            max_specs: Max number of specs to include
            include_examples: Include code examples

        Returns:
            Dict with structure:
                {
                    "summary": str,  # 2-3 sentence overview
                    "relevant_specs": [
                        {
                            "id": str,
                            "title": str,
                            "relevance": float,  # 0-1 score
                            "key_points": List[str],
                            "excerpt": str  # Relevant section
                        }
                    ],
                    "code_examples": [
                        {
                            "path": str,
                            "lines": str,  # "10-30"
                            "description": str,
                            "code": str
                        }
                    ],
                    "constraints": List[str],  # Architectural rules
                    "related_concepts": List[str]
                }

        Examples:
            >>> context.get_context_for_task(
            ...     "Implement authentication use case",
            ...     max_specs=5
            ... )
            {
                "summary": "Add use case following hexagonal pattern...",
                "relevant_specs": [...],
                "constraints": ["Domain MUST NOT import adapters", ...]
            }
        """
        pass


# ============================================================================
# RENDERER PORT
# ============================================================================


class RenderFormat(str, Enum):
    """Supported output formats."""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    LLM_CONTEXT = "llm_context"  # Optimized for LLM consumption


class IDocumentationRenderer(ABC):
    """
    Port: Render specifications in various formats.

    Implementations:
        - MarkdownRenderer (Markdown with YAML frontmatter)
        - HTMLRenderer (Static site generation)
        - LLMContextRenderer (Optimized for LLM context windows)

    Responsibilities:
        - Transform Specification entity to output format
        - Include metadata appropriately
        - Render links as appropriate for format
    """

    @abstractmethod
    def render(self, spec: Specification, format: RenderFormat) -> str:
        """
        Render specification in specified format.

        Args:
            spec: Specification to render
            format: Output format

        Returns:
            Rendered content as string

        Examples:
            >>> renderer.render(spec, RenderFormat.MARKDOWN)
            '---\\ntitle: "My Spec"\\n---\\n\\n# Content...'
        """
        pass

    @abstractmethod
    def render_with_links(
        self, spec: Specification, format: RenderFormat, depth: int = 1
    ) -> str:
        """
        Render specification with linked specifications included.

        Args:
            spec: Root specification
            format: Output format
            depth: How many levels of links to follow

        Returns:
            Rendered content including linked specs
        """
        pass


# ============================================================================
# LLM SUMMARY GENERATOR PORT
# ============================================================================


class LLMProvider(str, Enum):
    """Supported LLM providers for headless CLI execution."""

    GEMINI = "gemini"  # Google Gemini via CLI
    QWEN = "qwen"  # Alibaba Qwen via CLI
    COPILOT = "copilot"  # GitHub Copilot via gh copilot CLI
    AUTO = "auto"  # Auto-detect best available


class ILLMSummaryGenerator(ABC):
    """
    Port: Auto-generate LLM summaries via headless CLI.

    Implementations:
        - GeminiCLISummaryGenerator (gemini CLI)
        - QwenCLISummaryGenerator (qwen CLI)
        - CopilotCLISummaryGenerator (gh copilot CLI)
        - MultiProviderSummaryGenerator (fallback chain)

    Responsibilities:
        - Execute LLM CLI in headless mode
        - Generate concise 2-3 sentence summaries
        - Validate summary quality
        - Handle provider failures gracefully

    Design Decision: Use CLI Headless Mode
        - Reuses existing CLI authentication
        - No API key management in code
        - Consistent with CDE philosophy (CLI as executor)
        - Supports multiple providers with same interface
    """

    @abstractmethod
    async def generate_summary(
        self,
        spec: Specification,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """
        Generate LLM-optimized summary for specification.

        Args:
            spec: Specification to summarize
            provider: Which LLM provider to use

        Returns:
            2-3 sentence summary optimized for LLM context

        Raises:
            LLMError: If generation fails

        Examples:
            >>> generator = GeminiCLISummaryGenerator()
            >>> summary = await generator.generate_summary(spec)
            >>> len(summary.split())
            45  # Within 100-word limit
        """
        pass

    @abstractmethod
    async def generate_summary_for_content(
        self,
        content: str,
        title: str,
        doc_type: DocumentType,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """
        Generate summary for raw content (before Specification created).

        Useful during migration.

        Args:
            content: Document content
            title: Document title
            doc_type: Document type
            provider: Which LLM provider to use

        Returns:
            LLM-optimized summary
        """
        pass

    @abstractmethod
    def is_provider_available(self, provider: LLMProvider) -> bool:
        """
        Check if LLM provider CLI is available.

        Args:
            provider: Provider to check

        Returns:
            True if CLI is installed and authenticated

        Examples:
            >>> generator.is_provider_available(LLMProvider.GEMINI)
            True
            >>> generator.is_provider_available(LLMProvider.QWEN)
            False  # Not installed
        """
        pass

    @abstractmethod
    def get_available_providers(self) -> List[LLMProvider]:
        """
        Get list of available LLM providers.

        Returns:
            List of providers with working CLI

        Examples:
            >>> generator.get_available_providers()
            [LLMProvider.GEMINI, LLMProvider.COPILOT]
        """
        pass
