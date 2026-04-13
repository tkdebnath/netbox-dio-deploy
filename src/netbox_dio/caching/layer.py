"""Unified cache layer for Diode devices.

This module provides the CacheLayer class that abstracts cache backend
details and provides a unified interface for caching devices, validation
results, and quality metrics.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Optional

from .backends import CacheBackend, CacheMetrics, RedisCacheBackend, InMemoryCacheBackend, generate_cache_key


class CacheLayer:
    """Unified cache layer for Diode devices.

    Provides a high-level interface for caching device data, validation
    results, and quality metrics. Automatically handles cache key generation
    and backend-specific operations.

    Attributes:
        _backend: The underlying cache backend
        _device_ttl: TTL for device cache entries
        _validation_ttl: TTL for validation results
        _quality_ttl: TTL for quality metrics
    """

    def __init__(
        self,
        backend: CacheBackend,
        device_ttl: int = 300,
        validation_ttl: int = 600,
        quality_ttl: int = 900,
    ) -> None:
        """Initialize the cache layer.

        Parameters:
            backend: The underlying cache backend
            device_ttl: TTL for device cache (default: 300s)
            validation_ttl: TTL for validation results (default: 600s)
            quality_ttl: TTL for quality metrics (default: 900s)
        """
        self._backend = backend
        self._device_ttl = device_ttl
        self._validation_ttl = validation_ttl
        self._quality_ttl = quality_ttl

    @property
    def metrics(self) -> CacheMetrics:
        """Get cache operation metrics from the backend."""
        return self._backend.metrics

    # Device caching methods

    async def get_device(self, name: str) -> Optional[dict]:
        """Get cached device data.

        Args:
            name: The device name

        Returns:
            Cached device data dictionary, or None if not found
        """
        key = generate_cache_key("device:", name)
        return await self._backend.get(key)

    async def set_device(self, name: str, data: dict, ttl: Optional[int] = None) -> None:
        """Cache device data.

        Args:
            name: The device name
            data: Device data dictionary
            ttl: Optional TTL override
        """
        key = generate_cache_key("device:", name)
        await self._backend.set(key, data, ttl or self._device_ttl)

    async def invalidate_device(self, name: str) -> bool:
        """Invalidate cached device data.

        Args:
            name: The device name

        Returns:
            True if invalidated, False if not found
        """
        key = generate_cache_key("device:", name)
        return await self._backend.delete(key)

    # Validation results caching

    async def get_validation_results(self, device_hash: str) -> Optional[dict]:
        """Get cached validation results.

        Args:
            device_hash: Hash of the device data

        Returns:
            Cached validation results dictionary, or None if not found
        """
        key = generate_cache_key("validation:", device_hash)
        return await self._backend.get(key)

    async def set_validation_results(
        self, device_hash: str, results: dict, ttl: Optional[int] = None
    ) -> None:
        """Cache validation results.

        Args:
            device_hash: Hash of the device data
            results: Validation results dictionary
            ttl: Optional TTL override
        """
        key = generate_cache_key("validation:", device_hash)
        await self._backend.set(key, results, ttl or self._validation_ttl)

    async def invalidate_validation_results(self, device_hash: str) -> bool:
        """Invalidate cached validation results.

        Args:
            device_hash: Hash of the device data

        Returns:
            True if invalidated, False if not found
        """
        key = generate_cache_key("validation:", device_hash)
        return await self._backend.delete(key)

    # Quality metrics caching

    async def get_quality_metrics(self, device_hash: str) -> Optional[dict]:
        """Get cached quality metrics.

        Args:
            device_hash: Hash of the device data

        Returns:
            Cached quality metrics dictionary, or None if not found
        """
        key = generate_cache_key("quality:", device_hash)
        return await self._backend.get(key)

    async def set_quality_metrics(
        self, device_hash: str, metrics: dict, ttl: Optional[int] = None
    ) -> None:
        """Cache quality metrics.

        Args:
            device_hash: Hash of the device data
            metrics: Quality metrics dictionary
            ttl: Optional TTL override
        """
        key = generate_cache_key("quality:", device_hash)
        await self._backend.set(key, metrics, ttl or self._quality_ttl)

    async def invalidate_quality_metrics(self, device_hash: str) -> bool:
        """Invalidate cached quality metrics.

        Args:
            device_hash: Hash of the device data

        Returns:
            True if invalidated, False if not found
        """
        key = generate_cache_key("quality:", device_hash)
        return await self._backend.delete(key)

    # Batch operations

    async def get_batch_cache(self, batch_id: str) -> Optional[dict]:
        """Get cached batch operation results.

        Args:
            batch_id: The batch operation ID

        Returns:
            Cached batch results dictionary, or None if not found
        """
        key = generate_cache_key("batch:", batch_id)
        return await self._backend.get(key)

    async def set_batch_cache(
        self, batch_id: str, results: dict, ttl: Optional[int] = None
    ) -> None:
        """Cache batch operation results.

        Args:
            batch_id: The batch operation ID
            results: Batch results dictionary
            ttl: Optional TTL override
        """
        key = generate_cache_key("batch:", batch_id)
        await self._backend.set(key, results, ttl or 1200)  # 20 min default

    async def invalidate_batch_cache(self, batch_id: str) -> bool:
        """Invalidate cached batch results.

        Args:
            batch_id: The batch operation ID

        Returns:
            True if invalidated, False if not found
        """
        key = generate_cache_key("batch:", batch_id)
        return await self._backend.delete(key)

    # Utility methods

    async def clear_all(self) -> None:
        """Clear all cached data."""
        await self._backend.clear()

    async def close(self) -> None:
        """Close the cache layer and release resources."""
        await self._backend.close()


def create_cache_layer(backend: str = "memory", **kwargs) -> CacheLayer:
    """Factory function to create a cache layer.

    Args:
        backend: Backend type ('memory' or 'redis')
        **kwargs: Backend-specific configuration

    Returns:
        A configured CacheLayer instance

    Example:
        # In-memory backend
        cache = create_cache_layer("memory", max_size=10000, ttl=300)

        # Redis backend
        cache = create_cache_layer(
            "redis",
            host="localhost",
            port=6379,
            db=0,
            password=None
        )
    """
    if backend == "memory":
        backend_instance = InMemoryCacheBackend(
            max_size=kwargs.get("max_size", 10000),
            ttl=kwargs.get("ttl", 300),
            key_prefix=kwargs.get("key_prefix", "netbox_dio:"),
        )
    elif backend == "redis":
        backend_instance = RedisCacheBackend(
            host=kwargs.get("host", "localhost"),
            port=kwargs.get("port", 6379),
            db=kwargs.get("db", 0),
            password=kwargs.get("password"),
            key_prefix=kwargs.get("key_prefix", "netbox_dio:"),
            max_connections=kwargs.get("max_connections", 10),
        )
    else:
        raise ValueError(f"Unknown backend: {backend}")

    return CacheLayer(backend_instance)
