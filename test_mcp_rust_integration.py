#!/usr/bin/env python3
"""Test Rust-accelerated MCP tools."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cde_orchestrator.application.documentation import AnalyzeDocumentationUseCase


def test_analyze_with_rust():
    """Test analyze documentation with Rust acceleration."""
    print("=" * 80)
    print("Testing Rust-Accelerated Documentation Analysis")
    print("=" * 80)

    use_case = AnalyzeDocumentationUseCase()

    print("\n✅ Use case initialized")
    print(f"   Rust scanner available: {use_case.rust_scanner is not None}")
    if use_case.rust_scanner:
        print(f"   Rust scanner ready: {use_case.rust_scanner.is_available}")

    project_path = str(Path(__file__).parent)

    print(f"\n🔍 Analyzing: {project_path}")
    result = use_case.execute(project_path)

    print("\n📊 Results:")
    print(f"   Rust accelerated: {result.get('rust_accelerated', False)}")
    print(f"   Quality Score: {result['quality_score']:.1f}/100")
    print(f"   Total Documents: {result['total_analyzed']}")
    print(f"   Links Analyzed: {result['link_analysis']['total_links']}")
    print(f"   Broken Links: {result['link_analysis']['broken_links']}")

    if result["link_analysis"].get("broken_link_details"):
        print("\n🔴 Broken Links (first 5):")
        for link in result["link_analysis"]["broken_link_details"][:5]:
            print(f"   - {link}")

    print(f"\n🔍 Issues ({len(result['issues'])}):")
    for issue in result["issues"]:
        print(f"   {issue}")

    print(f"\n💡 Suggestions ({len(result['suggestions'])}):")
    for suggestion in result["suggestions"]:
        print(f"   {suggestion}")

    print("\n" + "=" * 80)
    print("✅ Test completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    test_analyze_with_rust()
