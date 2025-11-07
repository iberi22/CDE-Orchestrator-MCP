#!/usr/bin/env python3
"""
Semana 2 Automation Script - Documentation Governance Cleanup

This script performs:
1. Add YAML frontmatter metadata to 160+ files
2. Fix metadata enum violations (completed → archived)
3. Normalize filename conventions (UPPERCASE → lowercase-hyphens)

Target: Reduce governance violations from 88 to <20
Effort: 6-8 hours

Run with: python scripts/automation/semana2-cleanup.py
"""

import re
from pathlib import Path

# ============================================================================
# PHASE 1: ADD YAML FRONTMATTER TO MISSING FILES
# ============================================================================


def add_yaml_frontmatter(file_path: str) -> bool:
    """Add YAML frontmatter to files missing it."""
    path = Path(file_path)

    if not path.exists() or not path.suffix == ".md":
        return False

    content = path.read_text(encoding="utf-8")

    # Check if already has frontmatter
    if content.startswith("---"):
        return False

    # Extract title from filename
    title = path.stem.replace("-", " ").title()

    # Determine type based on directory
    if "agent-docs/execution" in str(path):
        doc_type = "execution"
    elif "agent-docs/sessions" in str(path):
        doc_type = "session"
    elif "agent-docs/feedback" in str(path):
        doc_type = "feedback"
    elif "agent-docs/research" in str(path):
        doc_type = "research"
    elif "specs/design" in str(path):
        doc_type = "design"
    elif "specs/features" in str(path):
        doc_type = "feature"
    elif "specs/tasks" in str(path):
        doc_type = "task"
    else:
        doc_type = "guide"

    # Generate llm_summary from content (first 2-3 sentences)
    lines = content.split("\n")[:10]
    summary = " ".join(lines).replace("#", "").strip()[:200]

    frontmatter = f"""---
title: "{title}"
description: "Documentation file for {doc_type}"
type: "{doc_type}"
status: "active"
created: "2025-11-07"
updated: "2025-11-07"
author: "Jules AI"
llm_summary: "{summary}..."
---

"""

    new_content = frontmatter + content
    path.write_text(new_content, encoding="utf-8")
    return True


# ============================================================================
# PHASE 2: FIX METADATA ENUM VIOLATIONS
# ============================================================================


def fix_status_enums(file_path: str) -> bool:
    """Fix invalid status enum values."""
    path = Path(file_path)

    if not path.exists() or not path.suffix == ".md":
        return False

    content = path.read_text(encoding="utf-8")
    original_content = content

    # Fix status enum violations
    replacements = {
        'status: "completed"': 'status: "archived"',
        'status: "in-progress"': 'status: "active"',
        'status: "ready"': 'status: "active"',
        'status: "done"': 'status: "archived"',
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    if content != original_content:
        path.write_text(content, encoding="utf-8")
        return True

    return False


def fix_date_formats(file_path: str) -> bool:
    """Fix date format violations (ISO 8601 → YYYY-MM-DD)."""
    path = Path(file_path)

    if not path.exists() or not path.suffix == ".md":
        return False

    content = path.read_text(encoding="utf-8")
    original_content = content

    # Match ISO 8601 dates and convert to YYYY-MM-DD
    iso_pattern = r"(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}Z"
    content = re.sub(iso_pattern, r"\1", content)

    if content != original_content:
        path.write_text(content, encoding="utf-8")
        return True

    return False


# ============================================================================
# PHASE 3: NORMALIZE FILENAME CONVENTIONS
# ============================================================================


def normalize_filename(file_path: str) -> tuple[str, bool]:
    """Convert filename from UPPERCASE to lowercase-hyphens."""
    path = Path(file_path)

    if not path.exists() or not path.suffix == ".md":
        return str(path), False

    # Skip if already lowercase
    if path.name.islower() or path.name == "README.md":
        return str(path), False

    # Convert to lowercase-hyphens
    new_name = path.name.lower().replace("_", "-")

    if new_name == path.name:
        return str(path), False

    new_path = path.parent / new_name
    path.rename(new_path)

    return str(new_path), True


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main() -> None:
    """Run all cleanup phases."""
    project_root = Path(".")

    print("=" * 70)
    print("SEMANA 2: DOCUMENTATION GOVERNANCE CLEANUP")
    print("=" * 70)

    # Phase 1: Add metadata
    print("\n📋 PHASE 1: Adding YAML metadata to files...")
    md_files = list(project_root.glob("**/*.md"))
    metadata_added = 0

    for md_file in md_files:
        if add_yaml_frontmatter(str(md_file)):
            metadata_added += 1

    print(f"✅ Added metadata to {metadata_added} files")

    # Phase 2: Fix enums
    print("\n🔧 PHASE 2: Fixing metadata enums and dates...")
    enum_fixed = 0
    date_fixed = 0

    for md_file in md_files:
        if fix_status_enums(str(md_file)):
            enum_fixed += 1
        if fix_date_formats(str(md_file)):
            date_fixed += 1

    print(f"✅ Fixed {enum_fixed} status enum violations")
    print(f"✅ Fixed {date_fixed} date format violations")

    # Phase 3: Normalize filenames
    print("\n📝 PHASE 3: Normalizing filename conventions...")
    renamed = 0

    for md_file in md_files:
        _, was_renamed = normalize_filename(str(md_file))
        if was_renamed:
            renamed += 1

    print(f"✅ Renamed {renamed} files to lowercase-hyphens pattern")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print(f"  - Metadata added: {metadata_added} files")
    print(f"  - Enum violations fixed: {enum_fixed} files")
    print(f"  - Date format fixed: {date_fixed} files")
    print(f"  - Filenames normalized: {renamed} files")
    print("\n✅ Cleanup complete! Run validation to check compliance:")
    print("   python scripts/validation/validate-docs.py --all")
    print("=" * 70)


if __name__ == "__main__":
    main()
