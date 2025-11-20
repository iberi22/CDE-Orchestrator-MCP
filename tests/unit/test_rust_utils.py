"""
Tests for Rust-accelerated documentation scanning utilities.

Tests cover:
- Data class initialization and conversion
- RustDocumentationScanner behavior with and without Rust core
- Fallback mechanisms when Rust is unavailable
- Error handling for invalid inputs
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from cde_orchestrator.rust_utils import (
    RUST_AVAILABLE,
    Document,
    LinkInfo,
    QualityReport,
    RustDocumentationScanner,
    YamlFrontmatter,
)


class TestYamlFrontmatter:
    """Test YamlFrontmatter data class."""

    def test_from_dict_with_all_fields(self):
        """Test creating YamlFrontmatter from complete dict."""
        data = {
            "title": "Test Doc",
            "description": "A test document",
            "type": "feature",
            "status": "active",
            "created": "2025-01-01",
            "updated": "2025-01-02",
            "author": "Test Author",
            "llm_summary": "Brief summary",
            "extra": {"custom": "field"},
        }

        frontmatter = YamlFrontmatter.from_dict(data)

        assert frontmatter.title == "Test Doc"
        assert frontmatter.description == "A test document"
        assert frontmatter.doc_type == "feature"
        assert frontmatter.status == "active"
        assert frontmatter.created == "2025-01-01"
        assert frontmatter.updated == "2025-01-02"
        assert frontmatter.author == "Test Author"
        assert frontmatter.llm_summary == "Brief summary"
        assert frontmatter.extra == {"custom": "field"}

    def test_from_dict_with_partial_fields(self):
        """Test creating YamlFrontmatter with only some fields."""
        data = {
            "title": "Partial Doc",
            "type": "design",
        }

        frontmatter = YamlFrontmatter.from_dict(data)

        assert frontmatter.title == "Partial Doc"
        assert frontmatter.doc_type == "design"
        assert frontmatter.description is None
        assert frontmatter.status is None
        assert frontmatter.extra == {}

    def test_from_dict_with_none_returns_none(self):
        """Test that None input returns None."""
        assert YamlFrontmatter.from_dict(None) is None

    def test_from_dict_with_empty_dict_returns_none(self):
        """Test that empty dict returns None (falsy check)."""
        frontmatter = YamlFrontmatter.from_dict({})

        # Empty dict is treated as falsy, returns None
        assert frontmatter is None

    def test_direct_initialization(self):
        """Test direct initialization of YamlFrontmatter."""
        frontmatter = YamlFrontmatter(
            title="Direct Title",
            description="Direct description",
            doc_type="task",
            status="draft",
        )

        assert frontmatter.title == "Direct Title"
        assert frontmatter.description == "Direct description"
        assert frontmatter.doc_type == "task"
        assert frontmatter.status == "draft"


class TestLinkInfo:
    """Test LinkInfo data class."""

    def test_initialization(self):
        """Test LinkInfo initialization."""
        link = LinkInfo(text="Example", url="https://example.com", is_internal=False)

        assert link.text == "Example"
        assert link.url == "https://example.com"
        assert link.is_internal is False

    def test_internal_link(self):
        """Test LinkInfo with internal link."""
        link = LinkInfo(text="Internal", url="/docs/page.md", is_internal=True)

        assert link.text == "Internal"
        assert link.url == "/docs/page.md"
        assert link.is_internal is True


class TestDocument:
    """Test Document data class."""

    def test_from_dict_with_metadata(self):
        """Test creating Document from dict with metadata."""
        data = {
            "path": "/docs/test.md",
            "content": "# Test\n\nContent here",
            "word_count": 100,
            "has_frontmatter": True,
            "metadata": {
                "title": "Test Doc",
                "type": "feature",
            },
            "links": [
                {"text": "Link1", "url": "http://example.com", "is_internal": False},
                {"text": "Link2", "url": "/internal.md", "is_internal": True},
            ],
            "headers": ["Test", "Section 1", "Section 2"],
        }

        doc = Document.from_dict(data)

        assert doc.path == "/docs/test.md"
        assert doc.content == "# Test\n\nContent here"
        assert doc.word_count == 100
        assert doc.has_frontmatter is True
        assert doc.metadata is not None
        assert doc.metadata.title == "Test Doc"
        assert doc.metadata.doc_type == "feature"
        assert len(doc.links) == 2
        assert doc.links[0].text == "Link1"
        assert doc.links[0].is_internal is False
        assert doc.links[1].is_internal is True
        assert doc.headers == ["Test", "Section 1", "Section 2"]

    def test_from_dict_without_metadata(self):
        """Test creating Document from dict without metadata."""
        data = {
            "path": "/docs/simple.md",
            "content": "Simple content",
            "word_count": 50,
            "has_frontmatter": False,
            "metadata": None,
            "links": [],
            "headers": ["Title"],
        }

        doc = Document.from_dict(data)

        assert doc.path == "/docs/simple.md"
        assert doc.has_frontmatter is False
        assert doc.metadata is None
        assert len(doc.links) == 0
        assert doc.headers == ["Title"]

    def test_from_dict_empty_lists(self):
        """Test Document with empty links and headers."""
        data = {
            "path": "/docs/empty.md",
            "content": "",
            "word_count": 0,
            "has_frontmatter": False,
            "metadata": None,
            "links": [],
            "headers": [],
        }

        doc = Document.from_dict(data)

        assert doc.path == "/docs/empty.md"
        assert doc.word_count == 0
        assert len(doc.links) == 0
        assert len(doc.headers) == 0


class TestQualityReport:
    """Test QualityReport data class."""

    def test_from_dict_complete(self):
        """Test creating QualityReport from complete dict."""
        data = {
            "quality_score": 85.5,
            "total_docs": 100,
            "docs_with_metadata": 90,
            "docs_without_metadata": 10,
            "total_links": 250,
            "broken_internal_links": ["/docs/missing1.md", "/docs/missing2.md"],
            "orphaned_docs": ["/docs/orphan.md"],
            "large_files": ["/docs/huge.md"],
            "issues": ["Missing metadata in 10 files", "2 broken links"],
            "recommendations": ["Add metadata", "Fix links"],
        }

        report = QualityReport.from_dict(data)

        assert report.quality_score == 85.5
        assert report.total_docs == 100
        assert report.docs_with_metadata == 90
        assert report.docs_without_metadata == 10
        assert report.total_links == 250
        assert len(report.broken_internal_links) == 2
        assert "/docs/missing1.md" in report.broken_internal_links
        assert len(report.orphaned_docs) == 1
        assert len(report.large_files) == 1
        assert len(report.issues) == 2
        assert len(report.recommendations) == 2

    def test_from_dict_empty_lists(self):
        """Test QualityReport with empty issue lists."""
        data = {
            "quality_score": 100.0,
            "total_docs": 50,
            "docs_with_metadata": 50,
            "docs_without_metadata": 0,
            "total_links": 100,
            "broken_internal_links": [],
            "orphaned_docs": [],
            "large_files": [],
            "issues": [],
            "recommendations": [],
        }

        report = QualityReport.from_dict(data)

        assert report.quality_score == 100.0
        assert report.total_docs == 50
        assert len(report.broken_internal_links) == 0
        assert len(report.orphaned_docs) == 0
        assert len(report.large_files) == 0
        assert len(report.issues) == 0
        assert len(report.recommendations) == 0


class TestRustDocumentationScanner:
    """Test RustDocumentationScanner with mocked Rust core."""

    def test_initialization(self):
        """Test scanner initialization."""
        scanner = RustDocumentationScanner()
        assert scanner.is_available == RUST_AVAILABLE

    @pytest.mark.skipif(not RUST_AVAILABLE, reason="Rust core not available")
    @patch("cde_orchestrator.rust_utils.cde_rust_core")
    def test_scan_documentation_success(self, mock_rust):
        """Test successful documentation scanning with Rust core."""
        mock_docs = [
            {
                "path": "/test.md",
                "content": "# Test",
                "word_count": 10,
                "has_frontmatter": False,
                "metadata": None,
                "links": [],
                "headers": ["Test"],
            }
        ]
        mock_rust.scan_documentation_py.return_value = json.dumps(mock_docs)

        scanner = RustDocumentationScanner()
        scanner.is_available = True

        docs = scanner.scan_documentation("./docs")

        assert isinstance(docs, list)
        assert len(docs) == 1
        assert docs[0].path == "/test.md"

    @patch("cde_orchestrator.rust_utils.RUST_AVAILABLE", False)
    def test_scan_documentation_raises_when_rust_unavailable(self):
        """Test that scanning raises RuntimeError when Rust is unavailable."""
        scanner = RustDocumentationScanner()
        scanner.is_available = False

        with pytest.raises(RuntimeError, match="Rust core not available"):
            scanner.scan_documentation("./docs")

    @pytest.mark.skipif(not RUST_AVAILABLE, reason="Rust core not available")
    @patch("cde_orchestrator.rust_utils.cde_rust_core")
    def test_scan_documentation_converts_path_to_string(self, mock_rust):
        """Test that Path objects are converted to strings."""
        mock_rust.scan_documentation_py.return_value = "[]"

        scanner = RustDocumentationScanner()
        scanner.is_available = True

        scanner.scan_documentation(Path("./docs"))

        # Verify string path was passed to Rust
        call_args = mock_rust.scan_documentation_py.call_args[0]
        assert isinstance(call_args[0], str)

    @pytest.mark.skipif(not RUST_AVAILABLE, reason="Rust core not available")
    @patch("cde_orchestrator.rust_utils.cde_rust_core")
    def test_scan_documentation_handles_rust_exceptions(self, mock_rust):
        """Test error handling when Rust core raises exception."""
        mock_rust.scan_documentation_py.side_effect = Exception("Rust error")

        scanner = RustDocumentationScanner()
        scanner.is_available = True

        with pytest.raises(ValueError, match="Failed to scan documentation"):
            scanner.scan_documentation("./docs")

    @pytest.mark.skipif(not RUST_AVAILABLE, reason="Rust core not available")
    def test_analyze_quality_raises_when_rust_unavailable(self):
        """Test that quality analysis raises RuntimeError when Rust unavailable."""
        scanner = RustDocumentationScanner()
        scanner.is_available = False

        with pytest.raises(RuntimeError, match="Rust core not available"):
            scanner.analyze_quality(".")

    @pytest.mark.skipif(not RUST_AVAILABLE, reason="Rust core not available")
    @patch("cde_orchestrator.rust_utils.cde_rust_core")
    def test_analyze_quality_converts_path_to_string(self, mock_rust):
        """Test that Path objects are converted to strings in analyze_quality."""
        mock_quality_data = {
            "quality_score": 75.0,
            "total_docs": 10,
            "docs_with_metadata": 8,
            "docs_without_metadata": 2,
            "total_links": 50,
            "broken_internal_links": [],
            "orphaned_docs": [],
            "large_files": [],
            "issues": [],
            "recommendations": [],
        }
        mock_rust.analyze_documentation_quality_py.return_value = json.dumps(
            mock_quality_data
        )

        scanner = RustDocumentationScanner()
        scanner.is_available = True

        scanner.analyze_quality(Path("."))

        # Verify string path was passed
        call_args = mock_rust.analyze_documentation_quality_py.call_args[0]
        assert isinstance(call_args[0], str)

    @pytest.mark.skipif(not RUST_AVAILABLE, reason="Rust core not available")
    @patch("cde_orchestrator.rust_utils.cde_rust_core")
    def test_analyze_quality_handles_rust_exceptions(self, mock_rust):
        """Test error handling in analyze_quality when Rust raises exception."""
        mock_rust.analyze_documentation_quality_py.side_effect = Exception("Rust error")

        scanner = RustDocumentationScanner()
        scanner.is_available = True

        with pytest.raises(ValueError, match="Failed to analyze quality"):
            scanner.analyze_quality(".")

    @pytest.mark.skipif(not RUST_AVAILABLE, reason="Rust core not available")
    @patch("cde_orchestrator.rust_utils.cde_rust_core")
    def test_scan_documentation_returns_document_list(self, mock_rust):
        """Test that scan_documentation returns list of Documents."""
        mock_docs = [
            {
                "path": "/test.md",
                "content": "# Test",
                "word_count": 10,
                "has_frontmatter": False,
                "metadata": None,
                "links": [],
                "headers": ["Test"],
            }
        ]
        mock_rust.scan_documentation_py.return_value = json.dumps(mock_docs)

        scanner = RustDocumentationScanner()
        scanner.is_available = True

        docs = scanner.scan_documentation("./docs")

        assert isinstance(docs, list)
        assert len(docs) == 1
        assert isinstance(docs[0], Document)
        assert docs[0].path == "/test.md"
        assert docs[0].word_count == 10

    @pytest.mark.skipif(not RUST_AVAILABLE, reason="Rust core not available")
    @patch("cde_orchestrator.rust_utils.cde_rust_core")
    def test_analyze_quality_returns_quality_report(self, mock_rust):
        """Test that analyze_quality returns QualityReport."""
        mock_report = {
            "quality_score": 90.0,
            "total_docs": 100,
            "docs_with_metadata": 95,
            "docs_without_metadata": 5,
            "total_links": 200,
            "broken_internal_links": [],
            "orphaned_docs": [],
            "large_files": [],
            "issues": [],
            "recommendations": [],
        }
        mock_rust.analyze_documentation_quality_py.return_value = json.dumps(
            mock_report
        )

        scanner = RustDocumentationScanner()
        scanner.is_available = True

        report = scanner.analyze_quality(".")

        assert isinstance(report, QualityReport)
        assert report.quality_score == 90.0
        assert report.total_docs == 100
        assert report.docs_with_metadata == 95


class TestRustAvailability:
    """Test behavior based on Rust availability."""

    def test_rust_available_constant(self):
        """Test that RUST_AVAILABLE is a boolean."""
        assert isinstance(RUST_AVAILABLE, bool)

    @patch("cde_orchestrator.rust_utils.RUST_AVAILABLE", True)
    def test_scanner_reports_available_when_rust_present(self):
        """Test scanner.is_available when Rust is present."""
        with patch("cde_orchestrator.rust_utils.RUST_AVAILABLE", True):
            scanner = RustDocumentationScanner()
            scanner.is_available = True
            assert scanner.is_available is True

    @patch("cde_orchestrator.rust_utils.RUST_AVAILABLE", False)
    def test_scanner_reports_unavailable_when_rust_missing(self):
        """Test scanner.is_available when Rust is missing."""
        with patch("cde_orchestrator.rust_utils.RUST_AVAILABLE", False):
            scanner = RustDocumentationScanner()
            scanner.is_available = False
            assert scanner.is_available is False
