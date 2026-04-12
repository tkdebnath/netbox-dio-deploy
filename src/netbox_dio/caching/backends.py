"""Cache backend implementations.

This module provides concrete implementations for cache backends:
RedisCacheBackend and InMemoryCacheBackend.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
from collections import OrderedDict


@dataclass
class CacheMetrics:
    """Metrics for cache operations.

    Tracks performance statistics for cache operations.

    Parameters:
        hits: Number of successful cache hits
        misses: Number of cache misses
        errors: Number of errors encountered
        set_ops: Number of set operations
        delete_ops: Number of delete operations
    """

    hits: int = 0
    misses: int = 0
    errors: int = 0
    set_ops: int = 0
    delete_ops: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate as a percentage."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "set_ops": self.set_ops,
            "delete_ops": self.delete_ops,
            "hit_rate": self.hit_rate,
        }


class CacheBackend(ABC):
    """Abstract base class for cache backends.

    Defines the interface that all cache backends must implement.
    """

    def __init__(self, key_prefix: str = "netbox_dio:") -> None:
        """Initialize the cache backend.

        Parameters:
            key_prefix: Prefix to prepend to all cache keys (default: "netbox_dio:")
        """
        self.key_prefix = key_prefix
        self._metrics = CacheMetrics()

    @property
    def metrics(self) -> CacheMetrics:
        """Get cache operation metrics."""
        return self._metrics

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value, or None if not found
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl: Time-to-live in seconds (default: 300)
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value from the cache.

        Args:
            key: The cache key

        Returns:
            True if the key was deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.

        Args:
            key: The cache key

        Returns:
            True if the key exists, False otherwise
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all values from the cache."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close any resources used by the cache backend."""
        pass

    def _normalize_key(self, key: str) -> str:
        """Normalize a key by adding the prefix.

        Args:
            key: The raw key

        Returns:
            The normalized key with prefix
        """
        return f"{self.key_prefix}{key}"

    def _sanitize_key(self, key: str) -> str:
        """Sanitize a key to remove invalid characters.

        Args:
            key: The key to sanitize

        Returns:
            A sanitized key
        """
        # Remove any characters that could cause issues
        return "".join(c for c in key if c.isalnum() or c in ("_", "-", ":"))


class RedisCacheBackend(CacheBackend):
    """Redis-backed cache implementation.

    Uses Redis as the backing store for caching operations.

    Attributes:
        _client: Redis client instance
        _key_prefix: Prefix for all cache keys
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = "netbox_dio:",
        max_connections: int = 10,
    ) -> None:
        """Initialize the Redis cache backend.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            key_prefix: Prefix for all cache keys
            max_connections: Maximum number of Redis connections
        """
        super().__init__(key_prefix)
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._max_connections = max_connections
        self._client = None
        self._key_prefix = key_prefix

    async def _get_client(self):
        """Get or create Redis client."""
        if self._client is None:
            import redis.asyncio as redis

            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                max_connections=self._max_connections,
                decode_responses=True,
            )
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis cache.

        Args:
            key: The cache key

        Returns:
            The cached value, or None if not found
        """
        try:
            client = await self._get_client()
            normalized_key = self._normalize_key(key)
            value = await client.get(normalized_key)

            if value is None:
                self._metrics.misses += 1
                return None

            self._metrics.hits += 1
            return value
        except Exception as e:
            self._metrics.errors += 1
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set a value in Redis cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl: Time-to-live in seconds
        """
        try:
            client = await self._get_client()
            normalized_key = self._normalize_key(key)

            # Serialize value to JSON
            import json

            serialized = json.dumps(value)

            await client.setex(normalized_key, ttl, serialized)
            self._metrics.set_ops += 1
        except Exception as e:
            self._metrics.errors += 1

    async def delete(self, key: str) -> bool:
        """Delete a value from Redis cache.

        Args:
            key: The cache key

        Returns:
            True if deleted, False if not found
        """
        try:
            client = await self._get_client()
            normalized_key = self._normalize_key(key)
            result = await client.delete(normalized_key)
            self._metrics.delete_ops += 1
            return result > 0
        except Exception as e:
            self._metrics.errors += 1
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis cache.

        Args:
            key: The cache key

        Returns:
            True if exists, False otherwise
        """
        try:
            client = await self._get_client()
            normalized_key = self._normalize_key(key)
            result = await client.exists(normalized_key)
            return result > 0
        except Exception as e:
            self._metrics.errors += 1
            return False

    async def clear(self) -> None:
        """Clear all values from Redis cache."""
        try:
            client = await self._get_client()
            # Find and delete all keys with our prefix
            pattern = f"{self._normalize_key('*')}"
            cursor = 0
            while True:
                cursor, keys = await client.scan(cursor, match=pattern, count=100)
                if keys:
                    await client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            self._metrics.errors += 1

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None


class InMemoryCacheBackend(CacheBackend):
    """In-memory cache implementation using LRU eviction.

    Uses an OrderedDict for O(1) LRU eviction when max_size is exceeded.

    Attributes:
        _cache: OrderedDict for key-value storage
        _ttl: Default TTL in seconds
        _max_size: Maximum number of items
        _creation_times: Dict tracking when items were added
    """

    def __init__(
        self, max_size: int = 10000, ttl: int = 300, key_prefix: str = "netbox_dio:"
    ) -> None:
        """Initialize the in-memory cache backend.

        Args:
            max_size: Maximum number of items to store
            ttl: Default time-to-live in seconds
            key_prefix: Prefix for all cache keys
        """
        super().__init__(key_prefix)
        self._cache: OrderedDict = OrderedDict()
        self._ttl = ttl
        self._max_size = max_size
        self._creation_times: dict[str, float] = {}

    def _evict_if_needed(self) -> None:
        """Evict oldest items if cache is full."""
        while len(self._cache) >= self._max_size:
            # Pop the oldest item (first item in OrderedDict)
            oldest_key = next(iter(self._cache))
            self._cache.popitem(last=False)
            if oldest_key in self._creation_times:
                del self._creation_times[oldest_key]

    def _is_expired(self, key: str) -> bool:
        """Check if a key has expired.

        Args:
            key: The cache key

        Returns:
            True if expired, False otherwise
        """
        if key not in self._creation_times:
            return True

        elapsed = time.time() - self._creation_times[key]
        return elapsed > self._ttl

    def _cleanup_expired(self) -> None:
        """Remove expired items."""
        expired = [k for k in self._creation_times.keys() if self._is_expired(k)]
        for key in expired:
            if key in self._cache:
                del self._cache[key]
            if key in self._creation_times:
                del self._creation_times[key]

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from in-memory cache.

        Args:
            key: The cache key

        Returns:
            The cached value, or None if not found or expired
        """
        normalized_key = self._normalize_key(key)

        # Cleanup expired items periodically
        if len(self._creation_times) > 1000:
            self._cleanup_expired()

        if normalized_key not in self._cache:
            self._metrics.misses += 1
            return None

        if self._is_expired(normalized_key):
            self._cleanup_expired()
            self._metrics.misses += 1
            return None

        # Move to end for LRU tracking
        self._cache.move_to_end(normalized_key)
        self._metrics.hits += 1
        return self._cache[normalized_key]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in in-memory cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        self._evict_if_needed()

        normalized_key = self._normalize_key(key)
        self._cache[normalized_key] = value
        self._creation_times[normalized_key] = time.time()
        self._metrics.set_ops += 1

    async def delete(self, key: str) -> bool:
        """Delete a value from in-memory cache.

        Args:
            key: The cache key

        Returns:
            True if deleted, False if not found
        """
        normalized_key = self._normalize_key(key)

        if normalized_key not in self._cache:
            self._metrics.delete_ops += 1
            return False

        del self._cache[normalized_key]
        if normalized_key in self._creation_times:
            del self._creation_times[normalized_key]
        self._metrics.delete_ops += 1
        return True

    async def exists(self, key: str) -> bool:
        """Check if a key exists in in-memory cache.

        Args:
            key: The cache key

        Returns:
            True if exists and not expired, False otherwise
        """
        normalized_key = self._normalize_key(key)

        if normalized_key not in self._cache:
            return False

        if self._is_expired(normalized_key):
            self._cleanup_expired()
            return False

        self._cache.move_to_end(normalized_key)
        return True

    async def clear(self) -> None:
        """Clear all values from in-memory cache."""
        self._cache.clear()
        self._creation_times.clear()

    async def close(self) -> None:
        """Close the in-memory cache (no-op for in-memory)."""
        pass


def generate_cache_key(prefix: str, *params: str) -> str:
    """Generate a consistent cache key from parameters.

    Args:
        prefix: The key prefix
        *params: Parameters to include in the key

    Returns:
        A hash-based cache key string
    """
    key_params = ":".join(params)
    hash_value = hashlib.md5(key_params.encode()).hexdigest()
    return f"{prefix}{hash_value}"
