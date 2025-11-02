"""
Workflow Selector Use Case

Analyzes user prompts to intelligently select:
1. Optimal workflow (standard, quick-fix, research, etc.)
2. Best recipe (ai-engineer, sprint-prioritizer, etc.)
3. Required skills (from base + ephemeral)

This is the entry point for all agent interactions with CDE.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
import re


class WorkflowComplexity(Enum):
    """Task complexity levels."""
    TRIVIAL = "trivial"  # < 5 min (typo fix, doc update)
    SIMPLE = "simple"  # 15-30 min (single file change)
    MODERATE = "moderate"  # 1-2 hours (multiple files, tests)
    COMPLEX = "complex"  # Half day (new feature, refactor)
    EPIC = "epic"  # Multi-day (major feature, architecture)


class WorkflowType(Enum):
    """Available workflow types."""
    STANDARD = "standard"  # Full 6-phase workflow
    QUICK_FIX = "quick-fix"  # Skip define/design, direct to implement
    RESEARCH = "research"  # Heavy research, light implementation
    DOCUMENTATION = "documentation"  # Focus on specs/docs
    REFACTOR = "refactor"  # Code improvement without new features
    HOTFIX = "hotfix"  # Emergency fix, minimal validation


class DomainCategory(Enum):
    """Domain categories for skill matching."""
    WEB_DEVELOPMENT = "web-dev"
    AI_ML = "ai-ml"
    DATABASE = "database"
    DEVOPS = "devops"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    GENERAL = "general"


@dataclass
class WorkflowRecommendation:
    """Result of workflow analysis."""
    workflow_type: WorkflowType
    complexity: WorkflowComplexity
    recipe_id: str
    estimated_duration: str
    required_skills: List[str]
    phases_to_skip: List[str]
    reasoning: str
    confidence: float  # 0.0-1.0


class WorkflowSelectorUseCase:
    """
    Intelligently selects workflows, recipes, and skills based on user prompt.

    This use case is the brain of CDE orchestration - it analyzes what the user
    wants and routes them to the optimal workflow + recipe + skills.
    """

    # Keywords for complexity detection
    COMPLEXITY_INDICATORS = {
        WorkflowComplexity.TRIVIAL: [
            "fix typo", "update comment", "rename variable", "fix formatting",
            "add docstring", "update readme", "fix lint"
        ],
        WorkflowComplexity.SIMPLE: [
            "add function", "fix bug", "update config", "add test",
            "improve error message", "add logging"
        ],
        WorkflowComplexity.MODERATE: [
            "implement feature", "add endpoint", "create component",
            "refactor module", "add validation", "integrate api"
        ],
        WorkflowComplexity.COMPLEX: [
            "new feature", "redesign", "major refactor", "migrate",
            "implement system", "add authentication", "create workflow"
        ],
        WorkflowComplexity.EPIC: [
            "build platform", "complete rewrite", "architecture change",
            "multi-service", "new product", "full migration"
        ]
    }

    # Keywords for workflow type detection
    WORKFLOW_KEYWORDS = {
        WorkflowType.QUICK_FIX: [
            "quick", "hotfix", "urgent", "emergency", "asap", "bug fix",
            "broken", "not working", "crash"
        ],
        WorkflowType.RESEARCH: [
            "research", "investigate", "analyze", "explore", "compare",
            "evaluate", "what is", "how does", "best way"
        ],
        WorkflowType.DOCUMENTATION: [
            "document", "write spec", "create guide", "add docs",
            "explain", "tutorial", "readme", "api docs"
        ],
        WorkflowType.REFACTOR: [
            "refactor", "clean up", "improve", "optimize", "restructure",
            "modernize", "technical debt", "code quality"
        ],
        WorkflowType.HOTFIX: [
            "production down", "critical bug", "security issue", "data loss",
            "outage", "failing", "broken prod"
        ]
    }

    # Domain detection patterns
    DOMAIN_PATTERNS = {
        DomainCategory.WEB_DEVELOPMENT: [
            "react", "vue", "angular", "frontend", "ui", "component",
            "html", "css", "javascript", "typescript", "dom"
        ],
        DomainCategory.AI_ML: [
            "ai", "ml", "machine learning", "neural", "model", "training",
            "llm", "gpt", "gemini", "copilot", "embedding", "vector"
        ],
        DomainCategory.DATABASE: [
            "database", "sql", "nosql", "redis", "postgres", "mongo",
            "query", "schema", "migration", "orm", "index"
        ],
        DomainCategory.DEVOPS: [
            "deploy", "ci/cd", "docker", "kubernetes", "aws", "azure",
            "pipeline", "infrastructure", "terraform", "helm"
        ],
        DomainCategory.TESTING: [
            "test", "unit test", "integration test", "e2e", "mock",
            "pytest", "jest", "coverage", "qa", "validation"
        ],
        DomainCategory.DOCUMENTATION: [
            "docs", "documentation", "spec", "guide", "tutorial",
            "readme", "changelog", "api docs", "architecture"
        ],
        DomainCategory.ARCHITECTURE: [
            "architecture", "design pattern", "hexagonal", "clean arch",
            "microservices", "event-driven", "ddd", "ports and adapters"
        ],
        DomainCategory.SECURITY: [
            "security", "auth", "authentication", "authorization", "oauth",
            "jwt", "encryption", "vulnerability", "penetration"
        ],
        DomainCategory.PERFORMANCE: [
            "performance", "optimize", "slow", "latency", "throughput",
            "cache", "scale", "bottleneck", "profiling"
        ]
    }

    # Recipe recommendations by domain
    RECIPE_BY_DOMAIN = {
        DomainCategory.AI_ML: "ai-engineer",
        DomainCategory.WEB_DEVELOPMENT: "ai-engineer",
        DomainCategory.DATABASE: "ai-engineer",
        DomainCategory.DEVOPS: "ai-engineer",
        DomainCategory.TESTING: "ai-engineer",
        DomainCategory.DOCUMENTATION: "documentation-writer",
        DomainCategory.ARCHITECTURE: "ai-engineer",
        DomainCategory.SECURITY: "ai-engineer",
        DomainCategory.PERFORMANCE: "ai-engineer",
        DomainCategory.GENERAL: "ai-engineer"
    }

    # Skill requirements by domain
    SKILL_BY_DOMAIN = {
        DomainCategory.AI_ML: ["ai-integration", "llm-prompting", "vector-db"],
        DomainCategory.WEB_DEVELOPMENT: ["react-patterns", "web-performance", "accessibility"],
        DomainCategory.DATABASE: ["sql-optimization", "nosql-patterns", "data-modeling"],
        DomainCategory.DEVOPS: ["containerization", "ci-cd", "infrastructure"],
        DomainCategory.TESTING: ["test-strategy", "mocking", "e2e-testing"],
        DomainCategory.DOCUMENTATION: ["technical-writing", "spec-kit", "markdown"],
        DomainCategory.ARCHITECTURE: ["design-patterns", "hexagonal-arch", "system-design"],
        DomainCategory.SECURITY: ["auth-best-practices", "encryption", "owasp"],
        DomainCategory.PERFORMANCE: ["profiling", "caching", "optimization"],
        DomainCategory.GENERAL: ["problem-solving", "code-quality"]
    }

    def execute(self, user_prompt: str, project_path: str = ".") -> Dict[str, Any]:
        """
        Analyze user prompt and recommend workflow, recipe, and skills.

        Args:
            user_prompt: User's request in natural language
            project_path: Path to project (for context analysis)

        Returns:
            {
                "recommendation": WorkflowRecommendation,
                "status": "success",
                "next_action": "start_workflow | research_skills | clarify_requirements"
            }
        """
        # 1. Detect complexity
        complexity = self._detect_complexity(user_prompt)

        # 2. Detect workflow type
        workflow_type = self._detect_workflow_type(user_prompt, complexity)

        # 3. Detect domain
        domain = self._detect_domain(user_prompt)

        # 4. Select recipe
        recipe_id = self._select_recipe(domain, workflow_type)

        # 5. Identify required skills
        required_skills = self._identify_skills(domain, complexity, user_prompt)

        # 6. Determine phases to skip
        phases_to_skip = self._determine_skippable_phases(workflow_type, complexity)

        # 7. Estimate duration
        estimated_duration = self._estimate_duration(complexity)

        # 8. Generate reasoning
        reasoning = self._generate_reasoning(
            user_prompt, complexity, workflow_type, domain, recipe_id
        )

        # 9. Calculate confidence
        confidence = self._calculate_confidence(user_prompt, domain)

        recommendation = WorkflowRecommendation(
            workflow_type=workflow_type,
            complexity=complexity,
            recipe_id=recipe_id,
            estimated_duration=estimated_duration,
            required_skills=required_skills,
            phases_to_skip=phases_to_skip,
            reasoning=reasoning,
            confidence=confidence
        )

        # 10. Determine next action
        next_action = self._determine_next_action(recommendation)

        return {
            "status": "success",
            "recommendation": {
                "workflow_type": workflow_type.value,
                "complexity": complexity.value,
                "recipe_id": recipe_id,
                "estimated_duration": estimated_duration,
                "required_skills": required_skills,
                "phases_to_skip": phases_to_skip,
                "reasoning": reasoning,
                "confidence": confidence,
                "domain": domain.value
            },
            "next_action": next_action,
            "user_prompt": user_prompt
        }

    def _detect_complexity(self, prompt: str) -> WorkflowComplexity:
        """Detect task complexity from prompt keywords."""
        prompt_lower = prompt.lower()

        # Score each complexity level
        scores = {}
        for complexity, keywords in self.COMPLEXITY_INDICATORS.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            scores[complexity] = score

        # Return highest scoring (if tie, choose higher complexity)
        if max(scores.values()) == 0:
            # No keywords matched, use heuristics
            word_count = len(prompt.split())
            if word_count < 10:
                return WorkflowComplexity.SIMPLE
            elif word_count < 30:
                return WorkflowComplexity.MODERATE
            else:
                return WorkflowComplexity.COMPLEX

        return max(scores.items(), key=lambda x: (x[1], list(WorkflowComplexity).index(x[0])))[0]

    def _detect_workflow_type(
        self, prompt: str, complexity: WorkflowComplexity
    ) -> WorkflowType:
        """Detect workflow type from prompt and complexity."""
        prompt_lower = prompt.lower()

        # Check for explicit workflow keywords
        for workflow_type, keywords in self.WORKFLOW_KEYWORDS.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return workflow_type

        # Default based on complexity
        if complexity == WorkflowComplexity.TRIVIAL:
            return WorkflowType.QUICK_FIX
        elif complexity == WorkflowComplexity.EPIC:
            return WorkflowType.STANDARD
        else:
            return WorkflowType.STANDARD

    def _detect_domain(self, prompt: str) -> DomainCategory:
        """Detect primary domain from prompt."""
        prompt_lower = prompt.lower()

        # Score each domain
        scores = {}
        for domain, keywords in self.DOMAIN_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            scores[domain] = score

        # Return highest scoring (default to GENERAL)
        if max(scores.values()) == 0:
            return DomainCategory.GENERAL

        return max(scores.items(), key=lambda x: x[1])[0]

    def _select_recipe(self, domain: DomainCategory, workflow_type: WorkflowType) -> str:
        """Select best recipe for domain and workflow."""
        # Override recipe for specific workflow types
        if workflow_type == WorkflowType.DOCUMENTATION:
            return "documentation-writer"
        elif workflow_type == WorkflowType.RESEARCH:
            return "deep-research"
        elif workflow_type == WorkflowType.HOTFIX:
            return "quick-fix"

        # Use domain-based recipe
        return self.RECIPE_BY_DOMAIN.get(domain, "ai-engineer")

    def _identify_skills(
        self, domain: DomainCategory, complexity: WorkflowComplexity, prompt: str
    ) -> List[str]:
        """Identify required skills for task."""
        skills = ["problem-solving"]  # Always needed

        # Add domain-specific skills
        domain_skills = self.SKILL_BY_DOMAIN.get(domain, [])
        skills.extend(domain_skills[:2])  # Top 2 domain skills

        # Add complexity-based skills
        if complexity in [WorkflowComplexity.COMPLEX, WorkflowComplexity.EPIC]:
            skills.extend(["system-design", "project-planning"])

        return list(set(skills))  # Remove duplicates

    def _determine_skippable_phases(
        self, workflow_type: WorkflowType, complexity: WorkflowComplexity
    ) -> List[str]:
        """Determine which workflow phases can be skipped."""
        if workflow_type == WorkflowType.QUICK_FIX:
            return ["define", "decompose", "design"]
        elif workflow_type == WorkflowType.HOTFIX:
            return ["define", "decompose", "design", "review"]
        elif workflow_type == WorkflowType.RESEARCH:
            return ["implement", "test"]
        elif workflow_type == WorkflowType.DOCUMENTATION:
            return ["implement", "test", "review"]
        elif complexity == WorkflowComplexity.TRIVIAL:
            return ["decompose", "design"]
        else:
            return []

    def _estimate_duration(self, complexity: WorkflowComplexity) -> str:
        """Estimate task duration based on complexity."""
        duration_map = {
            WorkflowComplexity.TRIVIAL: "< 5 minutes",
            WorkflowComplexity.SIMPLE: "15-30 minutes",
            WorkflowComplexity.MODERATE: "1-2 hours",
            WorkflowComplexity.COMPLEX: "4-8 hours",
            WorkflowComplexity.EPIC: "2-5 days"
        }
        return duration_map[complexity]

    def _generate_reasoning(
        self,
        prompt: str,
        complexity: WorkflowComplexity,
        workflow_type: WorkflowType,
        domain: DomainCategory,
        recipe_id: str
    ) -> str:
        """Generate human-readable reasoning for recommendation."""
        return (
            f"Based on prompt analysis:\n"
            f"- Complexity: {complexity.value} ({self._estimate_duration(complexity)})\n"
            f"- Domain: {domain.value}\n"
            f"- Workflow: {workflow_type.value}\n"
            f"- Recipe: {recipe_id}\n\n"
            f"This task requires {complexity.value}-level effort in {domain.value}. "
            f"Using {workflow_type.value} workflow with {recipe_id} recipe."
        )

    def _calculate_confidence(self, prompt: str, domain: DomainCategory) -> float:
        """Calculate confidence score (0.0-1.0) for recommendation."""
        confidence = 0.5  # Base confidence

        # Increase confidence if domain is clearly detected
        prompt_lower = prompt.lower()
        domain_keywords = self.DOMAIN_PATTERNS.get(domain, [])
        keyword_matches = sum(1 for kw in domain_keywords if kw in prompt_lower)

        if keyword_matches >= 3:
            confidence += 0.3
        elif keyword_matches >= 1:
            confidence += 0.15

        # Increase confidence if prompt is detailed
        word_count = len(prompt.split())
        if word_count > 50:
            confidence += 0.15
        elif word_count > 20:
            confidence += 0.05

        return min(confidence, 1.0)

    def _determine_next_action(self, recommendation: WorkflowRecommendation) -> str:
        """Determine next action based on recommendation."""
        if recommendation.confidence < 0.6:
            return "clarify_requirements"
        elif recommendation.complexity in [WorkflowComplexity.COMPLEX, WorkflowComplexity.EPIC]:
            return "research_skills"
        else:
            return "start_workflow"
