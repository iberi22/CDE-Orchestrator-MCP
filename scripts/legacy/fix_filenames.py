import os
from pathlib import Path

SKIP_DIRS = {".git", ".github", "node_modules", "venv", ".venv", "__pycache__"}
# Whitelist for naming validation (case insensitive check)
WHITELIST = {
    "README.MD", "SKILL.MD", "SKILL_TEMPLATE.MD",
    "AGENTS.MD", "CHANGELOG.MD", "CONTRIBUTING.MD", "LICENSE", "CODE_OF_CONDUCT.MD"
}

def fix_filenames(root="."):
    print("Starting filename fix...")
    count = 0
    for path in Path(root).rglob("*.md"):
        # Skip hidden/ignored dirs
        if any(part in SKIP_DIRS for part in path.parts):
            continue

        # Skip whitelisted filenames
        if path.name.upper() in WHITELIST:
            continue

        new_name = path.name.lower().replace(" ", "-")
        # Replace underscores with hyphens?
        # validate-docs says: "Use hyphens for spaces". It allows underscores in regex: `^[a-z0-9\-_.]+\.md$`
        # So underscores are fine.

        if new_name != path.name:
            new_path = path.with_name(new_name)
            try:
                path.rename(new_path)
                print(f"Renamed: {path} -> {new_path}")
                count += 1
            except Exception as e:
                print(f"Error renaming {path}: {e}")

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    fix_filenames()
