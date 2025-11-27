import asyncio
import shutil
import sys
from pathlib import Path
from typing import Any, Dict

import psutil

from cde_orchestrator.infrastructure.cache import CacheManager
from cde_orchestrator.infrastructure.circuit_breaker import get_circuit_breaker_registry
from cde_orchestrator.infrastructure.rate_limiter import get_rate_limiter
from cde_orchestrator.rust_utils import RUST_AVAILABLE


class CheckHealthUseCase:
    """
    Use case to check the health of the CDE Orchestrator system.

    Provides comprehensive health checks including:
    - Component availability (Python, Rust, Git, GH)
    - Cache health and metrics
    - Disk space availability
    - Memory usage
    - Circuit breaker status
    - Rate limiter metrics
    """

    def __init__(self, project_root: Path | None = None):
        self.cache_manager = CacheManager()
        """
        Initialize health check use case.

        Args:
            project_root: Project root directory for disk checks
        """
        self.project_root = project_root or Path.cwd()

    def execute(self) -> Dict[str, Any]:
        """
        Execute comprehensive health check.

        Returns:
            Dictionary with overall status and component details
        """
        # Component checks
        rust_status = "ok" if RUST_AVAILABLE else "degraded"
        git_available = shutil.which("git") is not None
        gh_available = shutil.which("gh") is not None

        # Cache health
        cache_health = self._check_cache()

        # Resource checks
        disk_health = self._check_disk_space()
        memory_health = self._check_memory()

        # Resilience components
        circuit_breaker_health = self._check_circuit_breakers()
        rate_limiter_health = self._check_rate_limiters()

        # Determine overall status
        overall_status = self._determine_overall_status(
            rust_available=RUST_AVAILABLE,
            cache_ok=cache_health["status"] == "ok",
            disk_ok=disk_health["status"] == "ok",
            memory_ok=memory_health["status"] == "ok",
        )

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
            "cache": cache_health,
            "resources": {
                "disk": disk_health,
                "memory": memory_health,
            },
            "resilience": {
                "circuit_breakers": circuit_breaker_health,
                "rate_limiters": rate_limiter_health,
            },
        }

    def check_readiness(self) -> Dict[str, Any]:
        """
        Check if system is ready to accept requests.

        Readiness probe - returns quickly, checks if system can handle requests.

        Returns:
            Dictionary with ready status and reasons
        """
        issues = []

        # Check critical components
        if self.cache_manager is None:
            issues.append("Cache not initialized")

        # Check disk space (need at least 100MB)
        disk = psutil.disk_usage(str(self.project_root))
        if disk.free < 100 * 1024 * 1024:  # 100MB
            issues.append(f"Low disk space: {disk.free / (1024**2):.1f}MB free")

        # Check memory (need at least 100MB)
        memory = psutil.virtual_memory()
        if memory.available < 100 * 1024 * 1024:  # 100MB
            issues.append(f"Low memory: {memory.available / (1024**2):.1f}MB available")

        ready = len(issues) == 0

        return {
            "ready": ready,
            "issues": issues if not ready else [],
            "timestamp": psutil.boot_time(),
        }

    def check_liveness(self) -> Dict[str, Any]:
        """
        Check if system is alive and functioning.

        Liveness probe - basic check that process is responsive.

        Returns:
            Dictionary with alive status
        """
        # Simple check - if we can execute this, we're alive
        return {
            "alive": True,
            "pid": psutil.Process().pid,
            "uptime_seconds": psutil.Process().create_time(),
        }

    def _check_cache(self) -> Dict[str, Any]:
        """Check cache health and metrics."""
        try:
            metrics = self.cache_manager.get_stats()

            # Cache is healthy if hit rate > 0.3 or not enough requests yet
            hit_rate = metrics.get("hit_rate", 0.0)
            total_requests = metrics.get("total_requests", 0)

            status = "ok"
            if total_requests > 100 and hit_rate < 0.3:
                status = "degraded"  # Low hit rate

            return {
                "status": status,
                "available": True,
                "metrics": metrics,
            }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e),
            }

    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space availability."""
        try:
            disk = psutil.disk_usage(str(self.project_root))

            # Thresholds
            free_gb = disk.free / (1024**3)
            percent_free = (disk.free / disk.total) * 100

            status = "ok"
            if free_gb < 1.0 or percent_free < 10:
                status = "critical"
            elif free_gb < 5.0 or percent_free < 20:
                status = "warning"

            return {
                "status": status,
                "total_gb": disk.total / (1024**3),
                "free_gb": free_gb,
                "used_gb": disk.used / (1024**3),
                "percent_free": percent_free,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()

            # Thresholds
            available_gb = memory.available / (1024**3)
            percent_available = memory.available / memory.total * 100

            status = "ok"
            if available_gb < 0.5 or percent_available < 10:
                status = "critical"
            elif available_gb < 1.0 or percent_available < 20:
                status = "warning"

            return {
                "status": status,
                "total_gb": memory.total / (1024**3),
                "available_gb": available_gb,
                "used_gb": memory.used / (1024**3),
                "percent_available": percent_available,
                "percent_used": memory.percent,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def _check_circuit_breakers(self) -> Dict[str, Any]:
        """Check circuit breaker status."""
        try:
            registry = get_circuit_breaker_registry()
            all_metrics = registry.get_all_metrics()

            # Count states
            open_count = sum(
                1 for m in all_metrics.values() if m.get("state") == "OPEN"
            )
            half_open_count = sum(
                1 for m in all_metrics.values() if m.get("state") == "HALF_OPEN"
            )

            status = "ok"
            if open_count > 0:
                status = "degraded"  # Some services are failing

            return {
                "status": status,
                "total_breakers": len(all_metrics),
                "open": open_count,
                "half_open": half_open_count,
                "closed": len(all_metrics) - open_count - half_open_count,
                "details": all_metrics,
            }
        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e),
            }

    def _check_rate_limiters(self) -> Dict[str, Any]:
        """Check rate limiter metrics."""

        async def _async_check():
            try:
                limiter = get_rate_limiter()
                all_metrics = await limiter.get_all_metrics()

                # Check for high rejection rates
                high_rejection = any(
                    m.get("rejection_rate", 0) > 0.5 for m in all_metrics.values()
                )

                status = "ok"
                if high_rejection:
                    status = "warning"  # High rejection rate

                return {
                    "status": status,
                    "active_limiters": len(all_metrics),
                    "metrics": all_metrics,
                }
            except Exception as e:
                return {
                    "status": "unknown",
                    "error": str(e),
                }

        try:
            return asyncio.run(_async_check())
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def _determine_overall_status(
        self,
        rust_available: bool,
        cache_ok: bool,
        disk_ok: bool,
        memory_ok: bool,
    ) -> str:
        """
        Determine overall system status.

        Args:
            rust_available: Whether Rust core is available
            cache_ok: Whether cache is healthy
            disk_ok: Whether disk space is adequate
            memory_ok: Whether memory is adequate

        Returns:
            Overall status: "healthy", "degraded", or "unhealthy"
        """
        # Critical issues
        if not disk_ok or not memory_ok:
            return "unhealthy"

        # Degraded issues
        if not rust_available or not cache_ok:
            return "degraded"

        return "healthy"
