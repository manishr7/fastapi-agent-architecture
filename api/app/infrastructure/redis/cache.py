import json
from typing import Any

import structlog
from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = structlog.get_logger(__name__)


class Cache:
    """Thin caching wrapper over Redis. Fails open: a Redis outage degrades

    to cache misses (more DB load) rather than failing the request — Redis
    here is a performance optimization, never the source of truth. Called
    directly by Use Cases, not Repositories (`08-repositories.md` keeps
    repositories cache-agnostic).
    """

    def __init__(self, client: Redis) -> None:
        self._client = client

    async def get(self, key: str) -> Any | None:
        try:
            raw = await self._client.get(key)
        except RedisError as exc:
            logger.warning("cache_unavailable", operation="get", key=key, error=str(exc))
            return None
        if raw is None:
            return None
        return json.loads(raw)

    async def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        try:
            await self._client.set(key, json.dumps(value), ex=ttl_seconds)
        except RedisError as exc:
            logger.warning("cache_unavailable", operation="set", key=key, error=str(exc))

    async def delete(self, key: str) -> None:
        try:
            await self._client.delete(key)
        except RedisError as exc:
            logger.warning("cache_unavailable", operation="delete", key=key, error=str(exc))

    async def invalidate_pattern(self, pattern: str) -> None:
        try:
            keys = [key async for key in self._client.scan_iter(match=pattern)]
            if keys:
                await self._client.delete(*keys)
        except RedisError as exc:
            logger.warning(
                "cache_unavailable", operation="invalidate_pattern", key=pattern, error=str(exc)
            )
