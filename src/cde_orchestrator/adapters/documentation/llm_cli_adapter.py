"""
LLM CLI Adapters - Headless CLI execution for multiple providers.

Implements ILLMSummaryGenerator port with support for:
    - Google Gemini (gemini CLI)
    - Alibaba Qwen (qwen CLI)
    - GitHub Copilot (gh copilot CLI)

Design Philosophy:
    - Reuse CLI authentication (no API keys in code)
    - Fallback chain for robustness
    - Unified interface across providers
    - Async execution for performance

Architecture:
    MultiProviderLLMCLIAdapter (facade)
    ├── GeminiCLIAdapter
    ├── QwenCLIAdapter
    └── CopilotCLIAdapter
"""

import asyncio
import shutil
from abc import ABC, abstractmethod
from typing import List

from ...domain.documentation.entities import DocumentType, Specification
from ...domain.documentation.ports import ILLMSummaryGenerator, LLMProvider


class LLMCLIError(Exception):
    """Base exception for LLM CLI execution errors."""

    pass


class LLMCLINotFoundError(LLMCLIError):
    """Raised when CLI executable not found."""

    pass


class LLMCLIExecutionError(LLMCLIError):
    """Raised when CLI execution fails."""

    pass


class BaseLLMCLIAdapter(ABC):
    """
    Abstract base for LLM CLI adapters.

    Subclasses implement provider-specific CLI invocation.
    """

    @property
    @abstractmethod
    def provider(self) -> LLMProvider:
        """Which provider this adapter supports."""
        pass

    @property
    @abstractmethod
    def cli_command(self) -> str:
        """CLI command name (e.g., 'gemini', 'qwen')."""
        pass

    def is_available(self) -> bool:
        """Check if CLI is installed and available."""
        return shutil.which(self.cli_command) is not None

    async def execute_cli(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 200
    ) -> str:
        """
        Execute CLI with prompt in headless mode.

        Args:
            prompt: Prompt to send to LLM
            temperature: Sampling temperature (0-1)
            max_tokens: Max tokens in response

        Returns:
            LLM response text

        Raises:
            LLMCLINotFoundError: If CLI not installed
            LLMCLIExecutionError: If CLI execution fails
        """
        if not self.is_available():
            raise LLMCLINotFoundError(
                f"{self.cli_command} CLI not found. Install: {self.get_install_instructions()}"
            )

        cmd = self._build_command(prompt, temperature, max_tokens)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise LLMCLIExecutionError(
                    f"{self.cli_command} failed: {stderr.decode()}"
                )

            return stdout.decode().strip()

        except FileNotFoundError:
            raise LLMCLINotFoundError(
                f"{self.cli_command} not found: {self.get_install_instructions()}"
            )
        except Exception as e:
            raise LLMCLIExecutionError(f"{self.cli_command} execution error: {str(e)}")

    @abstractmethod
    def _build_command(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> List[str]:
        """Build CLI command with provider-specific flags."""
        pass

    @abstractmethod
    def get_install_instructions(self) -> str:
        """Get installation instructions for this CLI."""
        pass


class GeminiCLIAdapter(BaseLLMCLIAdapter, ILLMSummaryGenerator):
    """
    Google Gemini CLI adapter.

    Assumes 'gemini' CLI is installed and authenticated.
    Installation: Follow Google AI Studio setup instructions.
    """

    @property
    def provider(self) -> LLMProvider:
        return LLMProvider.GEMINI

    @property
    def cli_command(self) -> str:
        return "gemini"

    def _build_command(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> List[str]:
        """
        Build Gemini CLI command.

        Example:
            gemini generate --prompt "..." --temperature 0.3 --max-tokens 200
        """
        return [
            self.cli_command,
            "generate",
            "--prompt",
            prompt,
            "--temperature",
            str(temperature),
            "--max-tokens",
            str(max_tokens),
        ]

    def get_install_instructions(self) -> str:
        return (
            "Install Google Gemini CLI from https://ai.google.dev/gemini-api/docs/cli"
        )

    async def generate_summary(
        self,
        spec: Specification,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """Generate summary using Gemini CLI."""
        prompt = self._build_summary_prompt(spec.title, spec.type, spec.content)
        response = await self.execute_cli(prompt, temperature=0.3, max_tokens=150)
        return self._extract_summary(response)

    async def generate_summary_for_content(
        self,
        content: str,
        title: str,
        doc_type: DocumentType,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """Generate summary for raw content."""
        prompt = self._build_summary_prompt(title, doc_type, content)
        response = await self.execute_cli(prompt, temperature=0.3, max_tokens=150)
        return self._extract_summary(response)

    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if Gemini CLI is available."""
        return provider == LLMProvider.GEMINI and self.is_available()

    def get_available_providers(self) -> List[LLMProvider]:
        """Get available providers (just Gemini)."""
        return [LLMProvider.GEMINI] if self.is_available() else []

    def _build_summary_prompt(
        self, title: str, doc_type: DocumentType, content: str
    ) -> str:
        """Build prompt for summary generation."""
        return f"""Generate a concise 2-3 sentence summary for this documentation.

Title: {title}
Type: {doc_type.value}

Content:
{content[:2000]}

Requirements:
- 2-3 sentences only
- Optimize for LLM context (answer: What is this? Why does it exist? When to use it?)
- Must be under 100 words
- Focus on key concepts and purpose

Summary:"""

    def _extract_summary(self, response: str) -> str:
        """Extract and validate summary from LLM response."""
        # Remove common prefixes
        summary = response.strip()
        for prefix in [
            "Summary:",
            "summary:",
            "Here's the summary:",
            "Here is the summary:",
        ]:
            if summary.startswith(prefix):
                summary = summary[len(prefix) :].strip()

        # Validate length
        if len(summary.split()) > 100:
            # Truncate to 100 words
            words = summary.split()[:100]
            summary = " ".join(words) + "..."

        return summary


class QwenCLIAdapter(BaseLLMCLIAdapter, ILLMSummaryGenerator):
    """
    Alibaba Qwen CLI adapter.

    Assumes 'qwen' CLI is installed.
    Installation: pip install qwen-cli
    """

    @property
    def provider(self) -> LLMProvider:
        return LLMProvider.QWEN

    @property
    def cli_command(self) -> str:
        return "qwen"

    def _build_command(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> List[str]:
        """
        Build Qwen CLI command.

        Example:
            qwen chat --message "..." --temperature 0.3 --max-tokens 200
        """
        return [
            self.cli_command,
            "chat",
            "--message",
            prompt,
            "--temperature",
            str(temperature),
            "--max-tokens",
            str(max_tokens),
        ]

    def get_install_instructions(self) -> str:
        return "Install Qwen CLI: pip install qwen-cli"

    async def generate_summary(
        self,
        spec: Specification,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """Generate summary using Qwen CLI."""
        prompt = self._build_summary_prompt(spec.title, spec.type, spec.content)
        response = await self.execute_cli(prompt, temperature=0.3, max_tokens=150)
        return self._extract_summary(response)

    async def generate_summary_for_content(
        self,
        content: str,
        title: str,
        doc_type: DocumentType,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """Generate summary for raw content."""
        prompt = self._build_summary_prompt(title, doc_type, content)
        response = await self.execute_cli(prompt, temperature=0.3, max_tokens=150)
        return self._extract_summary(response)

    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if Qwen CLI is available."""
        return provider == LLMProvider.QWEN and self.is_available()

    def get_available_providers(self) -> List[LLMProvider]:
        """Get available providers (just Qwen)."""
        return [LLMProvider.QWEN] if self.is_available() else []

    def _build_summary_prompt(
        self, title: str, doc_type: DocumentType, content: str
    ) -> str:
        """Build prompt for summary generation."""
        return f"""请为以下文档生成一个简洁的2-3句话总结：

标题：{title}
类型：{doc_type.value}

内容：
{content[:2000]}

要求：
- 仅2-3句话
- 优化用于LLM上下文（回答：这是什么？为什么存在？何时使用？）
- 必须少于100个单词
- 关注关键概念和目的

总结："""

    def _extract_summary(self, response: str) -> str:
        """Extract and validate summary from LLM response."""
        summary = response.strip()
        for prefix in ["总结：", "摘要：", "Summary:", "summary:"]:
            if summary.startswith(prefix):
                summary = summary[len(prefix) :].strip()

        if len(summary.split()) > 100:
            words = summary.split()[:100]
            summary = " ".join(words) + "..."

        return summary


class CopilotCLIAdapter(BaseLLMCLIAdapter, ILLMSummaryGenerator):
    """
    GitHub Copilot CLI adapter.

    Uses 'gh copilot suggest' in headless mode.
    Installation: gh extension install github/gh-copilot
    """

    @property
    def provider(self) -> LLMProvider:
        return LLMProvider.COPILOT

    @property
    def cli_command(self) -> str:
        return "gh"

    def _build_command(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> List[str]:
        """
        Build GitHub Copilot CLI command.

        Example:
            gh copilot suggest --prompt "..." --no-interactive
        """
        return [
            self.cli_command,
            "copilot",
            "suggest",
            prompt,
            "--no-interactive",
        ]

    def get_install_instructions(self) -> str:
        return "Install GitHub Copilot CLI: gh extension install github/gh-copilot"

    async def generate_summary(
        self,
        spec: Specification,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """Generate summary using Copilot CLI."""
        prompt = self._build_summary_prompt(spec.title, spec.type, spec.content)
        response = await self.execute_cli(prompt, temperature=0.3, max_tokens=150)
        return self._extract_summary(response)

    async def generate_summary_for_content(
        self,
        content: str,
        title: str,
        doc_type: DocumentType,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """Generate summary for raw content."""
        prompt = self._build_summary_prompt(title, doc_type, content)
        response = await self.execute_cli(prompt, temperature=0.3, max_tokens=150)
        return self._extract_summary(response)

    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if Copilot CLI is available."""
        return provider == LLMProvider.COPILOT and self.is_available()

    def get_available_providers(self) -> List[LLMProvider]:
        """Get available providers (just Copilot)."""
        return [LLMProvider.COPILOT] if self.is_available() else []

    def _build_summary_prompt(
        self, title: str, doc_type: DocumentType, content: str
    ) -> str:
        """Build prompt for summary generation."""
        return f"""Generate a concise 2-3 sentence summary for this documentation.

Title: {title}
Type: {doc_type.value}

Content:
{content[:2000]}

Requirements:
- 2-3 sentences only
- Optimize for LLM context (answer: What is this? Why does it exist? When to use it?)
- Must be under 100 words
- Focus on key concepts and purpose

Summary:"""

    def _extract_summary(self, response: str) -> str:
        """Extract and validate summary from LLM response."""
        summary = response.strip()
        for prefix in ["Summary:", "summary:", "Suggestion:", "suggestion:"]:
            if summary.startswith(prefix):
                summary = summary[len(prefix) :].strip()

        if len(summary.split()) > 100:
            words = summary.split()[:100]
            summary = " ".join(words) + "..."

        return summary


class MultiProviderLLMCLIAdapter(ILLMSummaryGenerator):
    """
    Multi-provider LLM CLI adapter with fallback chain.

    Tries providers in order:
        1. Gemini (if available)
        2. Copilot (if available)
        3. Qwen (if available)

    Provides robust summary generation with automatic failover.
    """

    def __init__(self):
        """Initialize with all provider adapters."""
        self.providers = {
            LLMProvider.GEMINI: GeminiCLIAdapter(),
            LLMProvider.QWEN: QwenCLIAdapter(),
            LLMProvider.COPILOT: CopilotCLIAdapter(),
        }
        self.fallback_order = [
            LLMProvider.GEMINI,
            LLMProvider.COPILOT,
            LLMProvider.QWEN,
        ]

    async def generate_summary(
        self,
        spec: Specification,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """
        Generate summary with automatic provider fallback.

        Args:
            spec: Specification to summarize
            provider: Preferred provider (AUTO = try all)

        Returns:
            Generated summary

        Raises:
            LLMCLIError: If all providers fail
        """
        if provider == LLMProvider.AUTO:
            providers_to_try = self.fallback_order
        else:
            providers_to_try = [provider]

        last_error = None
        for provider_name in providers_to_try:
            adapter = self.providers[provider_name]
            if not adapter.is_available():
                continue

            try:
                return await adapter.generate_summary(spec, provider_name)
            except LLMCLIError as e:
                last_error = e
                continue

        # All providers failed
        if last_error:
            raise last_error
        else:
            raise LLMCLINotFoundError(
                "No LLM CLI providers available. Install at least one: "
                f"{', '.join(p.value for p in self.fallback_order)}"
            )

    async def generate_summary_for_content(
        self,
        content: str,
        title: str,
        doc_type: DocumentType,
        provider: LLMProvider = LLMProvider.AUTO,
    ) -> str:
        """Generate summary for raw content with fallback."""
        if provider == LLMProvider.AUTO:
            providers_to_try = self.fallback_order
        else:
            providers_to_try = [provider]

        last_error = None
        for provider_name in providers_to_try:
            adapter = self.providers[provider_name]
            if not adapter.is_available():
                continue

            try:
                return await adapter.generate_summary_for_content(
                    content, title, doc_type, provider_name
                )
            except LLMCLIError as e:
                last_error = e
                continue

        if last_error:
            raise last_error
        else:
            raise LLMCLINotFoundError("No LLM CLI providers available")

    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if specific provider is available."""
        if provider == LLMProvider.AUTO:
            return any(self.providers[p].is_available() for p in self.fallback_order)
        return self.providers[provider].is_available()

    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of all available providers."""
        available = []
        for provider_name in self.fallback_order:
            if self.providers[provider_name].is_available():
                available.append(provider_name)
        return available
