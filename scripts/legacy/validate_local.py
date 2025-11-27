#!/usr/bin/env python3
"""
Comprehensive Local Validation for Nexus AI MCP Server
Verifica que TODOS los componentes funcionen correctamente sin Docker.

Tests:
1. Python environment & dependencies
2. Rust module compilation & import
3. MCP server initialization
4. Core MCP tools execution
5. Workflow orchestration
6. File system operations
"""
import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class ValidationReport:
    """Track validation results."""

    def __init__(self) -> None:
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures: list[tuple[str, str | None]] = []

    def test(self, name: str, passed: bool, error: str | None = None) -> None:
        """Record test result."""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"[OK] {name}")
        else:
            self.tests_failed += 1
            self.failures.append((name, error))
            print(f"[FAIL] {name}")
            if error:
                print(f"       Error: {error}")

    def summary(self) -> bool:
        """Print final summary."""
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")

        if self.failures:
            print("\nFailed Tests:")
            for name, error in self.failures:
                print(f"  - {name}")
                if error:
                    print(f"    {error}")

        success = self.tests_failed == 0
        print(f"\nResult: {'SUCCESS' if success else 'FAILURE'}")
        return success


async def validate_environment(report: ValidationReport) -> None:
    """Phase 1: Validate Python environment."""
    print("\n[PHASE 1] Python Environment")
    print("-" * 60)

    # Python version
    import sys

    version = sys.version_info
    passed = version >= (3, 11)
    error_msg: str | None = None if passed else "Python 3.11+ required"
    report.test(
        f"Python version >= 3.11 (found {version.major}.{version.minor}.{version.micro})",
        passed,
        error_msg,
    )

    # Virtual environment
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    report.test("Virtual environment active", in_venv)

    # Critical dependencies
    deps = [
        ("fastmcp", "fastmcp"),
        ("pydantic", "pydantic"),
        ("yaml", "pyyaml"),
        ("dotenv", "python-dotenv"),
        ("aiohttp", "aiohttp"),
    ]
    for module_name, package_name in deps:
        try:
            __import__(module_name)
            report.test(f"Dependency '{package_name}' installed", True)
        except ImportError as e:
            report.test(f"Dependency '{package_name}' installed", False, str(e))


async def validate_rust(report: ValidationReport) -> None:
    """Phase 2: Validate Rust module."""
    print("\n[PHASE 2] Rust Module")
    print("-" * 60)

    # Import Rust module
    try:
        import cde_rust_core

        report.test("Rust module 'cde_rust_core' imported", True)

        # Check exported functions
        functions = [x for x in dir(cde_rust_core) if not x.startswith("_")]
        expected = [
            "scan_documentation_py",
            "analyze_documentation_quality_py",
            "scan_project_py",
            "validate_workflows_py",
        ]

        for func in expected:
            has_func = func in functions
            report.test(f"Rust function '{func}' available", has_func)

    except ImportError as e:
        report.test("Rust module 'cde_rust_core' imported", False, str(e))


async def validate_server(report: ValidationReport) -> None:
    """Phase 3: Validate MCP server."""
    print("\n[PHASE 3] MCP Server Initialization")
    print("-" * 60)

    # Import server
    try:
        from server import app

        report.test("MCP server module imported", True)

        # Get tools
        try:
            tools = await app.get_tools()
            tool_count = len(tools)
            report.test(f"MCP tools registered ({tool_count} tools)", tool_count > 0)

            # Check critical tools
            critical_tools = [
                "cde_startFeature",
                "cde_selectWorkflow",
                "cde_scanDocumentation",
                "cde_executeWithBestAgent",
            ]

            for tool_name in critical_tools:
                has_tool = tool_name in tools
                report.test(f"Critical tool '{tool_name}' registered", has_tool)

        except Exception as e:
            report.test("MCP tools retrieved", False, str(e))

    except Exception as e:
        report.test("MCP server module imported", False, str(e))


async def validate_tools(report: ValidationReport) -> None:
    """Phase 4: Validate MCP tool execution."""
    print("\n[PHASE 4] MCP Tool Execution")
    print("-" * 60)

    import inspect

    # Test cde_checkRecipes
    try:
        from mcp_tools import cde_checkRecipes

        if inspect.iscoroutinefunction(cde_checkRecipes):
            result = await cde_checkRecipes()
        else:
            result = cde_checkRecipes()

        data = json.loads(result)
        report.test("Tool 'cde_checkRecipes' executed", True)
        print(f"       .cde/ exists: {data.get('exists')}")

    except Exception as e:
        report.test("Tool 'cde_checkRecipes' executed", False, str(e))

    # Test cde_scanDocumentation
    try:
        from mcp_tools import cde_scanDocumentation

        if inspect.iscoroutinefunction(cde_scanDocumentation):
            result = await cde_scanDocumentation(detail_level="name_only")
        else:
            result = cde_scanDocumentation(detail_level="name_only")

        data = json.loads(result)
        report.test("Tool 'cde_scanDocumentation' executed", True)
        print(f"       Found {data.get('total', 0)} documentation files")

    except Exception as e:
        report.test("Tool 'cde_scanDocumentation' executed", False, str(e))


async def validate_workflows(report: ValidationReport) -> None:
    """Phase 5: Validate workflow orchestration."""
    print("\n[PHASE 5] Workflow Orchestration")
    print("-" * 60)

    import inspect

    # Test selectWorkflow
    try:
        from mcp_tools import cde_selectWorkflow

        test_prompt = "Add user authentication feature"

        if inspect.iscoroutinefunction(cde_selectWorkflow):
            result = await cde_selectWorkflow(test_prompt)
        else:
            result = cde_selectWorkflow(test_prompt)

        data = json.loads(result)
        report.test("Workflow selection executed", True)
        print(f"       Workflow type: {data.get('workflow_type')}")
        print(f"       Complexity: {data.get('complexity')}")

    except Exception as e:
        report.test("Workflow selection executed", False, str(e))


async def validate_filesystem(report: ValidationReport) -> None:
    """Phase 6: Validate filesystem operations."""
    print("\n[PHASE 6] Filesystem Operations")
    print("-" * 60)

    # Check critical directories
    project_root = Path(__file__).parent

    dirs = [
        ("src/", "Source code directory"),
        ("specs/", "Specifications directory"),
        ("tests/", "Tests directory"),
        (".cde/", "CDE workspace directory"),
    ]

    for dir_path, description in dirs:
        full_path = project_root / dir_path
        exists = full_path.exists()
        report.test(f"{description} exists", exists)


async def main() -> bool:
    """Run all validations."""
    print("=" * 60)
    print("NEXUS AI LOCAL VALIDATION")
    print("=" * 60)
    print("Testing all components without Docker...\n")

    report = ValidationReport()

    await validate_environment(report)
    await validate_rust(report)
    await validate_server(report)
    await validate_tools(report)
    await validate_workflows(report)
    await validate_filesystem(report)

    success = report.summary()
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
