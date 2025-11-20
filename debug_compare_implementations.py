#!/usr/bin/env python3
"""Debug script to compare file count between Rust and Python implementations."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)


def dummy_progress(tool_name: str, progress: float, message: str):
    """Dummy progress reporter for testing."""
    pass


def get_rust_result(project_path: str):
    """Get analysis result from Rust implementation."""
    try:

        use_case = ProjectAnalysisUseCase()
        result = use_case._execute_rust(project_path, dummy_progress)
        result["engine"] = "rust"
        return result
    except Exception as e:
        print(f"❌ Rust failed: {e}")
        import traceback

        traceback.print_exc()
        return None


def get_python_result(project_path: str):
    """Get analysis result from Python implementation."""
    try:
        use_case = ProjectAnalysisUseCase()
        result = use_case._execute_python(project_path, dummy_progress)
        result["engine"] = "python"
        return result
    except Exception as e:
        print(f"❌ Python failed: {e}")
        import traceback

        traceback.print_exc()
        return None


def compare_results(rust_result, python_result):
    """Compare file counts and extensions."""
    print("\n" + "=" * 60)
    print("COMPARISON: Rust vs Python File Analysis")
    print("=" * 60)

    if not rust_result:
        print("❌ Rust result unavailable")
        return

    if not python_result:
        print("❌ Python result unavailable")
        return

    rust_count = rust_result["file_count"]
    python_count = python_result["file_count"]
    diff = rust_count - python_count
    pct_diff = (diff / python_count) * 100 if python_count > 0 else 0

    print("\n📊 FILE COUNT")
    print(f"   Rust:   {rust_count} files")
    print(f"   Python: {python_count} files")
    print(f"   Diff:   {diff:+d} files ({pct_diff:+.1f}%)")

    # Compare by extension
    print("\n📁 TOP FILE TYPES (by extension)")
    print("\n   Rust:")
    rust_stats = rust_result["language_stats"]
    for ext, count in sorted(rust_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"      {ext:15s}: {count:5d}")

    print("\n   Python:")
    python_stats = python_result["language_stats"]
    for ext, count in sorted(python_stats.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]:
        print(f"      {ext:15s}: {count:5d}")

    # Find extensions that differ
    print("\n⚠️  EXTENSIONS WITH DIFFERENCES")
    all_exts = set(rust_stats.keys()) | set(python_stats.keys())
    diffs = {}
    for ext in all_exts:
        rust_cnt = rust_stats.get(ext, 0)
        python_cnt = python_stats.get(ext, 0)
        if rust_cnt != python_cnt:
            diffs[ext] = (rust_cnt, python_cnt, rust_cnt - python_cnt)

    if diffs:
        print(f"   {'Extension':<15} {'Rust':>6} {'Python':>6} {'Diff':>6}")
        print(f"   {'-'*15} {'-'*6} {'-'*6} {'-'*6}")
        for ext in sorted(diffs.keys()):
            rust_cnt, python_cnt, diff = diffs[ext]
            print(f"   {ext:<15} {rust_cnt:>6} {python_cnt:>6} {diff:>+6}")
    else:
        print("   ✅ All extensions match!")

    # Time comparison
    print("\n⏱️  PERFORMANCE")
    rust_time = rust_result.get("analysis_time_ms", 0)
    python_time = python_result.get("analysis_time_ms", 0)
    if rust_time > 0 and python_time > 0:
        ratio = rust_time / python_time
        print(f"   Rust:   {rust_time:6.0f}ms")
        print(f"   Python: {python_time:6.0f}ms")
        print(f"   Ratio:  {ratio:6.2f}x")

    # Dependency files
    print("\n📦 DEPENDENCY FILES")
    rust_deps = set(rust_result.get("dependency_files", []))
    python_deps = set(python_result.get("dependency_files", []))

    print(f"   Rust ({len(rust_deps)} files):")
    for dep in sorted(rust_deps):
        print(f"      {dep}")

    print(f"\n   Python ({len(python_deps)} files):")
    for dep in sorted(python_deps):
        print(f"      {dep}")

    common = rust_deps & python_deps
    print(f"\n   Common: {len(common)} files")


def main():
    project_path = "."

    print("🔍 Analyzing project with both engines...")
    print(f"   Project: {Path(project_path).resolve()}")

    # Get results
    rust_result = get_rust_result(project_path)
    python_result = get_python_result(project_path)

    # Compare
    compare_results(rust_result, python_result)

    print("\n" + "=" * 60)
    print("✅ Comparison complete!")


if __name__ == "__main__":
    main()
