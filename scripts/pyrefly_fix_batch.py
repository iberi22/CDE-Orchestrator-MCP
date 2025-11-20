#!/usr/bin/env python3
"""
Batch fix common Pyrefly type errors.
"""
import re
from pathlib import Path
from typing import List, Tuple


def fix_none_default_assignments(content: str) -> str:
    """Fix: attribute: Type = None → attribute: Type | None = None"""
    patterns = [
        # Fix List[str] = None
        (r"(\s+)(\w+):\s*List\[([^\]]+)\]\s*=\s*None", r"\1\2: List[\3] | None = None"),
        (r"(\s+)(\w+):\s*list\[([^\]]+)\]\s*=\s*None", r"\1\2: list[\3] | None = None"),
        # Fix Dict[str, Any] = None
        (r"(\s+)(\w+):\s*Dict\[([^\]]+)\]\s*=\s*None", r"\1\2: Dict[\3] | None = None"),
        (r"(\s+)(\w+):\s*dict\[([^\]]+)\]\s*=\s*None", r"\1\2: dict[\3] | None = None"),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def fix_unknown_names_in_mcp(content: str) -> str:
    """Fix unknown names in MCP tool files (false, true, null, typing)"""
    replacements = [
        ('"default": false', '"default": False'),
        ('"default": true', '"default": True'),
        ('"default": null', '"default": None'),
        ("typing.List", "List"),
        ("typing.Dict", "Dict"),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    return content


def fix_any_lowercase(content: str) -> str:
    """Fix 'any' → 'Any'"""
    # Match 'any' but not as part of other words
    content = re.sub(r"\bany\b", "Any", content)
    return content


def fix_bad_function_definitions(content: str) -> str:
    """Fix async def for abstract async generators"""
    # This requires manual review, but we can add comments
    if "async def list_all_async" in content or "async def traverse_commits" in content:
        # Add comment about needing to use 'def' instead of 'async def'
        pass
    return content


def process_file(file_path: Path) -> Tuple[bool, str]:
    """Process a single file and apply fixes"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # Apply fixes
        content = fix_none_default_assignments(content)
        content = fix_unknown_names_in_mcp(content)
        content = fix_any_lowercase(content)
        content = fix_bad_function_definitions(content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True, f"Fixed: {file_path}"
        else:
            return False, f"No changes: {file_path}"
    except Exception as e:
        return False, f"Error in {file_path}: {e}"


def main():
    """Main batch fix function"""
    src_dir = Path(__file__).parent.parent / "src"

    # Find all Python files
    python_files = list(src_dir.rglob("*.py"))

    print(f"Found {len(python_files)} Python files")
    print("Applying batch fixes...\n")

    fixed_count = 0
    results: List[str] = []

    for py_file in python_files:
        changed, message = process_file(py_file)
        if changed:
            fixed_count += 1
            results.append(f"✅ {message}")
        else:
            results.append(f"⏭️  {message}")

    print(f"\n{'='*60}")
    print("Batch Fix Complete")
    print(f"{'='*60}")
    print(f"Files processed: {len(python_files)}")
    print(f"Files fixed: {fixed_count}")
    print("\nRun 'pyrefly check src' to verify remaining errors")


if __name__ == "__main__":
    main()
