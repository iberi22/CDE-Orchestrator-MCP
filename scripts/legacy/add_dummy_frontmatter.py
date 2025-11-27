import yaml
from pathlib import Path
from datetime import datetime

DEFAULT_FM = {
    "title": "Legacy Document",
    "description": "Legacy documentation file",
    "type": "guide",
    "status": "archived",
    "created": datetime.now().strftime("%Y-%m-%d"),
    "updated": datetime.now().strftime("%Y-%m-%d"),
    "author": "Legacy"
}

def add_frontmatter(root):
    for path in Path(root).rglob("*.md"):
        # Skip if allowed or invalid (tests, etc)
        if "tests/" in str(path) or ".github" in str(path):
            continue

        try:
            content = path.read_text(encoding="utf-8")
            if not content.startswith("---"):
                print(f"Adding frontmatter to {path}")
                # Customize title based on filename
                fm = DEFAULT_FM.copy()
                fm["title"] = path.stem.replace("-", " ").title()

                # Customize type based on dir
                if "agent-docs/execution" in str(path):
                    fm["type"] = "execution_report"
                elif "agent-docs/sessions" in str(path):
                    fm["type"] = "session"
                elif "agent-docs/research" in str(path):
                    fm["type"] = "research"

                fm_str = "---\n" + yaml.dump(fm, sort_keys=False) + "---\n\n"
                path.write_text(fm_str + content, encoding="utf-8")
        except Exception as e:
            print(f"Error {path}: {e}")

if __name__ == "__main__":
    add_frontmatter("docs")
    add_frontmatter("agent-docs")
    # Also fix specs/tasks/detailed-analysis.md if it exists and has bad yaml?
    # No, that file had *invalid* yaml, meaning it starts with --- but content is broken.
    # This script only handles missing ---.
