#!/usr/bin/env python3
"""Find which .md files are being excluded by .gitignore in Python."""

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

    # Collect all .md files
    print("🔍 Analyzing .md files...\n")
    all_md_files = list(project_path.rglob("*.md"))
    print(f"Total .md files found: {len(all_md_files)}\n")

    excluded_by_gitignore = []
    included = []

    for md_file in all_md_files:
        try:
            relative_path = md_file.relative_to(project_path)

            # Check excluded directories
            if any(
                excluded_dir in relative_path.parts
                for excluded_dir in use_case.EXCLUDED_DIRS
            ):
                continue  # Skip, not gitignore-related

            # Check .gitignore
            if spec and spec.match_file(str(relative_path)):
                excluded_by_gitignore.append(str(relative_path))
                continue

            included.append(str(relative_path))
        except Exception as e:
            print(f"Error processing {md_file}: {e}")

    print("📊 .MD FILE ANALYSIS\n")
    print(f"   Included:                {len(included)}")
    print(f"   Excluded by .gitignore: {len(excluded_by_gitignore)}")
    print(f"   Total:                  {len(all_md_files)}\n")

    if excluded_by_gitignore:
        print(f"❌ EXCLUDED BY .gitignore ({len(excluded_by_gitignore)}):")
        for f in sorted(excluded_by_gitignore):
            print(f"   {f}")

    print(f"\n✅ INCLUDED ({len(included)}):")
    for f in sorted(included):
        print(f"   {f}")


if __name__ == "__main__":
    main()
