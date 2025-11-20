#!/usr/bin/env python3
"""Debug gitignore matching in both implementations."""

import sys
from pathlib import Path

import pathspec

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_gitignore_matching():
    """Test if gitignore patterns are matching correctly."""

    project_path = Path(".")
    gitignore_path = project_path / ".gitignore"

    print("🔍 Loading .gitignore patterns\n")

    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            content = f.read()
            lines = [
                l.strip()
                for l in content.split("\n")
                if l.strip() and not l.strip().startswith("#")
            ]
            print(f"Total patterns: {len(lines)}\n")

            # Show first 20 patterns
            print("First 20 patterns:")
            for i, pattern in enumerate(lines[:20], 1):
                print(f"  {i:2d}. {pattern}")

            if len(lines) > 20:
                print(f"\n... and {len(lines) - 20} more patterns")

    # Test some specific paths
    print("\n\n🔍 Testing specific paths against .gitignore\n")

    spec = pathspec.PathSpec.from_lines(
        "gitwildmatch", Path(gitignore_path).read_text().split("\n")
    )

    test_paths = [
        ".cde/issues/local-20251120-010817.md",
        "specs/features/test.md",
        "scripts/test.py",
        "servers/cde/test.py",
        "src/cde_orchestrator/test.py",
    ]

    for test_path in test_paths:
        matches = spec.match_file(test_path)
        status = "❌ IGNORED" if matches else "✅ INCLUDED"
        print(f"{status:15} {test_path}")


if __name__ == "__main__":
    test_gitignore_matching()
