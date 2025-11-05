"""
Agent Selection Policy - Intelligent agent routing based on task characteristics.

This module implements the decision logic for selecting the best AI agent
for a given task based on complexity, capabilities, and availability.

Architecture: Hexagonal (Adapters Layer)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List

__all__ = [
    "TaskComplexity",
    "AgentType",
    "AgentCapabilities",
    "AgentSelectionPolicy",
]


class TaskComplexity(Enum):
    """Task complexity levels for agent selection."""
    TRIVIAL = "trivial"          # < 5 min (typo fixes, doc updates)
    SIMPLE = "simple"            # 15-30 min (single file changes)
    MODERATE = "moderate"        # 1-2 hours (multiple files, tests)
    COMPLEX = "complex"          # 4-8 hours (new feature, refactor)
    EPIC = "epic"                # 2-5 days (major feature, architecture)


class AgentType(Enum):
    """Available AI coding agents."""
    JULES = "jules"              # Async API with full repo context
    COPILOT = "copilot"          # GitHub Copilot CLI
    GEMINI = "gemini"            # Google Gemini CLI
    QWEN = "qwen"                # Alibaba Qwen CLI
    DEEPAGENTS = "deepagents"    # DeepAgents CLI for research
    CODEX = "codex"              # Codex CLI for code analysis
    ROVODEV = "rovodev"          # Rovo Dev CLI for task completion


class AgentCapability(Enum):
    """Agent capability types."""
    ASYNC = "async"              # Supports long-running operations
    PLAN_APPROVAL = "plan_approval"  # Supports interactive plan approval
    FULL_CONTEXT = "full_context"    # Can access full repository
    QUICK_FIX = "quick_fix"      # Optimized for quick fixes
    CODE_GENERATION = "code_gen" # Good at code generation
    DOCUMENTATION = "docs"       # Good at documentation
    REFACTORING = "refactor"     # Good at refactoring


@dataclass
class AgentCapabilities:
    """
    Agent capability definition.

    Attributes:
        agent_type: The agent type
        supports_async: Whether agent supports async/long-running tasks
        supports_plan_approval: Whether agent supports plan approval
        max_context_lines: Maximum source code lines agent can handle
        best_for: List of use cases agent is best for
        requires_auth: Whether agent requires authentication
    """
    agent_type: AgentType
    supports_async: bool
    supports_plan_approval: bool
    max_context_lines: int
    best_for: List[str]
    requires_auth: bool

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        if capability == AgentCapability.ASYNC:
            return self.supports_async
        if capability == AgentCapability.PLAN_APPROVAL:
            return self.supports_plan_approval
        if capability == AgentCapability.FULL_CONTEXT:
            return self.max_context_lines > 50000
        return capability.value in self.best_for


class AgentSelectionPolicy:
    """
    Intelligent agent selection policy.

    Selects the best agent for a task based on:
    1. Task complexity (trivial → epic)
    2. Required capabilities (async, plan approval, context)
    3. Agent availability
    4. Fallback chain

    Usage:
        policy = AgentSelectionPolicy()
        agent = policy.select_agent(
            complexity=TaskComplexity.COMPLEX,
            require_plan_approval=True,
            context_size=5000,
            available_agents=[AgentType.JULES, AgentType.COPILOT, AgentType.GEMINI]
        )
    """

    # Agent capability matrix
    CAPABILITIES = {
        AgentType.JULES: AgentCapabilities(
            agent_type=AgentType.JULES,
            supports_async=True,
            supports_plan_approval=True,
            max_context_lines=100000,  # Full repository
            best_for=["refactoring", "feature_development", "complex_tasks"],
            requires_auth=True
        ),
        AgentType.COPILOT: AgentCapabilities(
            agent_type=AgentType.COPILOT,
            supports_async=False,
            supports_plan_approval=False,
            max_context_lines=5000,
            best_for=["quick_fixes", "code_generation", "suggestions"],
            requires_auth=True  # Requires GitHub CLI auth
        ),
        AgentType.GEMINI: AgentCapabilities(
            agent_type=AgentType.GEMINI,
            supports_async=False,
            supports_plan_approval=False,
            max_context_lines=8000,
            best_for=["documentation", "analysis", "quick_fixes"],
            requires_auth=False  # Uses CLI auth
        ),
        AgentType.QWEN: AgentCapabilities(
            agent_type=AgentType.QWEN,
            supports_async=False,
            supports_plan_approval=False,
            max_context_lines=4000,
            best_for=["fallback"],
            requires_auth=False
        ),
        AgentType.DEEPAGENTS: AgentCapabilities(
            agent_type=AgentType.DEEPAGENTS,
            supports_async=True,
            supports_plan_approval=False,
            max_context_lines=20000,
            best_for=["research", "prototyping", "refactoring"],
            requires_auth=True
        ),
        AgentType.CODEX: AgentCapabilities(
            agent_type=AgentType.CODEX,
            supports_async=False,
            supports_plan_approval=False,
            max_context_lines=8000,
            best_for=["code_review", "analysis"],
            requires_auth=True
        ),
        AgentType.ROVODEV: AgentCapabilities(
            agent_type=AgentType.ROVODEV,
            supports_async=False,
            supports_plan_approval=False,
            max_context_lines=10000,
            best_for=["task_completion", "jira_integration"],
            requires_auth=True
        ),
    }

    # Default fallback chain
    FALLBACK_CHAIN = [
        AgentType.JULES,
        AgentType.DEEPAGENTS,
        AgentType.ROVODEV,
        AgentType.COPILOT,
        AgentType.CODEX,
        AgentType.GEMINI,
        AgentType.QWEN,
    ]

    @classmethod
    def select_agent(
        cls,
        complexity: TaskComplexity,
        require_plan_approval: bool = False,
        context_size: int = 1000,
        available_agents: List[AgentType] = None,
    ) -> AgentType:
        """
        Select best agent for task.

        Algorithm:
            1. If plan approval required → Jules only (if available)
            2. If COMPLEX/EPIC → Jules preferred (if available)
            3. If context > 8000 lines → Jules or Gemini
            4. Otherwise → First available in fallback chain

        Args:
            complexity: Task complexity level
            require_plan_approval: Whether task requires plan approval
            context_size: Estimated context size in lines
            available_agents: List of available agents (defaults to all)

        Returns:
            Selected AgentType

        Raises:
            ValueError: If no suitable agent available
        """
        if available_agents is None:
            available_agents = list(AgentType)

        # Plan approval → Jules only
        if require_plan_approval:
            if AgentType.JULES in available_agents:
                return AgentType.JULES
            raise ValueError(
                "Plan approval requires Jules, but Jules is not available"
            )

        # COMPLEX/EPIC → Jules preferred
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.EPIC]:
            if AgentType.JULES in available_agents:
                return AgentType.JULES

        # Large context → Jules or Gemini
        if context_size > 8000:
            for agent in [AgentType.JULES, AgentType.GEMINI]:
                if agent in available_agents:
                    return agent

        # Large context (5000-8000) → Try Copilot first, fallback to Gemini
        if context_size > 5000:
            for agent in [AgentType.COPILOT, AgentType.GEMINI]:
                if agent in available_agents:
                    return agent

        # Default fallback chain
        for agent in cls.FALLBACK_CHAIN:
            if agent in available_agents:
                return agent

        raise ValueError("No suitable agent available for task")

    @classmethod
    def get_capability_matrix(cls) -> dict:
        """
        Get complete capability matrix for all agents.

        Returns:
            Dictionary mapping agent type to capabilities
        """
        return {
            agent_type: {
                "async": cap.supports_async,
                "plan_approval": cap.supports_plan_approval,
                "max_context": cap.max_context_lines,
                "best_for": cap.best_for,
                "requires_auth": cap.requires_auth,
            }
            for agent_type, cap in cls.CAPABILITIES.items()
        }

    @classmethod
    def suggest_agent(cls, task_description: str) -> AgentType:
        """
        Suggest agent based on task description.

        Uses advanced heuristics to estimate complexity and requirements:
        - Keyword analysis with weights
        - Task scope detection
        - Technology stack consideration
        - Context size estimation

        Args:
            task_description: Natural language task description

        Returns:
            Suggested AgentType
        """
        desc_lower = task_description.lower()

        # Advanced complexity detection with weighted keywords
        complexity_score = cls._calculate_complexity_score(desc_lower)

        # Map score to complexity level
        if complexity_score >= 8:
            complexity = TaskComplexity.EPIC
        elif complexity_score >= 6:
            complexity = TaskComplexity.COMPLEX
        elif complexity_score >= 4:
            complexity = TaskComplexity.MODERATE
        elif complexity_score >= 2:
            complexity = TaskComplexity.SIMPLE
        else:
            complexity = TaskComplexity.TRIVIAL

        # Detect plan approval need with better heuristics
        require_approval = cls._requires_plan_approval(desc_lower)

        # Estimate context size based on task description
        context_size = cls._estimate_context_size(desc_lower)

        return cls.select_agent(
            complexity=complexity,
            require_plan_approval=require_approval,
            context_size=context_size,
            available_agents=list(AgentType),
        )

    @classmethod
    def _calculate_complexity_score(cls, desc_lower: str) -> float:
        """
        Calculate complexity score based on task description.

        Uses weighted keywords and patterns to determine task complexity.
        Higher scores indicate more complex tasks.

        Scoring:
        - Epic (8+): Architecture, system-wide changes, migrations
        - Complex (6-7): New features, integrations, refactors
        - Moderate (4-5): Multiple files, testing, documentation
        - Simple (2-3): Single file changes, fixes
        - Trivial (0-1): Typos, comments, simple docs
        """
        score = 0.0

        # Epic keywords (weight: 3)
        epic_patterns = [
            "architecture", "system", "migration", "refactor.*entire",
            "redesign", "restructure", "complete.*rewrite", "platform",
            "infrastructure", "enterprise", "scalability", "performance.*optimization"
        ]
        for pattern in epic_patterns:
            if pattern in desc_lower:
                score += 3

        # Complex keywords (weight: 2)
        complex_patterns = [
            "feature", "module", "integration", "api", "database",
            "authentication", "authorization", "security", "complex",
            "multiple.*files", "cross-cutting", "dependency.*injection",
            "microservices", "distributed", "concurrent", "async.*await"
        ]
        for pattern in complex_patterns:
            if pattern in desc_lower:
                score += 2

        # Moderate keywords (weight: 1)
        moderate_patterns = [
            "test", "testing", "documentation", "config", "settings",
            "validation", "error.*handling", "logging", "monitoring",
            "deployment", "ci.*cd", "docker", "kubernetes"
        ]
        for pattern in moderate_patterns:
            if pattern in desc_lower:
                score += 1

        # Simple keywords (weight: 0.5, but reduce complexity)
        simple_patterns = [
            "fix", "bug", "typo", "comment", "readme", "doc",
            "update", "change", "modify", "add.*field", "remove.*field"
        ]
        for pattern in simple_patterns:
            if pattern in desc_lower:
                score -= 0.5  # Reduce score for simple tasks

        # Technology stack complexity
        tech_complexity = cls._calculate_tech_complexity(desc_lower)
        score += tech_complexity

        # Task scope indicators
        scope_score = cls._calculate_scope_score(desc_lower)
        score += scope_score

        return max(0, min(10, score))  # Clamp between 0-10

    @classmethod
    def _calculate_tech_complexity(cls, desc_lower: str) -> float:
        """Calculate complexity based on technology stack."""
        complexity = 0.0

        # High complexity technologies
        high_complexity_tech = [
            "kubernetes", "docker.*compose", "microservices", "graphql",
            "blockchain", "machine.*learning", "ai", "neural", "tensorflow",
            "pytorch", "cuda", "gpu", "distributed.*computing"
        ]
        for tech in high_complexity_tech:
            if tech in desc_lower:
                complexity += 2

        # Medium complexity technologies
        medium_complexity_tech = [
            "react", "vue", "angular", "typescript", "webpack",
            "database", "sql", "nosql", "redis", "mongodb",
            "authentication", "oauth", "jwt", "encryption"
        ]
        for tech in medium_complexity_tech:
            if tech in desc_lower:
                complexity += 1

        return complexity

    @classmethod
    def _calculate_scope_score(cls, desc_lower: str) -> float:
        """Calculate scope score based on task breadth."""
        scope = 0.0

        # Broad scope indicators
        broad_patterns = [
            "all.*files", "entire.*project", "whole.*system",
            "every.*component", "all.*modules", "system.*wide",
            "across.*application", "end.*to.*end"
        ]
        for pattern in broad_patterns:
            if pattern in desc_lower:
                scope += 2

        # Medium scope indicators
        medium_patterns = [
            "multiple.*files", "several.*components", "various.*modules",
            "different.*parts", "several.*areas"
        ]
        for pattern in medium_patterns:
            if pattern in desc_lower:
                scope += 1

        return scope

    @classmethod
    def _requires_plan_approval(cls, desc_lower: str) -> bool:
        """Determine if task requires plan approval."""
        approval_keywords = [
            "approval", "review", "architectural", "design.*review",
            "stakeholder", "business.*requirements", "critical",
            "high.*impact", "breaking.*changes", "migration"
        ]

        # Check for explicit approval requests
        if any(kw in desc_lower for kw in approval_keywords):
            return True

        # Check for high-risk patterns
        risk_patterns = [
            "delete.*data", "drop.*table", "remove.*feature",
            "breaking.*change", "major.*version", "api.*change"
        ]

        return any(pattern in desc_lower for pattern in risk_patterns)

    @classmethod
    def _estimate_context_size(cls, desc_lower: str) -> int:
        """Estimate context size in lines based on task description."""
        base_context = 1000  # Default

        # Large context indicators
        if any(kw in desc_lower for kw in ["architecture", "system", "refactor", "migration"]):
            base_context = 50000  # Full codebase

        # Medium context indicators
        elif any(kw in desc_lower for kw in ["feature", "module", "integration", "multiple.*files"]):
            base_context = 10000

        # Small context indicators
        elif any(kw in desc_lower for kw in ["fix", "typo", "single.*file", "one.*file"]):
            base_context = 500

        return base_context
