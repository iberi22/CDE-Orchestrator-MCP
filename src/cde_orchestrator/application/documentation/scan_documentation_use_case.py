"""
Scan Documentation Use Case - Optimized Version.

Analyzes project documentation structure and identifies issues.
Uses high-performance Rust core for I/O intensive operations.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class ScanDocumentationUseCase:
    """
    Scan and analyze documentation in a project.

    Provides immediate value by:
    - Finding all .md files
    - Checking YAML frontmatter
    - Detecting missing metadata
    - Identifying orphaned documents
    - Suggesting organizational improvements

    Uses Rust core for performance when available, falls back to Python.
    """

    def execute(self, project_path: str) -> Dict[str, Any]:
        """
        Scan documentation in project.

        Args:
            project_path: Root path of project to scan

        Returns:
            Dict with scan results including:
                - total_docs: Total markdown files found
                - by_type: Documents grouped by type/location
                - missing_metadata: Files without YAML frontmatter
                - orphaned_docs: Files not in standard directories
                - recommendations: List of improvement suggestions
        """
        project = Path(project_path)

        if not project.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

        # Try to use Rust core for performance
        try:
            import cde_rust_core

            rust_result = self._scan_with_rust(project_path)
            return self._process_rust_result(rust_result, project_path)
        except ImportError:
            # Fallback to Python implementation
            return self._scan_with_python(project_path)

    def _scan_with_rust(self, project_path: str) -> List[Dict[str, Any]]:
        """Use high-performance Rust core for scanning."""
        try:
            import cde_rust_core

            # Call the fast Rust scanning function
            result_json = cde_rust_core.scan_documentation_py(project_path)
            return json.loads(result_json)
        except ImportError:
            # Rust module not available, raise error to trigger fallback
            raise ImportError("Rust core module not available")
        except Exception as e:
            # Rust module failed, log and fallback to Python
            print(
                f"Warning: Rust scanning failed ({e}), falling back to Python implementation"
            )
            raise ImportError("Rust scanning failed")

    def _process_rust_result(
        self, rust_result: List[Dict[str, Any]], project_path: str
    ) -> Dict[str, Any]:
        """Process and enhance Rust scan results with Python logic."""
        project = Path(project_path)

        results = {
            "total_docs": len(rust_result),
            "scanned_at": datetime.now().isoformat(),
            "project_path": str(project),
            "by_location": {},
            "missing_metadata": [],
            "orphaned_docs": [],
            "large_files": [],
            "recommendations": [],
        }

        standard_dirs = {
            "specs/features": [],
            "specs/design": [],
            "specs/tasks": [],
            "specs/governance": [],
            "docs": [],
            "agent-docs/sessions": [],
            "agent-docs/execution": [],
            "agent-docs/feedback": [],
            "agent-docs/research": [],
            "root": [],
            "other": [],
        }

        for doc_data in rust_result:
            md_file = project / doc_data["path"]
            relative = md_file.relative_to(project)

            # Re-use Python logic for analysis
            file_info = {
                "path": str(relative),
                "size": len(doc_data["content"]),  # Approximation
                "lines": doc_data["content"].count("\n") + 1,
            }

            has_metadata = self._has_yaml_frontmatter(md_file)
            file_info["has_metadata"] = has_metadata
            if not has_metadata:
                results["missing_metadata"].append(str(relative))

            location = self._categorize_file(relative)
            standard_dirs[location].append(file_info)

            if file_info["lines"] > 1000:
                results["large_files"].append(
                    {"path": str(relative), "lines": file_info["lines"]}
                )

            if relative.parent == Path(".") and relative.name not in {
                "README.md",
                "CHANGELOG.md",
                "CONTRIBUTING.md",
                "CODE_OF_CONDUCT.md",
                "LICENSE.md",
                "AGENTS.md",
                "GEMINI.md",
            }:
                results["orphaned_docs"].append(str(relative))

        results["by_location"] = {
            loc: files for loc, files in standard_dirs.items() if files
        }
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _enhance_location_categorization(
        self, by_location: Dict[str, Any], project: Path
    ) -> Dict[str, Any]:
        """Enhance location categorization with additional Python logic."""
        # The Rust version provides basic categorization
        # Python can add more sophisticated analysis if needed
        return by_location

    def _scan_with_python(self, project_path: str) -> Dict[str, Any]:
        """Fallback Python implementation."""
        # Import here to avoid circular import
        from mcp_tools._progress_http import report_progress_http

        project = Path(project_path)

        # Find all markdown files
        md_files = list(project.rglob("*.md"))

        # Exclude common directories
        excluded_dirs = {
            ".git",
            ".venv",
            "node_modules",
            "venv",
            "__pycache__",
            ".pytest_cache",
        }
        md_files = [
            f
            for f in md_files
            if not any(excluded in f.parts for excluded in excluded_dirs)
        ]

        # Analyze each file
        results = {
            "total_docs": len(md_files),
            "scanned_at": datetime.now().isoformat(),
            "project_path": str(project),
            "by_location": {},
            "missing_metadata": [],
            "orphaned_docs": [],
            "large_files": [],
            "recommendations": [],
        }

        # Standard directories
        standard_dirs = {
            "specs/features": [],
            "specs/design": [],
            "specs/tasks": [],
            "specs/governance": [],
            "docs": [],
            "agent-docs/sessions": [],
            "agent-docs/execution": [],
            "agent-docs/feedback": [],
            "agent-docs/research": [],
            "root": [],
            "other": [],
        }

        # Report initial progress
        report_progress_http(
            "scanDocumentation", 0.0, f"Found {len(md_files)} markdown files to scan"
        )

        for idx, md_file in enumerate(md_files):
            relative = md_file.relative_to(project)
            file_info = {
                "path": str(relative),
                "size": md_file.stat().st_size,
                "lines": sum(
                    1 for _ in open(md_file, encoding="utf-8", errors="ignore")
                ),
            }

            # Check for YAML frontmatter
            has_metadata = self._has_yaml_frontmatter(md_file)
            file_info["has_metadata"] = has_metadata

            if not has_metadata:
                results["missing_metadata"].append(str(relative))

            # Categorize by location
            location = self._categorize_file(relative)
            standard_dirs[location].append(file_info)

            # Check for large files
            if file_info["lines"] > 1000:
                results["large_files"].append(
                    {
                        "path": str(relative),
                        "lines": file_info["lines"],
                    }
                )

            # Check if orphaned (root level .md files except standard ones)
            if relative.parent == Path(".") and relative.name not in {
                "README.md",
                "CHANGELOG.md",
                "CONTRIBUTING.md",
                "CODE_OF_CONDUCT.md",
                "LICENSE.md",
                "AGENTS.md",
                "GEMINI.md",
            }:
                results["orphaned_docs"].append(str(relative))

            # Report progress after each file
            progress = (idx + 1) / len(md_files)
            report_progress_http(
                "scanDocumentation",
                progress,
                f"Scanned {idx + 1}/{len(md_files)} files",
            )

        # Populate by_location
        results["by_location"] = {
            loc: files for loc, files in standard_dirs.items() if files
        }

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        # Report completion
        report_progress_http("scanDocumentation", 1.0, "Scan complete")

        return results

    def _has_yaml_frontmatter(self, file_path: Path) -> bool:
        """Check if file has valid YAML frontmatter."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(500)  # Read first 500 chars

            # Check for YAML frontmatter pattern
            pattern = r"^---\s*\n.*?\n---\s*\n"
            return bool(re.match(pattern, content, re.DOTALL))
        except Exception:
            return False

    def _categorize_file(self, relative_path: Path) -> str:
        """Categorize file by its location."""
        parts = relative_path.parts

        if len(parts) == 1:
            return "root"

        # Check standard directories
        if parts[0] == "specs":
            if len(parts) > 1:
                if parts[1] == "features":
                    return "specs/features"
                elif parts[1] == "design":
                    return "specs/design"
                elif parts[1] == "tasks":
                    return "specs/tasks"
                elif parts[1] == "governance":
                    return "specs/governance"
        elif parts[0] == "docs":
            return "docs"
        elif parts[0] == "agent-docs":
            if len(parts) > 1:
                if parts[1] == "sessions":
                    return "agent-docs/sessions"
                elif parts[1] == "execution":
                    return "agent-docs/execution"
                elif parts[1] == "feedback":
                    return "agent-docs/feedback"
                elif parts[1] == "research":
                    return "agent-docs/research"

        return "other"

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on scan results."""
        recommendations = []

        # Missing metadata
        missing_count = len(results["missing_metadata"])
        if missing_count > 0:
            recommendations.append(
                f"🔴 {missing_count} documents missing YAML frontmatter metadata. "
                f"Run cde_addMetadata to fix."
            )

        # Orphaned docs
        orphaned_count = len(results["orphaned_docs"])
        if orphaned_count > 0:
            recommendations.append(
                f"⚠️  {orphaned_count} orphaned documents in root directory. "
                f"Consider moving to appropriate subdirectories."
            )

        # Large files
        large_count = len(results["large_files"])
        if large_count > 0:
            recommendations.append(
                f"📝 {large_count} documents exceed 1000 lines. "
                f"Consider splitting into smaller, focused documents."
            )

        # Check directory structure
        if "specs/features" not in results["by_location"]:
            recommendations.append(
                "📁 No specs/features directory found. "
                "Create it to organize feature specifications."
            )

        if "docs" not in results["by_location"]:
            recommendations.append(
                "📁 No docs directory found. "
                "Create it to organize user-facing documentation."
            )

        # Success message
        if not recommendations:
            recommendations.append(
                "✅ Documentation structure looks good! All files properly organized."
            )

        return recommendations
