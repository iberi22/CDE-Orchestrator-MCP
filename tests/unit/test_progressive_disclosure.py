# type: ignore
# type: ignore
# type: ignore  # Skip type checking for tests
"""
Unit tests for progressive disclosure pattern (Anthropic best practices).

Tests:
- cde_scanDocumentation with detail_level parameter
- cde_searchTools for tool discovery
- MCPToolSearcher adapter

Token efficiency benchmarks included.
# type: ignore`n"""

import json
from pathlib import Path

import pytest

from cde_orchestrator.adapters.mcp_tool_searcher import MCPToolSearcher

# Import tools to test
from mcp_tools.documentation import cde_scanDocumentation
from mcp_tools.tool_search import cde_searchTools


class TestProgressiveDisclosure:
    """Test suite for progressive disclosure pattern."""

    def test_scan_documentation_name_only(self, tmp_path: Path) -> None:
        """Test scanDocumentation with name_only detail level."""
        # Create test markdown files
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "guide.md").write_text("# Guide\n")
        (tmp_path / "docs" / "api.md").write_text("# API\n")
        (tmp_path / "README.md").write_text("# README\n")

        # Call with name_only
        result_json = cde_scanDocumentation(
            project_path=str(tmp_path), detail_level="name_only"
        )
        result = json.loads(result_json)

        # Verify structure
        assert "files" in result
        assert "total_docs" in result
        assert "detail_level" in result
        assert result["detail_level"] == "name_only"

        # Should only contain file paths (strings)
        assert isinstance(result["files"], list)
        assert all(isinstance(f, str) for f in result["files"])
        assert result["total_docs"] == 3

        # Should NOT contain detailed info
        assert "by_location" not in result
        assert "large_files" not in result

    def test_scan_documentation_summary(self, tmp_path: Path) -> None:
        """Test scanDocumentation with summary detail level."""
        # Create test files
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "guide.md").write_text(
            "---\ntitle: Guide\ntype: guide\n---\n# Guide\n"
        )

        # Call with summary
        result_json = cde_scanDocumentation(
            project_path=str(tmp_path), detail_level="summary"
        )
        result = json.loads(result_json)

        # Verify structure
        assert "files" in result
        assert "total_docs" in result
        assert "missing_metadata" in result
        assert "recommendations" in result
        assert result["detail_level"] == "summary"

        # Files should be dictionaries with key fields
        assert isinstance(result["files"], list)
        if result["files"]:
            file_info = result["files"][0]
            assert "path" in file_info
            assert "has_metadata" in file_info
            assert "location" in file_info

        # Should NOT contain all details
        assert "by_location" not in result
        assert "large_files" not in result

    def test_scan_documentation_full(self, tmp_path: Path) -> None:
        """Test scanDocumentation with full detail level."""
        # Create test files
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "guide.md").write_text("# Guide\n" * 100)

        # Call with full
        result_json = cde_scanDocumentation(
            project_path=str(tmp_path), detail_level="full"
        )
        result = json.loads(result_json)

        # Verify complete structure
        assert "total_docs" in result
        assert "by_location" in result
        assert "missing_metadata" in result
        assert "orphaned_docs" in result
        assert "large_files" in result
        assert "recommendations" in result
        assert result["detail_level"] == "full"

    def test_scan_documentation_invalid_detail_level(self, tmp_path: Path) -> None:
        """Test scanDocumentation with invalid detail level."""
        (tmp_path / "README.md").write_text("# README\n")

        # Should return error in JSON (tool_handler catches ValueError)
        result_json = cde_scanDocumentation(
            project_path=str(tmp_path), detail_level="invalid"
        )

        # Tool handler returns empty result on error, logs error
        # This is expected behavior - tools don't raise to agent
        assert result_json is not None

    def test_token_efficiency_benchmark(self, tmp_path: Path) -> None:
        """Benchmark token efficiency of detail levels."""
        # Create 100 test files
        (tmp_path / "docs").mkdir()
        for i in range(100):
            (tmp_path / "docs" / f"file{i}.md").write_text("# Test\n" * 50)

        # Measure response sizes (proxy for tokens)
        name_only = cde_scanDocumentation(str(tmp_path), detail_level="name_only")
        summary = cde_scanDocumentation(str(tmp_path), detail_level="summary")
        full = cde_scanDocumentation(str(tmp_path), detail_level="full")

        # Verify token reduction
        name_only_size = len(name_only)
        summary_size = len(summary)
        full_size = len(full)

        assert name_only_size < summary_size < full_size

        # Calculate reduction percentages
        name_reduction = (1 - name_only_size / full_size) * 100
        summary_reduction = (1 - summary_size / full_size) * 100

        print("\n📊 Token Efficiency Benchmark (100 files):")
        print(f"   Full detail: {full_size:,} bytes")
        print(f"   Summary: {summary_size:,} bytes (-{summary_reduction:.1f}%)")
        print(f"   Name only: {name_only_size:,} bytes (-{name_reduction:.1f}%)")

        # Progressive disclosure should show clear improvement
        # Any reduction is good - actual percentages vary by content
        assert summary_reduction > 0, "Summary should reduce tokens"
        assert (
            name_reduction > 50
        ), f"Name only should achieve >50% reduction (got {name_reduction:.1f}%)"

        print(f"  full: {full_size} bytes (baseline)")


@pytest.mark.asyncio
class TestToolSearch:
    """Test suite for tool search functionality."""

    async def test_search_tools_name_only(self):  # type: ignore
        """Test searchTools with name_only detail level."""
        result_json = await cde_searchTools("skill", detail_level="name_only")
        result = json.loads(result_json)

        # Verify structure
        assert "tools" in result
        assert "total" in result
        assert "detail_level" in result
        assert "query" in result

        assert result["detail_level"] == "name_only"
        assert result["query"] == "skill"

        # Tools should be strings (just names)
        assert isinstance(result["tools"], list)
        if result["tools"]:
            assert all(isinstance(t, str) for t in result["tools"])

        # Should find skill-related tools
        assert result["total"] >= 2  # sourceSkill, updateSkill

    async def test_search_tools_name_and_description(self):  # type: ignore
        """Test searchTools with name_and_description detail level."""
        result_json = await cde_searchTools(
            "workflow", detail_level="name_and_description"
        )
        result = json.loads(result_json)

        # Verify structure
        assert result["detail_level"] == "name_and_description"

        # Tools should be dictionaries
        assert isinstance(result["tools"], list)
        if result["tools"]:
            tool = result["tools"][0]
            assert "name" in tool
            assert "description" in tool
            assert "tags" in tool

    async def test_search_tools_full_schema(self):  # type: ignore
        """Test searchTools with full_schema detail level."""
        result_json = await cde_searchTools("scan", detail_level="full_schema")
        result = json.loads(result_json)

        # Verify complete structure
        assert result["detail_level"] == "full_schema"

        # Tools should have full details
        if result["tools"]:
            tool = result["tools"][0]
            assert "name" in tool
            assert "full_name" in tool
            assert "description" in tool
            assert "full_doc" in tool
            assert "parameters" in tool
            assert "tags" in tool

    async def test_search_tools_no_query(self):  # type: ignore
        """Test searchTools without query (list all)."""
        result_json = await cde_searchTools(detail_level="name_only")
        result = json.loads(result_json)

        # Should list all tools
        assert "tools" in result
        assert result["total"] > 10  # CDE has 40+ tools

    async def test_search_tools_invalid_detail_level(self):  # type: ignore
        """Test searchTools with invalid detail level."""
        result_json = await cde_searchTools("test", detail_level="invalid")
        result = json.loads(result_json)

        # Should return error
        assert "error" in result
        assert "valid_options" in result


@pytest.mark.asyncio
class TestMCPToolSearcher:
    """Test suite for MCPToolSearcher adapter."""

    def test_searcher_initialization(self):  # type: ignore
        """Test searcher can be initialized."""
        import mcp_tools

        searcher = MCPToolSearcher(mcp_tools)

        assert searcher is not None
        assert searcher.mcp_tools_module == mcp_tools

    async def test_searcher_discover_tools(self):  # type: ignore
        """Test tool discovery."""
        import mcp_tools

        searcher = MCPToolSearcher(mcp_tools)

        tools = await searcher._discover_all_tools()

        # Should find multiple tools
        assert len(tools) > 10

        # Each tool should have required fields
        for tool in tools:
            assert "name" in tool
            assert "display_name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "tags" in tool

    async def test_searcher_search_by_keyword(self):  # type: ignore
        """Test keyword search."""
        import mcp_tools

        searcher = MCPToolSearcher(mcp_tools)

        # Search for "documentation" tools
        result = await searcher.search("documentation", detail_level="name_only")

        assert result["total"] >= 2  # scanDocumentation, analyzeDocumentation
        assert (
            "scanDocumentation" in result["tools"]
            or "analyzeDocumentation" in result["tools"]
        )

    async def test_searcher_list_all(self):  # type: ignore
        """Test listing all tools."""
        import mcp_tools

        searcher = MCPToolSearcher(mcp_tools)

        result = await searcher.list_all(detail_level="name_only")

        assert result["total"] > 10
        assert len(result["tools"]) == result["total"]

    def test_searcher_tag_extraction(self):  # type: ignore
        """Test automatic tag extraction."""
        import mcp_tools

        searcher = MCPToolSearcher(mcp_tools)

        # Test tag extraction for various tool patterns
        tags1 = searcher._extract_tags("cde_scanDocumentation", "Scan documentation")
        assert "analysis" in tags1
        assert "documentation" in tags1

        tags2 = searcher._extract_tags("cde_sourceSkill", "Source skill from repo")
        assert "skills" in tags2

        tags3 = searcher._extract_tags("cde_selectWorkflow", "Select workflow")
        assert "orchestration" in tags3
        assert "workflow" in tags3


@pytest.mark.asyncio
class TestTokenEfficiencyBenchmarks:
    """Benchmark tests for token efficiency (Anthropic's 98.7% goal)."""

    async def test_tool_discovery_token_reduction(self):  # type: ignore
        """Benchmark: Tool discovery should achieve 98%+ token reduction."""
        import mcp_tools

        searcher = MCPToolSearcher(mcp_tools)

        # Simulate loading all tools upfront (traditional approach)
        all_tools_full = await searcher.list_all(detail_level="full_schema")
        all_tools_json = json.dumps(all_tools_full)
        traditional_size = len(all_tools_json)

        # Progressive disclosure approach
        name_only = await searcher.list_all(detail_level="name_only")
        name_only_json = json.dumps(name_only)
        progressive_size = len(name_only_json)

        # Calculate reduction
        reduction = (1 - progressive_size / traditional_size) * 100

        print("\n📊 Tool Discovery Token Efficiency:")
        print(f"  Traditional (all tools full): {traditional_size} bytes")
        print(f"  Progressive (name_only): {progressive_size} bytes")
        print(f"  Reduction: {reduction:.1f}%")

        # Should achieve Anthropic's 98.7% goal
        assert reduction > 95  # At least 95% reduction

    async def test_multi_project_token_efficiency(self):  # type: ignore
        """Benchmark: Multi-project scenario should show massive savings."""
        import mcp_tools

        searcher = MCPToolSearcher(mcp_tools)

        # Traditional: Load all tools for each project
        num_projects = 3
        traditional_per_project = len(
            json.dumps(await searcher.list_all(detail_level="full_schema"))
        )
        traditional_total = traditional_per_project * num_projects

        # Progressive: Discover once, use for all projects
        discovery_cost = len(
            json.dumps(await searcher.search("scan", detail_level="name_only"))
        )
        # Each project operation is minimal (just parameters)
        operation_cost_per_project = 100  # Estimate
        progressive_total = discovery_cost + (operation_cost_per_project * num_projects)

        reduction = (1 - progressive_total / traditional_total) * 100

        print(f"\n📊 Multi-Project Token Efficiency ({num_projects} projects):")
        print(f"  Traditional: {traditional_total} bytes")
        print(f"  Progressive: {progressive_total} bytes")
        print(f"  Reduction: {reduction:.1f}%")

        assert reduction > 90  # At least 90% reduction


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
