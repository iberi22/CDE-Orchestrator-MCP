#!/usr/bin/env python3
"""
Fix Document Types Script for CDE Orchestrator MCP.

Corrects document types in YAML frontmatter based on governance rules.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)

# Correct type mapping based on directory and governance rules
# Order matters: more specific paths first (longest to shortest)
DIR_TO_CORRECT_TYPE = [
    ("agent-docs/sessions", "session"),
    ("agent-docs/execution", "execution"),
    ("agent-docs/feedback", "feedback"),
    ("agent-docs/research", "research"),
    ("specs/templates", "guide"),  # Templates are guides
    ("specs/reviews", "feedback"),  # Reviews are feedback
    ("specs/governance", "governance"),
    ("specs/features", "feature"),
    ("specs/design", "design"),
    ("specs/tasks", "task"),
    ("specs/api", "design"),  # API docs are design docs
    ("memory", "governance"),  # Constitution is governance
    ("scripts", "guide"),  # Script docs are guides
    (".github", "guide"),  # GitHub docs are guides
    ("docs", "guide"),
    (".", "guide"),  # Root level docs are guides (README, etc.)
]

# Status corrections for agent-docs
AGENT_DOCS_STATUS_CORRECTIONS = {
    "completed": "active",  # Agent docs shouldn't be "completed"
}

class TypeFixer:
    """Fixes document types in YAML frontmatter."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def get_correct_type(self, file_path: Path) -> str:
        """Get the correct document type based on file location."""
        relative_path = file_path.relative_to(self.repo_root)
        path_parts = relative_path.parts

        # Check each directory pattern in order of specificity (most specific first)
        for dir_pattern, doc_type in DIR_TO_CORRECT_TYPE:
            if dir_pattern == ".":
                # Root level files - only if no directory parts
                if len(path_parts) == 1:
                    return doc_type
            else:
                # Check if path starts with this directory pattern
                pattern_parts = dir_pattern.split('/')
                if len(path_parts) > len(pattern_parts):
                    if path_parts[:len(pattern_parts)] == tuple(pattern_parts):
                        return doc_type

        # Default to guide for unknown locations
        return "guide"

    def fix_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """Fix the document type in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith("---"):
                return False  # No frontmatter to fix

            # Split frontmatter from content
            parts = content.split("---", 2)
            if len(parts) < 3:
                return False

            frontmatter_text = parts[1]
            body = parts[2]

            # Parse YAML
            try:
                metadata = yaml.safe_load(frontmatter_text)
            except yaml.YAMLError:
                return False

            if not isinstance(metadata, dict):
                return False

            # Get correct type
            correct_type = self.get_correct_type(file_path)
            current_type = metadata.get('type', '')
            changed = False

            # Fix status for agent-docs
            if str(file_path).startswith(str(self.repo_root / "agent-docs")):
                current_status = metadata.get('status', '')
                if current_status in AGENT_DOCS_STATUS_CORRECTIONS:
                    metadata['status'] = AGENT_DOCS_STATUS_CORRECTIONS[current_status]
                    changed = True

            # Check if type needs fixing
            if current_type != correct_type:
                metadata['type'] = correct_type
                changed = True

            if not changed:
                return False

            if dry_run:
                changes = []
                if current_type != correct_type:
                    changes.append(f"type: '{current_type}' → '{correct_type}'")
                if str(file_path).startswith(str(self.repo_root / "agent-docs")):
                    old_status = metadata.get('status', '')
                    if old_status in AGENT_DOCS_STATUS_CORRECTIONS:
                        changes.append(f"status: '{old_status}' → '{AGENT_DOCS_STATUS_CORRECTIONS[old_status]}'")
                print(f"DRY-RUN: Would change {', '.join(changes)} in {file_path}")
                return True

            # Write back
            new_frontmatter = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
            new_content = f"---\n{new_frontmatter}---{body}"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            changes = []
            if current_type != correct_type:
                changes.append(f"type from '{current_type}' to '{correct_type}'")
            if str(file_path).startswith(str(self.repo_root / "agent-docs")):
                old_status = metadata.get('status', '')
                if old_status in AGENT_DOCS_STATUS_CORRECTIONS:
                    changes.append(f"status from '{old_status}' to '{AGENT_DOCS_STATUS_CORRECTIONS[old_status]}'")
            print(f"✅ Fixed {', '.join(changes)} in {file_path}")
            return True

        except Exception as e:
            print(f"ERROR processing {file_path}: {e}")
            return False

        return False

    def fix_all(self, dry_run: bool = False) -> tuple[int, int]:
        """Fix all markdown files in the repository."""
        fixed = 0
        total = 0

        for md_file in self.repo_root.rglob("*.md"):
            total += 1
            if self.fix_file(md_file, dry_run):
                fixed += 1

        return fixed, total


def main():
    parser = argparse.ArgumentParser(description="Fix document types in YAML frontmatter")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without modifying files")
    parser.add_argument("--path", type=str, help="Fix a specific file path")

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent.parent  # scripts/metadata/ -> scripts/ -> root
    fixer = TypeFixer(repo_root)

    if args.path:
        file_path = Path(args.path)
        if not file_path.is_absolute():
            file_path = repo_root / file_path

        if fixer.fix_file(file_path, args.dry_run):
            print(f"Fixed 1 file")
        else:
            print("No changes needed")
    else:
        fixed, total = fixer.fix_all(args.dry_run)
        print(f"Processed {total} files, fixed {fixed} files")


if __name__ == "__main__":
    main()