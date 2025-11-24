# src/cde_orchestrator/application/ai_config/ai_config_use_case.py
"""
AI Config Use Case - Generates configuration files for various AI coding assistants.
Inspired by Spec-Kit's multi-agent support approach.
"""
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for an AI assistant/agent."""

    name: str  # Display name (e.g., "GitHub Copilot")
    key: str  # Identifier (e.g., "copilot")
    folder: str  # Configuration folder (e.g., ".github/")
    install_url: Optional[str]  # Installation URL (None for IDE-based)
    requires_cli: bool  # Whether it requires CLI tool
    config_files: List[
        str
    ]  # Files to generate (e.g., ["AGENTS.md", "copilot-instructions.md"])


class AIConfigUseCase:
    """
    Configures AI coding assistants for a project during onboarding.

    Supports multiple AI assistants following industry best practices:
    - GitHub Copilot (.github/copilot-instructions.md)
    - Claude Code (.claude/)
    - Gemini CLI (.gemini/)
    - Cursor (.cursor/)
    - Windsurf (.windsurf/)
    - And more...

    Based on Spec-Kit's approach: https://github.com/github/spec-kit
    """

    # Configuration for all supported AI assistants
    AGENT_CONFIG: Dict[str, AgentConfig] = {
        "copilot": AgentConfig(
            name="GitHub Copilot",
            key="copilot",
            folder=".github/",
            install_url=None,  # IDE-based
            requires_cli=False,
            config_files=["copilot-instructions.md", "AGENTS.md"],
        ),
        "claude": AgentConfig(
            name="Claude Code",
            key="claude",
            folder=".claude/",
            install_url="https://docs.anthropic.com/en/docs/claude-code/setup",
            requires_cli=True,
            config_files=["AGENTS.md"],
        ),
        "gemini": AgentConfig(
            name="Gemini CLI",
            key="gemini",
            folder=".gemini/",
            install_url="https://github.com/google-gemini/gemini-cli",
            requires_cli=True,
            config_files=["AGENTS.md", "GEMINI.md"],
        ),
        "cursor": AgentConfig(
            name="Cursor",
            key="cursor",
            folder=".cursor/",
            install_url=None,  # IDE-based
            requires_cli=False,
            config_files=["AGENTS.md"],
        ),
        "windsurf": AgentConfig(
            name="Windsurf",
            key="windsurf",
            folder=".windsurf/",
            install_url=None,  # IDE-based
            requires_cli=False,
            config_files=["AGENTS.md"],
        ),
        "amp": AgentConfig(
            name="Amp",
            key="amp",
            folder=".agents/",
            install_url="https://ampcode.com/manual#install",
            requires_cli=True,
            config_files=["AGENTS.md"],
        ),
    }

    def __init__(self, project_root: Path):
        """
        Initialize configurator for a project.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.detected_agents: List[str] = []

    def detect_installed_agents(self) -> List[str]:
        """
        Detect which AI assistants are installed on the system.

        Returns:
            List of agent keys that are installed
        """
        detected = []

        for agent_key, config in self.AGENT_CONFIG.items():
            if config.requires_cli:
                # Check if CLI tool is available
                if self._check_cli_tool(agent_key):
                    detected.append(agent_key)
                    logger.info(f"Detected {config.name} CLI")
            else:
                # IDE-based agents - check for existing config folders
                config_path = self.project_root / config.folder.rstrip("/")
                if config_path.exists():
                    detected.append(agent_key)
                    logger.info(f"Detected {config.name} configuration")

        self.detected_agents = detected
        return detected

    def _check_cli_tool(self, tool_name: str) -> bool:
        """
        Check if a CLI tool is available in PATH.

        Args:
            tool_name: Name of the CLI tool

        Returns:
            True if tool is available, False otherwise
        """
        try:
            # Try to get version or help
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 or "not found" not in result.stderr.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # Try with 'which' or 'where' command
            try:
                which_cmd = (
                    "where"
                    if subprocess.run(
                        ["where", "where"],
                        capture_output=True,
                        timeout=2,
                    ).returncode
                    == 0
                    else "which"
                )

                result = subprocess.run(
                    [which_cmd, tool_name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return result.returncode == 0
            except Exception:
                return False

    def generate_config_files(
        self,
        agents: Optional[List[str]] = None,
        force: bool = False,
        enriched_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate configuration files for specified AI assistants.

        Args:
            agents: List of agent keys to configure (None = auto-detect + defaults)
            force: Whether to overwrite existing files
            enriched_context: Enriched project context from analysis (optional)

        Returns:
            Dictionary with generation results
        """
        results: Dict[str, Any] = {
            "generated": [],
            "skipped": [],
            "errors": [],
        }

        # Determine which agents to configure
        if agents is None:
            # Auto-detect installed + always include Copilot and AGENTS.md
            agents_to_config = list(set(self.detect_installed_agents() + ["copilot"]))
        else:
            agents_to_config = agents

        logger.info(f"Configuring AI assistants: {', '.join(agents_to_config)}")

        # Generate root-level instruction files (AGENTS.md, GEMINI.md)
        for agent_key in agents_to_config:
            if agent_key not in self.AGENT_CONFIG:
                logger.warning(f"Unknown agent: {agent_key}")
                results["errors"].append(f"Unknown agent: {agent_key}")
                continue

            config = self.AGENT_CONFIG[agent_key]

            # Generate root-level files
            for config_file in config.config_files:
                if config_file in ["AGENTS.md", "GEMINI.md"]:
                    file_path = self.project_root / config_file
                    if file_path.exists() and not force:
                        results["skipped"].append(str(file_path))
                        logger.debug(f"Skipping existing file: {file_path}")
                        continue

                    try:
                        self._generate_root_instruction_file(
                            config_file, enriched_context
                        )
                        results["generated"].append(str(file_path))
                        logger.info(f"Generated {config_file}")
                    except Exception as e:
                        logger.error(f"Failed to generate {config_file}: {e}")
                        results["errors"].append(f"{config_file}: {str(e)}")

        # Generate agent-specific configuration files
        for agent_key in agents_to_config:
            # Skip unknown agents (already logged above)
            if agent_key not in self.AGENT_CONFIG:
                continue
            config = self.AGENT_CONFIG[agent_key]

            # Create agent folder
            agent_folder = self.project_root / config.folder.rstrip("/")

            try:
                # Generate agent-specific config
                if agent_key == "copilot":
                    self._generate_copilot_config(
                        agent_folder, force, results, enriched_context
                    )
                elif agent_key == "gemini":
                    self._generate_gemini_config(agent_folder, force, results)
                # Add more agent-specific handlers as needed

            except Exception as e:
                logger.error(f"Failed to configure {config.name}: {e}")
                results["errors"].append(f"{config.name}: {str(e)}")

        return results

    def _generate_root_instruction_file(
        self, filename: str, enriched_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Generate root-level instruction files (AGENTS.md, GEMINI.md).

        Args:
            filename: Name of the file to generate
            enriched_context: Enriched project context (optional)
        """
        # Ensure project root exists (especially in temp dirs during tests)
        self.project_root.mkdir(parents=True, exist_ok=True)
        file_path = self.project_root / filename

        # Get project name from directory
        project_name = self.project_root.name

        if filename == "AGENTS.md":
            content = self._get_agents_md_template(project_name, enriched_context)
        elif filename == "GEMINI.md":
            content = self._get_gemini_md_template(project_name, enriched_context)
        else:
            raise ValueError(f"Unknown instruction file: {filename}")

        # Write text as UTF-8, but ensure content is ASCII-safe to avoid
        # Windows cp1252 read_text() decoding issues in tests.
        file_path.write_text(content, encoding="utf-8")

    def _generate_copilot_config(
        self,
        agent_folder: Path,
        force: bool,
        results: Dict[str, Any],
        enriched_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Generate GitHub Copilot configuration.

        Args:
            agent_folder: Path to .github/ folder
            force: Whether to overwrite existing files
            results: Results dictionary to update
            enriched_context: Enriched project context (optional)
        """
        agent_folder.mkdir(parents=True, exist_ok=True)

        # Generate copilot-instructions.md
        instructions_file = agent_folder / "copilot-instructions.md"
        if instructions_file.exists() and not force:
            results["skipped"].append(str(instructions_file))
            return

        project_name = self.project_root.name
        content = self._get_copilot_instructions_template(
            project_name, enriched_context
        )
        instructions_file.write_text(content, encoding="utf-8")
        results["generated"].append(str(instructions_file))

    def _extract_context_data(
        self, enriched_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract and format data from enriched context.

        Args:
            enriched_context: Enriched project context

        Returns:
            Dictionary with formatted context data
        """
        if not enriched_context:
            return {
                "architecture": "[Architecture pattern]",
                "project_type": "[Project type]",
                "tech_stack": "[Tech stack]",
                "frameworks": "[Frameworks]",
                "recent_commits_count": 0,
                "commit_frequency": "[Commit frequency]",
                "active_branches": "[Branches]",
                "main_contributors": "[Contributors]",
                "build_commands": [],
                "test_commands": [],
                "primary_language": "[Primary language]",
            }

        return {
            "architecture": enriched_context.get(
                "architecture_description", "[Architecture pattern]"
            ),
            "project_type": enriched_context.get("project_type", "[Project type]"),
            "tech_stack": ", ".join(enriched_context.get("tech_stack", [])[:5])
            or "[Tech stack]",
            "frameworks": ", ".join(enriched_context.get("detected_frameworks", []))
            or "[Frameworks]",
            "recent_commits_count": len(enriched_context.get("recent_commits", [])),
            "commit_frequency": enriched_context.get(
                "commit_frequency", "[Commit frequency]"
            ),
            "active_branches": ", ".join(
                enriched_context.get("active_branches", [])[:3]
            )
            or "[Branches]",
            "main_contributors": ", ".join(
                enriched_context.get("main_contributors", [])[:3]
            )
            or "[Contributors]",
            "build_commands": enriched_context.get("build_commands", [])[:3],
            "test_commands": enriched_context.get("test_commands", [])[:3],
            "primary_language": self._get_primary_language(enriched_context),
        }

    def _get_primary_language(self, enriched_context: Dict[str, Any]) -> str:
        """Get primary language from language stats."""
        lang_stats = enriched_context.get("language_stats", {})
        if not lang_stats:
            return "[Primary language]"

        # Find language with most files
        primary = max(lang_stats.items(), key=lambda x: x[1], default=None)
        if primary:
            ext = primary[0]
            # Map extensions to language names
            lang_map = {
                ".py": "Python",
                ".js": "JavaScript",
                ".ts": "TypeScript",
                ".java": "Java",
                ".go": "Go",
                ".rs": "Rust",
                ".cpp": "C++",
                ".c": "C",
                ".rb": "Ruby",
                ".php": "PHP",
            }
            return lang_map.get(ext, ext.lstrip(".").upper())
        return "[Primary language]"

    def _generate_gemini_config(
        self, agent_folder: Path, force: bool, results: Dict[str, Any]
    ) -> None:
        """
        Generate Gemini CLI configuration.

        Args:
            agent_folder: Path to .gemini/ folder
            force: Whether to overwrite existing files
            results: Results dictionary to update
        """
        agent_folder.mkdir(parents=True, exist_ok=True)

        # Gemini-specific configuration files can be added here
        # For now, GEMINI.md in root is sufficient
        logger.debug(f"Gemini configuration folder created: {agent_folder}")

    def _get_agents_md_template(
        self, project_name: str, enriched_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate AGENTS.md content template with enriched context.

        Args:
            project_name: Name of the project
            enriched_context: Enriched project context (optional)

        Returns:
            Content for AGENTS.md
        """
        # Extract context data
        ctx = self._extract_context_data(enriched_context)

        # Format build commands section
        build_cmds = (
            "\n".join([f"# {cmd}" for cmd in ctx["build_commands"]])
            if ctx["build_commands"]
            else "# [Your build command]"
        )
        test_cmds = (
            "\n".join([f"# {cmd}" for cmd in ctx["test_commands"]])
            if ctx["test_commands"]
            else "# [Your test command]"
        )

        return f"""# {project_name} - Agent Instructions

> Format: AGENTS.md (OpenAI Standard)
> Target: AI Coding Agents (Cursor, Windsurf, Aider, Bolt, etc.)
> Last Updated: Auto-generated during onboarding
> Priority: High-level guidelines and project navigation

---
## 🎯 Project Overview

What: {ctx['architecture']}
Scale: {ctx['project_type']}
Architecture: {ctx['architecture']}
Language: {ctx['primary_language']}
Tech Stack: {ctx['tech_stack']}
Frameworks: {ctx['frameworks']}

---
## 📊 Recent Activity

- {ctx['recent_commits_count']} commits in last 30 days ({ctx['commit_frequency']})
- Active branches: {ctx['active_branches']}
- Main contributors: {ctx['main_contributors']}

---
## 📁 Quick Navigation

### Start Here (First-time agents)
1. Read `specs/design/architecture/README.md` for system design (if exists)
2. Check `specs/features/` for feature specifications
3. Review `memory/constitution.md` for project principles

### Core Directories
```
src/                 # Source code
├── domain/          # Core business logic (if using Clean Architecture)
├── application/     # Use cases/application logic
└── infrastructure/  # External dependencies

specs/               # All documentation (Spec-Kit standard)
├── features/        # Feature specifications
├── design/          # Architecture decisions
├── api/             # API documentation
└── reviews/         # Code reviews

tests/               # Test suites
```

---
## 🏗️ Architecture Rules

Architecture Pattern: {ctx['architecture']}

### Dependency Rules
- Dependencies should follow clean architecture principles
- Keep business logic independent of frameworks and infrastructure

---
## 🛠️ Development Workflow

### Before Any Code Changes
1. Check existing specs: `specs/features/*.md`
2. Search codebase: Use grep or semantic search
3. Understand context: Read related files fully

### Making Changes
1. Create/update spec: `specs/features/your-feature.md`
2. Follow architecture pattern: {ctx['architecture']}
3. Write tests first: TDD approach
4. Run validation: Pre-commit hooks

---
## 📝 Documentation Rules

### File Placement (MANDATORY)
- Features: `specs/features/` - User-facing functionality
- Design: `specs/design/` - Technical decisions
- API: `specs/api/` - API documentation

### Metadata Requirement
All `.md` files in `specs/` MUST include YAML frontmatter:
```yaml
---
title: "Document Title"
description: "One-sentence summary"
type: "feature|design|api|review"
status: "draft|active|deprecated"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Name or Agent ID"
---
```

---
## 🧪 Testing Strategy

### Test Organization
```
tests/
├── unit/            # Fast, isolated tests
├── integration/     # With I/O (adapters, repositories)
└── e2e/             # End-to-end tests
```

---
## 🚀 Quick Commands Reference

```bash
# Build project
{build_cmds}

# Run tests
{test_cmds}

# Format code
# [Your format command]
```

---
## ⚠️ Common Pitfalls

### DON'T
1. Skip writing specifications before code
2. Put complex logic in wrong layer
3. Skip tests for new functionality
4. Make breaking changes without updating specs

### DO
1. Follow architecture strictly
2. Write specs before code
3. Add tests for all new functionality
4. Use semantic commit messages: `feat:`, `fix:`, `docs:`, `refactor:`

---
## 🔍 Finding Information

### Key Documents
- Architecture: `specs/design/architecture/README.md`
- Features: `specs/features/`
- API Docs: `specs/api/`

---
## 💡 When Stuck

1. Check specs: `specs/features/` or `specs/design/`
2. Search code: Use semantic search or grep
3. Review constitution: `memory/constitution.md`

---
For detailed GitHub Copilot instructions: see `.github/copilot-instructions.md`
For Google AI Studio (Gemini) instructions: see `GEMINI.md` (if using Gemini)
"""

    def _get_gemini_md_template(
        self, project_name: str, enriched_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate GEMINI.md content template with enriched context.

        Args:
            project_name: Name of the project
            enriched_context: Enriched project context (optional)

        Returns:
            Content for GEMINI.md
        """
        # Extract context data
        ctx = self._extract_context_data(enriched_context)

        return f"""# {project_name} - Gemini AI Instructions
> Format: GEMINI.md (Google AI Studio Standard)
> Target: Google Gemini AI (AI Studio, Gemini CLI, IDX)
> Last Updated: Auto-generated during onboarding
> Context Window: 1M+ tokens


## 🎯 Project Overview

What: {ctx['architecture']}
Scale: {ctx['project_type']}
Architecture: {ctx['architecture']}
Language: {ctx['primary_language']}
Tech Stack: {ctx['tech_stack']}
Frameworks: {ctx['frameworks']}

---

## 📊 Recent Activity

- {ctx['recent_commits_count']} commits in last 30 days ({ctx['commit_frequency']})
- Active branches: {ctx['active_branches']}
- Main contributors: {ctx['main_contributors']}

---

## Quick Navigation
[See AGENTS.md for full project navigation and documentation rules]

---

## 🎨 Gemini-Specific Optimizations
### 1. Large Context Window (1M+ tokens)

Best Practices:
- Request FULL file contents instead of summaries
- Analyze multiple related files simultaneously
- Process entire feature specs in one go
- Review complete test suites together

Example Request:
Show me ALL the code in src/domain/ directory, including ALL files.
I want to see the complete implementation, not summaries.
```

### 2. Multi-Modal Capabilities

Use When:
- Analyzing architecture diagrams
- Understanding UML or flow charts
- Code visualization analysis
- Documentation with embedded images

Example:
```
Here is our architecture diagram [image]. Analyze how the current
codebase matches this design and identify any discrepancies.
```

### 3. Function Calling and Structured Outputs

When Generating Code:
- Use response_mime_type="application/json" for structured data
- Define response_schema for type-safe outputs
- Leverage function calling for complex operations

---

## 💡 Pro Tips for Gemini

1. **Leverage Context Window**: Request full file contents, not summaries
2. **Batch Operations**: Analyze multiple files simultaneously
3. **Structured Outputs**: Use JSON schema for predictable responses
4. **Parallel Research**: Use Gemini CLI with background jobs
5. **Multimodal Analysis**: Include diagrams and images in prompts

---

**Your 1M+ token context window is a superpower. When analyzing code or designing solutions, request FULL file contents instead of summaries.**

For complete instructions and workflow: see `AGENTS.md`
"""

    def _get_copilot_instructions_template(
        self, project_name: str, enriched_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate GitHub Copilot instructions template with enriched context.

        Args:
            project_name: Name of the project
            enriched_context: Enriched project context (optional)

        Returns:
            Content for .github/copilot-instructions.md
        """
        # Extract context data
        ctx = self._extract_context_data(enriched_context)

        # Format build/test commands
        build_cmds = (
            "\n".join([f"# {cmd}" for cmd in ctx["build_commands"]])
            if ctx["build_commands"]
            else "# [Your build command]"
        )
        test_cmds = (
            "\n".join([f"# {cmd}" for cmd in ctx["test_commands"]])
            if ctx["test_commands"]
            else "# [Your test command]"
        )

        return f"""---
description: GitHub Copilot custom instructions for {project_name}
---

# GitHub Copilot Instructions - {project_name}

## 🎯 Project Overview

What: {ctx['architecture']}
Scale: {ctx['project_type']}
Architecture: {ctx['architecture']}
Language: {ctx['primary_language']}
Tech Stack: {ctx['tech_stack']}
Frameworks: {ctx['frameworks']}

## 📊 Recent Activity

- {ctx['recent_commits_count']} commits in last 30 days ({ctx['commit_frequency']})
- Active branches: {ctx['active_branches']}
- Main contributors: {ctx['main_contributors']}

## 🏗️ Architecture

Pattern: {ctx['architecture']}

### Key Principles
- Follow clean architecture boundaries
- Keep business logic independent of frameworks
- Dependencies point inward

## 📝 Code Standards

### Language & Style
- Language: {ctx['primary_language']}
- Frameworks: {ctx['frameworks']}
- Follow project conventions consistently

### Testing
- Test Location: `tests/`
- Write tests for all new functionality
- Maintain high test coverage

## 📁 File Organization

```
src/                 # Source code
specs/               # Documentation (Spec-Kit)
tests/               # Test suites
```

## ✅ DO's

- Write specifications before implementation
- Follow architecture patterns strictly
- Add tests for new functionality
- Use semantic commit messages: `feat:`, `fix:`, `docs:`, `refactor:`

## ❌ DON'Ts

- Don't skip writing specs
- Don't put logic in wrong layer
- Don't skip tests
- Don't make breaking changes without updating docs

## 🚀 Quick Commands

```bash
# Build project
{build_cmds}

# Run tests
{test_cmds}
```

## 📚 Resources

- Full Guidelines: `AGENTS.md`
- Architecture: `specs/design/architecture/README.md`
- Constitution: `memory/constitution.md` (if exists)
"""

    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get a summary of AI assistant configuration status.

        Returns:
            Dictionary with configuration summary
        """
        summary: Dict[str, Any] = {
            "total_agents": len(self.AGENT_CONFIG),
            "detected_agents": self.detected_agents,
            "configured_agents": [],
            "available_agents": list(self.AGENT_CONFIG.keys()),
        }

        # Check which agents are configured
        for agent_key, config in self.AGENT_CONFIG.items():
            agent_folder = self.project_root / config.folder.rstrip("/")

            # Check for root-level instruction files
            has_config = False
            for config_file in config.config_files:
                if config_file in ["AGENTS.md", "GEMINI.md"]:
                    if (self.project_root / config_file).exists():
                        has_config = True
                        break

            # Or check for agent-specific folder
            if agent_folder.exists():
                has_config = True

            if has_config:
                summary["configured_agents"].append(agent_key)

        return summary
