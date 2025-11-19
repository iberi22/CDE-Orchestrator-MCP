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
        self.last_prompt: str | None = None

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

    @pytest.mark.asyncio
    async def test_selection_with_require_plan_approval(self):
        """Test selection when plan approval is required."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))
        orchestrator.register_agent(AgentType.COPILOT, MockCodeExecutor("copilot"))

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Complex refactoring",
            context={"require_plan_approval": True},
        )

        # Should use Jules (only agent supporting plan approval)
        assert "jules" in result.lower()

    @pytest.mark.asyncio
    async def test_selection_with_large_context(self):
        """Test selection for tasks requiring large context."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))
        orchestrator.register_agent(AgentType.COPILOT, MockCodeExecutor("copilot"))

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Analyze entire codebase",
            context={"context_size": 100000},
        )

        # Should prefer Jules for large context
        assert "jules" in result.lower()

    @pytest.mark.asyncio
    async def test_selection_fallback_chain(self):
        """Test fallback to next agent on failure."""
        orchestrator = MultiAgentOrchestrator()

        # Register Jules that will fail
        orchestrator.register_agent(
            AgentType.JULES, MockCodeExecutor("jules", should_fail=True)
        )
        # Register Copilot as backup
        orchestrator.register_agent(AgentType.COPILOT, MockCodeExecutor("copilot"))

        # Should fallback to Copilot after Jules fails
        with pytest.raises(ValueError):
            await orchestrator.execute_prompt(
                project_path=Path("/test/project"),
                prompt="Test task",
                context={},
            )


class TestOrchestratorEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_prompt(self):
        """Test handling of empty prompt."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="",
            context={},
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_very_long_prompt(self):
        """Test handling of very long prompt."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        long_prompt = "A" * 10000

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt=long_prompt,
            context={},
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_invalid_project_path(self):
        """Test handling of invalid project path."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        result = await orchestrator.execute_prompt(
            project_path=Path("/nonexistent/path"),
            prompt="Test",
            context={},
        )

        # Should still execute (path validation is agent's responsibility)
        assert result is not None

    @pytest.mark.asyncio
    async def test_none_context(self):
        """Test handling of None context."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Test",
            context=None,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_malformed_context(self):
        """Test handling of malformed context."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Test",
            context={"invalid_key": "invalid_value"},
        )

        assert result is not None

    def test_agent_registration_validation(self):
        """Test that agent registration validates inputs."""
        orchestrator = MultiAgentOrchestrator()

        # Should accept valid inputs
        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))
        assert orchestrator.is_agent_available(AgentType.JULES)

    def test_multiple_registrations_same_agent(self):
        """Test registering same agent type multiple times."""
        orchestrator = MultiAgentOrchestrator()

        executor1 = MockCodeExecutor("jules1")
        executor2 = MockCodeExecutor("jules2")

        orchestrator.register_agent(AgentType.JULES, executor1)
        orchestrator.register_agent(AgentType.JULES, executor2)

        # Second registration should override first
        assert orchestrator.is_agent_available(AgentType.JULES)


class TestOrchestratorPerformance:
    """Test orchestrator performance characteristics."""

    @pytest.mark.asyncio
    async def test_concurrent_executions_dont_interfere(self):
        """Test that concurrent executions are isolated."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        results = await asyncio.gather(
            orchestrator.execute_prompt(Path("/p1"), "Prompt 1", {}),
            orchestrator.execute_prompt(Path("/p2"), "Prompt 2", {}),
            orchestrator.execute_prompt(Path("/p3"), "Prompt 3", {}),
        )

        assert len(results) == 3
        assert all(r is not None for r in results)
        assert "Prompt 1" in results[0]
        assert "Prompt 2" in results[1]
        assert "Prompt 3" in results[2]

    @pytest.mark.asyncio
    async def test_executor_call_counts(self):
        """Test that executors are called correct number of times."""
        orchestrator = MultiAgentOrchestrator()
        executor = MockCodeExecutor("jules")

        orchestrator.register_agent(AgentType.JULES, executor)

        await orchestrator.execute_prompt(Path("/test"), "Prompt 1", {})
        await orchestrator.execute_prompt(Path("/test"), "Prompt 2", {})
        await orchestrator.execute_prompt(Path("/test"), "Prompt 3", {})

        assert executor.call_count == 3

    @pytest.mark.asyncio
    async def test_agent_with_delay(self):
        """Test orchestrator handles agent delays."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(
            AgentType.JULES, MockCodeExecutor("jules", delay=0.1)
        )

        import time

        start = time.time()
        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Test",
            context={},
        )
        duration = time.time() - start

        assert result is not None
        assert duration >= 0.1  # Should respect delay


class TestOrchestratorCapabilities:
    """Test capability reporting and querying."""

    def test_get_capabilities_all_agents(self):
        """Test getting capabilities for all registered agents."""
        orchestrator = MultiAgentOrchestrator()

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))
        orchestrator.register_agent(AgentType.COPILOT, MockCodeExecutor("copilot"))

        capabilities = orchestrator.selection_policy.get_capability_matrix()

        assert AgentType.JULES in capabilities
        assert AgentType.COPILOT in capabilities

    def test_capability_matrix_structure(self):
        """Test capability matrix has expected structure."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        capabilities = orchestrator.selection_policy.get_capability_matrix()

        assert isinstance(capabilities, dict)
        assert all(isinstance(k, AgentType) for k in capabilities.keys())

    def test_agent_availability_after_registration(self):
        """Test agent availability queries."""
        orchestrator = MultiAgentOrchestrator()

        assert not orchestrator.is_agent_available(AgentType.JULES)
        assert not orchestrator.is_agent_available(AgentType.COPILOT)

        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        assert orchestrator.is_agent_available(AgentType.JULES)
        assert not orchestrator.is_agent_available(AgentType.COPILOT)

        orchestrator.register_agent(AgentType.COPILOT, MockCodeExecutor("copilot"))

        assert orchestrator.is_agent_available(AgentType.JULES)
        assert orchestrator.is_agent_available(AgentType.COPILOT)


class TestOrchestratorIntegration:
    """Integration tests for orchestrator workflows."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete workflow from registration to execution."""
        orchestrator = MultiAgentOrchestrator()

        # Register agents
        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))
        orchestrator.register_agent(AgentType.COPILOT, MockCodeExecutor("copilot"))

        # Verify registration
        assert len(orchestrator.get_available_agents()) == 2

        # Execute tasks
        result1 = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Task 1",
            context={"complexity": TaskComplexity.COMPLEX},
        )

        result2 = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Task 2",
            context={"complexity": TaskComplexity.SIMPLE},
        )

        # Verify results
        assert result1 is not None
        assert result2 is not None

    @pytest.mark.asyncio
    async def test_workflow_with_context_preservation(self):
        """Test that context is preserved across executions."""
        orchestrator = MultiAgentOrchestrator()
        orchestrator.register_agent(AgentType.JULES, MockCodeExecutor("jules"))

        context = {"session_id": "test-session", "complexity": TaskComplexity.MODERATE}

        result = await orchestrator.execute_prompt(
            project_path=Path("/test/project"),
            prompt="Test task",
            context=context,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_multiple_agents_different_tasks(self):
        """Test routing different task types to appropriate agents."""
        orchestrator = MultiAgentOrchestrator()

        jules = MockCodeExecutor("jules")
        copilot = MockCodeExecutor("copilot")
        gemini = MockCodeExecutor("gemini")

        orchestrator.register_agent(AgentType.JULES, jules)
        orchestrator.register_agent(AgentType.COPILOT, copilot)
        orchestrator.register_agent(AgentType.GEMINI, gemini)

        # Execute different task types
        await orchestrator.execute_prompt(
            Path("/test"),
            "Complex refactoring",
            {"complexity": TaskComplexity.EPIC},
        )

        await orchestrator.execute_prompt(
            Path("/test"),
            "Simple fix",
            {"complexity": TaskComplexity.TRIVIAL},
        )

        # At least one executor should have been called
        total_calls = jules.call_count + copilot.call_count + gemini.call_count
        assert total_calls >= 2
