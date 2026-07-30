from unittest.mock import AsyncMock, MagicMock

import pytest
from redis.exceptions import LockError, RedisError

from app.core.exceptions import ServiceUnavailableException
from app.infrastructure.redis.locks import acquire_lock


def _client_with_lock(
    *, acquired: bool = True, acquire_error: Exception | None = None
) -> MagicMock:
    lock = MagicMock()
    lock.acquire = AsyncMock(side_effect=acquire_error, return_value=acquired)
    lock.release = AsyncMock()
    client = MagicMock()
    client.lock.return_value = lock
    return client


@pytest.mark.asyncio
async def test_acquire_lock_yields_and_releases_on_success() -> None:
    client = _client_with_lock(acquired=True)

    async with acquire_lock(client, "key"):
        pass

    client.lock.return_value.release.assert_awaited_once()


@pytest.mark.asyncio
async def test_acquire_lock_fails_closed_on_redis_error() -> None:
    client = _client_with_lock(acquire_error=RedisError("connection refused"))

    with pytest.raises(ServiceUnavailableException) as exc_info:
        async with acquire_lock(client, "key"):
            pass  # pragma: no cover - must not be reached

    assert exc_info.value.code == "LOCK_UNAVAILABLE"
    assert exc_info.value.log_context["operation"] == "lock_acquire"


@pytest.mark.asyncio
async def test_acquire_lock_fails_closed_on_timeout() -> None:
    # acquire() returning False (no exception) means the blocking_timeout
    # elapsed without ever acquiring the lock — distinct from a Redis error,
    # but the same fail-closed contract: never let the caller proceed
    # without the exclusivity guarantee it asked for (22-redis.md).
    client = _client_with_lock(acquired=False)

    with pytest.raises(ServiceUnavailableException) as exc_info:
        async with acquire_lock(client, "key"):
            pass  # pragma: no cover - must not be reached

    assert exc_info.value.code == "LOCK_UNAVAILABLE"
    assert exc_info.value.log_context["operation"] == "lock_timeout"


@pytest.mark.asyncio
async def test_acquire_lock_suppresses_release_failure() -> None:
    # The TTL is what actually guarantees no permanent deadlock — a failed
    # release (e.g. because the TTL already elapsed) must not raise and
    # must not mask whatever happened inside the `async with` block.
    client = _client_with_lock(acquired=True)
    client.lock.return_value.release = AsyncMock(side_effect=LockError("already released"))

    async with acquire_lock(client, "key"):
        pass
