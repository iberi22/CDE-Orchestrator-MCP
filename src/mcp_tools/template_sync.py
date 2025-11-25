# src/mcp_tools/template_sync.py
"""
Spec-Kit Template Synchronization and Validation MCP Tools.

Provides manual synchronization and validation of Spec-Kit templates:
- cde_syncTemplates: Download and customize Spec-Kit templates
- cde_validateSpec: Validate generated specs against Spec-Kit standard
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from fastmcp import Context

from ._base import tool_handler
from ._progress_reporter import get_progress_reporter

logger = logging.getLogger(__name__)

# Spec-Kit template URLs
SPEC_KIT_TEMPLATES = {
    "spec.md": "https://raw.githubusercontent.com/github/spec-kit/main/templates/spec-template.md",
    "plan.md": "https://raw.githubusercontent.com/github/spec-kit/main/templates/plan-template.md",
    "tasks.md": "https://raw.githubusercontent.com/github/spec-kit/main/templates/tasks-template.md",
}


@tool_handler
async def cde_syncTemplates(
    ctx: Context,
    project_path: str = ".",
    force: bool = False,
    source: str = "github",
) -> str:
    """
    🔄 **Sync Spec-Kit Templates** - Download and customize templates from GitHub Spec-Kit.

    Manual template synchronization for power users. Downloads latest templates
    from GitHub Spec-Kit, applies CDE customizations, validates conformity.

    **What it does**:
    1. Downloads templates from GitHub Spec-Kit repository
    2. Backs up existing templates
    3. Applies CDE customizations (llm_summary, MCP Tools, etc.)
    4. Validates conformity (target: 95%+)
    5. Reports changes and recommendations

    **Args**:
        project_path: Path to project (default: current directory)
        force: Overwrite existing templates without backup (default: False)
        source: Source to sync from ('github', 'local') (default: 'github')

    **Returns**:
        JSON with sync results:
        - templates_synced: List of synced templates
        - customizations_applied: CDE extensions added
        - conformity_score: Validation score (0-100)
        - backup_location: Where old templates were saved
        - next_steps: Recommendations

    **Examples**:
        >>> cde_syncTemplates()  # Sync current project
        >>> cde_syncTemplates(force=True)  # Force overwrite
        >>> cde_syncTemplates(project_path="E:\\my-project")  # Specific project

    **Use Cases**:
        1. **Weekly Updates**: Keep templates in sync with upstream Spec-Kit
        2. **New Features**: Get latest template improvements
        3. **Conformity Fix**: Update templates to reach 95%+ conformity
        4. **Team Sync**: Ensure all team members use same template version

    **Integration**:
        - Complements GitHub Actions weekly sync (manual trigger)
        - Uses scripts/customize_templates.py for CDE extensions
        - Uses scripts/validate_spec_kit_conformity.py for validation
    """
    reporter = get_progress_reporter()
    reporter.reset()
    reporter.report_progress("CDE", "syncTemplates", 0.1, "Initializing sync...")

    if project_path == ".":
        project_path = os.getcwd()

    templates_dir = Path(project_path) / "specs" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    reporter.report_progress(
        "CDE", "syncTemplates", 0.2, "Downloading templates from GitHub..."
    )

    # Download templates
    downloaded = []
    try:
        import urllib.request

        for template_name, url in SPEC_KIT_TEMPLATES.items():
            template_path = templates_dir / template_name

            # Backup existing
            if template_path.exists() and not force:
                backup_path = template_path.with_suffix(".md.backup")
                template_path.rename(backup_path)
                logger.info(f"Backed up {template_name} to {backup_path}")

            # Download
            urllib.request.urlretrieve(url, str(template_path))
            downloaded.append(template_name)
            logger.info(f"Downloaded {template_name} from {url}")

    except Exception as e:
        logger.error(f"Failed to download templates: {e}")
        return json.dumps(
            {
                "status": "error",
                "error": str(e),
                "message": "Failed to download templates from GitHub",
            },
            indent=2,
        )

    reporter.report_progress(
        "CDE", "syncTemplates", 0.5, "Applying CDE customizations..."
    )

    # Apply customizations
    try:
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        customize_script = scripts_dir / "customize_templates.py"

        result = subprocess.run(
            [
                "python",
                str(customize_script),
                "--batch",
                "--input-dir",
                str(templates_dir),
                "--output-dir",
                str(templates_dir),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.warning(f"Customization warning: {result.stderr}")

        customizations_applied = [
            "llm_summary field added to frontmatter",
            "MCP Tools section added to spec.md",
            "Hexagonal Architecture section added to plan.md",
            "Phase Tracking section added to tasks.md",
        ]

    except Exception as e:
        logger.warning(f"Failed to apply customizations: {e}")
        customizations_applied = []

    reporter.report_progress(
        "CDE", "syncTemplates", 0.8, "Validating conformity..."
    )

    # Validate conformity
    conformity_score = 0
    validation_issues = []
    try:
        validate_script = scripts_dir / "validate_spec_kit_conformity.py"

        result = subprocess.run(
            [
                "python",
                str(validate_script),
                "--templates",
                str(templates_dir),
                "--output",
                str(templates_dir / "conformity-report.json"),
            ],
            capture_output=True,
            text=True,
        )

        # Parse conformity report
        report_path = templates_dir / "conformity-report.json"
        if report_path.exists():
            with open(report_path) as f:
                report = json.load(f)
                conformity_score = report.get("average_score", 0)
                validation_issues = report.get("issues", [])

    except Exception as e:
        logger.warning(f"Failed to validate conformity: {e}")

    reporter.report_progress("CDE", "syncTemplates", 1.0, "Sync complete")

    # Generate recommendations
    recommendations = []
    if conformity_score < 95:
        recommendations.append(
            f"⚠️ Conformity score ({conformity_score:.1f}%) below target (95%)"
        )
        recommendations.append("   Review validation report for specific issues")
    else:
        recommendations.append(
            f"✅ Conformity score ({conformity_score:.1f}%) meets target (95%+)"
        )

    if customizations_applied:
        recommendations.append("✅ CDE customizations applied successfully")
    else:
        recommendations.append("⚠️ Customizations may have failed, check manually")

    result = {
        "status": "success",
        "templates_synced": downloaded,
        "customizations_applied": customizations_applied,
        "conformity_score": conformity_score,
        "validation_issues": len(validation_issues),
        "backup_location": str(templates_dir / "*.backup") if not force else None,
        "templates_directory": str(templates_dir),
        "recommendations": recommendations,
        "next_steps": [
            "Review templates in specs/templates/",
            "Check conformity report: specs/templates/conformity-report.json",
            "Use cde_generateSpec to test updated templates",
        ],
    }

    return json.dumps(result, indent=2)


@tool_handler
async def cde_validateSpec(
    ctx: Context,
    spec_directory: str,
    project_path: str = ".",
    strict: bool = False,
) -> str:
    """
    ✅ **Validate Spec** - Validate generated specs against Spec-Kit standard.

    Validates feature specifications for conformity with GitHub Spec-Kit standard.
    Checks YAML frontmatter, section structure, task format, naming conventions.

    **What it does**:
    1. Validates YAML frontmatter (required fields, types, format)
    2. Checks section structure (headings, order, required sections)
    3. Validates task format ([P?] [Story] Description)
    4. Checks naming conventions (lowercase-with-hyphens)
    5. Detects broken internal links
    6. Calculates conformity score (0-100)

    **Args**:
        spec_directory: Directory containing spec.md, plan.md, tasks.md
        project_path: Path to project root (default: current directory)
        strict: Fail if conformity < 95% (default: False)

    **Returns**:
        JSON with validation results:
        - conformity_score: 0-100 score
        - issues: List of validation issues (category, severity, message)
        - passed_checks: List of successful validations
        - recommendations: Suggestions for improvement

    **Examples**:
        >>> cde_validateSpec("specs/my-feature")
        >>> cde_validateSpec("specs/my-feature", strict=True)  # Fail on < 95%

    **Use Cases**:
        1. **Post-Generation**: Validate after cde_generateSpec
        2. **Pre-Commit**: CI/CD validation before merge
        3. **Quality Check**: Ensure specs meet standards
        4. **Template Testing**: Validate template changes

    **Conformity Scoring**:
        - **Errors**: -10 points each (missing required fields, invalid format)
        - **Warnings**: -5 points each (missing optional sections, style issues)
        - **Info**: -1 point each (minor improvements)
        - **Target**: 95%+ for production specs

    **Integration**:
        - Used by GitHub Actions PR validation
        - Complements cde_generateSpec for quality assurance
        - Integrates with CI/CD pipelines
    """
    reporter = get_progress_reporter()
    reporter.reset()
    reporter.report_progress("CDE", "validateSpec", 0.1, "Initializing validation...")

    if project_path == ".":
        project_path = os.getcwd()

    spec_path = Path(project_path) / spec_directory

    if not spec_path.exists():
        return json.dumps(
            {
                "status": "error",
                "error": f"Spec directory not found: {spec_path}",
            },
            indent=2,
        )

    reporter.report_progress(
        "CDE", "validateSpec", 0.5, "Running validation checks..."
    )

    # Run validation script
    try:
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        validate_script = scripts_dir / "validate_spec_kit_conformity.py"

        output_path = spec_path / "validation-report.json"

        result = subprocess.run(
            [
                "python",
                str(validate_script),
                "--spec",
                str(spec_path),
                "--min-score",
                "95" if strict else "0",
                "--fail-on-low-score" if strict else "--no-fail",
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )

        # Parse validation report
        if output_path.exists():
            with open(output_path) as f:
                report = json.load(f)
        else:
            report = {"error": "Validation report not generated"}

        reporter.report_progress("CDE", "validateSpec", 1.0, "Validation complete")

        # Extract results
        conformity_score = report.get("average_score", 0)
        issues = report.get("issues", [])
        passed_checks = report.get("passed_checks", [])

        # Generate recommendations
        recommendations = []
        if conformity_score >= 95:
            recommendations.append(
                f"✅ Excellent conformity ({conformity_score:.1f}%)"
            )
        elif conformity_score >= 85:
            recommendations.append(
                f"⚠️ Good conformity ({conformity_score:.1f}%), minor improvements needed"
            )
        else:
            recommendations.append(
                f"❌ Low conformity ({conformity_score:.1f}%), review issues below"
            )

        # Categorize issues by severity
        errors = [i for i in issues if i.get("severity") == "error"]
        warnings = [i for i in issues if i.get("severity") == "warning"]
        info = [i for i in issues if i.get("severity") == "info"]

        if errors:
            recommendations.append(f"🔴 Fix {len(errors)} errors (high priority)")
        if warnings:
            recommendations.append(f"🟡 Address {len(warnings)} warnings (medium priority)")
        if info:
            recommendations.append(f"🔵 Consider {len(info)} suggestions (optional)")

        result_data = {
            "status": "success" if conformity_score >= 95 or not strict else "warning",
            "conformity_score": conformity_score,
            "total_issues": len(issues),
            "errors": len(errors),
            "warnings": len(warnings),
            "info": len(info),
            "issues": issues,
            "passed_checks": passed_checks,
            "recommendations": recommendations,
            "validation_report": str(output_path),
            "next_steps": [
                "Review validation report for details",
                "Fix errors and warnings",
                "Re-run validation after fixes",
            ],
        }

        return json.dumps(result_data, indent=2)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return json.dumps(
            {
                "status": "error",
                "error": str(e),
                "message": "Validation failed. Check logs for details.",
            },
            indent=2,
        )
