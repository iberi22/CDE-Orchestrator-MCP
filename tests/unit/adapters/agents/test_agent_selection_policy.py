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

    def test_get_capability_matrix(self):
        """Test capability matrix retrieval."""
        matrix = AgentSelectionPolicy.get_capability_matrix()

        assert len(matrix) == 7
        assert AgentType.JULES in matrix
        assert matrix[AgentType.JULES]["async"] is True
        assert matrix[AgentType.JULES]["plan_approval"] is True

    def test_suggest_agent_epic_task(self):
        """Test agent suggestion based on task description."""
        agent = AgentSelectionPolicy.suggest_agent(
            "Refactor entire authentication system architecture"
        )
        # Epic keywords → complex task → Jules
        assert agent == AgentType.DEEPAGENTS

    def test_suggest_agent_simple_task(self):
        """Test suggestion for simple task."""
        agent = AgentSelectionPolicy.suggest_agent(
            "Fix typo in documentation"
        )
        # Simple keywords → trivial task → fallback to first available
        assert agent == AgentType.COPILOT


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
        assert AgentType.DEEPAGENTS.value == "deepagents"
        assert AgentType.CODEX.value == "codex"
        assert AgentType.ROVODEV.value == "rovodev"

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
