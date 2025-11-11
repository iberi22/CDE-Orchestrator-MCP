"""
Integration tests for CLI Code Adapters.

Tests the actual CLI execution for Copilot, Gemini, and Qwen adapters.
These tests require the respective CLIs to be installed and authenticated.
"""

from unittest.mock import AsyncMock, patch

import pytest

from cde_orchestrator.adapters.agents.code_cli_adapters import (
    CodeCLIExecutionError,
    CodeCLINotFoundError,
    CodexAdapter,
    CopilotCLIAdapter,
    DeepAgentsAdapter,
    GeminiCLIAdapter,
    QwenCLIAdapter,
    RovoDevAdapter,
)


class TestCopilotCLIAdapter:
    """Test Copilot CLI adapter integration."""

    @pytest.fixture
    def adapter(self):
        return CopilotCLIAdapter()

    def test_provider_name(self, adapter):
        assert adapter.provider_name == "GitHub Copilot"

    def test_cli_command(self, adapter):
        assert adapter.cli_command == "gh"

    def test_is_available_when_gh_installed(self, adapter):
        """Test availability check when gh CLI is installed."""
        with patch("shutil.which", return_value="/usr/bin/gh"):
            assert adapter.is_available() is True

    def test_is_available_when_gh_not_installed(self, adapter):
        """Test availability check when gh CLI is not installed."""
        with patch("shutil.which", return_value=None):
            assert adapter.is_available() is False

    @pytest.mark.asyncio
    async def test_execute_prompt_cli_not_found(self, adapter, tmp_path):
        """Test that CodeCLINotFoundError is raised when CLI not found."""
        with patch.object(adapter, "is_available", return_value=False):
            with pytest.raises(CodeCLINotFoundError, match="gh CLI not found"):
                await adapter.execute_prompt(tmp_path, "test prompt", {})

    @pytest.mark.asyncio
    async def test_execute_prompt_success(self, adapter, tmp_path):
        """Test successful prompt execution."""
        mock_response = "def hello():\n    return 'world'"

        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                # Mock the process
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (mock_response.encode(), b"")
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                result = await adapter.execute_prompt(
                    tmp_path, "create hello function", {}
                )

                # Verify the command was built correctly
                mock_subprocess.assert_called_once()
                args, kwargs = mock_subprocess.call_args
                assert args[0] == "gh"
                assert "copilot" in args
                assert "suggest" in args
                assert "create hello function" in args
                assert "--no-interactive" in args

                # Verify result processing
                assert "def hello():" in result

    @pytest.mark.asyncio
    async def test_execute_prompt_with_context(self, adapter, tmp_path):
        """Test prompt execution with language and file context."""
        context = {
            "language": "python",
            "target_file": "utils.py",
            "existing_code": "class Utils:\n    pass",
        }

        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b'print("hello")', b"")
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                await adapter.execute_prompt(tmp_path, "add print function", context)

                # Verify enhanced prompt was used
                args, kwargs = mock_subprocess.call_args
                prompt_arg = None
                for arg in args:
                    if "Generate python code:" in str(arg):
                        prompt_arg = arg
                        break
                assert prompt_arg is not None
                assert "python" in prompt_arg
                assert "utils.py" in prompt_arg

    @pytest.mark.asyncio
    async def test_execute_prompt_cli_error(self, adapter, tmp_path):
        """Test handling of CLI execution errors."""
        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (
                    b"",
                    b"Error: authentication failed",
                )
                mock_process.returncode = 1
                mock_subprocess.return_value = mock_process

                with pytest.raises(CodeCLIExecutionError, match="gh failed"):
                    await adapter.execute_prompt(tmp_path, "test", {})


class TestGeminiCLIAdapter:
    """Test Gemini CLI adapter integration."""

    @pytest.fixture
    def adapter(self):
        return GeminiCLIAdapter()

    def test_provider_name(self, adapter):
        assert adapter.provider_name == "Google Gemini"

    def test_cli_command(self, adapter):
        assert adapter.cli_command == "gemini"

    @pytest.mark.asyncio
    async def test_execute_prompt_success(self, adapter, tmp_path):
        """Test successful Gemini prompt execution."""
        mock_response = "```python\ndef hello():\n    return 'world'\n```"

        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (mock_response.encode(), b"")
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                result = await adapter.execute_prompt(
                    tmp_path, "create hello function", {}
                )

                # Verify command structure
                args, kwargs = mock_subprocess.call_args
                assert args[0] == "gemini"
                assert "generate" in args
                assert "--prompt" in args
                assert "--temperature" in args
                assert "--max-tokens" in args

                # Verify code extraction from response
                assert "def hello():" in result
                assert "return 'world'" in result

    @pytest.mark.asyncio
    async def test_execute_prompt_with_code_blocks(self, adapter, tmp_path):
        """Test code extraction from Gemini responses with code blocks."""
        mock_response = """Here's the code you requested:

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}
```

This function takes a name parameter and returns a greeting."""

        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (mock_response.encode(), b"")
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                result = await adapter.execute_prompt(
                    tmp_path, "create greet function", {}
                )

                # Should extract only the code between ``` markers
                assert "function greet(name) {" in result
                assert "return `Hello, ${name}!`;" in result
                assert "Here's the code" not in result
                assert "This function takes" not in result


class TestQwenCLIAdapter:
    """Test Qwen CLI adapter integration."""

    @pytest.fixture
    def adapter(self):
        return QwenCLIAdapter()

    def test_provider_name(self, adapter):
        assert adapter.provider_name == "Alibaba Qwen"

    def test_cli_command(self, adapter):
        assert adapter.cli_command == "qwen"

    @pytest.mark.asyncio
    async def test_execute_prompt_success(self, adapter, tmp_path):
        """Test successful Qwen prompt execution."""
        mock_response = "```python\nclass Calculator:\n    def add(self, a, b):\n        return a + b\n```"

        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (mock_response.encode(), b"")
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                result = await adapter.execute_prompt(
                    tmp_path, "create calculator class", {}
                )

                # Verify command structure
                args, kwargs = mock_subprocess.call_args
                assert args[0] == "qwen"
                assert "chat" in args
                assert "--message" in args
                assert "--temperature" in args
                assert "--max-tokens" in args

                # Verify code extraction
                assert "class Calculator:" in result
                assert "def add(self, a, b):" in result

    @pytest.mark.asyncio
    async def test_execute_prompt_chinese_context(self, adapter, tmp_path):
        """Test Qwen prompt enhancement with Chinese context."""
        context = {"language": "python", "target_file": "math_utils.py"}

        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (
                    b"def multiply(a, b): return a * b",
                    b"",
                )
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                await adapter.execute_prompt(
                    tmp_path, "create multiply function", context
                )

                # Verify Chinese prompt enhancement
                args, kwargs = mock_subprocess.call_args
                message_arg = None
                for arg in args:
                    if isinstance(arg, str) and "生成python代码" in arg:
                        message_arg = arg
                        break
                assert message_arg is not None
                assert "python" in message_arg
                assert "math_utils.py" in message_arg


class TestCLIAdapterErrorHandling:
    """Test error handling across all CLI adapters."""

    @pytest.mark.parametrize(
        "adapter_class",
        [
            CopilotCLIAdapter,
            GeminiCLIAdapter,
            QwenCLIAdapter,
            DeepAgentsAdapter,
            CodexAdapter,
            RovoDevAdapter,
        ],
    )
    @pytest.mark.asyncio
    async def test_subprocess_execution_error(self, adapter_class, tmp_path):
        """Test handling of subprocess execution errors."""
        adapter = adapter_class()

        with patch.object(adapter, "is_available", return_value=True):
            with patch(
                "asyncio.create_subprocess_exec", side_effect=OSError("Command failed")
            ):
                with pytest.raises(CodeCLIExecutionError):
                    await adapter.execute_prompt(tmp_path, "test", {})

    @pytest.mark.parametrize(
        "adapter_class",
        [
            CopilotCLIAdapter,
            GeminiCLIAdapter,
            QwenCLIAdapter,
        ],
    )
    def test_install_instructions(self, adapter_class):
        """Test that install instructions are provided."""
        adapter = adapter_class()
        instructions = adapter.get_install_instructions()
        assert isinstance(instructions, str)
        assert len(instructions) > 0
        assert "install" in instructions.lower() or "Install" in instructions


class TestDeepAgentsAdapter:
    """Test DeepAgents CLI adapter integration."""

    @pytest.fixture
    def adapter(self):
        return DeepAgentsAdapter()

    @pytest.mark.asyncio
    async def test_execute_prompt_success(self, adapter, tmp_path):
        """Test successful prompt execution."""
        mock_response = "Research complete"

        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (mock_response.encode(), b"")
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                result = await adapter.execute_prompt(tmp_path, "research topic", {})
                assert "Research complete" in result


class TestCodexAdapter:
    """Test Codex CLI adapter integration."""

    @pytest.fixture
    def adapter(self):
        return CodexAdapter()

    @pytest.mark.asyncio
    async def test_execute_prompt_success(self, adapter, tmp_path):
        """Test successful prompt execution."""
        mock_response = "Analysis complete"

        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (mock_response.encode(), b"")
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                result = await adapter.execute_prompt(tmp_path, "analyze code", {})
                assert "Analysis complete" in result


class TestRovoDevAdapter:
    """Test Rovo Dev CLI adapter integration."""

    @pytest.fixture
    def adapter(self):
        return RovoDevAdapter()

    @pytest.mark.asyncio
    async def test_execute_prompt_success(self, adapter, tmp_path):
        """Test successful prompt execution."""
        mock_response = "Task JIRA-123 complete"

        with patch.object(adapter, "is_available", return_value=True):
            with patch("asyncio.create_subprocess_exec") as mock_subprocess:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (mock_response.encode(), b"")
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process

                result = await adapter.execute_prompt(
                    tmp_path, "complete task JIRA-123", {}
                )
                assert "Task JIRA-123 complete" in result
