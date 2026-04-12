"""Shared test fixtures for caching scenarios.

This module provides common test data structures for testing the caching system.
"""

import pytest

from netbox_dio.caching.backends import InMemoryCacheBackend, RedisCacheBackend
from netbox_dio.caching.layer import CacheLayer


def sample_device_dict():
    """Create a sample device dictionary for caching.

    Returns:
        Dictionary with sample device data
    """
    return {
        "name": "router-01",
        "site": "site-a",
        "device_type": "cisco-9300",
        "role": "core-router",
        "serial": "SN123456789",
        "asset_tag": "AT-001",
        "platform": "Cisco IOS XE",
        "status": "active",
        "custom_fields": {"location": "rack-a1"},
    }


def sample_validation_results():
    """Create sample validation results.

    Returns:
        Dictionary with validation results
    """
    return {
        "passed": True,
        "rules_executed": 5,
        "errors": [],
        "warnings": [],
        "info_messages": [],
    }


async def cache_layer_with_memory():
    """Create a cache layer with in-memory backend.

    Returns:
        CacheLayer instance
    """
    backend = InMemoryCacheBackend(max_size=10000, ttl=300)
    return CacheLayer(backend)


async def cache_layer_with_redis():
    """Create a cache layer with Redis backend.

    Returns:
        CacheLayer instance (will return None if Redis not available)
    """
    try:
        backend = RedisCacheBackend(host="localhost", port=6379, db=0)
        return CacheLayer(backend)
    except Exception:
        return None


class CacheFixtures:
    """Fixture class for cache testing."""

    @staticmethod
    def create_in_memory_cache():
        """Create an in-memory cache layer.

        Returns:
            CacheLayer instance
        """
        backend = InMemoryCacheBackend(max_size=10000, ttl=300)
        return CacheLayer(backend)

    @staticmethod
    def sample_device(name: str = "test-device"):
        """Create a sample device dictionary.

        Args:
            name: Device name

        Returns:
            Device dictionary
        """
        return {
            "name": name,
            "site": "site-a",
            "device_type": "cisco-9300",
            "role": "core-router",
            "serial": f"SN-{name}",
            "asset_tag": f"AT-{name}",
            "platform": "Cisco IOS XE",
            "status": "active",
        }

    @staticmethod
    def sample_validation(device_name: str = "test-device"):
        """Create sample validation results.

        Args:
            device_name: Device name

        Returns:
            Validation results dictionary
        """
        return {
            "passed": True,
            "rules_executed": 5,
            "errors": [],
            "warnings": [],
            "info_messages": [],
            "device_name": device_name,
        }

    @staticmethod
    def sample_quality(device_name: str = "test-device"):
        """Create sample quality metrics.

        Args:
            device_name: Device name

        Returns:
            Quality metrics dictionary
        """
        return {
            "device_name": device_name,
            "completeness_score": 0.95,
            "validity_score": 0.98,
            "overall_score": 0.96,
            "error_count": 0,
            "warning_count": 2,
            "info_count": 3,
        }

    @staticmethod
    def sample_batch_results(batch_id: str = "batch-001"):
        """Create sample batch results.

        Args:
            batch_id: Batch ID

        Returns:
            Batch results dictionary
        """
        return {
            "batch_id": batch_id,
            "total": 100,
            "success": 100,
            "failed": 0,
            "errors": [],
            "timing_ms": 1234.56,
            "throughput_sps": 81.0,
        }
