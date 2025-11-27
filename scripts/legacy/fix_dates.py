import re
from pathlib import Path

def fix_date(content):
    # Replace ISO timestamps with YYYY-MM-DD
    # created: 2025-11-16T23:19:18.789462
    return re.sub(r'(created|updated): ["\']?(\d{4}-\d{2}-\d{2})T.*?["\']?', r'\1: "\2"', content)

def fix_files():
    print("Fixing dates in agent-docs...")
    for path in Path("agent-docs").rglob("*.md"):
        try:
            content = path.read_text(encoding="utf-8")
            new_content = fix_date(content)
            if content != new_content:
                path.write_text(new_content, encoding="utf-8")
                print(f"Fixed dates in {path}")
        except Exception as e:
            print(f"Error {path}: {e}")

if __name__ == "__main__":
    fix_files()
