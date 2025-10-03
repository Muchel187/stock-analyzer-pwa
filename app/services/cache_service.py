"""
Multi-Level Cache Service
L1: Redis (fast, volatile)
L2: Database (persistent, medium speed)
L3: Mock Data (fallback)
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)

# Try to import Redis, fallback to simple dict cache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")


class CacheService:
    """Multi-level caching service"""

    # TTL Constants (in seconds)
    TTL_LIVE_QUOTE = 300         # 5 minutes
    TTL_HISTORICAL = 3600        # 1 hour
    TTL_FUNDAMENTALS = 86400     # 1 day
    TTL_AI_ANALYSIS = 604800     # 1 week
    TTL_NEWS = 1800              # 30 minutes

    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache

        if REDIS_AVAILABLE:
            try:
                import os
                redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using memory cache")
                self.redis_client = None

    def get(self, key: str, ttl_level: str = 'quote') -> Optional[Any]:
        """
        Get data from multi-level cache

        Args:
            key: Cache key
            ttl_level: Type of data (quote, historical, fundamentals, ai)

        Returns:
            Cached data or None
        """
        # L1: Redis Cache
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    logger.debug(f"Cache HIT (Redis): {key}")
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Redis get error: {e}")

        # L1b: Memory Cache (fallback)
        if key in self.memory_cache:
            cached_data, expires_at = self.memory_cache[key]
            if expires_at > datetime.now(timezone.utc):
                logger.debug(f"Cache HIT (Memory): {key}")
                return cached_data
            else:
                # Expired, remove
                del self.memory_cache[key]

        # L2: Database Cache (handled by StockCache model)
        # This is queried separately in service layers

        logger.debug(f"Cache MISS: {key}")
        return None

    def set(self, key: str, data: Any, ttl_level: str = 'quote'):
        """
        Set data in multi-level cache

        Args:
            key: Cache key
            data: Data to cache
            ttl_level: Type of data for TTL selection
        """
        # Determine TTL based on level
        ttl_map = {
            'quote': self.TTL_LIVE_QUOTE,
            'historical': self.TTL_HISTORICAL,
            'fundamentals': self.TTL_FUNDAMENTALS,
            'ai': self.TTL_AI_ANALYSIS,
            'news': self.TTL_NEWS
        }
        ttl = ttl_map.get(ttl_level, self.TTL_LIVE_QUOTE)

        # L1: Redis Cache
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(data, default=str)
                )
                logger.debug(f"Cached in Redis: {key} (TTL: {ttl}s)")
            except Exception as e:
                logger.error(f"Redis set error: {e}")

        # L1b: Memory Cache (fallback)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        self.memory_cache[key] = (data, expires_at)
        logger.debug(f"Cached in Memory: {key}")

        # L2: Database Cache (handled by StockCache model in service layers)

    def delete(self, key: str):
        """Delete from all cache levels"""
        # Redis
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")

        # Memory
        if key in self.memory_cache:
            del self.memory_cache[key]

    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern (Redis only)"""
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} keys matching '{pattern}'")
            except Exception as e:
                logger.error(f"Redis pattern delete error: {e}")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        stats = {
            'redis_available': self.redis_client is not None,
            'memory_cache_size': len(self.memory_cache)
        }

        if self.redis_client:
            try:
                info = self.redis_client.info('stats')
                stats['redis_keys'] = self.redis_client.dbsize()
                stats['redis_hits'] = info.get('keyspace_hits', 0)
                stats['redis_misses'] = info.get('keyspace_misses', 0)
                if stats['redis_hits'] + stats['redis_misses'] > 0:
                    stats['redis_hit_rate'] = stats['redis_hits'] / (stats['redis_hits'] + stats['redis_misses'])
            except Exception as e:
                logger.error(f"Error getting Redis stats: {e}")

        return stats


# Global cache instance
_cache_instance = None


def get_cache() -> CacheService:
    """Get global cache instance (singleton)"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance


def cached(ttl_level: str = 'quote', key_prefix: str = ''):
    """
    Decorator for caching function results

    Usage:
        @cached(ttl_level='quote', key_prefix='stock')
        def get_stock_quote(ticker):
            # ... expensive API call
            return data
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ':'.join(key_parts)

            # Try cache first
            cache = get_cache()
            cached_data = cache.get(cache_key, ttl_level)
            if cached_data is not None:
                return cached_data

            # Cache miss, call function
            result = func(*args, **kwargs)

            # Cache result
            if result is not None:
                cache.set(cache_key, result, ttl_level)

            return result
        return wrapper
    return decorator


# Cleanup function for old memory cache entries
def cleanup_memory_cache():
    """Remove expired entries from memory cache"""
    cache = get_cache()
    now = datetime.now(timezone.utc)
    expired_keys = [
        key for key, (_, expires_at) in cache.memory_cache.items()
        if expires_at <= now
    ]
    for key in expired_keys:
        del cache.memory_cache[key]
    if expired_keys:
        logger.info(f"Cleaned up {len(expired_keys)} expired memory cache entries")
