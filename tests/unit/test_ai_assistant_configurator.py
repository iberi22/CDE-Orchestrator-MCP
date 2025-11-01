# tests/unit/test_ai_assistant_configurator.py
"""
Unit tests for AIAssistantConfigurator.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.cde_orchestrator.ai_assistant_configurator import (
    AIAssistantConfigurator,
    AgentConfig,
)


@pytest.fixture
def temp_project_root(tmp_path):
    """Create a temporary project root directory."""
    return tmp_path / "test_project"


@pytest.fixture
def configurator(temp_project_root):
    """Create an AIAssistantConfigurator instance."""
    temp_project_root.mkdir(parents=True, exist_ok=True)
    return AIAssistantConfigurator(temp_project_root)


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_agent_config_creation(self):
        """Test creating an AgentConfig instance."""
        config = AgentConfig(
            name="Test Agent",
            key="test",
            folder=".test/",
            install_url="https://test.com",
            requires_cli=True,
            config_files=["TEST.md"],
        )

        assert config.name == "Test Agent"
        assert config.key == "test"
        assert config.folder == ".test/"
        assert config.install_url == "https://test.com"
        assert config.requires_cli is True
        assert config.config_files == ["TEST.md"]


class TestAIAssistantConfigurator:
    """Tests for AIAssistantConfigurator class."""

    def test_initialization(self, configurator, temp_project_root):
        """Test configurator initialization."""
        assert configurator.project_root == temp_project_root
        assert configurator.detected_agents == []
        assert len(configurator.AGENT_CONFIG) > 0

    def test_agent_config_structure(self, configurator):
        """Test that AGENT_CONFIG has required structure."""
        for agent_key, config in configurator.AGENT_CONFIG.items():
            assert isinstance(config, AgentConfig)
            assert config.name is not None
            assert config.key == agent_key
            assert config.folder is not None
            assert isinstance(config.requires_cli, bool)
            assert isinstance(config.config_files, list)

    def test_detect_installed_agents_no_tools(self, configurator):
        """Test detection when no tools are installed."""
        with patch.object(configurator, "_check_cli_tool", return_value=False):
            detected = configurator.detect_installed_agents()
            # Should only detect IDE-based agents with existing folders (none in temp dir)
            assert isinstance(detected, list)

    def test_detect_installed_agents_with_cli(self, configurator):
        """Test detection when CLI tools are installed."""

        def mock_check(tool_name):
            return tool_name in ["gemini", "claude"]

        with patch.object(configurator, "_check_cli_tool", side_effect=mock_check):
            detected = configurator.detect_installed_agents()
            assert "gemini" in detected
            assert "claude" in detected

    def test_detect_installed_agents_with_existing_folders(
        self, configurator, temp_project_root
    ):
        """Test detection when agent folders already exist."""
        # Create .github folder (Copilot)
        github_folder = temp_project_root / ".github"
        github_folder.mkdir(parents=True, exist_ok=True)

        # Create .cursor folder
        cursor_folder = temp_project_root / ".cursor"
        cursor_folder.mkdir(parents=True, exist_ok=True)

        with patch.object(configurator, "_check_cli_tool", return_value=False):
            detected = configurator.detect_installed_agents()
            assert "copilot" in detected
            assert "cursor" in detected

    def test_check_cli_tool_not_found(self, configurator):
        """Test checking for a CLI tool that doesn't exist."""
        result = configurator._check_cli_tool("nonexistent_tool_xyz_12345")
        assert result is False

    @patch("subprocess.run")
    def test_check_cli_tool_found(self, mock_run, configurator):
        """Test checking for a CLI tool that exists."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = configurator._check_cli_tool("git")
        assert result is True

    def test_generate_config_files_default(self, configurator):
        """Test generating config files with defaults."""
        with patch.object(
            configurator, "detect_installed_agents", return_value=["copilot"]
        ):
            with patch.object(
                configurator, "_generate_root_instruction_file"
            ) as mock_generate:
                with patch.object(
                    configurator, "_generate_copilot_config"
                ) as mock_copilot:
                    results = configurator.generate_config_files()

                    assert "generated" in results
                    assert "skipped" in results
                    assert "errors" in results

    def test_generate_config_files_specific_agents(self, configurator):
        """Test generating config files for specific agents."""
        with patch.object(
            configurator, "_generate_root_instruction_file"
        ) as mock_generate:
            with patch.object(configurator, "_generate_copilot_config") as mock_copilot:
                results = configurator.generate_config_files(agents=["copilot"])

                assert "generated" in results
                # Should attempt to generate AGENTS.md
                assert (
                    mock_generate.called
                    or len(results["generated"]) > 0
                    or len(results["skipped"]) > 0
                )

    def test_generate_config_files_unknown_agent(self, configurator):
        """Test generating config files with unknown agent."""
        results = configurator.generate_config_files(agents=["unknown_agent"])

        assert "errors" in results
        assert len(results["errors"]) > 0
        assert any("unknown_agent" in str(err).lower() for err in results["errors"])

    def test_generate_agents_md(self, configurator, temp_project_root):
        """Test generating AGENTS.md file."""
        configurator._generate_root_instruction_file("AGENTS.md")

        agents_md = temp_project_root / "AGENTS.md"
        assert agents_md.exists()

        content = agents_md.read_text(encoding="utf-8")
        assert "Agent Instructions" in content
        assert "Project Overview" in content
        assert "Architecture Rules" in content
        assert "Development Workflow" in content

    def test_generate_gemini_md(self, configurator, temp_project_root):
        """Test generating GEMINI.md file."""
        configurator._generate_root_instruction_file("GEMINI.md")

        gemini_md = temp_project_root / "GEMINI.md"
        assert gemini_md.exists()

        content = gemini_md.read_text(encoding="utf-8")
        assert "Gemini AI Instructions" in content
        assert "Gemini-Specific Optimizations" in content
        assert "1M+ token" in content or "Large Context Window" in content

    def test_generate_copilot_config(self, configurator, temp_project_root):
        """Test generating GitHub Copilot configuration."""
        results = {"generated": [], "skipped": [], "errors": []}

        agent_folder = temp_project_root / ".github"
        configurator._generate_copilot_config(
            agent_folder, force=False, results=results
        )

        assert agent_folder.exists()
        instructions_file = agent_folder / "copilot-instructions.md"
        assert instructions_file.exists()
        assert str(instructions_file) in results["generated"]

        content = instructions_file.read_text()
        assert "GitHub Copilot Instructions" in content
        assert "Project Overview" in content

    def test_generate_copilot_config_skip_existing(
        self, configurator, temp_project_root
    ):
        """Test that existing Copilot config is skipped when force=False."""
        results = {"generated": [], "skipped": [], "errors": []}

        # Create existing file
        agent_folder = temp_project_root / ".github"
        agent_folder.mkdir(parents=True, exist_ok=True)
        instructions_file = agent_folder / "copilot-instructions.md"
        instructions_file.write_text("Existing content")

        configurator._generate_copilot_config(
            agent_folder, force=False, results=results
        )

        assert str(instructions_file) in results["skipped"]
        assert instructions_file.read_text() == "Existing content"

    def test_generate_copilot_config_overwrite(self, configurator, temp_project_root):
        """Test that existing Copilot config is overwritten when force=True."""
        results = {"generated": [], "skipped": [], "errors": []}

        # Create existing file
        agent_folder = temp_project_root / ".github"
        agent_folder.mkdir(parents=True, exist_ok=True)
        instructions_file = agent_folder / "copilot-instructions.md"
        instructions_file.write_text("Existing content")

        configurator._generate_copilot_config(agent_folder, force=True, results=results)

        assert str(instructions_file) in results["generated"]
        content = instructions_file.read_text()
        assert content != "Existing content"
        assert "GitHub Copilot Instructions" in content

    def test_get_configuration_summary(self, configurator, temp_project_root):
        """Test getting configuration summary."""
        # Create some config files
        (temp_project_root / "AGENTS.md").write_text("# AGENTS")
        (temp_project_root / ".github").mkdir(parents=True, exist_ok=True)

        summary = configurator.get_configuration_summary()

        assert "total_agents" in summary
        assert "detected_agents" in summary
        assert "configured_agents" in summary
        assert "available_agents" in summary

        assert summary["total_agents"] == len(configurator.AGENT_CONFIG)
        assert isinstance(summary["configured_agents"], list)
        assert isinstance(summary["available_agents"], list)

    def test_get_agents_md_template_includes_project_name(
        self, configurator, temp_project_root
    ):
        """Test that AGENTS.md template includes project name."""
        content = configurator._get_agents_md_template("MyProject")

        assert "MyProject" in content
        assert "Agent Instructions" in content

    def test_get_gemini_md_template_includes_project_name(
        self, configurator, temp_project_root
    ):
        """Test that GEMINI.md template includes project name."""
        content = configurator._get_gemini_md_template("MyProject")

        assert "MyProject" in content
        assert "Gemini AI Instructions" in content

    def test_get_copilot_instructions_template_includes_project_name(
        self, configurator, temp_project_root
    ):
        """Test that Copilot instructions template includes project name."""
        content = configurator._get_copilot_instructions_template("MyProject")

        assert "MyProject" in content
        assert "GitHub Copilot Instructions" in content


class TestIntegration:
    """Integration tests for AIAssistantConfigurator."""

    def test_full_onboarding_flow(self, temp_project_root):
        """Test complete onboarding flow with AI assistant configuration."""
        configurator = AIAssistantConfigurator(temp_project_root)

        # Generate config files
        results = configurator.generate_config_files(
            agents=["copilot", "gemini"], force=False
        )

        # Verify results
        assert "generated" in results
        assert "skipped" in results
        assert "errors" in results

        # Check that files were created
        assert (temp_project_root / "AGENTS.md").exists()
        assert (temp_project_root / "GEMINI.md").exists()
        assert (temp_project_root / ".github" / "copilot-instructions.md").exists()

        # Verify summary
        summary = configurator.get_configuration_summary()
        assert "copilot" in summary["configured_agents"]
        # gemini might be in configured_agents if GEMINI.md exists

    def test_template_content_quality(self, temp_project_root):
        """Test that generated templates have expected quality."""
        configurator = AIAssistantConfigurator(temp_project_root)
        configurator.generate_config_files(agents=["copilot", "gemini"], force=False)

        # Check AGENTS.md
        agents_md = temp_project_root / "AGENTS.md"
        content = agents_md.read_text(encoding="utf-8")

        # Should have key sections
        assert "## 🎯 Project Overview" in content
        assert "## 📁 Quick Navigation" in content
        assert "## 🏗️ Architecture Rules" in content
        assert "## 🛠️ Development Workflow" in content
        assert "## 📝 Documentation Rules" in content
        assert "## 🧪 Testing Strategy" in content

        # Check GEMINI.md
        gemini_md = temp_project_root / "GEMINI.md"
        content = gemini_md.read_text(encoding="utf-8")

        # Should have Gemini-specific sections
        assert "## 🎨 Gemini-Specific Optimizations" in content
        assert "### 1. Large Context Window" in content
        assert "### 2. Multi-Modal Capabilities" in content
        assert "### 3. Function Calling" in content
        assert "### 4. Parallel Processing" in content

        # Check Copilot instructions
        copilot_md = temp_project_root / ".github" / "copilot-instructions.md"
        content = copilot_md.read_text(encoding="utf-8")

        # Should have YAML frontmatter
        assert content.startswith("---")
        assert "description:" in content
        assert "## Project Overview" in content
