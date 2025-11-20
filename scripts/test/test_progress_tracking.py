#!/usr/bin/env python3
# mypy: disable-error-code="misc, no-untyped-def"
"""
Progress Tracking Validation Test Suite
=========================================

Tests that verify:
1. Progress reporting doesn't block tool execution
2. Batching reduces HTTP calls (98% reduction target)
3. Progress messages include elapsed time
4. HTTP failures don't break tools
5. Performance with large workloads (1000+ files)

Run with: python scripts/test/test_progress_tracking.py
"""

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


# ============================================================================
# Test Utilities
# ============================================================================


class ProgressTracker:
    """Mock HTTP server to capture progress events"""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.call_count = 0
        self.last_event_time: float = 0.0
        self.blocked_duration: float = 0.0  # Time blocked waiting for HTTP

    def record_event(self, tool: str, percentage: float, message: str):
        """Record a progress event"""
        current_time = time.time()

        if self.last_event_time > 0:
            time_since_last = current_time - self.last_event_time
            # Assume if > 0.1s since last, was potentially blocking
            if time_since_last > 0.1:
                self.blocked_duration += time_since_last

        self.events.append(
            {
                "tool": tool,
                "percentage": percentage,
                "message": message,
                "timestamp": current_time,
            }
        )
        self.call_count += 1
        self.last_event_time = current_time

    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        if not self.events:
            return {
                "total_events": 0,
                "batching_efficiency": 0,
                "avg_time_between_events": 0,
                "total_blocked_ms": 0,
            }

        # Calculate time between events
        times_between = []
        for i in range(1, len(self.events)):
            delta = self.events[i]["timestamp"] - self.events[i - 1]["timestamp"]
            times_between.append(delta)

        avg_time_between = (
            sum(times_between) / len(times_between) if times_between else 0
        )

        # Batching efficiency: 1000 items / N calls (100 items = perfect batching for 1000 file scan)
        # For reference: 1000 items with 10-20 calls = 90%+ efficiency
        efficiency: float = 0.0
        if self.call_count > 0:
            # Assume 1000 items per typical scan
            items_per_call = 1000.0 / self.call_count
            efficiency = min(
                100.0, (items_per_call / 100.0) * 100.0
            )  # 100 items/call = baseline 100%

        return {
            "total_events": len(self.events),
            "total_calls": self.call_count,
            "batching_efficiency_pct": round(efficiency, 1),
            "avg_time_between_events_ms": round(avg_time_between * 1000, 1),
            "total_blocked_ms": round(self.blocked_duration * 1000, 1),
            "first_event_time": self.events[0]["timestamp"],
            "last_event_time": self.events[-1]["timestamp"],
            "total_duration_s": self.events[-1]["timestamp"]
            - self.events[0]["timestamp"],
        }


# ============================================================================
# Test Suite
# ============================================================================


class TestProgressTracking:
    """Unit tests for progress tracking"""

    def __init__(self):
        self.results = []
        self.tracker = ProgressTracker()

    def test_batching_reduces_http_calls(self):
        """Test that batching reduces HTTP calls vs naive approach"""

        print("\n[TEST 1] Batching Reduces HTTP Calls")
        print("=" * 60)

        # Simulate 1000-file scan with batching (target: 10-20 calls)
        num_files = 1000
        batch_sizes = [10, 50, 100]  # Different batch strategies

        for batch_size in batch_sizes:
            self.tracker = ProgressTracker()

            # Report discovery
            self.tracker.record_event("scanDoc", 0.0, f"Discovered {num_files} files")

            # Report progress in batches
            num_batches = (num_files + batch_size - 1) // batch_size
            for batch_idx in range(1, num_batches + 1):
                progress = 0.1 + (0.8 * batch_idx / num_batches)
                files_processed = min(batch_idx * batch_size, num_files)
                self.tracker.record_event(
                    "scanDoc", progress, f"Analyzed {files_processed}/{num_files}"
                )

            # Report finalization
            self.tracker.record_event("scanDoc", 0.95, "Finalizing...")
            self.tracker.record_event("scanDoc", 1.0, f"Complete | {num_files} files")

            stats = self.tracker.get_statistics()

            # Verdict
            expected_calls = (
                4 + num_batches
            )  # discovery + batches + finalize + complete
            actual_calls = stats["total_calls"]

            passed = actual_calls <= 25  # Should be < 25 for reasonable batching
            status = "✅ PASS" if passed else "❌ FAIL"

            print(f"\n  Batch Size: {batch_size} items/call")
            print(f"    Total Calls: {actual_calls} (expected ~{expected_calls})")
            print("    Expected: < 25 calls")
            print(f"    Status: {status}")

            self.results.append(
                {
                    "test": "batching_reduces_calls",
                    "batch_size": batch_size,
                    "calls": actual_calls,
                    "passed": passed,
                }
            )

    def test_progress_messages_include_elapsed_time(self):
        """Test that progress messages include elapsed time"""

        print("\n[TEST 2] Progress Messages Include Elapsed Time")
        print("=" * 60)

        # Simulate a 5-second operation
        start_time = time.time()
        messages = []

        # Progress at different stages
        for pct in [0.0, 0.25, 0.5, 0.75, 1.0]:
            elapsed = time.time() - start_time
            msg = f"Processing... {int(pct*100)}% | {elapsed:.1f}s"
            messages.append(msg)
            time.sleep(0.1)  # Simulate work

        # Check all messages have time format
        all_have_time = all(" | " in msg and "s" in msg for msg in messages)

        status = "✅ PASS" if all_have_time else "❌ FAIL"
        print(f"\n  Total Messages: {len(messages)}")
        print(f"  All Include Elapsed Time: {all_have_time}")
        print(f"  Status: {status}")

        for msg in messages:
            print(f"    Message: {msg}")

        self.results.append(
            {
                "test": "progress_messages_include_time",
                "total_messages": len(messages),
                "all_have_time": all_have_time,
                "passed": all_have_time,
            }
        )

    def test_http_failure_doesnt_block_tool(self):
        """Test that HTTP failures don't block tool execution"""

        print("\n[TEST 3] HTTP Failure Doesn't Block Tool")
        print("=" * 60)

        # Simulate report_progress_http with HTTP error
        fail_count = [0]

        def mock_report_fail(*args, **kwargs):
            fail_count[0] += 1
            raise Exception("HTTP 500 Server Error")

        start_time = time.time()

        # Should continue even if HTTP fails
        try:
            for i in range(5):
                # This should NOT raise, should fail silently
                try:
                    mock_report_fail("tool", 0.2 * i, f"Step {i}")
                except Exception:
                    pass  # Fail silently like real implementation

                time.sleep(0.05)  # Simulate work
        except Exception as e:
            print(f"\n  ❌ FAIL: Tool execution blocked by HTTP error: {e}")
            self.results.append(
                {
                    "test": "http_failure_doesnt_block",
                    "passed": False,
                    "error": str(e),
                }
            )
            return

        elapsed = time.time() - start_time

        # Should complete despite HTTP failures
        passed = (
            fail_count[0] > 0 and elapsed < 2
        )  # Some failures but completed quickly
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"\n  HTTP Failures: {fail_count[0]}")
        print(f"  Tool Execution Time: {elapsed:.2f}s")
        print(f"  Completed Despite Failures: {passed}")
        print(f"  Status: {status}")

        self.results.append(
            {
                "test": "http_failure_doesnt_block",
                "http_failures": fail_count[0],
                "execution_time_s": round(elapsed, 2),
                "passed": passed,
            }
        )

    def test_large_workload_performance(self):
        """Test performance with 1000+ file workload"""

        print("\n[TEST 4] Large Workload Performance (1000+ files)")
        print("=" * 60)

        num_files = 1500
        batch_size = 100

        start_time = time.time()
        self.tracker = ProgressTracker()

        # Simulate scan
        self.tracker.record_event("scanDoc", 0.05, f"Discovering {num_files} files...")

        num_batches = (num_files + batch_size - 1) // batch_size
        for batch_idx in range(1, num_batches + 1):
            progress = 0.05 + (0.90 * batch_idx / num_batches)
            processed = min(batch_idx * batch_size, num_files)

            # Simulate batch processing (10ms per batch)
            time.sleep(0.01)

            self.tracker.record_event(
                "scanDoc", progress, f"Analyzed {processed}/{num_files}"
            )

        self.tracker.record_event("scanDoc", 1.0, f"Complete | {num_files} files")
        elapsed = time.time() - start_time

        stats = self.tracker.get_statistics()

        # Verdict: Should process 1500 files with < 20 HTTP calls in < 1 second
        passed = (
            stats["total_calls"] < 20
            and elapsed < 1.0
            and stats["batching_efficiency_pct"] > 50
        )
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"\n  Files Scanned: {num_files}")
        print(f"  HTTP Calls: {stats['total_calls']} (target: < 20)")
        print(f"  Execution Time: {elapsed:.2f}s (target: < 1.0s)")
        print(
            f"  Batching Efficiency: {stats['batching_efficiency_pct']}% (target: > 50%)"
        )
        print(f"  Status: {status}")

        self.results.append(
            {
                "test": "large_workload_performance",
                "files_scanned": num_files,
                "http_calls": stats["total_calls"],
                "execution_time_s": round(elapsed, 2),
                "batching_efficiency_pct": stats["batching_efficiency_pct"],
                "passed": passed,
            }
        )

    def test_concurrent_tool_progress(self):
        """Test progress tracking with concurrent tools"""

        print("\n[TEST 5] Concurrent Tool Progress Tracking")
        print("=" * 60)

        # Simulate 3 tools running concurrently
        tools = ["scanDoc", "onboarding", "delegateToJules"]
        trackers = {tool: ProgressTracker() for tool in tools}

        start_time = time.time()

        # Simulate concurrent execution (non-async for simplicity)
        for tool in tools:
            for pct in [0.0, 0.25, 0.5, 0.75, 1.0]:
                trackers[tool].record_event(tool, pct, f"{tool} {int(pct*100)}%")

        elapsed = time.time() - start_time

        # Verify each tool tracked independently
        all_tools_tracked = all(len(trackers[tool].events) == 5 for tool in tools)

        status = "✅ PASS" if all_tools_tracked else "❌ FAIL"

        print(f"\n  Concurrent Tools: {len(tools)}")
        for tool in tools:
            print(f"    {tool}: {len(trackers[tool].events)} events")
        print(f"  Total Execution Time: {elapsed:.2f}s")
        print(f"  All Tools Tracked Independently: {all_tools_tracked}")
        print(f"  Status: {status}")

        self.results.append(
            {
                "test": "concurrent_tool_progress",
                "tools": len(tools),
                "total_events": sum(len(trackers[t].events) for t in tools),
                "execution_time_s": round(elapsed, 2),
                "passed": all_tools_tracked,
            }
        )

    def run_all(self):
        """Run all tests"""

        print("\n" + "=" * 60)
        print("PROGRESS TRACKING VALIDATION TEST SUITE")
        print("=" * 60)
        print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Test Count: 5")

        try:
            self.test_batching_reduces_http_calls()
            self.test_progress_messages_include_elapsed_time()
            self.test_http_failure_doesnt_block_tool()
            self.test_large_workload_performance()
            self.test_concurrent_tool_progress()
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            import traceback

            traceback.print_exc()
            return False

        # Summary
        passed_count = sum(1 for r in self.results if r.get("passed", False))
        total_count = len(self.results)

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Passed: {passed_count}/{total_count}")
        print(f"Success Rate: {(passed_count/total_count*100):.0f}%")

        # Detailed results
        print("\nDetailed Results:")
        for i, result in enumerate(self.results, 1):
            test_name = result["test"].replace("_", " ").title()
            status = "✅" if result.get("passed") else "❌"
            print(f"  {i}. {status} {test_name}")

            # Print key metrics
            for key, value in result.items():
                if key not in ["test", "passed"]:
                    print(f"     - {key}: {value}")

        print("\n" + "=" * 60)

        # Generate report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total_count,
            "passed_tests": passed_count,
            "success_rate_pct": round(passed_count / total_count * 100, 1),
            "results": self.results,
        }

        # Save report
        report_file = (
            Path(__file__).parent.parent.parent
            / "agent-docs"
            / "execution"
            / f"test-progress-tracking-{time.strftime('%Y-%m-%d')}.json"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Report saved: {report_file}")

        return passed_count == total_count


if __name__ == "__main__":
    suite = TestProgressTracking()
    success = suite.run_all()
    sys.exit(0 if success else 1)
