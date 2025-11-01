# src/cde_orchestrator/ai_assistant_configurator.py
"""
AI Assistant Configurator - Generates configuration files for various AI coding assistants.
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


class AIAssistantConfigurator:
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
        self, agents: Optional[List[str]] = None, force: bool = False
    ) -> Dict[str, Any]:
        """
        Generate configuration files for specified AI assistants.

        Args:
            agents: List of agent keys to configure (None = auto-detect + defaults)
            force: Whether to overwrite existing files

        Returns:
            Dictionary with generation results
        """
        results = {
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
                        self._generate_root_instruction_file(config_file)
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
                    self._generate_copilot_config(agent_folder, force, results)
                elif agent_key == "gemini":
                    self._generate_gemini_config(agent_folder, force, results)
                # Add more agent-specific handlers as needed

            except Exception as e:
                logger.error(f"Failed to configure {config.name}: {e}")
                results["errors"].append(f"{config.name}: {str(e)}")

        return results

    def _generate_root_instruction_file(self, filename: str) -> None:
        """
        Generate root-level instruction files (AGENTS.md, GEMINI.md).

        Args:
            filename: Name of the file to generate
        """
        # Ensure project root exists (especially in temp dirs during tests)
        self.project_root.mkdir(parents=True, exist_ok=True)
        file_path = self.project_root / filename

        # Get project name from directory
        project_name = self.project_root.name

        if filename == "AGENTS.md":
            content = self._get_agents_md_template(project_name)
        elif filename == "GEMINI.md":
            content = self._get_gemini_md_template(project_name)
        else:
            raise ValueError(f"Unknown instruction file: {filename}")

        # Write text as UTF-8, but ensure content is ASCII-safe to avoid
        # Windows cp1252 read_text() decoding issues in tests.
        file_path.write_text(content, encoding="utf-8")

    def _generate_copilot_config(
        self, agent_folder: Path, force: bool, results: Dict[str, Any]
    ) -> None:
        """
        Generate GitHub Copilot configuration.

        Args:
            agent_folder: Path to .github/ folder
            force: Whether to overwrite existing files
            results: Results dictionary to update
        """
        agent_folder.mkdir(parents=True, exist_ok=True)

        # Generate copilot-instructions.md
        instructions_file = agent_folder / "copilot-instructions.md"
        if instructions_file.exists() and not force:
            results["skipped"].append(str(instructions_file))
            return

        project_name = self.project_root.name
        content = self._get_copilot_instructions_template(project_name)
        instructions_file.write_text(content, encoding="utf-8")
        results["generated"].append(str(instructions_file))

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

    def _get_agents_md_template(self, project_name: str) -> str:
        """
        Generate AGENTS.md content template.

        Args:
            project_name: Name of the project

        Returns:
            Content for AGENTS.md
        """
        return f"""# {project_name} - Agent Instructions

> Format: AGENTS.md (OpenAI Standard)
> Target: AI Coding Agents (Cursor, Windsurf, Aider, Bolt, etc.)
> Last Updated: Auto-generated during onboarding
> Priority: High-level guidelines and project navigation

---
## 🎯 Project Overview

What: [Brief description of what this project does]
Scale: [Project scale/scope information]
Architecture: [Architecture pattern used - e.g., Hexagonal, Clean, MVC]
Language: [Primary language and version]

---
## 📁 Quick Navigation

### Start Here (First-time agents)
1. Read `specs/design/ARCHITECTURE.md` for system design (if exists)
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

[Add architecture-specific rules here based on your project]

### Example: Dependency Rules
- Dependencies point INWARD: Infrastructure -> Application -> Domain
---
## 🛠️ Development Workflow

### Before Any Code Changes
1. Check existing specs: `specs/features/*.md`
2. Search codebase: Use grep or semantic search
3. Understand context: Read related files fully

### Making Changes
1. Create/update spec: `specs/features/your-feature.md`
2. Follow architecture pattern: [Your pattern]
3. Write tests first: TDD approach
4. Run validation: Pre-commit hooks

---
## 📝 Documentation Rules

### File Placement (MANDATORY)
- Features: `specs/features/` - User-facing functionality
### Metadata Requirement
All `.md` files in `specs/` MUST include YAML frontmatter:
```yaml
---
description: "One-sentence summary"
type: "feature|design|api|review"
status: "draft|active|deprecated"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
author: "Name or Agent ID"
---

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
## Common Pitfalls

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
## Finding Information

### Key Documents
- Architecture: `specs/design/ARCHITECTURE.md`
---
## When Stuck

1. Check specs: `specs/features/` or `specs/design/`
2. Search code: Use semantic search or grep
3. Review constitution: `memory/constitution.md`

---
## Quick Commands Reference

```bash
# Run tests
[Your test command]

# Build project
[Your build command]

# Format code
[Your format command]
```

---
For detailed GitHub Copilot instructions: see `.github/copilot-instructions.md`
For Google AI Studio (Gemini) instructions: see `GEMINI.md` (if using Gemini)
"""
    def _get_gemini_md_template(self, project_name: str) -> str:
        """
        Generate GEMINI.md content template.

        Args:

        Returns:
            Content for GEMINI.md
        """
        return f"""# {project_name} - Gemini AI Instructions
> Format: GEMINI.md (Google AI Studio Standard)
> Target: Google Gemini AI (AI Studio, Gemini CLI, IDX)
> Last Updated: Auto-generated during onboarding
> Context Window: 1M+ tokens


## Project Overview

What: [Brief description of what this project does]
Scale: [Project scale/scope information]
Language: [Primary language and version]

---

## Quick Navigation
[Same as AGENTS.md - see that file for structure]

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

Example (Python):
```python
# Request structured analysis
response = model.generate_content(
    prompt,
    generation_config={{
        "response_mime_type": "application/json",
        "response_schema": AnalysisSchema
    }}
)
```

### 4. Parallel Processing with Gemini CLI

**For Research Tasks**:
```powershell
# Run multiple analyses in parallel (Windows PowerShell)
$jobs = @(
    (Start-Job -ScriptBlock {{ gemini --model=gemini-2.5-flash "Analyze architecture patterns in this codebase" }}),
    (Start-Job -ScriptBlock {{ gemini --model=gemini-2.5-flash "Review test coverage and suggest improvements" }}),
    (Start-Job -ScriptBlock {{ gemini --model=gemini-2.5-flash "Identify technical debt and refactoring opportunities" }})
)

$jobs | Wait-Job | Receive-Job
```

---

## 🏗️ Architecture Rules

[Same as AGENTS.md]

---

## 🛠️ Development Workflow

[Same as AGENTS.md]

---

## 📝 Documentation Rules

[Same as AGENTS.md]

---

## 🧪 Testing Strategy

[Same as AGENTS.md]

---

## ⚠️ Common Pitfalls

[Same as AGENTS.md]

---

## 🔍 Finding Information

[Same as AGENTS.md]

---

## 💡 Pro Tips for Gemini

1. **Leverage Context Window**: Request full file contents, not summaries
2. **Batch Operations**: Analyze multiple files simultaneously
3. **Structured Outputs**: Use JSON schema for predictable responses
4. **Parallel Research**: Use Gemini CLI with background jobs for research
5. **Multimodal Analysis**: Include diagrams and images in your prompts

---

**Your 1M+ token context window is a superpower. When analyzing code or designing solutions, request FULL file contents instead of summaries.**
"""

    def _get_copilot_instructions_template(self, project_name: str) -> str:
        """
        Generate GitHub Copilot instructions template.

        Args:
            project_name: Name of the project

        Returns:
            Content for .github/copilot-instructions.md
        """
        return f"""---
description: GitHub Copilot custom instructions for {project_name}
---

# GitHub Copilot Instructions - {project_name}

## Project Overview

[Brief description of the project]

## Architecture

[Architecture pattern and key principles]

## Code Standards

### Language & Style
- Language: [Primary language]
- Style Guide: [Style guide reference]
- Formatting: [Formatter used]

### Testing
- Test Framework: [Framework name]
- Coverage Target: [Percentage]
- Test Location: `tests/`

## File Organization

```
[Project structure]
```

## Common Patterns

### [Pattern 1]
```[language]
# Example code showing the pattern
```

### [Pattern 2]
```[language]
# Example code showing the pattern
```

## DO's

- Write specifications before implementation
- Follow architecture patterns strictly
- Add tests for new functionality
- Use semantic commit messages

## DON'Ts

- Don't skip writing specs
- Don't put logic in wrong layer
- Don't skip tests
- Don't make breaking changes without updating docs

## Resources

- Full Guidelines: `AGENTS.md`
- Architecture: `specs/design/ARCHITECTURE.md`
- Constitution: `memory/constitution.md`
"""

    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get a summary of AI assistant configuration status.

        Returns:
            Dictionary with configuration summary
        """
        summary = {
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
