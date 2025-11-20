import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Centralized configuration for CDE Orchestrator."""

    # Environment
    ENV: str = os.getenv("CDE_ENV", "development")
    DEBUG: bool = os.getenv("CDE_DEBUG", "false").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.getenv("CDE_LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("CDE_LOG_FORMAT", "json")

    # External Tools
    JULIUS_API_KEY: Optional[str] = os.getenv("JULIUS_API_KEY")
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")

    # Paths
    WORKSPACE_ROOT: str = os.getcwd()

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"


# Singleton instance
config = Config()
