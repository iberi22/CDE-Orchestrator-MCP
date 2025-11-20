import json
from unittest.mock import patch

from cde_orchestrator.domain.exceptions import ProjectError
from mcp_tools.documentation import cde_scanDocumentation


def test_scan_documentation_success():
    # Mock the use case to return a valid result
    with patch("mcp_tools.documentation.ScanDocumentationUseCase") as MockUseCase:
        mock_instance = MockUseCase.return_value
        mock_instance.execute.return_value = {"files": [], "total": 0}

        result = cde_scanDocumentation(project_path=".", detail_level="name_only")

        # Result should be a JSON string
        assert isinstance(result, str)
        data = json.loads(result)
        assert data == {"files": [], "total": 0}


def test_scan_documentation_domain_error():
    # Mock the use case to raise a CDEError
    with patch("mcp_tools.documentation.ScanDocumentationUseCase") as MockUseCase:
        mock_instance = MockUseCase.return_value
        mock_instance.execute.side_effect = ProjectError(
            "Project not found", code="E001", context={"path": "/invalid"}
        )

        result = cde_scanDocumentation(project_path="/invalid")

        # Result should be a Dict (from handle_errors)
        # Wait, if handle_errors returns a Dict, and the tool was supposed to return a str...
        # FastMCP handles it, but here we are calling the decorated function directly.

        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert result["error_code"] == "E001"
        assert result["message"] == "Project not found"
        assert result["details"] == {"path": "/invalid"}


def test_scan_documentation_system_error():
    # Mock the use case to raise a generic Exception
    with patch("mcp_tools.documentation.ScanDocumentationUseCase") as MockUseCase:
        mock_instance = MockUseCase.return_value
        mock_instance.execute.side_effect = ValueError("Something went wrong")

        result = cde_scanDocumentation(project_path=".")

        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert result["error_code"] == "E999"
        assert "Something went wrong" in result["message"]
