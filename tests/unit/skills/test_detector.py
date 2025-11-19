"""
Unit tests for SkillRequirementDetector.

Tests skill requirement analysis, domain detection, and complexity assessment.
"""

import pytest

from cde_orchestrator.skills.detector import SkillRequirementDetector
from cde_orchestrator.skills.models import ComplexityLevel, SkillDomain


class TestSkillRequirementDetector:
    """Tests for SkillRequirementDetector class."""

    @pytest.fixture
    def detector(self):
        """Create detector instance."""
        return SkillRequirementDetector()

    # Domain Detection Tests

    def test_detect_backend_domain(self, detector):
        """Test detection of backend domain."""
        task = "Add authentication middleware to FastAPI endpoints with JWT validation"
        result = detector.analyze_task(task)

        assert result.domain == SkillDomain.BACKEND
        # Includes "authentication" keyword, should detect knowledge gap
        assert result.needs_skill is True

    def test_detect_frontend_domain(self, detector):
        """Test detection of frontend domain."""
        task = "Create React component with state management using Redux"
        result = detector.analyze_task(task)

        assert result.domain == SkillDomain.FRONTEND
        # Frontend tasks may not always need skills unless complex
        # This is MEDIUM complexity without specific knowledge gaps

    def test_detect_database_domain(self, detector):
        """Test detection of database domain."""
        task = "Add Redis caching layer to user queries with connection pooling and optimization"
        result = detector.analyze_task(task)

        assert result.domain == SkillDomain.DATABASE
        # Contains "redis" and "caching" - should detect knowledge gap
        assert result.needs_skill is True

    def test_detect_devops_domain(self, detector):
        """Test detection of devops domain."""
        task = "Configure Docker compose for multi-container deployment with kubernetes orchestration"
        result = detector.analyze_task(task)

        assert result.domain == SkillDomain.DEVOPS
        # Contains "docker" and "orchestration" - should detect knowledge gap
        assert result.needs_skill is True

    def test_detect_security_domain(self, detector):
        """Test detection of security domain."""
        task = (
            "Implement OAuth2 authorization flow with JWT token validation and refresh"
        )
        result = detector.analyze_task(task)

        assert result.domain == SkillDomain.SECURITY
        # Contains "oauth" and "jwt" - should detect authentication knowledge gap
        assert result.needs_skill is True

    def test_detect_architecture_domain(self, detector):
        """Test detection of architecture domain."""
        task = "Completely redesign microservices architecture with event-driven communication patterns"
        result = detector.analyze_task(task)

        assert result.domain == SkillDomain.ARCHITECTURE
        # Contains "redesign" (HIGH complexity) and "microservices" (knowledge gap)
        assert result.needs_skill is True

    # Complexity Detection Tests

    def test_detect_low_complexity(self, detector):
        """Test detection of low complexity tasks."""
        task = "Fix typo in README documentation"
        result = detector.analyze_task(task)

        assert result.complexity == ComplexityLevel.LOW
        assert result.needs_skill is False  # Simple fix doesn't need skills

    def test_detect_medium_complexity(self, detector):
        """Test detection of medium complexity tasks."""
        task = "Add new API endpoint with validation and error handling"
        result = detector.analyze_task(task)

        assert result.complexity == ComplexityLevel.MEDIUM

    def test_detect_high_complexity(self, detector):
        """Test detection of high complexity tasks."""
        task = "Complete redesign and refactor of authentication system to support OAuth2 and SAML"
        result = detector.analyze_task(task)

        assert result.complexity == ComplexityLevel.HIGH
        assert result.needs_skill is True  # HIGH complexity triggers needs_skill

    def test_detect_epic_complexity(self, detector):
        """Test detection of epic complexity tasks."""
        task = "Complete system overhaul: Architect new microservices infrastructure with Kubernetes orchestration"
        result = detector.analyze_task(task)

        assert result.complexity == ComplexityLevel.EPIC
        assert result.needs_skill is True  # EPIC complexity triggers needs_skill

    # Knowledge Gap Detection Tests

    def test_detect_redis_knowledge_gap(self, detector):
        """Test detection of Redis-related knowledge gaps."""
        task = "Add Redis caching with connection pooling"
        result = detector.analyze_task(task)

        assert "redis" in [gap.lower() for gap in result.knowledge_gaps]

    def test_detect_oauth_knowledge_gap(self, detector):
        """Test detection of OAuth-related knowledge gaps."""
        task = "Implement OAuth2 authentication flow"
        result = detector.analyze_task(task)

        assert "oauth" in [gap.lower() for gap in result.knowledge_gaps]

    def test_detect_docker_knowledge_gap(self, detector):
        """Test detection of Docker-related knowledge gaps."""
        task = "Containerize application with Docker Compose"
        result = detector.analyze_task(task)

        assert "docker" in [gap.lower() for gap in result.knowledge_gaps]

    def test_detect_multiple_knowledge_gaps(self, detector):
        """Test detection of multiple knowledge gaps."""
        task = "Build FastAPI backend with Redis caching and PostgreSQL database"
        result = detector.analyze_task(task)

        gaps_lower = [gap.lower() for gap in result.knowledge_gaps]
        assert "fastapi" in gaps_lower or "api" in gaps_lower
        assert "redis" in gaps_lower
        assert "postgresql" in gaps_lower or "postgres" in gaps_lower

    # Edge Cases

    def test_empty_task_description(self, detector):
        """Test handling of empty task description."""
        result = detector.analyze_task("")

        assert result.needs_skill is False
        assert len(result.knowledge_gaps) == 0

    def test_simple_task_no_skills_needed(self, detector):
        """Test simple tasks that don't need skills."""
        task = "Update version number in config file"
        result = detector.analyze_task(task)

        assert result.needs_skill is False
        assert result.complexity == ComplexityLevel.LOW

    def test_task_with_mixed_domains(self, detector):
        """Test task spanning multiple domains."""
        task = "Build full-stack app with React frontend and FastAPI backend"
        result = detector.analyze_task(task)

        # Should detect at least one domain
        assert result.domain in [SkillDomain.FRONTEND, SkillDomain.BACKEND]
        assert result.needs_skill is True

    def test_confidence_score_calculation(self, detector):
        """Test confidence score is within valid range."""
        task = "Add Redis caching to authentication module"
        result = detector.analyze_task(task)

        assert 0.0 <= result.confidence <= 1.0
        assert result.confidence > 0.5  # Should be reasonably confident

    def test_needs_skill_true_for_complex_tasks(self, detector):
        """Test that complex tasks are marked as needing skills."""
        task = "Refactor database layer to use async/await patterns"
        result = detector.analyze_task(task)

        assert result.needs_skill is True
        assert result.complexity in [ComplexityLevel.MEDIUM, ComplexityLevel.HIGH]

    def test_needs_skill_false_for_trivial_tasks(self, detector):
        """Test that trivial tasks don't need skills."""
        task = "Fix typo"
        result = detector.analyze_task(task)

        assert result.needs_skill is False

    # Case Sensitivity Tests

    def test_case_insensitive_keyword_detection(self, detector):
        """Test that keyword detection is case insensitive."""
        task_upper = "ADD REDIS CACHING TO FASTAPI"
        task_lower = "add redis caching to fastapi"
        task_mixed = "Add Redis Caching to FastAPI"

        result_upper = detector.analyze_task(task_upper)
        result_lower = detector.analyze_task(task_lower)
        result_mixed = detector.analyze_task(task_mixed)

        assert result_upper.domain == result_lower.domain == result_mixed.domain
        assert (
            result_upper.needs_skill
            == result_lower.needs_skill
            == result_mixed.needs_skill
        )

    # Validation Tests

    def test_skill_requirement_has_all_fields(self, detector):
        """Test that SkillRequirement has all expected fields."""
        task = "Add authentication to API"
        result = detector.analyze_task(task)

        assert hasattr(result, "needs_skill")
        assert hasattr(result, "complexity")
        assert hasattr(result, "domain")
        assert hasattr(result, "knowledge_gaps")
        assert hasattr(result, "confidence")

    def test_knowledge_gaps_are_strings(self, detector):
        """Test that knowledge gaps are returned as strings."""
        task = "Add Redis caching with OAuth2 authentication"
        result = detector.analyze_task(task)

        assert all(isinstance(gap, str) for gap in result.knowledge_gaps)

    def test_no_duplicate_knowledge_gaps(self, detector):
        """Test that knowledge gaps list doesn't contain duplicates."""
        task = "Add Redis caching and Redis connection pooling"
        result = detector.analyze_task(task)

        gaps_lower = [gap.lower() for gap in result.knowledge_gaps]
        assert len(gaps_lower) == len(set(gaps_lower))

    # Integration Tests

    def test_realistic_feature_request(self, detector):
        """Test realistic feature request analysis."""
        task = """
        Add user profile editing feature:
        - React frontend with form validation
        - FastAPI backend endpoint
        - PostgreSQL database updates
        - Image upload to S3
        - Email notification on change
        """
        result = detector.analyze_task(task)

        assert result.needs_skill is True
        assert result.complexity in [ComplexityLevel.HIGH, ComplexityLevel.EPIC]
        assert len(result.knowledge_gaps) > 0

    def test_realistic_bug_fix(self, detector):
        """Test realistic bug fix analysis."""
        task = "Fix memory leak in Redis connection pooling"
        result = detector.analyze_task(task)

        assert result.needs_skill is True
        assert "redis" in [gap.lower() for gap in result.knowledge_gaps]

    def test_realistic_refactoring_task(self, detector):
        """Test realistic refactoring task analysis."""
        task = "Refactor authentication layer to use dependency injection"
        result = detector.analyze_task(task)

        assert result.needs_skill is True
        assert result.complexity in [ComplexityLevel.MEDIUM, ComplexityLevel.HIGH]
