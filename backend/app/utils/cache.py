"""
Prediction cache with Redis backend and in-memory dict fallback.
Predictions are cached for CACHE_TTL seconds to avoid redundant model calls.
"""
import json
from loguru import logger

# In-memory fallback cache (used when Redis is unavailable)
_memory_cache: dict = {}


async def get_cached(key: str):
    """
    Retrieve a cached prediction by key.

    Tries Redis first, falls back to in-memory dict.

    Args:
        key: Cache key (MD5 hash of request JSON).

    Returns:
        Cached dict or None if not found.
    """
    # Try Redis
    try:
        import redis.asyncio as aioredis
        from app.config import settings
        r = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
        val = await r.get(key)
        await r.aclose()
        if val:
            return json.loads(val)
    except Exception:
        pass  # Redis unavailable — use memory cache

    return _memory_cache.get(key)


async def set_cached(key: str, value: dict, ttl: int = 3600) -> None:
    """
    Store a prediction result in cache.

    Args:
        key: Cache key.
        value: Dict to cache (must be JSON-serializable).
        ttl: Time-to-live in seconds.
    """
    # Try Redis
    try:
        import redis.asyncio as aioredis
        from app.config import settings
        r = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
        await r.setex(key, ttl, json.dumps(value))
        await r.aclose()
        return
    except Exception:
        pass  # Redis unavailable — fall back to memory

    # Memory cache (no TTL enforcement — simple dict)
    _memory_cache[key] = value

    # Prevent unbounded growth
    if len(_memory_cache) > 10_000:
        oldest_keys = list(_memory_cache.keys())[:1000]
        for k in oldest_keys:
            _memory_cache.pop(k, None)


def clear_cache() -> None:
    """Clear the in-memory cache (used in tests)."""
    _memory_cache.clear()
