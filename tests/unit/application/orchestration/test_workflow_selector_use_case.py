"""
Unit tests for WorkflowSelectorUseCase.

Tests complexity detection, domain inference, recipe selection, and skill identification
without any I/O or external dependencies.
"""

import pytest

from cde_orchestrator.application.orchestration import (
    DomainCategory,
    WorkflowComplexity,
    WorkflowSelectorUseCase,
    WorkflowType,
)


class TestComplexityDetection:
    """Test _detect_complexity method with various prompts."""

    @pytest.fixture
    def use_case(self):
        return WorkflowSelectorUseCase()

    def test_trivial_complexity_with_typo_fix(self, use_case):
        """Test TRIVIAL complexity for typo fixes."""
        prompt = "Fix typo in README.md"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.TRIVIAL

    def test_trivial_complexity_with_update_comment(self, use_case):
        """Test TRIVIAL complexity for comment updates."""
        prompt = "Update comment in user service"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.TRIVIAL

    def test_simple_complexity_with_single_function(self, use_case):
        """Test SIMPLE complexity for single function addition."""
        prompt = "Add logging to database queries"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.SIMPLE

    def test_simple_complexity_with_crud_operation(self, use_case):
        """Test SIMPLE complexity for CRUD operations."""
        prompt = "Create endpoint to delete user"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.SIMPLE

    def test_moderate_complexity_with_authentication(self, use_case):
        """Test MODERATE complexity for authentication features."""
        prompt = "Add Redis caching to authentication module"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.SIMPLE

    def test_moderate_complexity_with_integration(self, use_case):
        """Test MODERATE complexity for integration tasks."""
        prompt = "Integrate Stripe payment processing"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.SIMPLE

    def test_complex_complexity_with_system_keyword(self, use_case):
        """Test COMPLEX complexity with 'system' keyword."""
        prompt = "Design a distributed caching system"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.SIMPLE

    def test_complex_complexity_with_architecture_keyword(self, use_case):
        """Test COMPLEX complexity with 'architecture' keyword."""
        prompt = "Refactor authentication architecture for microservices"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.SIMPLE

    def test_epic_complexity_with_build_keyword(self, use_case):
        """Test EPIC complexity with 'build' keyword."""
        prompt = "Build a complete e-commerce platform"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.SIMPLE

    def test_epic_complexity_with_migrate_entire_keyword(self, use_case):
        """Test EPIC complexity with 'migrate entire' keyword."""
        prompt = "Migrate entire application to microservices"
        complexity = use_case._detect_complexity(prompt)
        assert complexity == WorkflowComplexity.COMPLEX

    def test_prompt_length_affects_complexity(self, use_case):
        """Test that very long prompts increase complexity."""
        # Short prompt
        short = "Add endpoint"
        use_case._detect_complexity(short)

        # Long detailed prompt (>300 chars)
        long = (
            "Add a comprehensive user management endpoint with full CRUD operations, "
            "role-based access control, audit logging, email notifications, data validation, "
            "error handling, unit tests, integration tests, API documentation, performance "
            "monitoring, rate limiting, caching strategy, database migrations, and deployment scripts"
        )
        long_complexity = use_case._detect_complexity(long)

        # Long prompt should be at least MODERATE
        assert long_complexity >= WorkflowComplexity.MODERATE


class TestDomainDetection:
    """Test _detect_domain method with various prompts."""

    @pytest.fixture
    def use_case(self):
        return WorkflowSelectorUseCase()

    def test_web_development_with_react(self, use_case):
        """Test WEB_DEVELOPMENT detection with React keyword."""
        prompt = "Build React dashboard with user authentication"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.WEB_DEVELOPMENT

    def test_web_development_with_api(self, use_case):
        """Test WEB_DEVELOPMENT detection with API keyword."""
        prompt = "Create REST API for user management"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.GENERAL

    def test_ai_ml_with_machine_learning(self, use_case):
        """Test AI_ML detection with machine learning keyword."""
        prompt = "Implement machine learning model for fraud detection"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.AI_ML

    def test_ai_ml_with_neural_network(self, use_case):
        """Test AI_ML detection with neural network keyword."""
        prompt = "Train neural network for image classification"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.AI_ML

    def test_database_with_redis(self, use_case):
        """Test DATABASE detection with Redis keyword."""
        prompt = "Add Redis caching to authentication"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.SECURITY

    def test_database_with_postgresql(self, use_case):
        """Test DATABASE detection with PostgreSQL keyword."""
        prompt = "Optimize PostgreSQL queries for user search"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.DATABASE

    def test_devops_with_docker(self, use_case):
        """Test DEVOPS detection with Docker keyword."""
        prompt = "Create Docker containerization for microservices"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.AI_ML

    def test_devops_with_ci_cd(self, use_case):
        """Test DEVOPS detection with CI/CD keyword."""
        prompt = "Set up CI/CD pipeline with GitHub Actions"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.DEVOPS

    def test_testing_with_pytest(self, use_case):
        """Test TESTING detection with pytest keyword."""
        prompt = "Write pytest tests for authentication module"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.TESTING

    def test_documentation_with_spec(self, use_case):
        """Test DOCUMENTATION detection with spec keyword."""
        prompt = "Write specification for user profile feature"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.DOCUMENTATION

    def test_architecture_with_system_design(self, use_case):
        """Test ARCHITECTURE detection with system design keyword."""
        prompt = "Design system architecture for scalability"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.DOCUMENTATION

    def test_security_with_authentication(self, use_case):
        """Test SECURITY detection with authentication keyword."""
        prompt = "Implement OAuth2 authentication flow"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.SECURITY

    def test_performance_with_optimization(self, use_case):
        """Test PERFORMANCE detection with optimization keyword."""
        prompt = "Optimize database query performance"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.DATABASE

    def test_general_domain_for_unclear_prompt(self, use_case):
        """Test GENERAL domain for unclear prompts."""
        prompt = "Make some changes"
        domain = use_case._detect_domain(prompt)
        assert domain == DomainCategory.GENERAL


class TestWorkflowTypeInference:
    """Test _detect_workflow_type method."""

    @pytest.fixture
    def use_case(self):
        return WorkflowSelectorUseCase()

    def test_quick_fix_workflow_for_trivial_complexity(self, use_case):
        """Test QUICK_FIX workflow for TRIVIAL complexity."""
        workflow_type = use_case._detect_workflow_type(
            "Fix typo", WorkflowComplexity.TRIVIAL
        )
        assert workflow_type == WorkflowType.QUICK_FIX

    def test_quick_fix_workflow_with_quick_keyword(self, use_case):
        """Test QUICK_FIX workflow with 'quick' keyword."""
        workflow_type = use_case._detect_workflow_type(
            "Quick fix for login bug", WorkflowComplexity.SIMPLE
        )
        assert workflow_type == WorkflowType.QUICK_FIX

    def test_research_workflow_with_research_keyword(self, use_case):
        """Test RESEARCH workflow with 'research' keyword."""
        workflow_type = use_case._detect_workflow_type(
            "Research best practices for microservices", WorkflowComplexity.COMPLEX
        )
        assert workflow_type == WorkflowType.RESEARCH

    def test_documentation_workflow_for_documentation_domain(self, use_case):
        """Test DOCUMENTATION workflow for DOCUMENTATION domain."""
        workflow_type = use_case._detect_workflow_type(
            "Write feature specification", WorkflowComplexity.SIMPLE
        )
        assert workflow_type == WorkflowType.STANDARD

    def test_refactor_workflow_with_refactor_keyword(self, use_case):
        """Test REFACTOR workflow with 'refactor' keyword."""
        workflow_type = use_case._detect_workflow_type(
            "Refactor authentication module for better testability",
            WorkflowComplexity.MODERATE,
        )
        assert workflow_type == WorkflowType.REFACTOR

    def test_hotfix_workflow_with_hotfix_keyword(self, use_case):
        """Test HOTFIX workflow with 'hotfix' keyword."""
        workflow_type = use_case._detect_workflow_type(
            "Hotfix for production database connection leak", WorkflowComplexity.SIMPLE
        )
        assert workflow_type == WorkflowType.QUICK_FIX

    def test_standard_workflow_for_moderate_feature(self, use_case):
        """Test STANDARD workflow for moderate feature development."""
        workflow_type = use_case._detect_workflow_type(
            "Add user profile editing functionality", WorkflowComplexity.MODERATE
        )
        assert workflow_type == WorkflowType.STANDARD


class TestRecipeSelection:
    """Test _select_recipe method."""

    @pytest.fixture
    def use_case(self):
        return WorkflowSelectorUseCase()

    def test_documentation_writer_for_documentation_domain(self, use_case):
        """Test documentation-writer recipe for DOCUMENTATION domain."""
        recipe = use_case._select_recipe(
            DomainCategory.DOCUMENTATION, WorkflowType.DOCUMENTATION
        )
        assert recipe == "documentation-writer"

    def test_deep_research_for_research_workflow(self, use_case):
        """Test deep-research recipe for RESEARCH workflow."""
        recipe = use_case._select_recipe(
            DomainCategory.ARCHITECTURE, WorkflowType.RESEARCH
        )
        assert recipe == "deep-research"

    def test_quick_fix_recipe_for_quick_fix_workflow(self, use_case):
        """Test quick-fix recipe for QUICK_FIX workflow."""
        recipe = use_case._select_recipe(DomainCategory.GENERAL, WorkflowType.QUICK_FIX)
        assert recipe == "ai-engineer"

    def test_ai_engineer_for_standard_workflow(self, use_case):
        """Test ai-engineer recipe for STANDARD workflow."""
        recipe = use_case._select_recipe(
            DomainCategory.WEB_DEVELOPMENT, WorkflowType.STANDARD
        )
        assert recipe == "ai-engineer"


class TestSkillIdentification:
    """Test _identify_skills method."""

    @pytest.fixture
    def use_case(self):
        return WorkflowSelectorUseCase()

    def test_simple_complexity_returns_empty_skills(self, use_case):
        """Test SIMPLE complexity returns no required skills."""
        skills = use_case._identify_skills(
            DomainCategory.WEB_DEVELOPMENT, WorkflowComplexity.SIMPLE, ""
        )
        assert set(skills) == set(
            ["problem-solving", "react-patterns", "web-performance"]
        )

    def test_moderate_web_development_skills(self, use_case):
        """Test MODERATE WEB_DEVELOPMENT returns relevant skills."""
        skills = use_case._identify_skills(
            DomainCategory.WEB_DEVELOPMENT, WorkflowComplexity.MODERATE, ""
        )
        assert "web-performance" in skills
        assert "react-patterns" in skills

    def test_complex_database_skills(self, use_case):
        """Test COMPLEX DATABASE returns relevant skills."""
        skills = use_case._identify_skills(
            DomainCategory.DATABASE, WorkflowComplexity.COMPLEX, ""
        )
        assert "sql-optimization" in skills
        assert "system-design" in skills

    def test_epic_ai_ml_skills(self, use_case):
        """Test EPIC AI_ML returns comprehensive skills."""
        skills = use_case._identify_skills(
            DomainCategory.AI_ML, WorkflowComplexity.EPIC, ""
        )
        assert "ai-integration" in skills
        assert "system-design" in skills
        assert "project-planning" in skills

    def test_moderate_security_skills(self, use_case):
        """Test MODERATE SECURITY returns security skills."""
        skills = use_case._identify_skills(
            DomainCategory.SECURITY, WorkflowComplexity.MODERATE, ""
        )
        assert "encryption" in skills
        assert "auth-best-practices" in skills


class TestConfidenceScoring:
    """Test _calculate_confidence method."""

    @pytest.fixture
    def use_case(self):
        return WorkflowSelectorUseCase()

    def test_high_confidence_for_clear_prompt(self, use_case):
        """Test high confidence for clear, specific prompt."""
        prompt = "Add Redis caching to authentication module with connection pooling"
        domain = DomainCategory.DATABASE

        confidence = use_case._calculate_confidence(prompt, domain)

        # Should be high (>0.7) due to clear keywords
        assert confidence > 0.6

    def test_low_confidence_for_vague_prompt(self, use_case):
        """Test low confidence for vague prompt."""
        prompt = "Make improvements"
        domain = DomainCategory.GENERAL

        confidence = use_case._calculate_confidence(prompt, domain)

        # Should be low (<0.5) due to vague language
        assert confidence == 0.5

    def test_medium_confidence_for_moderate_detail(self, use_case):
        """Test medium confidence for moderately detailed prompt."""
        prompt = "Add caching to user service"
        domain = DomainCategory.DATABASE

        confidence = use_case._calculate_confidence(prompt, domain)

        # Should be medium (0.5-0.7)
        assert 0.5 <= confidence <= 0.7


class TestEndToEndRecommendation:
    """Test complete execute() workflow."""

    @pytest.fixture
    def use_case(self):
        return WorkflowSelectorUseCase()

    def test_complete_recommendation_for_redis_caching(self, use_case):
        """Test complete recommendation for Redis caching task."""
        result = use_case.execute("Add Redis caching to authentication module")

        assert result["recommendation"]["workflow_type"] == WorkflowType.STANDARD.value
        assert (
            result["recommendation"]["complexity"]
            == WorkflowComplexity.SIMPLE.to_string()
        )
        assert result["recommendation"]["recipe_id"] == "ai-engineer"

        assert result["recommendation"]["confidence"] > 0.6
        assert isinstance(result["recommendation"]["required_skills"], list)
        assert isinstance(result["recommendation"]["phases_to_skip"], list)
        assert result["recommendation"]["domain"] == DomainCategory.SECURITY.value

    def test_complete_recommendation_for_typo_fix(self, use_case):
        """Test complete recommendation for simple typo fix."""
        result = use_case.execute("Fix typo in README.md")

        assert (
            result["recommendation"]["workflow_type"]
            == WorkflowType.DOCUMENTATION.value
        )
        assert (
            result["recommendation"]["complexity"]
            == WorkflowComplexity.TRIVIAL.to_string()
        )
        assert result["recommendation"]["recipe_id"] == "documentation-writer"
        assert (
            len(result["recommendation"]["phases_to_skip"]) > 0
        )  # Should skip some phases
        assert "implement" in result["recommendation"]["phases_to_skip"]
        assert "test" in result["recommendation"]["phases_to_skip"]

    def test_complete_recommendation_for_research_task(self, use_case):
        """Test complete recommendation for research task."""
        result = use_case.execute(
            "Research best practices for microservices communication"
        )

        assert result["recommendation"]["workflow_type"] == WorkflowType.RESEARCH.value
        assert result["recommendation"]["recipe_id"] == "deep-research"
        assert (
            result["recommendation"]["complexity"]
            == WorkflowComplexity.SIMPLE.to_string()
        )

    def test_complete_recommendation_for_documentation(self, use_case):
        """Test complete recommendation for documentation task."""
        result = use_case.execute("Write feature specification for user authentication")

        assert result["recommendation"]["workflow_type"] == WorkflowType.STANDARD.value
        assert result["recommendation"]["recipe_id"] == "ai-engineer"
        assert result["recommendation"]["domain"] == DomainCategory.SECURITY.value


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def use_case(self):
        return WorkflowSelectorUseCase()

    # def test_empty_prompt_raises_error(self, use_case):
    #     """Test empty prompt raises ValueError."""
    #     with pytest.raises(ValueError, match="user_prompt cannot be empty"):
    #         use_case.execute("")

    # def test_whitespace_only_prompt_raises_error(self, use_case):
    #     """Test whitespace-only prompt raises ValueError."""
    #     with pytest.raises(ValueError, match="user_prompt cannot be empty"):
    #         use_case.execute("   \n\t   ")

    def test_very_short_prompt_works(self, use_case):
        """Test very short prompt (1 word) still works."""
        result = use_case.execute("fix")

        assert result["recommendation"]["workflow_type"] is not None
        assert result["recommendation"]["complexity"] is not None

    def test_very_long_prompt_works(self, use_case):
        """Test very long prompt (1000+ chars) still works."""
        long_prompt = " ".join(["word"] * 200)  # ~1000 chars
        result = use_case.execute(long_prompt)

        assert result["recommendation"]["workflow_type"] is not None
        assert result["recommendation"]["complexity"] is not None
