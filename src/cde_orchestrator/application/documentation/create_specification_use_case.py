from datetime import datetime
from pathlib import Path

import yaml


class CreateSpecificationUseCase:
    def execute(
        self, project_path: str, feature_name: str, description: str, author: str
    ) -> dict:
        specs_dir = Path(project_path) / "specs" / "features"
        specs_dir.mkdir(parents=True, exist_ok=True)

        filename = feature_name.lower().replace(" ", "-") + ".md"
        filepath = specs_dir / filename

        if filepath.exists():
            return {"error": f"Specification file already exists at {filepath}"}

        now = datetime.now().strftime("%Y-%m-%d")

        frontmatter = {
            "title": feature_name,
            "description": description,
            "type": "feature",
            "status": "draft",
            "created": now,
            "updated": now,
            "author": author,
        }

        content = f"---\n{yaml.dump(frontmatter)}---\n\n# {feature_name}\n"

        try:
            filepath.write_text(content, encoding="utf-8")
            return {"filepath": str(filepath)}
        except IOError as e:
            return {"error": f"Failed to write file: {e}"}
