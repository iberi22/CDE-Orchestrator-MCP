# src/cde_orchestrator/application/onboarding/framework_detector.py
"""
Framework Detector - Identifies frameworks, libraries, and architecture patterns.

Detects:
- Web frameworks: Next.js, React, Vue, Angular
- Backend frameworks: FastAPI, Django, Flask, Express
- MCP frameworks: FastMCP
- Architecture patterns: Hexagonal, Clean Architecture, MVC
"""
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class FrameworkDetector:
    """
    Detects frameworks, libraries, and architectural patterns in a project.

    Detection methods:
    - Configuration files (next.config.js, pyproject.toml, package.json)
    - Directory structure (src/domain/, src/application/)
    - Import patterns (from fastapi import, from mcp import)

    Provides context about project type and architecture for documentation.
    """

    # Framework signatures: file patterns and import patterns
    FRAMEWORK_SIGNATURES = {
        # Python Frameworks
        "FastAPI": {
            "files": ["requirements.txt", "pyproject.toml"],
            "content_patterns": ["fastapi", "from fastapi import"],
        },
        "Django": {
            "files": ["requirements.txt", "pyproject.toml", "manage.py"],
            "content_patterns": ["django", "from django"],
        },
        "Flask": {
            "files": ["requirements.txt", "pyproject.toml"],
            "content_patterns": ["flask", "from flask import"],
        },
        "FastMCP": {
            "files": ["pyproject.toml"],
            "content_patterns": ["fastmcp", "from mcp import", "FastMCP"],
        },
        # JavaScript/TypeScript Frameworks
        "Next.js": {
            "files": ["next.config.js", "next.config.ts", "next.config.mjs"],
            "dirs": ["pages", "app"],
        },
        "React": {
            "files": ["package.json"],
            "content_patterns": ["react", "react-dom"],
        },
        "Vue": {
            "files": ["package.json", "vue.config.js"],
            "content_patterns": ["vue", "@vue/"],
        },
        "Express": {
            "files": ["package.json"],
            "content_patterns": ["express"],
        },
    }

    # Architecture pattern detection
    ARCHITECTURE_PATTERNS = {
        "Hexagonal (Ports & Adapters)": {
            "dirs": ["domain", "application", "adapters", "infrastructure"],
            "description": "Clean separation with domain/application/adapters layers",
        },
        "Clean Architecture": {
            "dirs": ["entities", "use_cases", "gateways", "controllers"],
            "description": "Layered architecture with dependency inversion",
        },
        "MVC": {
            "dirs": ["models", "views", "controllers"],
            "description": "Model-View-Controller pattern",
        },
    }

    def __init__(self, project_path: Path):
        """
        Initialize detector for a project.

        Args:
            project_path: Root directory of the project
        """
        self.project_path = project_path

    async def detect(self) -> Dict[str, Any]:
        """
        Detect frameworks and architectural patterns.

        Returns:
            Dictionary with detection results:
            {
                "frameworks": List[str],
                "architecture_pattern": str,
                "project_type": str,
            }
        """
        detected = {
            "frameworks": [],
            "architecture_pattern": "Unknown",
            "project_type": "unknown",
        }

        # Detect frameworks
        detected["frameworks"] = self._detect_frameworks()

        # Detect architecture pattern
        detected["architecture_pattern"] = self._detect_architecture_pattern()

        # Infer project type from frameworks
        detected["project_type"] = self._infer_project_type(detected["frameworks"])

        logger.debug(
            f"Detected: {detected['frameworks']}, "
            f"Architecture: {detected['architecture_pattern']}, "
            f"Type: {detected['project_type']}"
        )

        return detected

    def _detect_frameworks(self) -> List[str]:
        """
        Detect frameworks by checking configuration files and patterns.

        Returns:
            List of detected framework names
        """
        detected = []

        for framework_name, signatures in self.FRAMEWORK_SIGNATURES.items():
            # Check for configuration files
            if "files" in signatures:
                for file_pattern in signatures["files"]:
                    if self._file_exists(file_pattern):
                        # Check content patterns if specified
                        if "content_patterns" in signatures:
                            if self._check_content_patterns(
                                file_pattern, signatures["content_patterns"]
                            ):
                                detected.append(framework_name)
                                break
                        else:
                            detected.append(framework_name)
                            break

            # Check for directories
            if "dirs" in signatures and framework_name not in detected:
                if self._check_directories(signatures["dirs"]):
                    detected.append(framework_name)

        return detected

    def _detect_architecture_pattern(self) -> str:
        """
        Detect architectural pattern by analyzing directory structure.

        Returns:
            Architecture pattern name or "Unknown"
        """
        # Check src/ directory first (most projects)
        src_path = self.project_path / "src"

        for pattern_name, pattern_info in self.ARCHITECTURE_PATTERNS.items():
            required_dirs = pattern_info["dirs"]

            if src_path.exists():
                # Check in src/ directory
                if self._check_directories(required_dirs, base_path=src_path):
                    return pattern_name
            else:
                # Check in project root
                if self._check_directories(required_dirs):
                    return pattern_name

        return "Unknown"

    def _infer_project_type(self, frameworks: List[str]) -> str:
        """
        Infer project type from detected frameworks.

        Args:
            frameworks: List of detected frameworks

        Returns:
            Project type: web-app, api, mcp-server, library, cli, unknown
        """
        # MCP Server
        if "FastMCP" in frameworks:
            return "mcp-server"

        # Web Application
        if any(fw in frameworks for fw in ["Next.js", "React", "Vue", "Angular"]):
            return "web-app"

        # API Server
        if any(fw in frameworks for fw in ["FastAPI", "Django", "Flask", "Express"]):
            return "api"

        # Check for CLI indicators
        if (self.project_path / "cli.py").exists() or (
            self.project_path / "src" / "cli.py"
        ).exists():
            return "cli"

        # Check for library indicators (no main entry point, focus on modules)
        if (self.project_path / "pyproject.toml").exists():
            try:
                toml_content = (self.project_path / "pyproject.toml").read_text(
                    encoding="utf-8"
                )
                if "[tool.poetry]" in toml_content or "[build-system]" in toml_content:
                    return "library"
            except Exception:
                pass

        return "unknown"

    def _file_exists(self, file_pattern: str) -> bool:
        """
        Check if a file exists in the project.

        Args:
            file_pattern: File name or pattern to check

        Returns:
            True if file exists, False otherwise
        """
        file_path = self.project_path / file_pattern
        return file_path.exists()

    def _check_content_patterns(self, file_pattern: str, patterns: List[str]) -> bool:
        """
        Check if file content matches any of the patterns.

        Args:
            file_pattern: File to check
            patterns: List of string patterns to look for

        Returns:
            True if any pattern found, False otherwise
        """
        file_path = self.project_path / file_pattern

        if not file_path.exists():
            return False

        try:
            content = file_path.read_text(encoding="utf-8").lower()
            return any(pattern.lower() in content for pattern in patterns)
        except Exception as e:
            logger.debug(f"Could not read {file_path}: {e}")
            return False

    def _check_directories(self, dir_names: List[str], base_path: Path = None) -> bool:
        """
        Check if all required directories exist.

        Args:
            dir_names: List of directory names to check
            base_path: Base path to check from (default: project_path)

        Returns:
            True if all directories exist, False otherwise
        """
        base = base_path or self.project_path

        # Require at least 2 out of the listed directories to exist
        # (more flexible than requiring all)
        existing_count = sum(1 for dir_name in dir_names if (base / dir_name).exists())

        # For small lists (2-3 dirs), require all
        # For larger lists (4+ dirs), require at least half
        threshold = len(dir_names) if len(dir_names) <= 3 else len(dir_names) // 2

        return existing_count >= threshold
