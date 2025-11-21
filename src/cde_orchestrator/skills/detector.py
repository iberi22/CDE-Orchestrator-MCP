"""
Skill Requirement Detector - Analyzes tasks to determine skill needs.

Identifies:
1. Whether a task needs external knowledge (skills)
2. The complexity level
3. The domain (backend, frontend, database, etc.)
4. Specific knowledge gaps to fill
"""

import re
from typing import Dict, List, Set, Tuple

from .models import ComplexityLevel, SkillDomain, SkillRequirement


class SkillRequirementDetector:
    """
    Analyzes task descriptions to determine if/what skills are needed.

    Uses heuristics and keyword analysis to detect:
    - Task complexity (low/medium/high/epic)
    - Knowledge domain (backend, frontend, database, etc.)
    - Specific knowledge gaps
    """

    # Domain keywords mapping
    DOMAIN_KEYWORDS: Dict[SkillDomain, List[str]] = {
        SkillDomain.BACKEND: [
            "api",
            "rest",
            "fastapi",
            "flask",
            "django",
            "express",
            "nodejs",
            "server",
            "endpoint",
            "route",
            "handler",
            "middleware",
            "authentication",
            "authorization",
            "session",
            "async",
            "await",
        ],
        SkillDomain.FRONTEND: [
            "react",
            "vue",
            "angular",
            "html",
            "css",
            "javascript",
            "typescript",
            "component",
            "state",
            "redux",
            "ui",
            "ux",
            "button",
            "form",
            "modal",
            "responsive",
            "mobile",
        ],
        SkillDomain.DATABASE: [
            "database",
            "sql",
            "postgres",
            "mysql",
            "mongodb",
            "redis",
            "cache",
            "query",
            "migration",
            "schema",
            "index",
            "transaction",
            "orm",
            "sqlalchemy",
            "datastore",
        ],
        SkillDomain.DEVOPS: [
            "docker",
            "kubernetes",
            "deployment",
            "ci/cd",
            "pipeline",
            "github",
            "gitlab",
            "jenkins",
            "terraform",
            "infrastructure",
            "aws",
            "gcp",
            "azure",
            "monitoring",
            "logging",
        ],
        SkillDomain.SECURITY: [
            "security",
            "encrypt",
            "hash",
            "ssl",
            "tls",
            "cors",
            "csrf",
            "xss",
            "vulnerability",
            "oauth",
            "jwt",
            "token",
            "permission",
            "access control",
        ],
        SkillDomain.DATA_SCIENCE: [
            "machine learning",
            "ml",
            "tensorflow",
            "pytorch",
            "pandas",
            "numpy",
            "analysis",
            "data",
            "visualization",
            "model",
            "training",
            "prediction",
            "algorithm",
        ],
        SkillDomain.TESTING: [
            "test",
            "pytest",
            "unittest",
            "jest",
            "mocha",
            "coverage",
            "mocking",
            "fixture",
            "integration test",
            "unit test",
            "e2e",
        ],
        SkillDomain.ARCHITECTURE: [
            "design",
            "architecture",
            "pattern",
            "hexagonal",
            "microservice",
            "monolith",
            "scalability",
            "performance",
            "refactor",
        ],
    }

    # Complexity indicators
    COMPLEXITY_INDICATORS: Dict[ComplexityLevel, List[str]] = {
        ComplexityLevel.LOW: [
            "simple",
            "basic",
            "fix",
            "typo",
            "format",
            "rename",
            "update",
        ],
        ComplexityLevel.MEDIUM: [
            "implement",
            "create",
            "add",
            "modify",
            "optimize",
            "refactor",
            "integrate",
        ],
        ComplexityLevel.HIGH: [
            "redesign",
            "architecture",
            "rewrite",
            "migrate",
            "complex",
            "challenging",
            "multi-component",
        ],
        ComplexityLevel.EPIC: [
            "full rewrite",
            "complete redesign",
            "massive refactor",
            "system overhaul",
            "end-to-end",
            "major migration",
        ],
    }

    # Knowledge gap patterns (regex patterns that indicate specific skills needed)
    KNOWLEDGE_GAP_PATTERNS: List[Tuple[str, str]] = [
        (r"redis\s+(caching|cache|pub[/\-]?sub)", "redis-caching"),
        (r"async\s+(python|code|patterns)", "python-async-patterns"),
        (r"fastapi\s+(websocket|async)", "fastapi-websockets"),
        (r"database\s+(design|schema|modeling)", "database-design"),
        (r"sql\s+(optimization|query|performance)", "sql-optimization"),
        (r"authentication|oauth|jwt", "authentication-patterns"),
        (r"microservices?(\s+.*)?pattern", "microservices-patterns"),
        (r"(docker|container).*orchestration", "docker-kubernetes"),
        (r"terraform|infrastructure\s+as\s+code", "infrastructure-as-code"),
        (r"testing.*strategy|test.*architecture", "testing-strategy"),
        (r"api\s+design|rest\s+design", "api-design"),
        (r"error\s+handling|exception\s+handling", "error-handling-patterns"),
        (r"logging|monitoring|observability", "logging-monitoring"),
        (r"performance\s+(tuning|optimization)", "performance-optimization"),
        (r"(ci|cd)\s+pipeline", "cicd-pipelines"),
    ]

    def __init__(self, aggressive_mode: bool = False):
        """
        Initialize detector.

        Args:
            aggressive_mode: If True, lower confidence thresholds for skill detection
        """
        self.aggressive_mode = aggressive_mode

    def analyze_task(self, task_description: str) -> SkillRequirement:
        """
        Analyze a task description and determine skill requirements.

        Args:
            task_description: Natural language task description

        Returns:
            SkillRequirement with analysis results
        """
        text_lower = task_description.lower()

        # Detect domain
        domain = self._detect_domain(text_lower)

        # Detect complexity
        complexity = self._detect_complexity(text_lower)

        # Detect knowledge gaps
        knowledge_gaps = self._detect_knowledge_gaps(text_lower)

        # Determine if skill is needed
        needs_skill = len(knowledge_gaps) > 0 or complexity in [
            ComplexityLevel.HIGH,
            ComplexityLevel.EPIC,
        ]

        # Calculate confidence (0-1)
        confidence = self._calculate_confidence(
            text_lower, domain, complexity, knowledge_gaps
        )

        # Build reasoning
        reasoning = self._build_reasoning(
            domain, complexity, knowledge_gaps, confidence
        )

        return SkillRequirement(
            needs_skill=needs_skill,
            complexity=complexity,
            domain=domain,
            knowledge_gaps=knowledge_gaps,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _detect_domain(self, text_lower: str) -> SkillDomain:
        """
        Detect the primary domain from task text.

        Args:
            text_lower: Lowercase task text

        Returns:
            SkillDomain enum value
        """
        domain_scores: Dict[SkillDomain, int] = {domain: 0 for domain in SkillDomain}

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                count = len(re.findall(r"\b" + keyword + r"\b", text_lower))
                domain_scores[domain] += count

        # Return domain with highest score, default to BACKEND
        best_domain = max(domain_scores, key=lambda k: domain_scores[k])
        return best_domain if domain_scores[best_domain] > 0 else SkillDomain.BACKEND

    def _detect_complexity(self, text_lower: str) -> ComplexityLevel:
        """
        Detect task complexity level.

        Args:
            text_lower: Lowercase task text

        Returns:
            ComplexityLevel enum value
        """
        # Score each complexity level
        complexity_scores: Dict[ComplexityLevel, int] = {
            level: 0 for level in ComplexityLevel
        }

        for level, indicators in self.COMPLEXITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in text_lower:
                    complexity_scores[level] += 1

        # Find max score complexity
        max_complexity = ComplexityLevel.LOW
        max_score = 0

        for level in [
            ComplexityLevel.EPIC,
            ComplexityLevel.HIGH,
            ComplexityLevel.MEDIUM,
            ComplexityLevel.LOW,
        ]:
            if complexity_scores[level] > max_score:
                max_score = complexity_scores[level]
                max_complexity = level

        # Check for multi-line or long descriptions (indicates complexity)
        lines = text_lower.split("\n")
        if len(lines) > 5:
            # Bump up complexity if description is long
            if max_complexity == ComplexityLevel.LOW:
                max_complexity = ComplexityLevel.MEDIUM
            elif max_complexity == ComplexityLevel.MEDIUM:
                max_complexity = ComplexityLevel.HIGH

        return max_complexity

    def _detect_knowledge_gaps(self, text_lower: str) -> List[str]:
        """
        Detect specific knowledge gaps that skills can fill.

        Args:
            text_lower: Lowercase task text

        Returns:
            List of skill IDs that would be helpful
        """
        gaps: Set[str] = set()

        for pattern, skill_id in self.KNOWLEDGE_GAP_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                gaps.add(skill_id)

        # Also check for domain-specific common patterns
        domain = self._detect_domain(text_lower)

        if domain == SkillDomain.BACKEND:
            if any(word in text_lower for word in ["cache", "performance", "fast"]):
                gaps.add("caching-patterns")
            if any(word in text_lower for word in ["stream", "queue", "background"]):
                gaps.add("background-jobs-patterns")

        elif domain == SkillDomain.DATABASE:
            if any(word in text_lower for word in ["optimize", "slow", "query"]):
                gaps.add("sql-optimization")
            if any(word in text_lower for word in ["migrate", "schema"]):
                gaps.add("database-migrations")

        elif domain == SkillDomain.TESTING:
            if any(word in text_lower for word in ["mock", "fixture"]):
                gaps.add("mocking-patterns")

        return sorted(list(gaps))

    def _calculate_confidence(
        self,
        text_lower: str,
        domain: SkillDomain,
        complexity: ComplexityLevel,
        knowledge_gaps: List[str],
    ) -> float:
        """
        Calculate confidence score for the analysis (0-1).

        Args:
            text_lower: Lowercase task text
            domain: Detected domain
            complexity: Detected complexity
            knowledge_gaps: Detected knowledge gaps

        Returns:
            Confidence score 0-1
        """
        confidence = 0.5  # Base score

        # Increase if clear domain keywords found
        domain_keywords = self.DOMAIN_KEYWORDS[domain]
        domain_keyword_count = sum(
            len(re.findall(r"\b" + kw + r"\b", text_lower)) for kw in domain_keywords
        )
        confidence += min(0.2, domain_keyword_count * 0.05)

        # Increase if complexity is clear
        if complexity in [ComplexityLevel.HIGH, ComplexityLevel.EPIC]:
            confidence += 0.15

        # Increase if knowledge gaps detected
        confidence += min(0.15, len(knowledge_gaps) * 0.05)

        # Decrease if very short description
        if len(text_lower) < 20:
            confidence -= 0.1

        # In aggressive mode, boost confidence
        if self.aggressive_mode:
            confidence += 0.1

        return max(0.0, min(1.0, confidence))

    def _build_reasoning(
        self,
        domain: SkillDomain,
        complexity: ComplexityLevel,
        knowledge_gaps: List[str],
        confidence: float,
    ) -> str:
        """
        Build human-readable reasoning string.

        Args:
            domain: Detected domain
            complexity: Detected complexity
            knowledge_gaps: Detected knowledge gaps
            confidence: Confidence score

        Returns:
            Reasoning string
        """
        parts = []

        parts.append(f"Domain: {domain.value}")
        parts.append(f"Complexity: {complexity.value}")

        if knowledge_gaps:
            parts.append(f"Knowledge gaps: {', '.join(knowledge_gaps)}")

        parts.append(f"Confidence: {confidence:.0%}")

        if len(knowledge_gaps) > 0:
            parts.append("→ Skills recommended to fill knowledge gaps")
        elif complexity in [ComplexityLevel.HIGH, ComplexityLevel.EPIC]:
            parts.append("→ Skills recommended for high-complexity task")
        else:
            parts.append("→ Task appears straightforward")

        return " | ".join(parts)
