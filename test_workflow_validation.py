#!/usr/bin/env python3
"""Test workflow validation with Rust acceleration."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from cde_orchestrator.rust_utils import RUST_AVAILABLE

try:
    import cde_rust_core
except ImportError:
    print("❌ Rust module not available")
    sys.exit(1)


def test_workflow_validation():
    """Test parallel workflow validation."""
    print("=" * 80)
    print("Testing Rust Workflow Validation")
    print("=" * 80)

    if not RUST_AVAILABLE:
        print("❌ Rust not available")
        return

    print("\n✅ Rust module loaded")
    print(
        f"Available functions: {[f for f in dir(cde_rust_core) if not f.startswith('_')]}"
    )

    # Test validating .cde directory
    project_path = str(Path(__file__).parent / ".cde")

    if not Path(project_path).exists():
        print("\n⚠️  .cde directory not found, using project root")
        project_path = str(Path(__file__).parent)

    print(f"\n🔍 Validating workflows in: {project_path}")

    result_json = cde_rust_core.validate_workflows_py(project_path)
    report = json.loads(result_json)

    print("\n📊 Validation Report:")
    print(f"   Total files: {report['total_files']}")
    print(f"   Valid files: {report['valid_files']}")
    print(f"   Invalid files: {report['invalid_files']}")
    print(f"   Overall valid: {'✅' if report['valid'] else '❌'}")

    if report["workflows_found"]:
        print(f"\n✅ Workflows found ({len(report['workflows_found'])}):")
        for wf in report["workflows_found"]:
            print(f"   - {wf}")

    if report["missing_templates"]:
        print(f"\n⚠️  Missing templates ({len(report['missing_templates'])}):")
        for template in report["missing_templates"]:
            print(f"   - {template}")

    if report["issues"]:
        print(f"\n🔍 Issues ({len(report['issues'])}):")
        for issue in report["issues"][:10]:  # Show first 10
            severity_emoji = {"error": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(
                issue["severity"], "•"
            )
            file_name = Path(issue["file"]).name
            line = f":{issue['line']}" if issue["line"] else ""
            print(f"   {severity_emoji} {file_name}{line}: {issue['message']}")

        if len(report["issues"]) > 10:
            print(f"   ... and {len(report['issues']) - 10} more")

    print(f"\n📝 {report['summary']}")

    print("\n" + "=" * 80)
    print("✅ Workflow validation test completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_workflow_validation()
