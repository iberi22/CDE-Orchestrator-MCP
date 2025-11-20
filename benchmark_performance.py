#!/usr/bin/env python3
"""Benchmark Rust scanner performance with warm-start measurements."""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)


def benchmark_rust_performance(
    project_path: str = ".",
    num_iterations: int = 5,
) -> Dict[str, List[float]]:
    """Benchmark Rust scanner performance over multiple iterations.

    Args:
        project_path: Project to scan
        num_iterations: Number of warm-start iterations after initial cold start

    Returns:
        Dict with cold_start, warm_starts, and analysis times
    """

    use_case = ProjectAnalysisUseCase()
    excluded_dirs = sorted(list(use_case.EXCLUDED_DIRS))
    excluded_patterns = sorted(list(use_case.EXCLUDED_PATTERNS))

    print("🔍 Benchmarking Rust Scanner Performance")
    print(f"   Project: {Path(project_path).resolve().name}")
    print(f"   Iterations: 1 cold + {num_iterations} warm starts\n")

    timings = {
        "cold_start": [],
        "warm_starts": [],
        "analysis_times": [],
    }

    # Cold start
    print("❄️  COLD START (1 iteration)")
    start = time.perf_counter()
    result1 = use_case._execute_rust(project_path, lambda *args: None)
    cold_elapsed = (time.perf_counter() - start) * 1000

    print(f"   Total time: {cold_elapsed:7.1f}ms")
    print(f"   Rust analysis: {result1['performance']['analysis_time_ms']:7.0f}ms")
    print(
        f"   Python overhead: {cold_elapsed - result1['performance']['analysis_time_ms']:7.1f}ms\n"
    )

    timings["cold_start"].append(cold_elapsed)
    timings["analysis_times"].append(result1["performance"]["analysis_time_ms"])

    # Warm starts
    print(f"🔥 WARM STARTS ({num_iterations} iterations)")
    for i in range(num_iterations):
        start = time.perf_counter()
        result = use_case._execute_rust(project_path, lambda *args: None)
        elapsed = (time.perf_counter() - start) * 1000

        print(
            f"   Iteration {i+1}: {elapsed:7.1f}ms (Rust: {result['performance']['analysis_time_ms']:7.0f}ms)"
        )

        timings["warm_starts"].append(elapsed)
        timings["analysis_times"].append(result["performance"]["analysis_time_ms"])

    # Stats
    cold = timings["cold_start"][0]
    warms = timings["warm_starts"]
    warm_avg = sum(warms) / len(warms) if warms else 0
    improvement = cold / warm_avg if warm_avg > 0 else 0

    print("\n📊 SUMMARY")
    print(f"   Cold start:       {cold:7.1f}ms")
    print(f"   Warm avg:         {warm_avg:7.1f}ms")
    print(f"   Improvement:      {improvement:7.2f}x")
    print(f"   Min warm:         {min(warms):7.1f}ms")
    print(f"   Max warm:         {max(warms):7.1f}ms")
    print(f"   Std dev:          {calculate_stddev(warms):7.1f}ms")

    # Target comparison
    target = 100
    status_cold = "✅ PASS" if cold < target else "❌ FAIL"
    status_warm = "✅ PASS" if warm_avg < target else "❌ FAIL"

    print(f"\n🎯 TARGET COMPARISON (<{target}ms)")
    print(f"   Cold start: {cold:7.1f}ms  {status_cold}")
    print(f"   Warm avg:   {warm_avg:7.1f}ms  {status_warm}")

    return timings


def calculate_stddev(values: List[float]) -> float:
    """Calculate standard deviation."""
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance**0.5


def benchmark_python_performance(
    project_path: str = ".",
    num_iterations: int = 5,
) -> Dict[str, List[float]]:
    """Benchmark Python scanner performance for comparison.

    Args:
        project_path: Project to scan
        num_iterations: Number of iterations

    Returns:
        Dict with timing results
    """

    use_case = ProjectAnalysisUseCase()

    print("\n\n🐍 Benchmarking Python Scanner (Reference)")
    print(f"   Project: {Path(project_path).resolve().name}")
    print(f"   Iterations: {num_iterations}\n")

    timings: List[float] = []

    for i in range(num_iterations):
        start = time.perf_counter()
        result = use_case._execute_python(project_path, lambda *args: None)
        elapsed = (time.perf_counter() - start) * 1000

        print(f"   Iteration {i+1}: {elapsed:7.1f}ms")
        timings.append(elapsed)

    py_avg = sum(timings) / len(timings)

    print(f"\n📊 PYTHON AVERAGE: {py_avg:7.1f}ms")

    return {"all": timings}


def main() -> None:
    """Run benchmarks and compare Rust vs Python."""

    project_path = "."

    # Benchmark Rust
    rust_times = benchmark_rust_performance(project_path, num_iterations=5)

    # Benchmark Python
    python_times = benchmark_python_performance(project_path, num_iterations=5)

    # Comparison
    print("\n\n" + "=" * 60)
    print("RUST vs PYTHON PERFORMANCE COMPARISON")
    print("=" * 60)

    rust_cold = rust_times["cold_start"][0]
    rust_warm_avg = sum(rust_times["warm_starts"]) / len(rust_times["warm_starts"])
    python_avg = sum(python_times["all"]) / len(python_times["all"])

    print(f"\nRust cold start:      {rust_cold:7.1f}ms")
    print(f"Rust warm average:    {rust_warm_avg:7.1f}ms")
    print(f"Python average:       {python_avg:7.1f}ms")

    if python_avg > 0:
        speedup = python_avg / rust_warm_avg
        print(f"\nRust warm vs Python:  {speedup:7.2f}x faster")

    # Save results
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "rust": {
            "cold_start_ms": rust_cold,
            "warm_avg_ms": rust_warm_avg,
            "warm_min_ms": min(rust_times["warm_starts"]),
            "warm_max_ms": max(rust_times["warm_starts"]),
            "analysis_avg_ms": sum(rust_times["analysis_times"])
            / len(rust_times["analysis_times"]),
        },
        "python": {
            "avg_ms": python_avg,
            "min_ms": min(python_times["all"]),
            "max_ms": max(python_times["all"]),
        },
    }

    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Results saved to benchmark_results.json")


if __name__ == "__main__":
    main()
