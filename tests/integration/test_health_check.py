import json
from unittest.mock import patch

from mcp_tools.health import cde_healthCheck


def test_health_check_structure():
    # Mock shutil.which to simulate tools being available
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/git"

        result = cde_healthCheck()

        assert isinstance(result, str)
        data = json.loads(result)

        assert data["status"] in ["healthy", "degraded"]
        assert "components" in data
        assert "python" in data["components"]
        assert "rust_core" in data["components"]
        assert "external_tools" in data["components"]
        assert data["components"]["external_tools"]["git"] == "available"
