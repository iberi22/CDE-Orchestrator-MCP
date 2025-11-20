#!/usr/bin/env python
# pyrefly: disable-error-code = "missing-attribute"
"""Test Rust project scanner implementation."""
import json
import time

import cde_rust_core  # type: ignore

# Test Rust implementation
excluded_dirs = [
    "node_modules",
    "__pycache__",
    ".venv",
    "target",
    "dist",
    "build",
    "out",
    "htmlcov",
    "ci-wheels",
    "temp-wheels",
    "vendor",
    ".git",
    ".cargo",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "env",
    "venv",
    ".gradle",
    ".m2",
    "bin",
    "obj",
]

excluded_patterns = [
    "*.map",
    "*.vsix",
    "*.whl",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dylib",
    "*.dll",
    "*.exe",
    "*.lock",
]

print("=" * 60)
print("RUST PROJECT SCANNER TEST")
print("=" * 60)
print()

start = time.time()
result_json = cde_rust_core.scan_project_py(".", excluded_dirs, excluded_patterns)
result = json.loads(result_json)
total_time = (time.time() - start) * 1000  # Convert to ms

print("✅ Rust Analysis Complete")
print(f"   Files analyzed: {result['file_count']}")
print(f"   Analysis time (Rust): {result['analysis_time_ms']}ms")
print(f"   Total time (incl. Python): {total_time:.0f}ms")
print(f"   Languages detected: {len(result['language_stats'])}")
print(f"   Dependency files: {result['dependency_files']}")
print()

print("Top 5 file extensions:")
stats = sorted(result["language_stats"].items(), key=lambda x: x[1], reverse=True)
for ext, count in stats[:5]:
    print(f"   {ext}: {count}")
print()

print(f"Excluded directories: {len(result['excluded_directories'])}")
print(f"Total excluded: {result['excluded_count']}")
