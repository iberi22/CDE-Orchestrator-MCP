#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidad CLI para ejecutar Pyrefly en el proyecto CDE Orchestrator MCP.

Usage:
    python scripts/pyrefly_check.py [--fix] [--report] [--watch]
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def run_pyrefly_check(paths: list[str], json_output: bool = False) -> int:
    """Ejecuta Pyrefly type checker."""
    cmd = ["pyrefly", "check"] + paths
    if json_output:
        cmd.append("--json")

    result = subprocess.run(cmd)
    return result.returncode


def run_pyrefly_watch(paths: list[str]) -> int:
    """Ejecuta Pyrefly en modo watch."""
    cmd = ["pyrefly", "check", "--watch"] + paths
    result = subprocess.run(cmd)
    return result.returncode


def generate_report() -> int:
    """Genera reporte detallado."""
    script_path = Path(__file__).parent / "pyrefly_report.py"
    result = subprocess.run([sys.executable, str(script_path)])
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Pyrefly type checking utility for CDE Orchestrator MCP"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate detailed markdown report"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run in watch mode (recheck on file changes)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["src", "tests"],
        help="Paths to check (default: src tests)",
    )

    args = parser.parse_args()

    if args.report:
        print("📊 Generating Pyrefly report...")
        return generate_report()
    elif args.watch:
        print(f"👀 Watching {', '.join(args.paths)} for changes...")
        return run_pyrefly_watch(args.paths)
    else:
        print(f"🔍 Type checking {', '.join(args.paths)}...")
        return run_pyrefly_check(args.paths, args.json)


if __name__ == "__main__":
    sys.exit(main())
