# tests/unit/application/use_cases/test_select_workflow.py
import pytest

from src.cde_orchestrator.application.use_cases.select_workflow import (
    SelectWorkflowUseCase,
)


@pytest.fixture
def workflow_patterns():
    return {
        "web_application": ["web", "api", "frontend", "backend"],
        "data_processing": ["data", "etl", "pipeline"],
        "bug_fix": ["fix", "bug", "error"],
    }


@pytest.fixture
def select_workflow_use_case(workflow_patterns):
    return SelectWorkflowUseCase(workflow_patterns)


def test_select_web_application_workflow(
    select_workflow_use_case: SelectWorkflowUseCase,
):
    """Should select 'web_application' for web-related prompts."""
    prompt = "I want to build a new web app with a frontend and a backend API."
    workflow_type = select_workflow_use_case.execute(prompt)
    assert workflow_type == "web_application"


def test_select_data_processing_workflow(
    select_workflow_use_case: SelectWorkflowUseCase,
):
    """Should select 'data_processing' for data-related prompts."""
    prompt = "I need to create a data processing pipeline for my ETL job."
    workflow_type = select_workflow_use_case.execute(prompt)
    assert workflow_type == "data_processing"


def test_select_bug_fix_workflow(select_workflow_use_case: SelectWorkflowUseCase):
    """Should select 'bug_fix' for bug-related prompts."""
    prompt = "There is a bug in the login form that is causing an error."
    workflow_type = select_workflow_use_case.execute(prompt)
    assert workflow_type == "bug_fix"


def test_select_default_workflow_for_no_match(
    select_workflow_use_case: SelectWorkflowUseCase,
):
    """Should return 'default' when no patterns match."""
    prompt = "I want to write some documentation."
    workflow_type = select_workflow_use_case.execute(prompt)
    assert workflow_type == "default"


def test_select_workflow_is_case_insensitive(
    select_workflow_use_case: SelectWorkflowUseCase,
):
    """Should match patterns regardless of case."""
    prompt = "I want to FIX a BUG in the API."
    workflow_type = select_workflow_use_case.execute(prompt)
    assert workflow_type == "bug_fix"
