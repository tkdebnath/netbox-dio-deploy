"""Caching layer for Diode devices.

This module provides a flexible caching layer that supports both Redis
and in-memory backends to reduce repeated API calls and improve performance.

Usage:
    from netbox_dio import DiodeDevice, CacheLayer, InMemoryCacheBackend

    # Create a cache layer with in-memory backend
    backend = InMemoryCacheBackend(max_size=10000, ttl=300)
    cache = CacheLayer(backend)

    # Cache device data
    cache.set_device("router-01", {"name": "router-01", ...})

    # Get cached data
    device = cache.get_device("router-01")
"""

from .backends import CacheBackend, RedisCacheBackend, InMemoryCacheBackend, CacheMetrics
from .layer import CacheLayer, generate_cache_key

__all__ = [
    "CacheBackend",
    "RedisCacheBackend",
    "InMemoryCacheBackend",
    "CacheMetrics",
    "CacheLayer",
    "generate_cache_key",
]
