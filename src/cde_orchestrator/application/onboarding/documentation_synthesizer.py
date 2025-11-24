# src/cde_orchestrator/application/onboarding/documentation_synthesizer.py
"""
Documentation Synthesizer - Reads and extracts key information from project docs.

Analyzes:
- README.md: Architecture, tech stack, setup commands
- CONTRIBUTING.md: Coding conventions, workflow
- pyproject.toml: Python dependencies
- package.json: Node.js dependencies and scripts
"""
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DocumentationSynthesizer:
    """
    Reads and synthesizes existing project documentation.

    Extracts actionable information from:
    - README.md: Project description, architecture, tech stack, commands
    - CONTRIBUTING.md: Coding conventions, development workflow
    - pyproject.toml: Python dependencies and metadata
    - package.json: JavaScript dependencies and scripts
    - docs/: Additional technical documentation

    This provides rich context for generating AI assistant instructions.
    """

    def __init__(self, project_path: Path):
        """
        Initialize synthesizer for a project.

        Args:
            project_path: Root directory of the project
        """
        self.project_path = project_path

    async def synthesize(self) -> Dict[str, Any]:
        """
        Synthesize all project documentation.

        Returns:
            Dictionary with extracted information:
            {
                "architecture": str,
                "tech_stack": List[str],
                "build_commands": List[str],
                "test_commands": List[str],
                "conventions": List[str],
            }
        """
        result = {
            "architecture": "",
            "tech_stack": [],
            "build_commands": [],
            "test_commands": [],
            "conventions": [],
        }

        # Read README.md
        readme_path = self.project_path / "README.md"
        if readme_path.exists():
            try:
                readme_content = readme_path.read_text(encoding="utf-8")
                result["architecture"] = self._extract_architecture(readme_content)
                result["tech_stack"].extend(self._extract_tech_stack(readme_content))
                result["build_commands"].extend(
                    self._extract_commands(readme_content, "build")
                )
                result["test_commands"].extend(
                    self._extract_commands(readme_content, "test")
                )
                logger.debug("Extracted information from README.md")
            except Exception as e:
                logger.error(f"Error reading README.md: {e}")

        # Read CONTRIBUTING.md
        contributing_path = self.project_path / "CONTRIBUTING.md"
        if contributing_path.exists():
            try:
                contrib_content = contributing_path.read_text(encoding="utf-8")
                result["conventions"].extend(self._extract_conventions(contrib_content))
                logger.debug("Extracted conventions from CONTRIBUTING.md")
            except Exception as e:
                logger.error(f"Error reading CONTRIBUTING.md: {e}")

        # Read pyproject.toml (Python)
        pyproject_path = self.project_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                pyproject_content = pyproject_path.read_text(encoding="utf-8")
                result["tech_stack"].extend(
                    self._extract_dependencies_toml(pyproject_content)
                )
                logger.debug("Extracted dependencies from pyproject.toml")
            except Exception as e:
                logger.error(f"Error reading pyproject.toml: {e}")

        # Read package.json (JavaScript/TypeScript)
        package_json_path = self.project_path / "package.json"
        if package_json_path.exists():
            try:
                package_data = json.loads(package_json_path.read_text(encoding="utf-8"))
                result["tech_stack"].extend(
                    self._extract_dependencies_json(package_data)
                )
                result["build_commands"].extend(
                    self._extract_scripts(package_data, "build")
                )
                result["test_commands"].extend(
                    self._extract_scripts(package_data, "test")
                )
                logger.debug("Extracted information from package.json")
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Error reading package.json: {e}")

        # Deduplicate lists
        result["tech_stack"] = list(dict.fromkeys(result["tech_stack"]))
        result["build_commands"] = list(dict.fromkeys(result["build_commands"]))
        result["test_commands"] = list(dict.fromkeys(result["test_commands"]))
        result["conventions"] = list(dict.fromkeys(result["conventions"]))

        return result

    def _extract_architecture(self, content: str) -> str:
        """
        Extract architecture description from README.

        Looks for sections: Architecture, Design, Technical Design

        Args:
            content: README.md content

        Returns:
            Architecture description or "Not documented"
        """
        # Pattern 1: ## Architecture section
        patterns = [
            r"## Architecture\s*\n\s*\n(.+?)(?=\n##|\Z)",
            r"## Design\s*\n\s*\n(.+?)(?=\n##|\Z)",
            r"## Technical Design\s*\n\s*\n(.+?)(?=\n##|\Z)",
            r"\*\*Architecture\*\*:\s*(.+?)(?=\n|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                # Take first paragraph (up to first double newline or 200 chars)
                text = match.group(1).strip()
                first_para = text.split("\n\n")[0]
                return first_para[:200] if len(first_para) > 200 else first_para

        return "Not documented"

    def _extract_tech_stack(self, content: str) -> List[str]:
        """
        Extract technology stack from README.

        Looks for common frameworks, languages, and tools.

        Args:
            content: README.md content

        Returns:
            List of detected technologies
        """
        stack = []

        # Common technology patterns
        tech_patterns = {
            r"Python\s+([\d.]+)": "Python",
            r"Node\.?js\s+([\d.]+)": "Node.js",
            r"TypeScript": "TypeScript",
            r"React": "React",
            r"Next\.?js": "Next.js",
            r"FastAPI": "FastAPI",
            r"Django": "Django",
            r"Flask": "Flask",
            r"FastMCP": "FastMCP",
            r"Express": "Express",
            r"Vue": "Vue",
            r"Angular": "Angular",
        }

        for pattern, tech_name in tech_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                # Try to extract version if present
                version_match = re.search(
                    pattern + r"\s+([\d.]+)", content, re.IGNORECASE
                )
                if version_match and len(version_match.groups()) > 0:
                    stack.append(f"{tech_name} {version_match.group(1)}")
                else:
                    stack.append(tech_name)

        return stack

    def _extract_commands(self, content: str, command_type: str) -> List[str]:
        """
        Extract build or test commands from README.

        Looks for code blocks containing relevant commands.

        Args:
            content: README.md content
            command_type: "build" or "test"

        Returns:
            List of commands
        """
        commands = []

        # Find all code blocks (bash, sh, shell, or no language specified)
        code_blocks = re.findall(
            r"```(?:bash|sh|shell|console|powershell)?\n(.*?)```",
            content,
            re.DOTALL | re.IGNORECASE,
        )

        for block in code_blocks:
            # Check if block mentions the command type
            if command_type.lower() in block.lower():
                # Extract non-comment lines
                lines = block.strip().split("\n")
                for line in lines:
                    stripped = line.strip()
                    # Skip comments and empty lines
                    if stripped and not stripped.startswith("#"):
                        commands.append(stripped)

        return commands[:5]  # Limit to 5 most relevant commands

    def _extract_conventions(self, content: str) -> List[str]:
        """
        Extract coding conventions from CONTRIBUTING.md.

        Looks for style guide sections and convention lists.

        Args:
            content: CONTRIBUTING.md content

        Returns:
            List of conventions
        """
        conventions = []

        # Look for code style sections
        patterns = [
            r"## Code Style\s*\n\s*\n(.*?)(?=\n##|\Z)",
            r"## Coding Conventions\s*\n\s*\n(.*?)(?=\n##|\Z)",
            r"## Style Guide\s*\n\s*\n(.*?)(?=\n##|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                section = match.group(1)
                # Extract bullet points
                bullets = re.findall(r"[-*]\s+(.+)", section)
                conventions.extend(bullets)

        return conventions[:10]  # Limit to 10 most important conventions

    def _extract_dependencies_toml(self, content: str) -> List[str]:
        """
        Extract main dependencies from pyproject.toml.

        Args:
            content: pyproject.toml content

        Returns:
            List of dependency names
        """
        deps = []

        # Look for dependencies section
        # Match both [project.dependencies] and [tool.poetry.dependencies]
        dep_patterns = [
            r"\[project\.dependencies\]\s*\n(.*?)(?=\n\[|\Z)",
            r"\[tool\.poetry\.dependencies\]\s*\n(.*?)(?=\n\[|\Z)",
        ]

        for pattern in dep_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                dep_section = match.group(1)
                # Extract package names (before = or >=)
                packages = re.findall(
                    r'["\']?([a-zA-Z0-9_-]+)["\']?\s*[>=]', dep_section
                )
                deps.extend(packages)

        return deps[:10]  # Top 10 dependencies

    def _extract_dependencies_json(self, data: Dict[str, Any]) -> List[str]:
        """
        Extract main dependencies from package.json.

        Args:
            data: Parsed package.json data

        Returns:
            List of dependency names
        """
        deps = []

        if "dependencies" in data:
            deps.extend(list(data["dependencies"].keys()))

        return deps[:10]  # Top 10 dependencies

    def _extract_scripts(self, data: Dict[str, Any], script_type: str) -> List[str]:
        """
        Extract npm scripts from package.json.

        Args:
            data: Parsed package.json data
            script_type: "build" or "test"

        Returns:
            List of npm commands
        """
        scripts = []

        if "scripts" in data:
            for name, command in data["scripts"].items():
                if script_type.lower() in name.lower():
                    scripts.append(f"npm run {name}")

        return scripts[:3]  # Top 3 relevant scripts
