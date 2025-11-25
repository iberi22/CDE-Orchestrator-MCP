import json
from pathlib import Path

import yaml


def calculate_score(missing_fields: list[str], missing_sections: list[str]) -> int:
    total_points = 100
    penalty_per_field = 10
    penalty_per_section = 15

    score = (
        total_points
        - (len(missing_fields) * penalty_per_field)
        - (len(missing_sections) * penalty_per_section)
    )
    return max(0, score)


def generate_recommendations(missing_fields: list[str], missing_sections: list[str]) -> list[str]:
    recommendations = []
    if missing_fields:
        recommendations.append(
            f"Add missing YAML frontmatter fields: {', '.join(missing_fields)}"
        )
    if missing_sections:
        recommendations.append(f"Add missing sections: {', '.join(missing_sections)}")
    return recommendations


def validate_template(template_path: Path, spec_kit_reference: dict) -> dict:
    """Compare CDE template against Spec-Kit reference."""

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter
    if content.startswith("---"):
        try:
            frontmatter = yaml.safe_load(content.split("---")[1])
        except yaml.YAMLError:
            frontmatter = {}
    else:
        frontmatter = {}

    # Check required fields
    required_fields = ["title", "description", "type", "status"]
    missing_fields = [f for f in required_fields if f not in frontmatter]

    # Check section structure
    required_sections = spec_kit_reference.get("required_sections", [])
    missing_sections = [s for s in required_sections if s not in content]

    return {
        "template": str(template_path),
        "conformity_score": calculate_score(missing_fields, missing_sections),
        "missing_fields": missing_fields,
        "missing_sections": missing_sections,
        "recommendations": generate_recommendations(missing_fields, missing_sections),
    }


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validate_spec_kit_conformity.py <template_path>")
        sys.exit(1)

    template_path = Path(sys.argv[1])

    # Mock reference for now
    reference = {"required_sections": ["## Summary", "## Technical Context"]}

    result = validate_template(template_path, reference)
    print(json.dumps(result, indent=2))
