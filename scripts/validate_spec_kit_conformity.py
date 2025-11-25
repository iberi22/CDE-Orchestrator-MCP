"""
Validate CDE templates against GitHub Spec-Kit standards.

This script performs comprehensive validation to ensure CDE templates maintain
95%+ conformity with Spec-Kit while preserving CDE-specific extensions.

Validation Checks:
1. YAML Frontmatter: Required fields present and valid
2. Section Structure: All required sections present in correct order
3. Naming Conventions: File and directory names match Spec-Kit patterns
4. Task Format: Tasks follow [ID] [P?] [Story] Description format
5. Link Integrity: Internal links resolve correctly

Usage:
    python validate_spec_kit_conformity.py --templates specs/templates/
    python validate_spec_kit_conformity.py --spec specs/my-feature/
    python validate_spec_kit_conformity.py --min-score 95 --fail-on-low-score
"""

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Spec-Kit Standard Configurations
SPEC_KIT_REFERENCES = {
    "spec.md": {
        "required_fields": [
            "title",
            "description",
            "type",
            "status",
            "created",
            "updated",
            "author",
        ],
        "optional_fields": ["llm_summary"],  # CDE extension
        "required_sections": [
            "## Summary",
            "## User Stories",
            "## Requirements",
            "## Acceptance Criteria",
        ],
        "optional_sections": [
            "## Non-Functional Requirements",
            "## Out of Scope",
            "## 🛠️ MCP Tools Available",  # CDE extension
        ],
        "naming_pattern": r"^[a-z0-9-]+\.md$",
    },
    "plan.md": {
        "required_fields": [
            "title",
            "description",
            "type",
            "status",
            "created",
            "updated",
            "author",
        ],
        "optional_fields": ["llm_summary"],
        "required_sections": [
            "## Overview",
            "## Architecture",
            "## Implementation Details",
            "## Testing Strategy",
        ],
        "optional_sections": [
            "## Performance Considerations",
            "## Security Considerations",
            "## Hexagonal Architecture Patterns",  # CDE extension
        ],
        "naming_pattern": r"^[a-z0-9-]+\.md$",
    },
    "tasks.md": {
        "required_fields": [
            "title",
            "description",
            "type",
            "status",
            "created",
            "updated",
            "author",
        ],
        "optional_fields": ["llm_summary"],
        "required_sections": ["## Tasks"],
        "optional_sections": ["## Phase Tracking"],  # CDE extension
        "task_pattern": r"^\s*\d+\.\s+\[P\d+\]\s+\[.*?\]\s+.+$",  # [ID] [P?] [Story] Description
        "naming_pattern": r"^[a-z0-9-]+\.md$",
    },
}


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a template."""

    category: str  # 'frontmatter', 'section', 'naming', 'task_format', 'link'
    severity: str  # 'error', 'warning', 'info'
    message: str
    location: str = ""  # File path or line number


@dataclass
class ValidationResult:
    """Result of template validation."""

    template: str
    conformity_score: int
    passed_checks: list[str] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "template": self.template,
            "conformity_score": self.conformity_score,
            "passed_checks": self.passed_checks,
            "issues": [
                {
                    "category": issue.category,
                    "severity": issue.severity,
                    "message": issue.message,
                    "location": issue.location,
                }
                for issue in self.issues
            ],
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }


def extract_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content

    try:
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content

        frontmatter = yaml.safe_load(parts[1])
        body = parts[2]
        return frontmatter or {}, body
    except yaml.YAMLError as e:
        return {"_parse_error": str(e)}, content


def validate_frontmatter(
    frontmatter: dict[str, Any], reference: dict[str, Any]
) -> list[ValidationIssue]:
    """Validate YAML frontmatter fields."""
    issues = []

    # Check for parse errors
    if "_parse_error" in frontmatter:
        issues.append(
            ValidationIssue(
                category="frontmatter",
                severity="error",
                message=f"YAML parse error: {frontmatter['_parse_error']}",
            )
        )
        return issues

    # Check required fields
    required_fields = reference.get("required_fields", [])
    for field in required_fields:
        if field not in frontmatter:
            issues.append(
                ValidationIssue(
                    category="frontmatter",
                    severity="error",
                    message=f"Missing required field: {field}",
                )
            )
        elif not frontmatter[field]:
            issues.append(
                ValidationIssue(
                    category="frontmatter",
                    severity="warning",
                    message=f"Empty required field: {field}",
                )
            )

    # Check field types
    if "created" in frontmatter and not isinstance(frontmatter["created"], str):
        issues.append(
            ValidationIssue(
                category="frontmatter",
                severity="warning",
                message="Field 'created' should be string (YYYY-MM-DD format)",
            )
        )

    if "updated" in frontmatter and not isinstance(frontmatter["updated"], str):
        issues.append(
            ValidationIssue(
                category="frontmatter",
                severity="warning",
                message="Field 'updated' should be string (YYYY-MM-DD format)",
            )
        )

    return issues


def validate_sections(content: str, reference: dict[str, Any]) -> list[ValidationIssue]:
    """Validate markdown section structure."""
    issues = []
    required_sections = reference.get("required_sections", [])

    for section in required_sections:
        if section not in content:
            issues.append(
                ValidationIssue(
                    category="section",
                    severity="error",
                    message=f"Missing required section: {section}",
                )
            )

    return issues


def validate_task_format(content: str, reference: dict[str, Any]) -> list[ValidationIssue]:
    """Validate task format for tasks.md."""
    issues = []

    if "task_pattern" not in reference:
        return issues  # Not a tasks.md file

    # Find tasks section
    if "## Tasks" not in content:
        return issues  # Already caught by section validation

    tasks_section = content.split("## Tasks")[1].split("##")[0] if "## Tasks" in content else ""

    # Extract numbered list items
    task_pattern = re.compile(r"^\s*\d+\.\s+(.+)$", re.MULTILINE)
    tasks = task_pattern.findall(tasks_section)

    # Validate each task
    expected_pattern = reference["task_pattern"]
    for idx, task in enumerate(tasks, 1):
        if not re.match(r"\[P\d+\]\s+\[.*?\]\s+.+", task):
            issues.append(
                ValidationIssue(
                    category="task_format",
                    severity="warning",
                    message=f"Task {idx} doesn't follow [P?] [Story] Description format: {task[:50]}...",
                    location=f"Task {idx}",
                )
            )

    return issues


def validate_naming(file_path: Path, reference: dict[str, Any]) -> list[ValidationIssue]:
    """Validate file naming conventions."""
    issues = []
    naming_pattern = reference.get("naming_pattern")

    if naming_pattern and not re.match(naming_pattern, file_path.name):
        issues.append(
            ValidationIssue(
                category="naming",
                severity="warning",
                message=f"Filename doesn't match Spec-Kit pattern: {naming_pattern}",
                location=str(file_path),
            )
        )

    return issues


def validate_links(content: str, base_path: Path) -> list[ValidationIssue]:
    """Validate internal markdown links."""
    issues = []

    # Find all markdown links [text](path)
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    links = link_pattern.findall(content)

    for text, path in links:
        # Skip external links
        if path.startswith(("http://", "https://", "#")):
            continue

        # Check if file exists
        target_path = (base_path / path).resolve()
        if not target_path.exists():
            issues.append(
                ValidationIssue(
                    category="link",
                    severity="warning",
                    message=f"Broken link: [{text}]({path})",
                )
            )

    return issues


def calculate_conformity_score(issues: list[ValidationIssue]) -> int:
    """Calculate conformity score (0-100) based on issues."""
    total_points = 100
    penalties = {"error": 10, "warning": 5, "info": 1}

    score = total_points
    for issue in issues:
        score -= penalties.get(issue.severity, 0)

    return max(0, score)


def generate_recommendations(issues: list[ValidationIssue]) -> list[str]:
    """Generate actionable recommendations based on issues."""
    recommendations = []

    # Group issues by category
    by_category: dict[str, list[ValidationIssue]] = {}
    for issue in issues:
        by_category.setdefault(issue.category, []).append(issue)

    # Frontmatter recommendations
    if "frontmatter" in by_category:
        missing_fields = [
            i.message.split(": ")[1]
            for i in by_category["frontmatter"]
            if "Missing required field" in i.message
        ]
        if missing_fields:
            recommendations.append(
                f"➡️ Add missing YAML frontmatter fields: {', '.join(missing_fields)}"
            )

    # Section recommendations
    if "section" in by_category:
        missing_sections = [
            i.message.split(": ")[1]
            for i in by_category["section"]
            if "Missing required section" in i.message
        ]
        if missing_sections:
            recommendations.append(
                f"➡️ Add missing sections: {', '.join(missing_sections)}"
            )

    # Task format recommendations
    if "task_format" in by_category:
        recommendations.append(
            "➡️ Fix task format: Use [P?] [Story] Description pattern for all tasks"
        )

    # Link recommendations
    if "link" in by_category:
        recommendations.append("➡️ Fix broken internal links")

    # General best practices
    if not issues:
        recommendations.append("✅ Template is fully conformant with Spec-Kit standards")
    elif len(issues) <= 3:
        recommendations.append("✅ Template is mostly conformant, minor improvements needed")
    else:
        recommendations.append("⚠️ Template needs significant updates for Spec-Kit conformity")

    return recommendations


def validate_template(template_path: Path, spec_kit_reference: dict[str, Any]) -> ValidationResult:
    """Perform comprehensive template validation."""
    if not template_path.exists():
        return ValidationResult(
            template=str(template_path),
            conformity_score=0,
            issues=[
                ValidationIssue(
                    category="file",
                    severity="error",
                    message=f"File not found: {template_path}",
                )
            ],
            recommendations=["Create the template file"],
        )

    # Read content
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)

    # Collect all issues
    all_issues: list[ValidationIssue] = []
    passed_checks: list[str] = []

    # Validate frontmatter
    frontmatter_issues = validate_frontmatter(frontmatter, spec_kit_reference)
    all_issues.extend(frontmatter_issues)
    if not frontmatter_issues:
        passed_checks.append("✅ YAML frontmatter complete and valid")

    # Validate sections
    section_issues = validate_sections(content, spec_kit_reference)
    all_issues.extend(section_issues)
    if not section_issues:
        passed_checks.append("✅ Required sections present")

    # Validate task format (for tasks.md)
    task_issues = validate_task_format(content, spec_kit_reference)
    all_issues.extend(task_issues)
    if not task_issues and "task_pattern" in spec_kit_reference:
        passed_checks.append("✅ Task format correct")

    # Validate naming
    naming_issues = validate_naming(template_path, spec_kit_reference)
    all_issues.extend(naming_issues)
    if not naming_issues:
        passed_checks.append("✅ Naming conventions followed")

    # Validate links
    link_issues = validate_links(content, template_path.parent)
    all_issues.extend(link_issues)
    if not link_issues:
        passed_checks.append("✅ No broken internal links")

    # Calculate score
    conformity_score = calculate_conformity_score(all_issues)

    # Generate recommendations
    recommendations = generate_recommendations(all_issues)

    # Metadata
    metadata = {
        "file_size": template_path.stat().st_size,
        "line_count": len(content.split("\n")),
        "has_frontmatter": bool(frontmatter and "_parse_error" not in frontmatter),
        "spec_kit_reference": spec_kit_reference.get("required_sections", []),
    }

    return ValidationResult(
        template=str(template_path),
        conformity_score=conformity_score,
        passed_checks=passed_checks,
        issues=all_issues,
        recommendations=recommendations,
        metadata=metadata,
    )


def validate_directory(directory: Path, min_score: int = 95) -> dict[str, Any]:
    """Validate all templates in a directory."""
    results = {}

    for template_name, reference in SPEC_KIT_REFERENCES.items():
        template_path = directory / template_name
        if template_path.exists():
            result = validate_template(template_path, reference)
            results[template_name] = result.to_dict()

    # Overall summary
    total_score = sum(r["conformity_score"] for r in results.values())
    avg_score = total_score / len(results) if results else 0

    summary = {
        "directory": str(directory),
        "templates_validated": len(results),
        "average_score": avg_score,
        "min_score_required": min_score,
        "passed": avg_score >= min_score,
        "results": results,
    }

    return summary


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate CDE templates against Spec-Kit standards"
    )
    parser.add_argument(
        "--templates",
        type=Path,
        help="Directory containing templates to validate",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        help="Specific feature spec directory to validate",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=95,
        help="Minimum conformity score required (default: 95)",
    )
    parser.add_argument(
        "--fail-on-low-score",
        action="store_true",
        help="Exit with code 1 if score below minimum",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write JSON report to file",
    )

    args = parser.parse_args()

    if not args.templates and not args.spec:
        parser.error("Either --templates or --spec must be provided")

    # Validate directory
    target_dir = args.templates or args.spec
    if not target_dir or not target_dir.exists():
        print(f"❌ Directory not found: {target_dir}")
        exit(1)

    print(f"🔍 Validating templates in: {target_dir}")
    summary = validate_directory(target_dir, args.min_score)

    # Print summary
    print(f"\n📊 Validation Summary")
    print(f"  Templates validated: {summary['templates_validated']}")
    print(f"  Average score: {summary['average_score']:.1f}/100")
    print(f"  Status: {'✅ PASSED' if summary['passed'] else '❌ FAILED'}")

    # Print individual results
    for template_name, result in summary["results"].items():
        print(f"\n📄 {template_name}")
        print(f"  Score: {result['conformity_score']}/100")
        print(f"  Passed checks: {len(result['passed_checks'])}")
        print(f"  Issues: {len(result['issues'])}")

        if result["issues"]:
            print("  Issues:")
            for issue in result["issues"]:
                icon = "🔴" if issue["severity"] == "error" else "⚠️"
                print(f"    {icon} {issue['message']}")

    # Write output file
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"\n💾 Report saved to: {args.output}")

    # Exit with appropriate code
    if args.fail_on_low_score and not summary["passed"]:
        print(f"\n❌ Conformity score below minimum ({args.min_score})")
        exit(1)


if __name__ == "__main__":
    main()
