import shutil
import sys
from typing import Any, Dict

from cde_orchestrator.rust_utils import RUST_AVAILABLE


class CheckHealthUseCase:
    """
    Use case to check the health of the CDE Orchestrator system.
    """

    def execute(self) -> Dict[str, Any]:
        rust_status = "ok" if RUST_AVAILABLE else "degraded"
        git_available = shutil.which("git") is not None
        gh_available = shutil.which("gh") is not None

        overall_status = "healthy"
        if not RUST_AVAILABLE:
            overall_status = "degraded"

        return {
            "status": overall_status,
            "components": {
                "python": {"version": sys.version.split()[0], "status": "ok"},
                "rust_core": {"available": RUST_AVAILABLE, "status": rust_status},
                "external_tools": {
                    "git": "available" if git_available else "missing",
                    "gh": "available" if gh_available else "missing",
                },
            },
        }
