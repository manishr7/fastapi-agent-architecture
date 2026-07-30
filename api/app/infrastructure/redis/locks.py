from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from redis.asyncio import Redis
from redis.exceptions import LockError, RedisError

from app.core.exceptions import ServiceUnavailableException

_DEFAULT_TTL_SECONDS = 30
_DEFAULT_BLOCKING_TIMEOUT_SECONDS = 10.0


@asynccontextmanager
async def acquire_lock(
    client: Redis,
    key: str,
    *,
    ttl_seconds: int = _DEFAULT_TTL_SECONDS,
    blocking_timeout_seconds: float = _DEFAULT_BLOCKING_TIMEOUT_SECONDS,
) -> AsyncIterator[None]:
    """Distributed mutual exclusion for one operation across all app instances.

    Fails closed, unlike `Cache`: if Redis is unreachable or the lock can't
    be acquired within `blocking_timeout_seconds`, raises
    `ServiceUnavailableException` rather than letting the caller proceed
    without the exclusivity guarantee it asked for. `ttl_seconds` bounds how
    long a crashed holder (killed pod, failed deploy) can block every other
    instance — the lock always expires on its own.
    """
    lock = client.lock(key, timeout=ttl_seconds, blocking_timeout=blocking_timeout_seconds)
    try:
        acquired = await lock.acquire()
    except RedisError as exc:
        raise ServiceUnavailableException(
            message="Distributed lock unavailable",
            code="LOCK_UNAVAILABLE",
            log_context={"dependency": "redis", "operation": "lock_acquire", "key": key},
        ) from exc
    if not acquired:
        raise ServiceUnavailableException(
            message="Could not acquire distributed lock",
            code="LOCK_UNAVAILABLE",
            log_context={"dependency": "redis", "operation": "lock_timeout", "key": key},
        )
    try:
        yield
    finally:
        # TTL already elapsed (or another process's release ran first) — the
        # TTL is exactly what guarantees no permanent deadlock here.
        with suppress(LockError):
            await lock.release()
