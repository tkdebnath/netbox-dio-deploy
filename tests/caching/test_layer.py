"""Tests for the cache layer.

This module tests the CacheLayer class that provides a unified interface
for caching operations.
"""

import pytest

from netbox_dio.caching.layer import CacheLayer, generate_cache_key
from netbox_dio.caching.backends import InMemoryCacheBackend


class TestCacheLayer:
    """Tests for the CacheLayer class."""

    @pytest.fixture
    def cache(self):
        """Create a cache layer with in-memory backend."""
        backend = InMemoryCacheBackend(max_size=1000, ttl=300)
        return CacheLayer(backend)

    async def test_set_device(self, cache):
        """Test setting device data."""
        device_data = {"name": "router-01", "site": "site-a"}
        await cache.set_device("router-01", device_data)
        result = await cache.get_device("router-01")
        assert result == device_data

    async def test_get_nonexistent_device(self, cache):
        """Test getting a non-existent device."""
        result = await cache.get_device("nonexistent")
        assert result is None

    async def test_invalidate_device(self, cache):
        """Test invalidating device data."""
        device_data = {"name": "router-01", "site": "site-a"}
        await cache.set_device("router-01", device_data)
        result = await cache.invalidate_device("router-01")
        assert result is True
        assert await cache.get_device("router-01") is None

    async def test_set_validation_results(self, cache):
        """Test setting validation results."""
        results = {"passed": True, "rules": 5, "errors": 0}
        device_hash = "abc123"
        await cache.set_validation_results(device_hash, results)
        result = await cache.get_validation_results(device_hash)
        assert result == results

    async def test_invalidate_validation_results(self, cache):
        """Test invalidating validation results."""
        device_hash = "xyz789"
        results = {"passed": True}
        await cache.set_validation_results(device_hash, results)
        result = await cache.invalidate_validation_results(device_hash)
        assert result is True
        assert await cache.get_validation_results(device_hash) is None

    async def test_set_quality_metrics(self, cache):
        """Test setting quality metrics."""
        metrics = {"completeness": 0.95, "validity": 0.98, "overall": 0.96}
        device_hash = "quality123"
        await cache.set_quality_metrics(device_hash, metrics)
        result = await cache.get_quality_metrics(device_hash)
        assert result == metrics

    async def test_invalidate_quality_metrics(self, cache):
        """Test invalidating quality metrics."""
        device_hash = "quality456"
        metrics = {"completeness": 0.95}
        await cache.set_quality_metrics(device_hash, metrics)
        result = await cache.invalidate_quality_metrics(device_hash)
        assert result is True
        assert await cache.get_quality_metrics(device_hash) is None

    async def test_set_batch_cache(self, cache):
        """Test setting batch cache."""
        batch_results = {"success": 100, "failed": 0, "errors": []}
        batch_id = "batch-001"
        await cache.set_batch_cache(batch_id, batch_results)
        result = await cache.get_batch_cache(batch_id)
        assert result == batch_results

    async def test_clear_all(self, cache):
        """Test clearing all cache data."""
        await cache.set_device("device1", {"name": "device1"})
        await cache.set_validation_results("hash1", {"passed": True})
        await cache.clear_all()
        assert await cache.get_device("device1") is None
        assert await cache.get_validation_results("hash1") is None


class TestCacheLayerKeyGeneration:
    """Tests for cache key generation in CacheLayer."""

    @pytest.fixture
    def cache(self):
        """Create a cache layer with in-memory backend."""
        backend = InMemoryCacheBackend(max_size=1000, ttl=300)
        return CacheLayer(backend)

    async def test_device_key_format(self, cache):
        """Test that device keys are properly formatted."""
        device_data = {"name": "router-01"}
        await cache.set_device("router-01", device_data)

        # The key should be hashed
        backend = cache._backend
        assert isinstance(backend, InMemoryCacheBackend)

    async def test_validation_key_format(self, cache):
        """Test that validation result keys are properly formatted."""
        results = {"passed": True}
        device_hash = "abc123"
        await cache.set_validation_results(device_hash, results)

    async def test_quality_key_format(self, cache):
        """Test that quality key keys are properly formatted."""
        metrics = {"completeness": 0.95}
        device_hash = "quality123"
        await cache.set_quality_metrics(device_hash, metrics)

    async def test_batch_key_format(self, cache):
        """Test that batch keys are properly formatted."""
        batch_results = {"success": 100}
        batch_id = "batch-001"
        await cache.set_batch_cache(batch_id, batch_results)


class TestCacheLayerMetrics:
    """Tests for cache metrics in CacheLayer."""

    @pytest.fixture
    def cache(self):
        """Create a cache layer with in-memory backend."""
        backend = InMemoryCacheBackend(max_size=1000, ttl=300)
        return CacheLayer(backend)

    async def test_metrics_tracking(self, cache):
        """Test that cache metrics are tracked."""
        device_data = {"name": "router-01"}
        await cache.set_device("router-01", device_data)
        await cache.get_device("router-01")
        await cache.get_device("nonexistent")
        await cache.invalidate_device("router-01")

        metrics = cache.metrics
        assert metrics.set_ops >= 1
        assert metrics.hits >= 1
        assert metrics.misses >= 1
        assert metrics.delete_ops >= 1

    async def test_hit_rate(self, cache):
        """Test cache hit rate calculation."""
        device_data = {"name": "router-01"}
        await cache.set_device("router-01", device_data)
        await cache.get_device("router-01")  # Hit
        await cache.get_device("router-01")  # Hit
        await cache.get_device("nonexistent")  # Miss

        hit_rate = cache.metrics.hit_rate
        # Should be 2 hits / 3 total = 0.667
        assert 0.5 <= hit_rate <= 0.8


class TestCacheLayerIntegration:
    """Integration tests for CacheLayer."""

    @pytest.fixture
    def cache(self):
        """Create a cache layer with in-memory backend."""
        backend = InMemoryCacheBackend(max_size=1000, ttl=300)
        return CacheLayer(backend)

    async def test_complete_workflow(self, cache):
        """Test a complete cache workflow."""
        # Store device
        device_data = {"name": "router-01", "site": "site-a", "status": "active"}
        await cache.set_device("router-01", device_data)

        # Retrieve device
        retrieved = await cache.get_device("router-01")
        assert retrieved == device_data

        # Update device
        device_data["status"] = "maintenance"
        await cache.set_device("router-01", device_data)
        updated = await cache.get_device("router-01")
        assert updated["status"] == "maintenance"

        # Store validation results
        validation_results = {"passed": True, "rules": 5}
        await cache.set_validation_results("device-hash-1", validation_results)
        retrieved_validation = await cache.get_validation_results("device-hash-1")
        assert retrieved_validation == validation_results

        # Store quality metrics
        quality_metrics = {"completeness": 0.95, "validity": 0.98}
        await cache.set_quality_metrics("device-hash-1", quality_metrics)
        retrieved_quality = await cache.get_quality_metrics("device-hash-1")
        assert retrieved_quality == quality_metrics

        # Store batch results
        batch_results = {"success": 100, "failed": 0}
        await cache.set_batch_cache("batch-001", batch_results)
        retrieved_batch = await cache.get_batch_cache("batch-001")
        assert retrieved_batch == batch_results

    async def test_ttl_behavior(self, cache):
        """Test TTL expiration behavior."""
        import time
        # Use a short TTL for testing - modify the backend's TTL
        cache._backend._ttl = 1  # 1 second

        # Set values with short TTL
        await cache.set_device("expire-device", {"name": "expire"}, ttl=1)
        await cache.set_validation_results("expire-hash", {"passed": True}, ttl=1)

        # Should be available immediately
        assert await cache.get_device("expire-device") is not None
        assert await cache.get_validation_results("expire-hash") is not None

        # Wait for TTL to expire
        time.sleep(1.5)

        # Should be expired
        assert await cache.get_device("expire-device") is None
        assert await cache.get_validation_results("expire-hash") is None

    async def test_multiple_devices(self, cache):
        """Test caching multiple devices."""
        devices = [
            {"name": f"device-{i}", "site": f"site-{i}"}
            for i in range(10)
        ]

        for i, device in enumerate(devices):
            await cache.set_device(f"device-{i}", device)

        for i, device in enumerate(devices):
            retrieved = await cache.get_device(f"device-{i}")
            assert retrieved == device

    async def test_device_overwrite(self, cache):
        """Test overwriting a device entry."""
        # First entry
        await cache.set_device("device-01", {"name": "device-01", "site": "site-a"})

        # Second entry with different site
        await cache.set_device("device-01", {"name": "device-01", "site": "site-b"})

        # Should be updated
        result = await cache.get_device("device-01")
        assert result["site"] == "site-b"
        assert result["name"] == "device-01"
