"""
Unit tests for MultiAgentOrchestrator.

Tests agent orchestration, fallback chain, and capability reporting.
"""

import asyncio
from pathlib import Path

import pytest

from cde_orchestrator.adapters.agents.agent_selection_policy import (
    AgentType,
    TaskComplexity,
)
from cde_orchestrator.adapters.agents.multi_agent_orchestrator import (
    AgentRegistry,
    MultiAgentOrchestrator,
)
from cde_orchestrator.domain.ports import ICodeExecutor


class MockCodeExecutor(ICodeExecutor):
    """Mock code executor for testing."""

    def __init__(self, name: str, should_fail: bool = False, delay: float = 0.0):
        """Initialize mock executor."""
        self.name = name
        self.should_fail = should_fail
        self.delay = delay
        self.call_count = 0
        self.last_prompt = None

    async def execute_prompt(
        self,
        project_path: Path,
        prompt: str,
        context: dict | None = None,
    ) -> str:
        """Execute prompt (mocked)."""
        self.call_count += 1
        self.last_prompt = prompt

        if self.should_fail:
            raise RuntimeError(f"{self.name} execution failed")

        if self.delay > 0:
            await asyncio.sleep(self.delay)

        return f"Result from {self.name}: {prompt[:20]}..."


class TestAgentRegistry:
    """Test AgentRegistry."""

    def test_register_agent(self):
        """Test agent registration."""
        registry = AgentRegistry()
        executor = MockCodeExecutor("test-agent")

        registry.register(AgentType.JULES, executor)

        assert registry.is_available(AgentType.JULES)

    def test_get_agent(self):
        """Test agent retrieval."""
        registry = AgentRegistry()
        executor = MockCodeExecutor("test-agent")

        registry.register(AgentType.JULES, executor)
        retrieved = registry.get(AgentType.JULES)

        assert retrieved == executor

    def test_get_unregistered_agent_returns_none(self):
        """Test retrieving unregistered agent."""
        registry = AgentRegistry()

        agent = registry.get(AgentType.JULES)

        assert agent is None

    def test_get_available_agents(self):
        """Test listing available agents."""
        registry = AgentRegistry()

        registry.register(AgentType.JULES, MockCodeExecutor("jules"))
        registry.register(AgentType.COPILOT, MockCodeExecutor("copilot"))

        agents = registry.get_available()

        assert len(agents) == 2
        assert AgentType.JULES in agents
        assert AgentType.COPILOT in agents

    def test_is_available(self):
        """Test checking if agent is available."""
        registry = AgentRegistry()

        assert registry.is_available(AgentType.JULES) is False

        registry.register(AgentType.JULES, MockCodeExecutor("jules"))

        assert registry.is_available(AgentType.JULES) is True

    def test_multiple_agents_isolation(self):
        """Test that registries are independent."""
        registry1 = AgentRegistry()
        registry2 = AgentRegistry()

        registry1.register(AgentType.JULES, MockCodeExecutor("jules"))

        assert registry1.is_available(AgentType.JULES)
        assert not registry2.is_available(AgentType.JULES)


class TestMultiAgentOrchestrator:
    """Test MultiAgentOrchestrator."""

    def test_implements_icode_executor(self):
        """Test that orchestrator implements ICodeExecutor."""
        orchestrator = MultiAgentOrchestrator()

        assert isinstance(orchestrator, ICodeExecutor)

    @pytest.mark.asyncio
    async def test_execute_prompt_success(self):
        """Test successful execution with available agent."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(
            AgentType.JULES,
            MockCodeExecutor("jules"),
        )

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Test prompt",
            context={},
        )

        assert result is not None
        assert "Result from jules" in result

    @pytest.mark.asyncio
    async def test_execute_prompt_with_context(self):
        """Test execution with task complexity context."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(
            AgentType.JULES,
            MockCodeExecutor("jules"),
        )

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Complex refactoring task",
            context={
                "complexity": TaskComplexity.COMPLEX,
                "context_size": 50000,
            },
        )

        assert result is not None
        assert "Result from jules" in result

    @pytest.mark.asyncio
    async def test_execute_prompt_with_preferred_agent(self):
        """Test execution with preferred agent override."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))
        orchestrator.register_agent(AgentType.COPILOT, MockCodeExecutor("copilot"))

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Test",
            context={"preferred_agent": AgentType.COPILOT},
        )

        assert "copilot" in result.lower()

    @pytest.mark.asyncio
    async def test_execute_prompt_agent_failure_raises(self):
        """Test that agent failure raises exception."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(
            AgentType.JULES,
            MockCodeExecutor("jules", should_fail=True),
        )

        with pytest.raises(ValueError, match="Execution failed"):
            await orchestrator.execute_prompt(
                project_path=Path("/test/project"),
                prompt="Test prompt",
                context={},
            )

    @pytest.mark.asyncio
    async def test_execute_prompt_no_agents_raises(self):
        """Test error when no agents registered."""
        orchestrator = MultiAgentOrchestrator()

        with pytest.raises(ValueError, match="No agents registered"):
            await orchestrator.execute_prompt(
                project_path=Path("/test/project"),
                prompt="Test prompt",
                context={},
            )

    def test_register_agent(self):
        """Test agent registration."""
        orchestrator = MultiAgentOrchestrator()
        executor = MockCodeExecutor("test")

        orchestrator.register_agent(AgentType.JULES, executor)

        assert orchestrator.is_agent_available(AgentType.JULES)

    def test_get_available_agents(self):
        """Test getting available agents."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))
        orchestrator.register_agent(AgentType.COPILOT, MockCodeExecutor("copilot"))

        available = orchestrator.get_available_agents()

        assert len(available) == 2
        assert AgentType.JULES in available
        assert AgentType.COPILOT in available

    def test_get_available_agents_empty(self):
        """Test getting available agents when none registered."""
        orchestrator = MultiAgentOrchestrator()

        available = orchestrator.get_available_agents()

        assert len(available) == 0

    def test_is_agent_available(self):
        """Test agent availability check."""
        orchestrator = MultiAgentOrchestrator()

        assert not orchestrator.is_agent_available(AgentType.JULES)

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        assert orchestrator.is_agent_available(AgentType.JULES)

    def test_get_agent_capabilities(self):
        """Test getting agent capabilities."""
        orchestrator = MultiAgentOrchestrator()

        capabilities = orchestrator.selection_policy.get_capability_matrix()

        assert isinstance(capabilities, dict)
        assert AgentType.JULES in capabilities
        assert "async" in capabilities[AgentType.JULES]

    @pytest.mark.asyncio
    async def test_multiple_sequential_executions(self):
        """Test multiple sequential executions."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        result1 = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Prompt 1",
            context={},
        )

        result2 = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Prompt 2",
            context={},
        )

        assert result1 is not None
        assert result2 is not None
        assert "Prompt 1" in result1
        assert "Prompt 2" in result2

    @pytest.mark.asyncio
    async def test_multiple_concurrent_executions(self):
        """Test multiple concurrent executions."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(
            AgentType.JULES,
            MockCodeExecutor("jules", delay=0.01),
        )
        orchestrator.register_agent(
            AgentType.COPILOT,
            MockCodeExecutor("copilot", delay=0.01),
        )

        results = await asyncio.gather(
            orchestrator.execute_prompt(
                Path("/test/project1"), "Prompt 1", {"preferred_agent": AgentType.JULES}
            ),
            orchestrator.execute_prompt(
                Path("/test/project2"),
                "Prompt 2",
                {"preferred_agent": AgentType.COPILOT},
            ),
        )

        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_orchestrator_isolation(self):
        """Test that orchestrators are isolated."""
        orchestrator1 = MultiAgentOrchestrator()
        orchestrator2 = MultiAgentOrchestrator()

        orchestrator1.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        assert orchestrator1.is_agent_available(AgentType.JULES)
        assert not orchestrator2.is_agent_available(AgentType.JULES)


class TestAgentSelection:
    """Test agent selection in orchestrator context."""

    @pytest.mark.asyncio
    async def test_selection_based_on_complexity(self):
        """Test that agent selection respects complexity."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))
        orchestrator.register_agent(AgentType.COPILOT, MockCodeExecutor("copilot"))

        # Complex task should prefer Jules
        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Complex task",
            context={"complexity": TaskComplexity.COMPLEX},
        )

        assert "jules" in result.lower()

    @pytest.mark.asyncio
    async def test_selection_with_limited_agents(self):
        """Test selection works with limited agents."""
        orchestrator = MultiAgentOrchestrator()

        # Only register Gemini
        orchestrator.register_agent(AgentType.GEMINI, MockCodeExecutor("gemini"))

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Test",
            context={"complexity": TaskComplexity.EPIC},
        )

        # Should use available agent (Gemini) even if not ideal for EPIC
        assert "gemini" in result.lower()
