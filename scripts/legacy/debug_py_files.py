#!/usr/bin/env python3
"""Debug script to find which .py files are being excluded."""

import sys
from pathlib import Path

import pathspec

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)


def main():
    project_path = Path(".")
    use_case = ProjectAnalysisUseCase()

    # Load .gitignore spec
    gitignore_path = project_path / ".gitignore"
    spec = None
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
        print(f"✅ Loaded .gitignore with {len(spec.patterns)} patterns\n")

    # Collect all .py files
    print("🔍 Analyzing .py files...\n")
    all_py_files = list(project_path.rglob("*.py"))
    print(f"Total .py files found: {len(all_py_files)}\n")

    included = []
    excluded_by_dir = []
    excluded_by_pattern = []
    excluded_by_gitignore = []

    for py_file in all_py_files:
        try:
            relative_path = py_file.relative_to(project_path)

            # Check excluded directories
            if any(
                excluded_dir in relative_path.parts
                for excluded_dir in use_case.EXCLUDED_DIRS
            ):
                excluded_by_dir.append(str(relative_path))
                continue

            # Check excluded patterns
            if any(py_file.match(pattern) for pattern in use_case.EXCLUDED_PATTERNS):
                excluded_by_pattern.append(str(relative_path))
                continue

            # Check .gitignore
            if spec and spec.match_file(str(relative_path)):
                excluded_by_gitignore.append(str(relative_path))
                continue

            included.append(str(relative_path))
        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    print("📊 ANALYSIS RESULTS\n")
    print(f"   Included:                {len(included)}")
    print(f"   Excluded by dir:        {len(excluded_by_dir)}")
    print(f"   Excluded by pattern:    {len(excluded_by_pattern)}")
    print(f"   Excluded by .gitignore: {len(excluded_by_gitignore)}")
    print(f"   Total:                  {len(all_py_files)}\n")

    if excluded_by_dir:
        print(f"❌ EXCLUDED BY DIRECTORY ({len(excluded_by_dir)}):")
        for f in sorted(excluded_by_dir)[:10]:
            print(f"   {f}")
        if len(excluded_by_dir) > 10:
            print(f"   ... and {len(excluded_by_dir) - 10} more")

    if excluded_by_pattern:
        print(f"\n❌ EXCLUDED BY PATTERN ({len(excluded_by_pattern)}):")
        for f in sorted(excluded_by_pattern)[:10]:
            print(f"   {f}")
        if len(excluded_by_pattern) > 10:
            print(f"   ... and {len(excluded_by_pattern) - 10} more")

    if excluded_by_gitignore:
        print(f"\n❌ EXCLUDED BY .gitignore ({len(excluded_by_gitignore)}):")
        for f in sorted(excluded_by_gitignore)[:20]:
            print(f"   {f}")
        if len(excluded_by_gitignore) > 20:
            print(f"   ... and {len(excluded_by_gitignore) - 20} more")

    print(f"\n✅ INCLUDED ({len(included)}):")
    for f in sorted(included)[:20]:
        print(f"   {f}")
    if len(included) > 20:
        print(f"   ... and {len(included) - 20} more")


if __name__ == "__main__":
    main()
