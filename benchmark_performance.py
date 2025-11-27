#!/usr/bin/env python3
"""Benchmark caching layer performance."""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent / "src"))

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)

def benchmark_caching_performance(
    project_path: str = ".",
    num_iterations: int = 5,
) -> Dict[str, List[float]]:
    """Benchmark caching layer performance."""

    use_case = ProjectAnalysisUseCase()

    print("🔍 Benchmarking Caching Layer Performance")
    print(f"   Project: {Path(project_path).resolve().name}")
    print(f"   Iterations: 1 cold + {num_iterations} warm starts\n")

    timings = {
        "cold_start": [],
        "warm_starts": [],
    }

    # Cold start (cache miss)
    print("❄️  COLD START (cache miss)")
    start = time.perf_counter()
    asyncio.run(use_case.execute(
        project_path=project_path,
        enrich_context=False,
    ))
    cold_elapsed = (time.perf_counter() - start) * 1000
    timings["cold_start"].append(cold_elapsed)
    print(f"   Cold start: {cold_elapsed:.2f}ms")

    # Warm starts (cache hits)
    print(f"\n🔥 WARM STARTS ({num_iterations} iterations, cache hits)")
    for i in range(num_iterations):
        start = time.perf_counter()
        asyncio.run(use_case.execute(
            project_path=project_path,
            enrich_context=False,
        ))
        elapsed = (time.perf_counter() - start) * 1000
        timings["warm_starts"].append(elapsed)
        print(f"   Iteration {i+1}: {elapsed:.2f}ms")

    # Calculate stats
    avg_warm = sum(timings["warm_starts"]) / len(timings["warm_starts"]) if timings["warm_starts"] else 0
    improvement = ((cold_elapsed - avg_warm) / cold_elapsed * 100) if cold_elapsed > 0 else 0

    print(f"\n📊 Summary:")
    print(f"   Cold start: {cold_elapsed:.2f}ms")
    print(f"   Avg warm start: {avg_warm:.2f}ms")
    print(f"   Improvement: {improvement:.1f}%")
    print(f"   Speedup: {cold_elapsed/avg_warm:.1f}x")

    return timings

if __name__ == "__main__":
    timings = benchmark_caching_performance(".")
    with open("benchmark_results.json", "w") as f:
        json.dump(timings, f, indent=2)
    print("\n✅ Results saved to benchmark_results.json")
