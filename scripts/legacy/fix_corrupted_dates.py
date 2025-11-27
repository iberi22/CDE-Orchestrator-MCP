import re
from pathlib import Path

def fix_corrupted(content):
    # Fix: created: "2025-11-16"23:19:18.789462"
    # To: created: "2025-11-16"
    # The trailing quote from original might still be there if my previous regex didn't catch it end.
    # Original: created: "2025...T..."
    # My regex replaced start.
    # Let's match line by line.

    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith("created:") or line.strip().startswith("updated:"):
            # Extract date
            match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if match:
                date = match.group(1)
                new_lines.append(f'{line.split(":")[0]}: "{date}"')
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

def fix_files():
    print("Fixing corrupted dates...")
    for path in Path("agent-docs").rglob("*.md"):
        try:
            content = path.read_text(encoding="utf-8")
            new_content = fix_corrupted(content)
            # Ensure final newline if it had one
            if content.endswith("\n") and not new_content.endswith("\n"):
                new_content += "\n"

            if content != new_content:
                path.write_text(new_content, encoding="utf-8")
                print(f"Fixed {path}")
        except Exception as e:
            print(f"Error {path}: {e}")

if __name__ == "__main__":
    fix_files()
