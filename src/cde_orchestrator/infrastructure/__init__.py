"""
Infrastructure Layer - Cross-cutting concerns.

Provides:
- Caching (cache.py)
- Metrics (cache_metrics.py)
- Cache strategies (cache_strategies.py)
"""

from .cache import CacheManager

__all__ = ["CacheManager"]
