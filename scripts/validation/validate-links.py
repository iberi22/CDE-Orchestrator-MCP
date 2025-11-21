#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation Link Validator and Repair Tool.

Validates internal markdown links in documentation:
- Checks if referenced files exist
- Detects common path typos (specs/featres, etc.)
- Identifies orphaned files (no incoming links)
- Generates repair suggestions and automated fixes

Usage:
    python scripts/validation/validate-links.py --check
    python scripts/validation/validate-links.py --fix
    python scripts/validation/validate-links.py --report
    python scripts/validation/validate-links.py --orphans
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


class LinkValidator:
    """Validates and repairs markdown links in documentation."""

    def __init__(self, root_path: Optional[Path] = None) -> None:
        """Initialize validator with project root."""
        self.root = root_path or Path.cwd()
        self.all_markdown_files: Set[Path] = set()
        self.broken_links: List[Dict] = []
        self.fixed_links: List[Dict] = []
        self.orphaned_files: Set[Path] = set()
        self.link_references: Dict[Path, Set[Path]] = defaultdict(set)

        # Common typo patterns and corrections
        self.typo_corrections = {
            "specs/featres/": "specs/features/",
            "specs/desgin/": "specs/design/",
            "specs/taask/": "specs/tasks/",
            "agent-docs/excecution/": "agent-docs/execution/",
            "agent-docs/sesions/": "agent-docs/sessions/",
            "agent-docs/feedbcak/": "agent-docs/feedback/",
        }

    def discover_markdown_files(self) -> int:
        """Discover all markdown files in project."""
        self.all_markdown_files = set(self.root.rglob("*.md"))
        print(
            f"{Colors.CYAN}Found {len(self.all_markdown_files)} markdown files{Colors.ENDC}"
        )
        return len(self.all_markdown_files)

    def extract_links(self, content: str, file_path: Path) -> List[Tuple[str, int]]:
        """Extract all markdown links from content."""
        links = []

        # Pattern 1: [text](path) format
        pattern1 = r"\[([^\]]+)\]\(([^\)]+)\)"
        for match in re.finditer(pattern1, content):
            link = match.group(2).strip()
            line_num = content[: match.start()].count("\n") + 1
            links.append((link, line_num))

        # Pattern 2: Direct file references
        pattern2 = r"(?:^|\s)(specs/[a-z]+/[^\s`<>\[\]()]+\.md|agent-docs/[a-z]+/[^\s`<>\[\]()]+\.md)"
        for match in re.finditer(pattern2, content, re.MULTILINE):
            link = match.group(1).strip()
            line_num = content[: match.start()].count("\n") + 1
            links.append((link, line_num))

        return links

    def normalize_link(self, link: str) -> Tuple[Optional[str], bool]:
        """
        Normalize and validate link.

        Returns:
            (normalized_path, was_corrected)
        """
        # Remove anchor fragments
        if "#" in link:
            link = link.split("#")[0]

        # Remove query parameters
        if "?" in link:
            link = link.split("?")[0]

        # Check for typos and correct them
        corrected = False
        for typo, correction in self.typo_corrections.items():
            if typo in link:
                link = link.replace(typo, correction)
                corrected = True

        normalized: Optional[str] = link or None
        return normalized, corrected

    def resolve_link(self, link: str, from_file: Path) -> Optional[Path]:
        """Resolve link to actual file path."""
        if not link:
            return None

        normalized_link, _ = self.normalize_link(link)
        if not normalized_link:
            return None

        # Try absolute path (from project root)
        absolute = self.root / normalized_link
        if absolute.exists() and absolute.is_file():
            return absolute

        # Try relative to document directory
        relative = from_file.parent / normalized_link
        if relative.exists() and relative.is_file():
            return relative

        return None

    def validate_file_links(self, file_path: Path) -> List[Dict]:
        """Validate all links in a file."""
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return [{"type": "read_error", "file": file_path, "error": str(e)}]

        links = self.extract_links(content, file_path)

        for link, line_num in links:
            if not link or link.startswith("http"):  # Skip external links
                continue

            normalized, was_corrected = self.normalize_link(link)
            if not normalized:
                continue

            resolved = self.resolve_link(link, file_path)

            if resolved:
                # Link is valid
                self.link_references[resolved].add(file_path)

                # Report correction if typo was fixed
                if was_corrected:
                    issues.append(
                        {
                            "type": "typo_corrected",
                            "file": file_path,
                            "line": line_num,
                            "original": link,
                            "corrected": normalized,
                            "target": resolved,
                        }
                    )
            else:
                # Link is broken
                issues.append(
                    {
                        "type": "broken_link",
                        "file": file_path,
                        "line": line_num,
                        "link": normalized or link,
                        "original": link,
                    }
                )

        return issues

    def find_orphaned_files(self) -> Set[Path]:
        """Find markdown files with no incoming links."""
        orphaned = set()

        excluded_patterns = {
            "README.md",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "AGENTS.md",
            "GEMINI.md",
            "readme.md",
            "index.md",
        }

        for file_path in self.all_markdown_files:
            # Check excluded patterns
            if file_path.name in excluded_patterns:
                continue

            # Check if file has incoming links
            if file_path not in self.link_references:
                orphaned.add(file_path)

        return orphaned

    def validate_all(self) -> int:
        """Validate all markdown files."""
        print(f"\n{Colors.HEADER}Validating Documentation Links{Colors.ENDC}")
        print("=" * 60)

        self.discover_markdown_files()

        issues_count = 0
        files_with_issues = 0

        for file_path in sorted(self.all_markdown_files):
            issues = self.validate_file_links(file_path)
            if issues:
                if files_with_issues == 0:
                    print()
                files_with_issues += 1
                issues_count += len(issues)
                self.broken_links.extend(issues)

                rel_path = file_path.relative_to(self.root)
                print(f"{Colors.YELLOW}Warning: {rel_path}{Colors.ENDC}")

                for issue in issues:
                    if issue["type"] == "broken_link":
                        print(
                            f"   L{issue['line']}: {Colors.RED}ERROR{Colors.ENDC} {issue['original']}"
                        )
                    elif issue["type"] == "typo_corrected":
                        print(
                            f"   L{issue['line']}: {Colors.YELLOW}TYPO{Colors.ENDC} {issue['original']} -> {issue['corrected']}"
                        )

        # Find orphaned files
        orphaned = self.find_orphaned_files()
        if orphaned:
            print(f"\n{Colors.YELLOW}Orphaned Files (no incoming links):{Colors.ENDC}")
            for file_path in sorted(orphaned):
                rel_path = file_path.relative_to(self.root)
                print(f"   {Colors.YELLOW}*{Colors.ENDC} {rel_path}")
            self.orphaned_files = orphaned

        # Summary
        print(f"\n{Colors.HEADER}Summary{Colors.ENDC}")
        print(f"Total files checked: {len(self.all_markdown_files)}")
        print(f"Files with issues: {files_with_issues}")
        print(f"Total issues: {issues_count}")

        broken_count = len([i for i in self.broken_links if i["type"] == "broken_link"])
        typo_count = len(
            [i for i in self.broken_links if i["type"] == "typo_corrected"]
        )

        if broken_count > 0:
            print(f"{Colors.RED}  Broken links: {broken_count}{Colors.ENDC}")
        if typo_count > 0:
            print(f"{Colors.YELLOW}  Typos detected: {typo_count}{Colors.ENDC}")
        if orphaned:
            print(f"{Colors.YELLOW}  Orphaned files: {len(orphaned)}{Colors.ENDC}")

        return broken_count

    def fix_broken_links(self) -> int:
        """Auto-fix broken links and typos."""
        print(f"\n{Colors.HEADER}Auto-Fixing Links{Colors.ENDC}")
        print("=" * 60)

        fixed_count = 0

        for issue in self.broken_links:
            file_path = issue["file"]

            if issue["type"] == "typo_corrected":
                original = issue["original"]
                corrected = issue["corrected"]

                try:
                    content = file_path.read_text(encoding="utf-8")
                    new_content = content.replace(original, corrected)

                    if new_content != content:
                        file_path.write_text(new_content, encoding="utf-8")
                        fixed_count += 1

                        rel_path = file_path.relative_to(self.root)
                        print(
                            f"{Colors.GREEN}FIXED{Colors.ENDC} {rel_path}:L{issue['line']}"
                        )
                        print(f"  {original} -> {corrected}")
                except Exception as e:
                    print(f"{Colors.RED}ERROR{Colors.ENDC} {file_path}: {e}")

        print(f"\n{Colors.GREEN}Fixed {fixed_count} issues{Colors.ENDC}")
        return fixed_count

    def generate_report(self) -> str:
        """Generate detailed link validation report."""
        report_lines = []
        report_lines.append("# Link Validation Report")
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append("")

        # Stats
        broken_count = len([i for i in self.broken_links if i["type"] == "broken_link"])
        typo_count = len(
            [i for i in self.broken_links if i["type"] == "typo_corrected"]
        )

        report_lines.append("## Statistics")
        report_lines.append(f"- Total markdown files: {len(self.all_markdown_files)}")
        report_lines.append(f"- Broken links: {broken_count}")
        report_lines.append(f"- Typos detected: {typo_count}")
        report_lines.append(f"- Orphaned files: {len(self.orphaned_files)}")
        report_lines.append("")

        # Broken links
        if broken_count > 0:
            report_lines.append("## Broken Links")
            for issue in [i for i in self.broken_links if i["type"] == "broken_link"]:
                file_path = issue["file"].relative_to(self.root)
                report_lines.append(
                    f"- `{file_path}` Line {issue['line']}: `{issue['original']}`"
                )
            report_lines.append("")

        # Typos
        if typo_count > 0:
            report_lines.append("## Typos Detected")
            for issue in [
                i for i in self.broken_links if i["type"] == "typo_corrected"
            ]:
                file_path = issue["file"].relative_to(self.root)
                report_lines.append(
                    f"- `{file_path}` Line {issue['line']}: `{issue['original']}` -> `{issue['corrected']}`"
                )
            report_lines.append("")

        # Orphaned
        if self.orphaned_files:
            report_lines.append("## Orphaned Files")
            for file_path in sorted(self.orphaned_files):
                file_path = file_path.relative_to(self.root)
                report_lines.append(f"- `{file_path}`")
            report_lines.append("")

        return "\n".join(report_lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate and repair documentation links"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check all links (default)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix broken links and typos",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report",
    )
    parser.add_argument(
        "--orphans",
        action="store_true",
        help="Find orphaned files",
    )

    args = parser.parse_args()

    validator = LinkValidator()

    # Default to check if no args
    if not any([args.check, args.fix, args.report, args.orphans]):
        args.check = True

    # Validate
    broken_count = 0
    if args.check or args.fix or args.orphans:
        broken_count = validator.validate_all()

    # Fix
    if args.fix:
        validator.fix_broken_links()

    # Report
    if args.report:
        report = validator.generate_report()
        report_path = Path("agent-docs/execution/link-validation-report.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"\n{Colors.GREEN}SAVED: {report_path}{Colors.ENDC}")

    # Return appropriate exit code
    if broken_count > 0 and not args.fix:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
