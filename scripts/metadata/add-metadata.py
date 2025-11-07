#!/usr/bin/env python3
"""
Auto-add Metadata Script for CDE Orchestrator MCP.

Automatically generates and inserts YAML frontmatter for markdown files
that are missing it.

Usage:
    python scripts/metadata/add-metadata.py --path specs/features/my-doc.md
    python scripts/metadata/add-metadata.py --all --dry-run
    python scripts/metadata/add-metadata.py --directory specs/features/
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)

# Type inference from directory
DIR_TO_TYPE = {
    "specs/features": "feature",
    "specs/design": "design",
    "specs/tasks": "task",
    "specs/governance": "governance",
    "docs": "guide",
    "agent-docs/sessions": "session",
    "agent-docs/execution": "execution",
    "agent-docs/feedback": "feedback",
    "agent-docs/research": "research",
}


class MetadataGenerator:
    """Generates YAML frontmatter for markdown files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def has_frontmatter(self, content: str) -> bool:
        """Check if content already has YAML frontmatter."""
        return content.startswith("---")

    def infer_type(self, file_path: Path) -> Optional[str]:
        """Infer document type from file location."""
        relative_path = file_path.relative_to(self.repo_root)

        for dir_pattern, doc_type in DIR_TO_TYPE.items():
            if str(relative_path).startswith(dir_pattern):
                return doc_type

        return None

    def extract_title(self, content: str) -> Optional[str]:
        """Extract title from first H1 heading."""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def generate_description(self, content: str, title: Optional[str]) -> str:
        """Generate description from content."""
        # Try to find first paragraph after title
        lines = content.split("\n")
        description_lines = []

        in_frontmatter = False
        found_title = False

        for line in lines:
            line = line.strip()

            # Skip frontmatter if present
            if line == "---":
                in_frontmatter = not in_frontmatter
                continue

            if in_frontmatter:
                continue

            # Skip title
            if line.startswith("#"):
                found_title = True
                continue

            # Skip empty lines before description
            if not found_title or not line:
                continue

            # Found description
            if line and not line.startswith(">") and not line.startswith("-"):
                description_lines.append(line)
                if len(" ".join(description_lines)) >= 50:
                    break

        description = " ".join(description_lines)[:150]

        if not description and title:
            description = title

        if len(description) < 50:
            description = f"{description} - Documentation for CDE Orchestrator MCP"

        return description

    def generate_llm_summary(self, content: str, title: str, doc_type: str) -> str:
        """Generate LLM-optimized summary."""
        # Extract first few paragraphs
        paragraphs = []
        lines = content.split("\n")

        in_frontmatter = False
        in_code_block = False

        for line in lines:
            line = line.strip()

            if line == "---":
                in_frontmatter = not in_frontmatter
                continue

            if in_frontmatter:
                continue

            if line.startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block or not line or line.startswith("#"):
                continue

            paragraphs.append(line)

            if len(" ".join(paragraphs)) >= 200:
                break

        summary_text = " ".join(paragraphs)[:300]

        # Build 3-sentence pattern
        type_desc = {
            "feature": "Feature specification",
            "design": "Design document",
            "task": "Task roadmap",
            "governance": "Governance document",
            "guide": "User guide",
            "session": "Agent session summary",
            "execution": "Execution report",
            "feedback": "Agent feedback",
            "research": "Research notes",
        }

        sentence1 = f"{type_desc.get(doc_type, 'Document')} for {title}."
        sentence2 = (
            summary_text if summary_text else "Detailed information and guidelines."
        )
        sentence3 = f"Reference when working with {doc_type} documentation."

        return f"{sentence1}\n  {sentence2}\n  {sentence3}"

    def extract_tags(self, file_path: Path, content: str) -> list:
        """Extract relevant tags from file name and content."""
        tags = set()

        # Add from file name
        file_name = file_path.stem.lower()
        tags.update(file_name.split("-"))

        # Common keywords from content
        keywords = [
            "python",
            "migration",
            "testing",
            "deployment",
            "architecture",
            "authentication",
            "security",
            "api",
            "database",
            "performance",
            "documentation",
            "workflow",
            "orchestration",
            "mcp",
            "spec-kit",
        ]

        content_lower = content.lower()
        for keyword in keywords:
            if keyword in content_lower:
                tags.add(keyword)

        return sorted(list(tags))[:6]  # Max 6 tags

    def generate_metadata(
        self, file_path: Path, author: str = "Auto-Generated"
    ) -> Dict:
        """Generate complete metadata for a file."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        doc_type = self.infer_type(file_path) or "guide"
        title = self.extract_title(content) or file_path.stem.replace("-", " ").title()
        description = self.generate_description(content, title)
        llm_summary = self.generate_llm_summary(content, title, doc_type)
        tags = self.extract_tags(file_path, content)

        today = datetime.now().strftime("%Y-%m-%d")

        metadata = {
            "title": title,
            "description": description,
            "type": doc_type,
            "status": "draft",
            "created": today,
            "updated": today,
            "author": author,
            "tags": tags,
            "llm_summary": llm_summary,
        }

        return metadata

    def insert_frontmatter(
        self, file_path: Path, metadata: Dict, dry_run: bool = False
    ) -> bool:
        """Insert frontmatter at the beginning of file."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if self.has_frontmatter(content):
            print(f"SKIP: {file_path.name} already has frontmatter")
            return False

        # Generate YAML
        yaml_content = yaml.dump(
            metadata, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        frontmatter = f"---\n{yaml_content}---\n\n"

        new_content = frontmatter + content

        if dry_run:
            print(f"DRY-RUN: Would add metadata to {file_path.name}")
            print(frontmatter)
            return True

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ Added metadata to {file_path.name}")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Add metadata to markdown files")
    parser.add_argument("--path", type=str, help="Add metadata to specific file")
    parser.add_argument(
        "--directory", type=str, help="Add metadata to all files in directory"
    )
    parser.add_argument(
        "--all", action="store_true", help="Add metadata to all markdown files"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without writing"
    )
    parser.add_argument(
        "--author", type=str, default="Auto-Generated", help="Author name to use"
    )

    args = parser.parse_args()

    # Determine repo root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent

    generator = MetadataGenerator(repo_root)

    # Determine which files to process
    files_to_process = []

    if args.path:
        file_path = Path(args.path)
        if not file_path.is_absolute():
            file_path = repo_root / file_path
        files_to_process = [file_path]
    elif args.directory:
        dir_path = Path(args.directory)
        if not dir_path.is_absolute():
            dir_path = repo_root / dir_path
        files_to_process = list(dir_path.glob("*.md"))
    elif args.all:
        files_to_process = list(repo_root.glob("**/*.md"))
    else:
        parser.print_help()
        return 1

    # Process files
    processed = 0
    skipped = 0

    for file_path in files_to_process:
        if not file_path.exists():
            print(f"SKIP: {file_path} (does not exist)")
            skipped += 1
            continue

        # Skip hidden directories
        relative_path = file_path.relative_to(repo_root)
        if any(
            part.startswith(".")
            for part in relative_path.parts
            if part not in [".github", ".cde"]
        ):
            skipped += 1
            continue

        try:
            metadata = generator.generate_metadata(file_path, author=args.author)
            if generator.insert_frontmatter(file_path, metadata, dry_run=args.dry_run):
                processed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"ERROR processing {file_path.name}: {e}")
            skipped += 1

    # Summary
    print("\n" + "=" * 80)
    print(f"Total files: {len(files_to_process)}")
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")

    if args.dry_run:
        print("\n⚠️  DRY-RUN MODE: No files were modified")

    return 0


if __name__ == "__main__":
    sys.exit(main())
