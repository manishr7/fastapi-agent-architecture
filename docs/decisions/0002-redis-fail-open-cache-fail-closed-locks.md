# ADR-0002: Redis — cache fails open, locks fail closed

## Context

This project runs multiple horizontally-scaled app instances against a
**single** Redis instance (no Sentinel/Cluster). A Redis outage has to
degrade the specific operations that depend on it — not take the whole
fleet out of rotation at once. But Redis is used for two genuinely
different jobs (caching and distributed locking), and a Redis failure means
something different for each one.

## Decision

Two different failure postures, not one uniform policy:

- **`Cache`** (`cache.py`) catches `redis.exceptions.RedisError`
  internally, logs once at WARNING, and returns a miss / no-op. It never
  raises.
- **`acquire_lock`** (`locks.py`) fails closed: if Redis is unreachable or
  the lock isn't acquired within `blocking_timeout_seconds`, it raises
  `ServiceUnavailableException` rather than letting the caller proceed
  without the exclusivity guarantee it asked for.

`/api/v6/ready` deliberately does **not** check Redis at all.

## Why

Redis-as-cache is a pure performance optimization — the database remains
the source of truth, so a cache-read failure can safely fall through to a
real database query. Correctness doesn't change, only latency. Failing the
whole request because the cache was unreachable would be strictly worse
than just being a bit slower.

Redis-as-lock is not a performance optimization — the lock exists
specifically to guarantee mutual exclusion under horizontal scaling. If
Redis is unreachable, the caller cannot know whether that exclusivity
guarantee holds. Proceeding anyway (treating the lock the same way as the
cache) would silently reintroduce the exact race condition the lock exists
to prevent. Failing closed here is the only choice that preserves the
guarantee the caller asked for.

This same asymmetry is why `/ready` skips Redis: every pod shares the one
Redis instance, so wiring it into readiness would fail the identical check
on every pod simultaneously the moment Redis blips, zeroing the entire
fleet's traffic over exactly the kind of transient failure the fail-open
cache path is designed to absorb without incident.

## Rejected or deferred alternatives

- **One uniform failure policy for all Redis operations.** Rejected as too
  coarse: uniform fail-open would let locks silently no-op (defeating their
  purpose); uniform fail-closed would fail the whole app over a cache blip
  that shouldn't matter.
- **Redis-backed rate limiting, built now.** Deferred, not rejected — no
  `rate_limit.py` exists yet (`auth`'s login/OTP endpoints are still a
  stub). The one decision locked in already: whenever it is built, it must
  be Redis-backed, never a per-process in-memory backend, since in-memory
  limits are trivially bypassed under horizontal scaling by hitting a
  different pod.
- **Pub/sub-based cache invalidation, built now.** Deferred — no local
  per-process cache layer exists to invalidate, and no downstream consumer
  needs domain events yet. Recorded explicitly because "ChatGPT-style
  'complete Redis architecture' advice bundles \[both of these] in on day
  one" and this project reviewed and declined that by default, not by
  oversight — the point of writing it down is so a future session doesn't
  silently reintroduce either one without a real, current requirement.

## Rule reference

`22-redis.md`.
