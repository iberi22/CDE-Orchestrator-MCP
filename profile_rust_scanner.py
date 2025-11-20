#!/usr/bin/env python3
"""Analyze Rust performance bottlenecks by profiling component timing."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import cde_rust_core


def profile_rust_scanner() -> None:
    """Profile Rust scanner to understand timing breakdown."""

    project_path = str(Path(".").absolute())
    excluded_dirs = [
        ".venv",
        "node_modules",
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "build",
        "dist",
        "htmlcov",
    ]
    excluded_patterns = ["*.pyc", "*.pyo", "*.pyd", "*.map", "*.lock"]

    print("🔬 PROFILING RUST SCANNER\n")
    print(f"Project path: {project_path}")
    print(f"Excluded dirs: {len(excluded_dirs)}")
    print(f"Excluded patterns: {len(excluded_patterns)}\n")

    # Run 1 iteration to get baseline
    print("Running analysis...")
    result_json = cde_rust_core.scan_project_py(
        project_path,
        excluded_dirs,
        excluded_patterns,
    )

    result = json.loads(result_json)

    print("\n✅ ANALYSIS COMPLETE\n")
    print("Results:")
    print(f"  Files analyzed:  {result['file_count']}")
    print(f"  Files excluded:  {result['excluded_count']}")
    print(f"  Analysis time:   {result['analysis_time_ms']}ms")
    print(f"  Total files:     {result['file_count'] + result['excluded_count']}")

    # Calculate metrics
    total_files = result["file_count"] + result["excluded_count"]
    analysis_time = result["analysis_time_ms"]

    if total_files > 0 and analysis_time > 0:
        us_per_file = (analysis_time * 1000) / total_files
        files_per_second = (total_files / analysis_time) * 1000

        print("\n📊 PERFORMANCE METRICS")
        print(f"  Microseconds per file: {us_per_file:.2f}µs")
        print(f"  Files per second:      {files_per_second:.0f}")

    # Language stats
    print("\n📝 LANGUAGE STATISTICS")
    lang_stats = result["language_stats"]
    for ext, count in sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {ext:10s}: {count:5d}")

    # Dependency files
    print("\n📦 DEPENDENCY FILES")
    for dep in result["dependency_files"]:
        print(f"  {dep}")

    # Analysis
    print("\n🔍 ANALYSIS & RECOMMENDATIONS")

    if analysis_time > 1000:
        print(f"  ⚠️  Analysis takes {analysis_time}ms (>1s)")
        print(f"      This is scanning {total_files} files")

        if total_files > 5000:
            print(f"      With {total_files} files, this is reasonable performance")
            print(f"      Approx {analysis_time/total_files:.2f}ms per file")

        print("\n  Optimization options:")
        print("  1. Use incremental scanning (cache previous results)")
        print("  2. Reduce thread pool for smaller projects")
        print("  3. Pre-compile gitignore patterns")
        print("  4. Use memory-mapped I/O for large projects")


if __name__ == "__main__":
    profile_rust_scanner()
