"""Tests for cache backend implementations.

This module tests RedisCacheBackend and InMemoryCacheBackend.
"""

import pytest

from netbox_dio.caching.backends import (
    CacheMetrics,
    RedisCacheBackend,
    InMemoryCacheBackend,
    generate_cache_key,
)


class TestCacheMetrics:
    """Tests for the CacheMetrics dataclass."""

    def test_creation(self):
        """Test creating cache metrics."""
        metrics = CacheMetrics()
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.errors == 0
        assert metrics.set_ops == 0
        assert metrics.delete_ops == 0

    def test_hit_rate(self):
        """Test hit rate calculation."""
        metrics = CacheMetrics(hits=5, misses=5)
        assert metrics.hit_rate == 0.5

    def test_hit_rate_empty(self):
        """Test hit rate with no operations."""
        metrics = CacheMetrics()
        assert metrics.hit_rate == 0.0

    def test_hit_rate_all_hits(self):
        """Test hit rate with all hits."""
        metrics = CacheMetrics(hits=10, misses=0)
        assert metrics.hit_rate == 1.0

    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = CacheMetrics(hits=5, misses=3, errors=1, set_ops=10, delete_ops=2)
        data = metrics.to_dict()
        assert data["hits"] == 5
        assert data["misses"] == 3
        assert data["errors"] == 1
        assert data["set_ops"] == 10
        assert data["delete_ops"] == 2
        assert "hit_rate" in data


class TestGenerateCacheKey:
    """Tests for the generate_cache_key function."""

    def test_key_generation(self):
        """Test generating a cache key."""
        key = generate_cache_key("prefix:", "param1", "param2")
        assert key.startswith("prefix:")
        assert len(key) > len("prefix:")

    def test_consistent_generation(self):
        """Test that same parameters produce same key."""
        key1 = generate_cache_key("prefix:", "a", "b")
        key2 = generate_cache_key("prefix:", "a", "b")
        assert key1 == key2

    def different_parameters_different_keys(self):
        """Test that different parameters produce different keys."""
        key1 = generate_cache_key("prefix:", "a", "b")
        key2 = generate_cache_key("prefix:", "c", "d")
        assert key1 != key2


class TestInMemoryCacheBackend:
    """Tests for the InMemoryCacheBackend."""

    @pytest.fixture
    def backend(self):
        """Create an in-memory cache backend."""
        return InMemoryCacheBackend(max_size=100, ttl=300)

    async def test_set_and_get(self, backend):
        """Test setting and getting a value."""
        await backend.set("test_key", {"data": "test_value"})
        value = await backend.get("test_key")
        assert value == {"data": "test_value"}

    async def test_get_nonexistent(self, backend):
        """Test getting a non-existent key returns None."""
        value = await backend.get("nonexistent_key")
        assert value is None

    async def test_delete(self, backend):
        """Test deleting a key."""
        await backend.set("delete_key", "value")
        result = await backend.delete("delete_key")
        assert result is True
        value = await backend.get("delete_key")
        assert value is None

    async def test_delete_nonexistent(self, backend):
        """Test deleting a non-existent key returns False."""
        result = await backend.delete("nonexistent")
        assert result is False

    async def test_exists(self, backend):
        """Test checking if a key exists."""
        await backend.set("exists_key", "value")
        assert await backend.exists("exists_key") is True
        assert await backend.exists("nonexistent") is False

    async def test_clear(self, backend):
        """Test clearing all keys."""
        await backend.set("key1", "value1")
        await backend.set("key2", "value2")
        await backend.clear()
        assert await backend.get("key1") is None
        assert await backend.get("key2") is None

    async def test_ttl_expiration(self, backend):
        """Test that keys expire after TTL."""
        import time
        backend._ttl = 1  # 1 second TTL
        await backend.set("expire_key", "value")
        assert await backend.get("expire_key") == "value"
        time.sleep(1.5)
        assert await backend.get("expire_key") is None

    async def test_lru_eviction(self, backend):
        """Test LRU eviction when max_size is exceeded."""
        backend._max_size = 3
        await backend.set("key1", "value1")
        await backend.set("key2", "value2")
        await backend.set("key3", "value3")
        await backend.set("key4", "value4")  # Should evict key1
        assert await backend.get("key4") == "value4"
        assert await backend.get("key1") is None

    async def test_metrics_tracking(self, backend):
        """Test that metrics are tracked."""
        await backend.set("key1", "value1")
        await backend.get("key1")
        await backend.get("nonexistent")
        await backend.delete("key1")

        metrics = backend.metrics
        assert metrics.set_ops >= 1
        assert metrics.hits >= 1
        assert metrics.misses >= 1
        assert metrics.delete_ops >= 1


class TestInMemoryCacheBackendIntegration:
    """Integration tests for InMemoryCacheBackend."""

    @pytest.fixture
    def backend(self):
        """Create an in-memory cache backend."""
        return InMemoryCacheBackend(max_size=100, ttl=300)

    async def test_workflow(self, backend):
        """Test a complete cache workflow."""
        # Set values
        await backend.set("device:router1", {"name": "router1", "site": "site-a"})
        await backend.set("device:router2", {"name": "router2", "site": "site-b"})

        # Get values
        router1 = await backend.get("device:router1")
        assert router1 == {"name": "router1", "site": "site-a"}

        # Update value
        await backend.set("device:router1", {"name": "router1", "site": "updated-site"})
        router1 = await backend.get("device:router1")
        assert router1["site"] == "updated-site"

        # Delete value
        await backend.delete("device:router1")
        assert await backend.get("device:router1") is None
