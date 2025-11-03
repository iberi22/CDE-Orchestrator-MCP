"""
Unit tests for AgentSelectionPolicy.

Tests agent selection logic, capability matrix, and fallback chain.
"""

import pytest
from cde_orchestrator.adapters.agents.agent_selection_policy import (
    AgentSelectionPolicy,
    AgentType,
    TaskComplexity,
    AgentCapabilities,
    AgentCapability,
)


class TestAgentCapabilities:
    """Test AgentCapabilities dataclass."""

    def test_has_capability_async(self):
        """Test async capability detection."""
        cap = AgentSelectionPolicy.CAPABILITIES[AgentType.JULES]
        assert cap.has_capability(AgentCapability.ASYNC) is True

        cap = AgentSelectionPolicy.CAPABILITIES[AgentType.COPILOT]
        assert cap.has_capability(AgentCapability.ASYNC) is False

    def test_has_capability_plan_approval(self):
        """Test plan approval capability."""
        cap = AgentSelectionPolicy.CAPABILITIES[AgentType.JULES]
        assert cap.has_capability(AgentCapability.PLAN_APPROVAL) is True

        cap = AgentSelectionPolicy.CAPABILITIES[AgentType.GEMINI]
        assert cap.has_capability(AgentCapability.PLAN_APPROVAL) is False

    def test_has_capability_full_context(self):
        """Test full context capability."""
        cap = AgentSelectionPolicy.CAPABILITIES[AgentType.JULES]
        assert cap.has_capability(AgentCapability.FULL_CONTEXT) is True

        cap = AgentSelectionPolicy.CAPABILITIES[AgentType.COPILOT]
        assert cap.has_capability(AgentCapability.FULL_CONTEXT) is False


class TestAgentSelectionPolicy:
    """Test AgentSelectionPolicy routing logic."""

    def test_select_agent_trivial_complexity(self):
        """Test selection for trivial tasks."""
        agent = AgentSelectionPolicy.select_agent(
            complexity=TaskComplexity.TRIVIAL,
            available_agents=list(AgentType),
        )
        # Trivial should use fallback chain: Jules -> Copilot -> Gemini -> Qwen
        assert agent == AgentType.JULES

    def test_select_agent_epic_complexity(self):
        """Test selection for epic tasks."""
        agent = AgentSelectionPolicy.select_agent(
            complexity=TaskComplexity.EPIC,
            available_agents=list(AgentType),
        )
        # Epic should prefer Jules
        assert agent == AgentType.JULES

    def test_select_agent_complex_complexity(self):
        """Test selection for complex tasks."""
        agent = AgentSelectionPolicy.select_agent(
            complexity=TaskComplexity.COMPLEX,
            available_agents=list(AgentType),
        )
        # Complex should prefer Jules
        assert agent == AgentType.JULES

    def test_select_agent_requires_plan_approval(self):
        """Test that plan approval requires Jules."""
        agent = AgentSelectionPolicy.select_agent(
            complexity=TaskComplexity.MODERATE,
            require_plan_approval=True,
            available_agents=list(AgentType),
        )
        # Plan approval → Jules only
        assert agent == AgentType.JULES

    def test_select_agent_plan_approval_without_jules_raises(self):
        """Test error when plan approval required but Jules unavailable."""
        with pytest.raises(ValueError, match="Plan approval requires Jules"):
            AgentSelectionPolicy.select_agent(
                complexity=TaskComplexity.MODERATE,
                require_plan_approval=True,
                available_agents=[AgentType.COPILOT, AgentType.GEMINI],
            )

    def test_select_agent_large_context(self):
        """Test agent selection with large context."""
        agent = AgentSelectionPolicy.select_agent(
            complexity=TaskComplexity.SIMPLE,
            context_size=50000,  # Large context
            available_agents=list(AgentType),
        )
        # Large context → Jules or Gemini
        assert agent in [AgentType.JULES, AgentType.GEMINI]

    def test_select_agent_fallback_chain(self):
        """Test fallback chain when Jules unavailable."""
        agent = AgentSelectionPolicy.select_agent(
            complexity=TaskComplexity.COMPLEX,
            available_agents=[AgentType.COPILOT, AgentType.GEMINI, AgentType.QWEN],
        )
        # Without Jules, should fallback to first available
        assert agent in [AgentType.COPILOT, AgentType.GEMINI]

    def test_select_agent_no_agents_raises(self):
        """Test error when no agents available."""
        with pytest.raises(ValueError, match="No suitable agent available"):
            AgentSelectionPolicy.select_agent(
                complexity=TaskComplexity.MODERATE,
                available_agents=[],
            )

    def test_get_capability_matrix(self):
        """Test capability matrix retrieval."""
        matrix = AgentSelectionPolicy.get_capability_matrix()

        assert len(matrix) == 4
        assert AgentType.JULES in matrix
        assert matrix[AgentType.JULES]["async"] is True
        assert matrix[AgentType.JULES]["plan_approval"] is True

    def test_suggest_agent_epic_task(self):
        """Test agent suggestion based on task description."""
        agent = AgentSelectionPolicy.suggest_agent(
            "Refactor entire authentication system architecture"
        )
        # Epic keywords → complex task → Jules
        assert agent == AgentType.JULES

    def test_suggest_agent_simple_task(self):
        """Test suggestion for simple task."""
        agent = AgentSelectionPolicy.suggest_agent(
            "Fix typo in documentation"
        )
        # Simple keywords → trivial task → fallback to first available
        assert agent is not None


class TestAgentTypeEnum:
    """Test AgentType enum."""

    def test_all_agent_types_have_capabilities(self):
        """Verify all agents have capability definitions."""
        for agent_type in AgentType:
            assert agent_type in AgentSelectionPolicy.CAPABILITIES
            cap = AgentSelectionPolicy.CAPABILITIES[agent_type]
            assert cap.best_for is not None
            assert len(cap.best_for) > 0

    def test_agent_type_values(self):
        """Test agent type values."""
        assert AgentType.JULES.value == "jules"
        assert AgentType.COPILOT.value == "copilot"
        assert AgentType.GEMINI.value == "gemini"
        assert AgentType.QWEN.value == "qwen"


class TestTaskComplexityEnum:
    """Test TaskComplexity enum."""

    def test_complexity_values(self):
        """Test complexity values."""
        assert TaskComplexity.TRIVIAL.value == "trivial"
        assert TaskComplexity.SIMPLE.value == "simple"
        assert TaskComplexity.MODERATE.value == "moderate"
        assert TaskComplexity.COMPLEX.value == "complex"
        assert TaskComplexity.EPIC.value == "epic"

    def test_complexity_ordering(self):
        """Test that complexities are ordered."""
        complexities = [
            TaskComplexity.TRIVIAL,
            TaskComplexity.SIMPLE,
            TaskComplexity.MODERATE,
            TaskComplexity.COMPLEX,
            TaskComplexity.EPIC,
        ]
        assert len(complexities) == 5


# Integration tests
class TestAgentSelectionIntegration:
    """Integration tests for agent selection."""

    def test_matrix_consistency(self):
        """Test that capability matrix is consistent."""
        policy = AgentSelectionPolicy()
        matrix = policy.get_capability_matrix()

        # Verify Jules has full context
        assert matrix[AgentType.JULES]["max_context"] > 50000

        # Verify Copilot has limited context
        assert matrix[AgentType.COPILOT]["max_context"] < 10000

    def test_selection_deterministic(self):
        """Test that selection is deterministic."""
        available = list(AgentType)

        agent1 = AgentSelectionPolicy.select_agent(
            complexity=TaskComplexity.COMPLEX,
            available_agents=available,
        )

        agent2 = AgentSelectionPolicy.select_agent(
            complexity=TaskComplexity.COMPLEX,
            available_agents=available,
        )

        assert agent1 == agent2

    def test_selection_respects_availability(self):
        """Test that selection respects agent availability."""
        limited_agents = [AgentType.GEMINI, AgentType.QWEN]

        agent = AgentSelectionPolicy.select_agent(
            complexity=TaskComplexity.COMPLEX,
            available_agents=limited_agents,
        )

        assert agent in limited_agents
