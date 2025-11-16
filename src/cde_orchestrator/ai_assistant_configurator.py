"""
AI Assistant Configurator - Generates configuration files for AI assistants.

This module creates and manages configuration files for various AI assistants:
- AGENTS.md (OpenAI/Anthropic standard)
- GEMINI.md (Google AI Studio)
- .github/copilot-instructions.md (GitHub Copilot)
- .cursor/rules (Cursor)

Following Spec-Kit best practices for AI assistant integration.
"""

import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AIAssistantConfigurator:
    """
    Configures AI assistant integration files for a project.
    Generates standardized configuration files following industry conventions.
    """

    def __init__(self, project_root: Path):
        """
        Initialize configurator for a specific project.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.config_files = {
            "agents_md": self.project_root / "AGENTS.md",
            "gemini_md": self.project_root / "GEMINI.md",
            "copilot_instructions": self.project_root
            / ".github"
            / "copilot-instructions.md",
            "cursor_rules": self.project_root / ".cursor" / "rules",
        }

    def analyze_existing_config(self) -> Dict[str, Any]:
        """
        Analyze existing AI assistant configuration files.

        Returns:
            Dict with analysis of existing configuration
        """
        analysis = {
            "has_agents_md": self.config_files["agents_md"].exists(),
            "has_gemini_md": self.config_files["gemini_md"].exists(),
            "has_copilot_instructions": self.config_files[
                "copilot_instructions"
            ].exists(),
            "has_cursor_rules": self.config_files["cursor_rules"].exists(),
            "missing_files": [],
            "existing_files": [],
        }

        for name, path in self.config_files.items():
            if path.exists():
                analysis["existing_files"].append(
                    str(path.relative_to(self.project_root))
                )
            else:
                analysis["missing_files"].append(
                    str(path.relative_to(self.project_root))
                )

        return analysis

    def generate_agents_md(self, project_info: Dict[str, Any]) -> str:
        """
        Generate AGENTS.md content following OpenAI/Anthropic standards.

        Args:
            project_info: Project metadata (name, description, tech stack)

        Returns:
            Content for AGENTS.md file
        """
        project_name = project_info.get("name", "Project")
        description = project_info.get("description", "AI-powered development project")

        content = f"""---
title: "{project_name} - AI Agent Instructions"
description: "Instructions for AI coding agents working with {project_name}"
type: guide
status: active
---

# {project_name} - Agent Instructions

> **Target**: AI Coding Agents (Cursor, Windsurf, Aider, Claude Desktop, etc.)
> **Purpose**: {description}

## Project Overview

**What**: {description}
**Architecture**: [Add architecture details]
**Language**: [Add primary language]

## Core Directories

```
src/               # Source code
tests/             # Test suite
docs/              # Documentation
specs/             # Specifications (Spec-Kit)
```

## Development Guidelines

### Before Making Changes

1. Check existing specs in `specs/features/*.md`
2. Search codebase for similar implementations
3. Understand context by reading related files

### Making Changes

1. Follow existing code patterns
2. Write tests for new functionality
3. Update documentation as needed

## Key Commands

```bash
# Run tests
pytest tests/

# Format code
black src/
ruff check src/

# Type checking
mypy src/
```

## Documentation Standards

All markdown files should include YAML frontmatter:

```yaml
---
title: "Document Title"
description: "Brief description"
type: "feature|design|guide"
status: "draft|active|deprecated"
---
```

---

**Remember**: Check documentation in `docs/` and `specs/` before making changes.
"""
        return content

    def generate_gemini_md(self, project_info: Dict[str, Any]) -> str:
        """
        Generate GEMINI.md content for Google AI Studio.

        Args:
            project_info: Project metadata

        Returns:
            Content for GEMINI.md file
        """
        project_name = project_info.get("name", "Project")

        content = f"""# {project_name} - Gemini Instructions

Instructions for Google AI Studio / Gemini integration.

## Project Context

This is {project_name}. See AGENTS.md for complete development guidelines.

## Key Points

- Follow existing code patterns
- Check `specs/` directory for requirements
- Run tests before committing: `pytest tests/`
- Format code: `black src/ && ruff check src/`

## Documentation

All project documentation is in:
- `docs/` - User-facing guides
- `specs/` - Technical specifications
- `AGENTS.md` - Complete agent instructions
"""
        return content

    def create_config_files(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create AI assistant configuration files.

        Args:
            project_info: Project metadata for generating configs

        Returns:
            Dict with results of file creation
        """
        results = {
            "created": [],
            "skipped": [],
            "errors": [],
        }

        try:
            # Create AGENTS.md
            agents_md = self.config_files["agents_md"]
            if not agents_md.exists():
                content = self.generate_agents_md(project_info)
                agents_md.write_text(content, encoding="utf-8")
                results["created"].append(str(agents_md.relative_to(self.project_root)))
                logger.info(f"Created {agents_md}")
            else:
                results["skipped"].append("AGENTS.md (already exists)")

            # Create GEMINI.md
            gemini_md = self.config_files["gemini_md"]
            if not gemini_md.exists():
                content = self.generate_gemini_md(project_info)
                gemini_md.write_text(content, encoding="utf-8")
                results["created"].append(str(gemini_md.relative_to(self.project_root)))
                logger.info(f"Created {gemini_md}")
            else:
                results["skipped"].append("GEMINI.md (already exists)")

            # Note: .github/copilot-instructions.md and .cursor/rules
            # are typically created manually by developers
            # We'll note their absence but not auto-create them

        except Exception as e:
            logger.error(f"Error creating config files: {e}")
            results["errors"].append(str(e))

        return results

    def update_existing_config(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing AI assistant configuration files.

        Args:
            project_info: Updated project metadata

        Returns:
            Dict with update results
        """
        results = {
            "updated": [],
            "unchanged": [],
            "errors": [],
        }

        # For now, we preserve existing files and don't overwrite
        # Future: implement intelligent merging of updates

        analysis = self.analyze_existing_config()

        for file in analysis["existing_files"]:
            results["unchanged"].append(f"{file} (preserved)")

        return results
