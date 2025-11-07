"""
Multi-Agent Orchestrator - Unified interface for multiple AI coding agents.

This module provides intelligent agent orchestration with fallback strategies,
enabling seamless task delegation across Jules, Copilot, Gemini, and Qwen.

Architecture: Hexagonal (Adapters Layer)
Implements: ICodeExecutor port from domain/ports.py
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from cde_orchestrator.adapters.agents.agent_selection_policy import (
    AgentSelectionPolicy,
    AgentType,
    TaskComplexity,
)
from cde_orchestrator.domain.ports import ICodeExecutor

__all__ = [
    "MultiAgentOrchestrator",
    "AgentRegistry",
]

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Registry for managing available agent adapters.

    Allows dynamic registration and retrieval of agent adapters.
    """

    def __init__(self):
        """Initialize empty agent registry."""
        self._adapters: Dict[AgentType, ICodeExecutor] = {}

    def register(self, agent_type: AgentType, adapter: ICodeExecutor) -> None:
        """
        Register an agent adapter.

        Args:
            agent_type: The agent type
            adapter: The adapter implementing ICodeExecutor
        """
        self._adapters[agent_type] = adapter
        logger.info(f"Registered agent: {agent_type.value}")

    def get(self, agent_type: AgentType) -> Optional[ICodeExecutor]:
        """
        Get adapter for agent type.

        Args:
            agent_type: The agent type

        Returns:
            The adapter, or None if not registered
        """
        return self._adapters.get(agent_type)

    def get_available(self) -> List[AgentType]:
        """
        Get list of available agents.

        Returns:
            List of registered agent types
        """
        return list(self._adapters.keys())

    def is_available(self, agent_type: AgentType) -> bool:
        """
        Check if agent is available.

        Args:
            agent_type: The agent type

        Returns:
            True if agent is registered and available
        """
        return agent_type in self._adapters


class MultiAgentOrchestrator(ICodeExecutor):
    """
    Multi-agent orchestrator with intelligent task delegation.

    Features:
        - Automatic agent selection based on task complexity
        - Fallback chain for unavailable agents
        - Unified execution interface
        - Capability-based routing
        - Full repository context (via Jules)

    Example:
        >>> from cde_orchestrator.adapters.agents import JulesAsyncAdapter
        >>> from cde_orchestrator.adapters.documentation.llm_cli_adapter import GeminiCLIAdapter
        >>>
        >>> orchestrator = MultiAgentOrchestrator()
        >>> orchestrator.register(AgentType.JULES, JulesAsyncAdapter(api_key="..."))
        >>> orchestrator.register(AgentType.GEMINI, GeminiCLIAdapter())
        >>>
        >>> result = await orchestrator.execute_prompt(
        ...     project_path=Path("."),
        ...     prompt="Add comprehensive error handling",
        ...     context={"complexity": TaskComplexity.COMPLEX}
        ... )
    """

    def __init__(self, selection_policy: Optional[AgentSelectionPolicy] = None):
        """
        Initialize multi-agent orchestrator.

        Args:
            selection_policy: Custom selection policy (defaults to AgentSelectionPolicy)
        """
        self.registry = AgentRegistry()
        self.selection_policy = selection_policy or AgentSelectionPolicy()

    def register_agent(self, agent_type: AgentType, adapter: ICodeExecutor) -> None:
        """
        Register an AI coding agent.

        Args:
            agent_type: Type of agent to register
            adapter: Adapter implementing ICodeExecutor interface

        Example:
            >>> from cde_orchestrator.adapters.agents import JulesAsyncAdapter
            >>> orchestrator.register_agent(
            ...     AgentType.JULES,
            ...     JulesAsyncAdapter(api_key=os.getenv("JULES_API_KEY"))
            ... )
        """
        self.registry.register(agent_type, adapter)

    def get_available_agents(self) -> List[AgentType]:
        """
        Get list of available agents.

        Returns:
            List of registered agent types
        """
        return self.registry.get_available()

    def is_agent_available(self, agent_type: AgentType) -> bool:
        """
        Check if specific agent is available.

        Args:
            agent_type: The agent to check

        Returns:
            True if agent is registered
        """
        return self.registry.is_available(agent_type)

    async def execute_prompt(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Execute prompt with best available agent.

        Automatically selects the best agent based on:
        - Task complexity (from context["complexity"])
        - Required capabilities (plan approval, async support)
        - Available agents
        - Fallback chain

        Args:
            project_path: Path to project directory
            prompt: Task description/prompt
            context: Execution context with optional keys:
                - complexity: TaskComplexity (default: MODERATE)
                - require_plan_approval: bool (default: False)
                - context_size: int lines of code (default: 1000)
                - preferred_agent: AgentType (optional override)

        Returns:
            JSON string with execution result

        Raises:
            ValueError: If no suitable agent available
            Exception: If selected agent execution fails

        Example:
            >>> result = await orchestrator.execute_prompt(
            ...     project_path=Path("."),
            ...     prompt="Add logging to all endpoints",
            ...     context={
            ...         "complexity": TaskComplexity.MODERATE,
            ...         "require_plan_approval": False,
            ...     }
            ... )
        """
        # Extract task parameters
        complexity = context.get("complexity", TaskComplexity.MODERATE)
        require_approval = context.get("require_plan_approval", False)
        context_size = context.get("context_size", 1000)
        preferred_agent = context.get("preferred_agent")

        # Get available agents
        available_agents = self.get_available_agents()

        if not available_agents:
            raise ValueError("No agents registered with orchestrator")

        # Select best agent
        if preferred_agent and self.is_agent_available(preferred_agent):
            selected_agent = preferred_agent
            logger.info(f"Using preferred agent: {selected_agent.value}")
        else:
            try:
                selected_agent = self.selection_policy.select_agent(
                    complexity=complexity,
                    require_plan_approval=require_approval,
                    context_size=context_size,
                    available_agents=available_agents,
                )
                logger.info(
                    f"Selected agent: {selected_agent.value} "
                    f"(complexity: {complexity.value}, "
                    f"context: {context_size} lines)"
                )
            except ValueError as e:
                # Log available agents for debugging
                logger.error(
                    f"Agent selection failed: {e}. "
                    f"Available agents: {[a.value for a in available_agents]}"
                )
                raise

        # Get adapter and execute
        adapter = self.registry.get(selected_agent)
        if adapter is None:
            raise ValueError(f"No adapter found for agent: {selected_agent.value}")

        try:
            logger.info(f"Executing with {selected_agent.value}: {prompt[:50]}...")
            result = await adapter.execute_prompt(project_path, prompt, context)
            logger.info(f"{selected_agent.value} execution completed successfully")
            return result

        except Exception as e:
            logger.error(
                f"{selected_agent.value} execution failed: {e}",
                exc_info=True,
            )

            # Try fallback chain
            logger.info("Attempting fallback agents...")
            for fallback_agent in AgentSelectionPolicy.FALLBACK_CHAIN:
                if fallback_agent == selected_agent:
                    continue  # Skip already tried agent
                if not self.is_agent_available(fallback_agent):
                    logger.debug(f"Fallback agent {fallback_agent.value} not available")
                    continue

                try:
                    logger.info(f"Trying fallback agent: {fallback_agent.value}")
                    fallback_adapter = self.registry.get(fallback_agent)
                    result = await fallback_adapter.execute_prompt(
                        project_path, prompt, context
                    )
                    logger.info(f"Fallback succeeded with {fallback_agent.value}")
                    return result

                except Exception as fallback_error:
                    logger.warning(
                        f"Fallback agent {fallback_agent.value} also failed: "
                        f"{fallback_error}"
                    )
                    continue

            # All agents failed
            logger.error("All agents failed, no fallback available")
            raise ValueError(
                f"Execution failed with {selected_agent.value} and all fallback agents: {e}"
            ) from e

    def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Get capability matrix for all available agents.

        Returns:
            Dictionary with agent capabilities
        """
        capabilities = {}
        for agent_type in self.get_available_agents():
            cap_data = AgentSelectionPolicy.CAPABILITIES.get(agent_type)
            if cap_data:
                capabilities[agent_type.value] = {
                    "async": cap_data.supports_async,
                    "plan_approval": cap_data.supports_plan_approval,
                    "max_context": cap_data.max_context_lines,
                    "best_for": cap_data.best_for,
                }
        return capabilities
