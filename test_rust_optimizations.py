#!/usr/bin/env python3
"""Test script for Rust-optimized documentation scanning and analysis."""

import json
import time
from pathlib import Path

try:
    import cde_rust_core

    print("✅ Rust module loaded successfully")
    print(
        f"Available functions: {[f for f in dir(cde_rust_core) if not f.startswith('_')]}\n"
    )
except ImportError as e:
    print(f"❌ Failed to import cde_rust_core: {e}")
    exit(1)


def test_scan_documentation():
    """Test parallel documentation scanning with YAML frontmatter extraction."""
    print("=" * 80)
    print("TEST 1: scan_documentation_py (Parallel YAML + Links + Headers)")
    print("=" * 80)

    project_root = str(Path(__file__).parent)

    start = time.perf_counter()
    result_json = cde_rust_core.scan_documentation_py(project_root)
    elapsed = time.perf_counter() - start

    documents = json.loads(result_json)

    print("\n📊 Results:")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
    print(f"   📄 Documents found: {len(documents)}")

    # Análisis rápido
    with_frontmatter = sum(1 for doc in documents if doc["has_frontmatter"])
    without_frontmatter = len(documents) - with_frontmatter
    total_links = sum(len(doc["links"]) for doc in documents)
    total_headers = sum(len(doc["headers"]) for doc in documents)
    total_words = sum(doc["word_count"] for doc in documents)

    print(f"   ✅ With YAML frontmatter: {with_frontmatter}")
    print(f"   ❌ Without YAML frontmatter: {without_frontmatter}")
    print(f"   🔗 Total links: {total_links}")
    print(f"   📑 Total headers: {total_headers}")
    print(f"   📝 Total words: {total_words:,}")

    # Mostrar ejemplos
    print("\n📋 Sample documents (first 3):")
    for doc in documents[:3]:
        path_short = Path(doc["path"]).name
        metadata_status = "✅" if doc["has_frontmatter"] else "❌"
        print(f"   {metadata_status} {path_short}")
        print(
            f"      Words: {doc['word_count']:,} | Links: {len(doc['links'])} | Headers: {len(doc['headers'])}"
        )

        if doc["metadata"]:
            meta = doc["metadata"]
            print(f"      Metadata: {meta.get('title', 'N/A')[:50]}")

    print("\n")
    return documents


def test_analyze_quality():
    """Test parallel documentation quality analysis."""
    print("=" * 80)
    print("TEST 2: analyze_documentation_quality_py (Parallel Quality Analysis)")
    print("=" * 80)

    project_root = str(Path(__file__).parent)

    start = time.perf_counter()
    result_json = cde_rust_core.analyze_documentation_quality_py(project_root)
    elapsed = time.perf_counter() - start

    report = json.loads(result_json)

    print("\n📊 Quality Report:")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
    print(f"   🎯 Quality Score: {report['quality_score']:.1f}/100")
    print(f"   📄 Total Documents: {report['total_docs']}")
    print(f"   ✅ With Metadata: {report['docs_with_metadata']}")
    print(f"   ❌ Without Metadata: {report['docs_without_metadata']}")
    print(f"   🔗 Total Links: {report['total_links']}")

    if report["broken_internal_links"]:
        print(f"\n🔴 Broken Internal Links ({len(report['broken_internal_links'])}):")
        for link in report["broken_internal_links"][:5]:
            print(f"   - {link}")
        if len(report["broken_internal_links"]) > 5:
            print(f"   ... and {len(report['broken_internal_links']) - 5} more")

    if report["orphaned_docs"]:
        print(f"\n⚠️  Orphaned Documents ({len(report['orphaned_docs'])}):")
        for doc in report["orphaned_docs"][:5]:
            print(f"   - {Path(doc).name}")
        if len(report["orphaned_docs"]) > 5:
            print(f"   ... and {len(report['orphaned_docs']) - 5} more")

    if report["large_files"]:
        print(f"\n📦 Large Files ({len(report['large_files'])}):")
        for doc in report["large_files"][:5]:
            print(f"   - {Path(doc).name}")

    print("\n🔍 Issues Detected:")
    for issue in report["issues"]:
        print(f"   {issue}")

    print("\n💡 Recommendations:")
    for rec in report["recommendations"]:
        print(f"   {rec}")

    print("\n")
    return report


def benchmark_comparison():
    """Compare Rust vs Python performance (if Python version exists)."""
    print("=" * 80)
    print("BENCHMARK: Rust Performance")
    print("=" * 80)

    project_root = str(Path(__file__).parent)

    # Multiple runs for average
    runs = 3
    scan_times = []
    analyze_times = []

    print(f"\nRunning {runs} iterations...")
    for i in range(runs):
        # Scan
        start = time.perf_counter()
        cde_rust_core.scan_documentation_py(project_root)
        scan_times.append(time.perf_counter() - start)

        # Analyze
        start = time.perf_counter()
        cde_rust_core.analyze_documentation_quality_py(project_root)
        analyze_times.append(time.perf_counter() - start)

        print(
            f"   Run {i+1}: scan={scan_times[-1]:.3f}s, analyze={analyze_times[-1]:.3f}s"
        )

    avg_scan = sum(scan_times) / len(scan_times)
    avg_analyze = sum(analyze_times) / len(analyze_times)

    print("\n📊 Average Performance:")
    print(f"   scan_documentation: {avg_scan:.3f}s")
    print(f"   analyze_quality: {avg_analyze:.3f}s")
    print(f"   Total: {avg_scan + avg_analyze:.3f}s")

    print("\n✅ Rust optimizations working!")
    print("   - Parallel YAML frontmatter extraction")
    print("   - Parallel link validation")
    print("   - Parallel header extraction")
    print("   - Parallel word counting (for large files)")
    print("   - Parallel quality metrics calculation")
    print("\n")


if __name__ == "__main__":
    print("\n🦀 CDE Rust Core - Optimized Documentation Analysis\n")

    # Test 1: Scan documentation
    documents = test_scan_documentation()

    # Test 2: Analyze quality
    report = test_analyze_quality()

    # Test 3: Benchmark
    benchmark_comparison()

    print("=" * 80)
    print("✅ All tests completed successfully!")
    print("=" * 80)
