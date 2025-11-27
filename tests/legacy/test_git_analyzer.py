"""
Test script for Git analyzer functionality.

Tests both Rust module and Python MCP tool wrapper.
"""

import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_rust_module():
    """Test Rust module directly."""
    print("=" * 80)
    print("TEST 1: Rust Module (analyze_git_repository_py)")
    print("=" * 80)

    try:
        import cde_rust_core
        print(f"DEBUG: cde_rust_core file: {cde_rust_core.__file__}")
        from cde_rust_core import analyze_git_repository_py

        # Analyze current project (last 90 days)
        project_path = os.getcwd()
        print(f"\n📂 Analyzing: {project_path}")
        print(f"⏰ Time period: Last 90 days\n")

        result_json = analyze_git_repository_py(project_path, 90)
        result = json.loads(result_json)

        # Display key metrics
        repo_info = result.get("repository_info", {})
        branch_analysis = result.get("branch_analysis", {})

        print(f"✅ RUST MODULE WORKS!")
        print(f"\n📊 Key Metrics:")
        print(f"   - Repository age: {repo_info.get('repository_age_days', 0)} days")
        print(f"   - Total commits: {repo_info.get('total_commits', 0)}")
        print(f"   - Total branches: {branch_analysis.get('total_branches', 0)}")
        print(f"   - Remote: {repo_info.get('remote_url', 'N/A')}")

        commit_history = result.get("commit_history", {})
        recent_commits = commit_history.get("recent_commits", [])
        print(f"\n📝 Recent commits: {len(recent_commits)}")
        if recent_commits:
            print(f"   Latest: {recent_commits[0].get('message', '')[:60]}")

        contributors = result.get("contributor_insights", [])
        print(f"\n👥 Contributors: {len(contributors)}")
        if contributors:
            top = contributors[0]
            print(f"   Top: {top.get('name')} ({top.get('total_commits')} commits)")

        return True

    except ImportError as e:
        print(f"❌ RUST MODULE NOT AVAILABLE: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_python_fallback():
    """Test Python fallback implementation."""
    print("\n" + "=" * 80)
    print("TEST 2: Python Fallback (GitPython)")
    print("=" * 80)

    try:
        from git import Repo

        repo = Repo(os.getcwd())
        commits = list(repo.iter_commits(max_count=10))

        print(f"\n✅ PYTHON FALLBACK WORKS!")
        print(f"📊 Recent commits: {len(commits)}")
        if commits:
            print(f"   Latest: {commits[0].message.split('\\n')[0][:60]}")

        return True

    except ImportError:
        print(f"\n⚠️  GitPython not installed (expected)")
        print(f"   Install: pip install gitpython")
        return True  # Not an error if not installed
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


async def test_mcp_tool():
    """Test MCP tool wrapper."""
    print("\n" + "=" * 80)
    print("TEST 3: MCP Tool (cde_analyzeGit)")
    print("=" * 80)

    try:
        from unittest.mock import MagicMock

        from mcp_tools.git_analysis import cde_analyzeGit

        # Create mock context
        ctx = MagicMock()

        print(f"\n📂 Testing MCP tool wrapper...")
        result_json = await cde_analyzeGit(ctx, project_path=".", days=90)
        result = json.loads(result_json)

        if "error" in result:
            print(f"❌ MCP TOOL ERROR: {result.get('error')}")
            return False

        print(f"✅ MCP TOOL WORKS!")

        # Display summary if available
        summary = result.get("analysis_summary", {})
        insights = summary.get("insights", [])
        if insights:
            print(f"\n💡 Analysis Insights:")
            for insight in insights[:5]:
                print(f"   {insight}")

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🧪 Git Analyzer Test Suite")
    print("Testing Rust module + Python MCP tool wrapper\n")

    results = {}

    # Test 1: Rust module
    results["rust_module"] = test_rust_module()

    # Test 2: Python fallback
    results["python_fallback"] = test_python_fallback()

    # Test 3: MCP tool
    import asyncio
    results["mcp_tool"] = asyncio.run(test_mcp_tool())

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
