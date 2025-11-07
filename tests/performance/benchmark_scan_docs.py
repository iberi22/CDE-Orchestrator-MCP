#!/usr/bin/env python3
"""
Performance benchmark for cde_scanDocumentation optimization.

Compares the performance of the original Python implementation
vs the new Rust-accelerated version.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def benchmark_scan_documentation(project_path: str, iterations: int = 3) -> dict:
    """Benchmark the scan documentation function."""
    from cde_orchestrator.application.documentation.scan_documentation_use_case import (
        ScanDocumentationUseCase,
    )

    use_case = ScanDocumentationUseCase()
    times = []

    print(f"🔍 Benchmarking scan on: {project_path}")
    print(f"📊 Running {iterations} iterations...")

    for i in range(iterations):
        start_time = time.time()
        try:
            result = use_case.execute(project_path)
            end_time = time.time()
            duration = end_time - start_time
            times.append(duration)
            print(".1f")
        except Exception as e:
            print(f"❌ Iteration {i+1} failed: {e}")
            return None

    if not times:
        return None

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    return {
        "project_path": project_path,
        "iterations": iterations,
        "avg_time": avg_time,
        "min_time": min_time,
        "max_time": max_time,
        "times": times,
        "rust_accelerated": _is_rust_available(),
    }


def _is_rust_available() -> bool:
    """Check if Rust acceleration is available."""
    try:
        import cde_rust_core

        return True
    except ImportError:
        return False


def count_markdown_files(project_path: str) -> int:
    """Count markdown files in project for context."""
    project = Path(project_path)
    md_files = list(project.rglob("*.md"))

    # Exclude common directories
    excluded_dirs = {
        ".git",
        ".venv",
        "node_modules",
        "venv",
        "__pycache__",
        ".pytest_cache",
    }
    md_files = [
        f
        for f in md_files
        if not any(excluded in f.parts for excluded in excluded_dirs)
    ]

    return len(md_files)


def main():
    """Run performance benchmarks."""
    print("🚀 CDE Scan Documentation Performance Benchmark")
    print("=" * 50)

    # Test on current project
    project_path = os.path.join(os.path.dirname(__file__), "..", "..")

    # Count files for context
    file_count = count_markdown_files(project_path)
    print(f"📁 Project: {os.path.basename(project_path)}")
    print(f"📄 Markdown files: {file_count}")
    print(
        f"🦀 Rust acceleration: {'Available' if _is_rust_available() else 'Not available'}"
    )
    print()

    # Run benchmark
    result = benchmark_scan_documentation(project_path, iterations=3)

    if result:
        print("\n📈 Results:")
        print(".2f")
        print(".2f")
        print(".2f")
        print(
            f"   Acceleration: {'🦀 Rust' if result['rust_accelerated'] else '🐍 Python'}"
        )

        # Save detailed results
        output_file = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Detailed results saved to: {output_file}")

        # Performance assessment
        if result["avg_time"] < 1.0:
            print("✅ Excellent performance (< 1 second)")
        elif result["avg_time"] < 5.0:
            print("👍 Good performance (< 5 seconds)")
        else:
            print("⚠️  Consider optimization (> 5 seconds)")

    else:
        print("❌ Benchmark failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
