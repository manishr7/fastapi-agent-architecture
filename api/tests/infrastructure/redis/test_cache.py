import json
from unittest.mock import AsyncMock

import pytest
from redis.exceptions import RedisError

from app.infrastructure.redis.cache import Cache


@pytest.mark.asyncio
async def test_get_returns_deserialized_value_on_hit() -> None:
    client = AsyncMock()
    client.get.return_value = json.dumps({"a": 1})

    result = await Cache(client).get("key")

    assert result == {"a": 1}


@pytest.mark.asyncio
async def test_get_returns_none_on_miss() -> None:
    client = AsyncMock()
    client.get.return_value = None

    result = await Cache(client).get("key")

    assert result is None


@pytest.mark.asyncio
async def test_get_fails_open_on_redis_error() -> None:
    client = AsyncMock()
    client.get.side_effect = RedisError("connection refused")

    # Fails open: 22-redis.md — a cache-read failure must fall through to
    # the database, never fail the request. Returning None (a miss) is the
    # entire contract; it must never raise.
    result = await Cache(client).get("key")

    assert result is None


@pytest.mark.asyncio
async def test_set_serializes_value_with_ttl() -> None:
    client = AsyncMock()

    await Cache(client).set("key", {"a": 1}, ttl_seconds=30)

    client.set.assert_awaited_once_with("key", json.dumps({"a": 1}), ex=30)


@pytest.mark.asyncio
async def test_set_fails_open_on_redis_error() -> None:
    client = AsyncMock()
    client.set.side_effect = RedisError("connection refused")

    # Must not raise — same fail-open contract as get().
    await Cache(client).set("key", {"a": 1})


@pytest.mark.asyncio
async def test_delete_fails_open_on_redis_error() -> None:
    client = AsyncMock()
    client.delete.side_effect = RedisError("connection refused")

    await Cache(client).delete("key")


@pytest.mark.asyncio
async def test_invalidate_pattern_deletes_all_matched_keys() -> None:
    client = AsyncMock()

    async def scan_iter(match: str):
        for key in ("a:1", "a:2"):
            yield key

    client.scan_iter = scan_iter

    await Cache(client).invalidate_pattern("a:*")

    client.delete.assert_awaited_once_with("a:1", "a:2")


@pytest.mark.asyncio
async def test_invalidate_pattern_fails_open_on_redis_error() -> None:
    client = AsyncMock()

    async def scan_iter(match: str):
        raise RedisError("connection refused")
        yield  # pragma: no cover - makes this an async generator

    client.scan_iter = scan_iter

    await Cache(client).invalidate_pattern("a:*")
