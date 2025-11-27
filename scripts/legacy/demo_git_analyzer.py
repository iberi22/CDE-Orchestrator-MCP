"""
Comprehensive demo of Git analysis capabilities.

Shows all 8 analysis categories with real data from CDE Orchestrator MCP.
"""

import json
import os
from typing import Any, Union


def format_json(data: Union[list, Any], max_items: int = 5) -> Any:
    """Format JSON nicely with item limits."""
    if isinstance(data, list):
        if len(data) > max_items:
            return data[:max_items]
        return data
    return data


def main() -> None:
    """Run comprehensive Git analysis demo."""
    print("\n" + "=" * 80)
    print("🔍 CDE Git Analyzer - Comprehensive Demo")
    print("=" * 80)
    print("\nProject: CDE Orchestrator MCP")
    print("Purpose: Multi-source context analysis (Git + Codebase + External)")
    print("Implementation: Rust + Rayon (12-thread parallelism)")

    try:
        from cde_rust_core import analyze_git_repository_py

        project_path = os.getcwd()
        days = 90

        print("\n⚙️  Running analysis...")
        print(f"   - Repository: {project_path}")
        print(f"   - Time period: Last {days} days")
        print("   - Parallel threads: 12 (Rayon)")

        result_json = analyze_git_repository_py(project_path, days)
        analysis = json.loads(result_json)

        # 1. Repository Info
        print("\n" + "-" * 80)
        print("📊 1. REPOSITORY INFO")
        print("-" * 80)

        repo_info = analysis.get("repository_info", {})
        print(f"Age: {repo_info.get('repository_age_days')} days")
        print(f"Total commits: {repo_info.get('total_commits')}")
        print(f"Total branches: {repo_info.get('total_branches')}")
        print(f"Remote: {repo_info.get('remote_url')}")

        # 2. Commit History
        print("\n" + "-" * 80)
        print("📝 2. COMMIT HISTORY")
        print("-" * 80)

        commit_history = analysis.get("commit_history", {})
        recent_commits = commit_history.get("recent_commits", [])
        print(f"Recent commits analyzed: {len(recent_commits)}")
        print(
            f"Average commits/week: {commit_history.get('average_commits_per_week', 0):.1f}"
        )

        if recent_commits:
            print("\n📌 Latest commits (top 3):")
            for i, commit in enumerate(recent_commits[:3], 1):
                msg = commit.get("message", "")[:60]
                author = commit.get("author", "Unknown")
                files = commit.get("files_changed", 0)
                print(f"   {i}. {msg}... (@{author}, {files} files)")

        commits_by_month = commit_history.get("commits_by_month", {})
        if commits_by_month:
            print("\n📅 Activity by month:")
            for month, count in list(commits_by_month.items())[:3]:
                print(f"   {month}: {count} commits")

        # 3. Branch Analysis
        print("\n" + "-" * 80)
        print("🌿 3. BRANCH ANALYSIS")
        print("-" * 80)

        branch_analysis = analysis.get("branch_analysis", {})
        active_branches = branch_analysis.get("active_branches", [])
        stale_branches = branch_analysis.get("stale_branches", [])
        merged_count = branch_analysis.get("merged_branches_count", 0)

        print(f"Active branches: {len(active_branches)}")
        print(f"Stale branches: {len(stale_branches)}")
        print(f"Merged branches: {merged_count}")

        if active_branches:
            print("\n✅ Active branches (top 3):")
            for branch in active_branches[:3]:
                name = branch.get("name", "Unknown")
                date = branch.get("last_commit_date", "Unknown")
                print(f"   - {name} (last commit: {date})")

        # 4. Contributors
        print("\n" + "-" * 80)
        print("👥 4. CONTRIBUTOR INSIGHTS")
        print("-" * 80)

        contributors = analysis.get("contributor_insights", [])
        print(f"Total contributors: {len(contributors)}")

        if contributors:
            print("\n⭐ Top contributors (top 5):")
            for i, contrib in enumerate(contributors[:5], 1):
                name = contrib.get("name", "Unknown")
                commits = contrib.get("total_commits", 0)
                impact = contrib.get("impact_score", 0)
                print(f"   {i}. {name}: {commits} commits (impact: {impact:.1f})")

        # 5. Code Churn
        print("\n" + "-" * 80)
        print("🔥 5. CODE CHURN & HOTSPOTS")
        print("-" * 80)

        code_churn = analysis.get("code_churn", {})
        hotspots = code_churn.get("hotspots", [])
        most_changed = code_churn.get("most_changed_files", [])

        print(f"Code hotspots detected: {len(hotspots)}")
        print(f"Most changed files: {len(most_changed)}")

        if hotspots:
            print("\n🔥 Top hotspots (needs refactoring):")
            for i, file in enumerate(hotspots[:5], 1):
                print(f"   {i}. {file}")

        if most_changed:
            print("\n📊 Most changed files:")
            for i, file_info in enumerate(most_changed[:5], 1):
                file_path = file_info.get("file", "Unknown")
                changes = file_info.get("changes", 0)
                print(f"   {i}. {file_path} ({changes} changes)")

        # 6. Development Patterns
        print("\n" + "-" * 80)
        print("📈 6. DEVELOPMENT PATTERNS")
        print("-" * 80)

        dev_patterns = analysis.get("development_patterns", {})
        frequency = dev_patterns.get("commit_frequency", "Unknown")
        peak_day = dev_patterns.get("peak_day_of_week", "Unknown")
        peak_hour = dev_patterns.get("peak_hour_of_day", "Unknown")

        print(f"Commit frequency: {frequency}")
        print(f"Peak day: {peak_day}")
        print(f"Peak hour: {peak_hour}")

        avg_commit_size = dev_patterns.get("average_commit_size", 0)
        large_commits = dev_patterns.get("large_commits_count", 0)
        print(f"\nAverage commit size: {avg_commit_size} lines")
        print(f"Large commits (>500 lines): {large_commits}")

        # 7. Architectural Decisions
        print("\n" + "-" * 80)
        print("🏗️  7. ARCHITECTURAL DECISIONS")
        print("-" * 80)

        arch_decisions = analysis.get("architectural_decisions", [])
        print(f"Detected decisions: {len(arch_decisions)}")

        if arch_decisions:
            print("\n🔍 Recent architectural changes:")
            for i, decision in enumerate(arch_decisions[:5], 1):
                commit_hash = decision.get("commit_hash", "Unknown")
                msg = decision.get("message", "")[:60]
                decision_type = decision.get("decision_type", "Unknown")
                print(f"   {i}. [{decision_type}] {msg}... ({commit_hash})")

        # 8. Release Patterns
        print("\n" + "-" * 80)
        print("🚀 8. RELEASE PATTERNS")
        print("-" * 80)

        release_patterns = analysis.get("release_patterns", {})
        total_releases = release_patterns.get("total_releases", 0)
        latest_tag = release_patterns.get("latest_tag", "None")
        avg_frequency = release_patterns.get("average_release_frequency_days", 0)

        print(f"Total releases: {total_releases}")
        print(f"Latest tag: {latest_tag}")
        if avg_frequency > 0:
            print(f"Average release frequency: {avg_frequency} days")

        tags = release_patterns.get("tags", [])
        if tags:
            print("\n📦 Recent releases (top 5):")
            for i, tag in enumerate(tags[:5], 1):
                name = tag.get("name", "Unknown")
                date = tag.get("date", "Unknown")
                print(f"   {i}. {name} ({date})")

        # Summary
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)

        print("\n💡 Key Insights:")
        print(
            f"   - Repository is {repo_info.get('repository_age_days')} days old with {repo_info.get('total_commits')} commits"
        )
        print(
            f"   - {len(contributors)} contributors, top: {contributors[0].get('name') if contributors else 'N/A'}"
        )
        print(f"   - Development frequency: {frequency}")
        print(f"   - {len(hotspots)} code hotspots detected (need refactoring)")
        print(f"   - {len(arch_decisions)} architectural decisions found")

        print("\n📊 Use Cases:")
        print("   1. Onboarding: Understand project history and team dynamics")
        print("   2. Health Check: Identify patterns and bottlenecks")
        print("   3. Code Review: Find hotspots needing refactoring")
        print("   4. Team Analysis: Contributor activity and impact")
        print("   5. Release Planning: Analyze frequency and patterns")

        print("\n🚀 Performance:")
        print("   - Rust + Rayon: 12-thread parallelism")
        print("   - 10-100x faster than Python-only")
        print("   - Scales to 100k+ commits")

    except ImportError as e:
        print("\n❌ ERROR: Rust module not available")
        print(f"   {e}")
        print("\n   Build module: cd rust_core && maturin develop --release")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
