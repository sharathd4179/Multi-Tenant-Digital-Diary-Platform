"""
Redis caching utilities for improving performance.
"""
import json
from typing import Any, Optional

import redis
from ..core.config import settings


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client. Returns None if Redis is not configured."""
    if not settings.redis_url:
        return None
    try:
        return redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        return None


def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache.
    
    Args:
        key: Cache key.
    Returns:
        Cached value or None if not found.
    """
    client = get_redis_client()
    if not client:
        return None
    
    try:
        value = client.get(key)
        if value:
            return json.loads(value)
    except Exception:
        pass
    return None


def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set a value in cache.
    
    Args:
        key: Cache key.
        value: Value to cache (must be JSON serializable).
        ttl: Time to live in seconds (default: 1 hour).
    Returns:
        True if successful, False otherwise.
    """
    client = get_redis_client()
    if not client:
        return False
    
    try:
        client.setex(key, ttl, json.dumps(value))
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:
    """Delete a key from cache.
    
    Args:
        key: Cache key to delete.
    Returns:
        True if successful, False otherwise.
    """
    client = get_redis_client()
    if not client:
        return False
    
    try:
        client.delete(key)
        return True
    except Exception:
        return False


def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "search:*").
    Returns:
        Number of keys deleted.
    """
    client = get_redis_client()
    if not client:
        return 0
    
    try:
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
    except Exception:
        pass
    return 0


def get_cache_key(prefix: str, **kwargs) -> str:
    """Generate a cache key from prefix and parameters.
    
    Args:
        prefix: Key prefix (e.g., "search").
        **kwargs: Key-value pairs to include in the key.
    Returns:
        Cache key string.
    """
    parts = [prefix]
    for key, value in sorted(kwargs.items()):
        if value is not None:
            parts.append(f"{key}:{value}")
    return ":".join(parts)

