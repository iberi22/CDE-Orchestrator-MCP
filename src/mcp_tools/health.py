import json

from cde_orchestrator.application.health import CheckHealthUseCase

from ._base import tool_handler


@tool_handler
def cde_healthCheck() -> str:
    """
    Check the health status of the CDE Orchestrator MCP server.

    Returns:
        JSON with health status of components (Python, Rust, External Tools).
    """
    use_case = CheckHealthUseCase()
    result = use_case.execute()
    return json.dumps(result, indent=2)
