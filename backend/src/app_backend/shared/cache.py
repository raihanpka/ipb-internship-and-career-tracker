import json
import os
from typing import Any, Optional

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/2")
ANALYTICS_CACHE_TTL = 0  # Real-time (0 menit) untuk presentasi


_redis_client = None
_redis_offline = False


def _client() -> Optional[redis.Redis]:
    global _redis_client, _redis_offline
    if _redis_offline:
        return None
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
            )
            # Test connection to fail fast if offline
            _redis_client.ping()
        except Exception:
            print(f"Redis is offline at {REDIS_URL}. Caching is disabled to prevent blocking Uvicorn threads.")
            _redis_offline = True
            _redis_client = None
    return _redis_client


def cache_get(key: str) -> Optional[Any]:
    try:
        client = _client()
        if client is None:
            return None
        data = client.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: int = ANALYTICS_CACHE_TTL) -> None:
    try:
        client = _client()
        if client is None:
            return
        client.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


def cache_delete(key: str) -> None:
    try:
        client = _client()
        if client is None:
            return
        client.delete(key)
    except Exception:
        pass


def cache_delete_pattern(pattern: str) -> None:
    """Hapus semua key yang cocok dengan pattern wildcard (misal 'vacancies:list:*')."""
    try:
        client = _client()
        if client is None:
            return
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
    except Exception:
        pass


def cache_ttl(key: str) -> int:
    """Kembalikan TTL key dalam detik, atau -2 jika tidak ada."""
    try:
        client = _client()
        if client is None:
            return -2
        return client.ttl(key)
    except Exception:
        return -2
