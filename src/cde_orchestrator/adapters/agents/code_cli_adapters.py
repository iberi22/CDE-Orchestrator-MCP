"""
Code Execution CLI Adapters - Headless CLI execution for code generation.

Implements ICodeExecutor port with support for:
    - GitHub Copilot (gh copilot suggest)
    - Google Gemini (gemini CLI)
    - Alibaba Qwen (qwen CLI)

Design Philosophy:
    - Reuse CLI authentication (no API keys in code)
    - Fallback chain for robustness
    - Unified interface across providers
    - Async execution for performance

Architecture:
    CodeCLIAdapter (base class)
    ├── CopilotCLIAdapter
    ├── GeminiCLIAdapter
    └── QwenCLIAdapter
"""

import asyncio
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from ...domain.ports import ICodeExecutor


class CodeCLIError(Exception):
    """Base exception for code CLI execution errors."""

    pass


class CodeCLINotFoundError(CodeCLIError):
    """Raised when CLI executable not found."""

    pass


class CodeCLIExecutionError(CodeCLIError):
    """Raised when CLI execution fails."""

    pass


class CodeCLIAdapter(ABC):
    """
    Abstract base for code execution CLI adapters.

    Subclasses implement provider-specific CLI invocation for code generation.
    """

    @property
    @abstractmethod
    def cli_command(self) -> str:
        """CLI command name (e.g., 'gh', 'gemini', 'qwen')."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name."""
        pass

    def is_available(self) -> bool:
        """Check if CLI is installed and available."""
        return shutil.which(self.cli_command) is not None

    async def execute_prompt(
        self, project_path: Path, prompt: str, context: Dict[str, Any]
    ) -> str:
        """
        Execute code generation prompt using CLI.

        Args:
            project_path: Path to the project
            prompt: Code generation prompt
            context: Additional context (language, files, etc.)

        Returns:
            Generated code or response

        Raises:
            CodeCLINotFoundError: If CLI not installed
            CodeCLIExecutionError: If CLI execution fails
        """
        if not self.is_available():
            raise CodeCLINotFoundError(
                f"{self.cli_command} CLI not found. Install: {self.get_install_instructions()}"
            )

        cmd = self._build_command(prompt, context)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(project_path),  # Execute in project directory
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise CodeCLIExecutionError(
                    f"{self.cli_command} failed: {stderr.decode()}"
                )

            return stdout.decode().strip()

        except FileNotFoundError:
            raise CodeCLINotFoundError(
                f"{self.cli_command} not found: {self.get_install_instructions()}"
            )
        except Exception as e:
            raise CodeCLIExecutionError(f"{self.cli_command} execution error: {str(e)}")

    @abstractmethod
    def _build_command(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        """Build CLI command with provider-specific flags."""
        pass

    @abstractmethod
    def get_install_instructions(self) -> str:
        """Get installation instructions for this CLI."""
        pass


class CopilotCLIAdapter(CodeCLIAdapter, ICodeExecutor):
    """
    GitHub Copilot CLI adapter for code execution.

    Uses 'gh copilot suggest' in headless mode for code generation.
    Installation: gh extension install github/gh-copilot
    """

    @property
    def cli_command(self) -> str:
        return "gh"

    @property
    def provider_name(self) -> str:
        return "GitHub Copilot"

    def _build_command(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        """
        Build GitHub Copilot CLI command for code generation.

        Example:
            gh copilot suggest "create a function to..." --no-interactive
        """
        cmd = [
            self.cli_command,
            "copilot",
            "suggest",
            prompt,
            "--no-interactive",
        ]

        # Add language context if provided
        if "language" in context:
            # GitHub Copilot can infer from file extensions, but we can add hints
            pass

        # Add target file context if provided
        if "target_file" in context:
            # Copilot works better with file context
            pass

        return cmd

    def get_install_instructions(self) -> str:
        return "Install GitHub Copilot CLI: gh extension install github/gh-copilot"

    async def execute_prompt(
        self, project_path: Path, prompt: str, context: Dict[str, Any]
    ) -> str:
        """
        Execute code generation prompt using GitHub Copilot CLI.

        Enhanced to handle code-specific context and formatting.
        """
        # Enhance prompt with code generation context
        enhanced_prompt = self._enhance_code_prompt(prompt, context)

        # Execute with base implementation
        result = await super().execute_prompt(project_path, enhanced_prompt, context)

        # Post-process Copilot response
        return self._extract_code_from_response(result)

    def _enhance_code_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with code generation context."""
        enhanced = prompt

        if "language" in context:
            enhanced = f"Generate {context['language']} code: {enhanced}"

        if "target_file" in context:
            file_path = context["target_file"]
            file_ext = Path(file_path).suffix
            enhanced = f"For file {file_path} ({file_ext}): {enhanced}"

        if "existing_code" in context:
            # Add context about existing code
            existing = context["existing_code"][:500]  # Limit context
            enhanced = f"Existing code context:\n{existing}\n\n{enhanced}"

        return enhanced

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from Copilot CLI response."""
        # Copilot CLI responses are typically just the suggestion
        # Remove Any prefixes or formatting
        lines = response.strip().split("\n")

        # Remove common prefixes
        if lines and lines[0].startswith(("```", "Suggestion:", "Code:")):
            lines = lines[1:]

        # Remove trailing code fences
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(lines).strip()


class GeminiCLIAdapter(CodeCLIAdapter, ICodeExecutor):
    """
    Google Gemini CLI adapter for code execution.

    Uses 'gemini generate' for code generation tasks.
    Installation: Follow Google AI Studio setup instructions.
    """

    @property
    def cli_command(self) -> str:
        return "gemini"

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    def _build_command(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        """
        Build Gemini CLI command for code generation.

        Example:
            gemini generate --prompt "write python function..." --temperature 0.2 --max-tokens 500
        """
        cmd = [
            self.cli_command,
            "generate",
            "--prompt",
            prompt,
            "--temperature",
            "0.2",  # Lower temperature for code generation
            "--max-tokens",
            "500",  # Allow more tokens for code
        ]

        return cmd

    def get_install_instructions(self) -> str:
        return (
            "Install Google Gemini CLI from https://ai.google.dev/gemini-api/docs/cli"
        )

    async def execute_prompt(
        self, project_path: Path, prompt: str, context: Dict[str, Any]
    ) -> str:
        """
        Execute code generation prompt using Gemini CLI.

        Enhanced for code generation with proper formatting.
        """
        # Enhance prompt with code generation context
        enhanced_prompt = self._enhance_code_prompt(prompt, context)

        # Execute with base implementation
        result = await super().execute_prompt(project_path, enhanced_prompt, context)

        # Post-process Gemini response
        return self._extract_code_from_response(result)

    def _enhance_code_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with code generation context."""
        enhanced = f"""Generate code for the following request. Provide only the code without explanation unless asked.

Request: {prompt}"""

        if "language" in context:
            enhanced = f"Generate {context['language']} code: {prompt}"

        if "target_file" in context:
            file_path = context["target_file"]
            enhanced += f"\n\nTarget file: {file_path}"

        if "existing_code" in context:
            existing = context["existing_code"][:1000]  # More context for Gemini
            enhanced += f"\n\nExisting code context:\n{existing}"

        enhanced += "\n\nProvide clean, well-formatted code ready for use."

        return enhanced

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from Gemini CLI response."""
        # Gemini responses are typically direct
        # Look for code blocks
        if "```" in response:
            # Extract from code blocks
            lines = response.split("\n")
            in_code_block = False
            code_lines = []

            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    code_lines.append(line)

            if code_lines:
                return "\n".join(code_lines).strip()

        # If no code blocks, return as-is but clean up
        return response.strip()


class QwenCLIAdapter(CodeCLIAdapter, ICodeExecutor):
    """
    Alibaba Qwen CLI adapter for code execution.

    Uses 'qwen chat' for code generation tasks.
    Installation: pip install qwen-cli
    """

    @property
    def cli_command(self) -> str:
        return "qwen"

    @property
    def provider_name(self) -> str:
        return "Alibaba Qwen"

    def _build_command(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        """
        Build Qwen CLI command for code generation.

        Example:
            qwen chat --message "write python function..." --temperature 0.2 --max-tokens 500
        """
        cmd = [
            self.cli_command,
            "chat",
            "--message",
            prompt,
            "--temperature",
            "0.2",  # Lower temperature for code generation
            "--max-tokens",
            "500",  # Allow more tokens for code
        ]

        return cmd

    def get_install_instructions(self) -> str:
        return "Install Qwen CLI: pip install qwen-cli"

    async def execute_prompt(
        self, project_path: Path, prompt: str, context: Dict[str, Any]
    ) -> str:
        """
        Execute code generation prompt using Qwen CLI.

        Enhanced for code generation with proper formatting.
        """
        # Enhance prompt with code generation context
        enhanced_prompt = self._enhance_code_prompt(prompt, context)

        # Execute with base implementation
        result = await super().execute_prompt(project_path, enhanced_prompt, context)

        # Post-process Qwen response
        return self._extract_code_from_response(result)

    def _enhance_code_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Enhance prompt with code generation context."""
        enhanced = f"""请为以下需求生成代码。只提供代码，不要解释除非被要求。

需求：{prompt}"""

        if "language" in context:
            enhanced = f"生成{context['language']}代码：{prompt}"

        if "target_file" in context:
            file_path = context["target_file"]
            enhanced += f"\n\n目标文件：{file_path}"

        if "existing_code" in context:
            existing = context["existing_code"][:1000]
            enhanced += f"\n\n现有代码上下文：\n{existing}"

        enhanced += "\n\n请提供干净、格式良好的代码。"

        return enhanced

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from Qwen CLI response."""
        # Qwen responses might be in Chinese or mixed
        # Look for code blocks first
        if "```" in response:
            lines = response.split("\n")
            in_code_block = False
            code_lines = []

            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    code_lines.append(line)

            if code_lines:
                return "\n".join(code_lines).strip()

        # If no code blocks, return as-is
        return response.strip()


class DeepAgentsAdapter(CodeCLIAdapter, ICodeExecutor):
    """DeepAgents CLI adapter for research and prototyping."""

    @property
    def cli_command(self) -> str:
        return "deepagents"

    @property
    def provider_name(self) -> str:
        return "DeepAgents"

    def _build_command(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        return [self.cli_command, "--non-interactive", prompt]

    def get_install_instructions(self) -> str:
        return "Install DeepAgents CLI: pip install deepagents-cli"


class CodexAdapter(CodeCLIAdapter, ICodeExecutor):
    """Codex CLI adapter for code analysis and review."""

    @property
    def cli_command(self) -> str:
        return "codex"

    @property
    def provider_name(self) -> str:
        return "OpenAI Codex"

    def _build_command(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        # Assuming a similar non-interactive flag exists
        return [self.cli_command, "exec", prompt]

    def get_install_instructions(self) -> str:
        return "Install Codex CLI: npm install -g @openai/codex"


class RovoDevAdapter(CodeCLIAdapter, ICodeExecutor):
    """Rovo Dev CLI adapter for Jira-integrated tasks."""

    @property
    def cli_command(self) -> str:
        return "rovo"

    @property
    def provider_name(self) -> str:
        return "Atlassian Rovo Dev"

    def _build_command(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        # Correct command for non-interactive execution
        return [self.cli_command, "dev", "run", prompt]

    def get_install_instructions(self) -> str:
        return "Install Rovo Dev CLI: Follow instructions at https://support.atlassian.com/rovo/docs/use-rovo-dev-cli/"
