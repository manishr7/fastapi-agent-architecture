"""Proves 04-async.md's "Concurrent Database Operations" rule with a real
AsyncSession, not a simulation: this deliberately writes the exact
`asyncio.gather()`-on-one-session pattern the rule calls Incorrect, against
an in-memory SQLite database (aiosqlite, dev/test-only — no network service
needed), and asserts SQLAlchemy itself detects and rejects it. The hazard
isn't hypothetical or something a linter enforces; it's the library's own
concurrency guard, exercised directly.
"""

import asyncio

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IllegalStateChangeError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.mark.asyncio
async def test_concurrent_queries_on_one_shared_session_are_rejected() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        # The raise doesn't necessarily happen at the gather() line itself —
        # empirically, it can surface later, when the session's own
        # __aexit__ (close()) detects the corrupted internal state left by
        # the concurrent execute() calls. The whole block is the honest
        # scope for "this is rejected," not just the gather() call.
        with pytest.raises(IllegalStateChangeError):
            async with factory() as session:
                # This is 04-async.md's Incorrect example, verbatim in
                # shape: await asyncio.gather(repo.get_user(...),
                # repo.get_roles(...)) when both share one AsyncSession.
                await asyncio.gather(
                    session.execute(text("SELECT 1")),
                    session.execute(text("SELECT 1")),
                )
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_sequential_queries_on_one_shared_session_succeed() -> None:
    # The rule's Correct alternative: same session, sequential awaits — no
    # concurrency guard trips because there's no concurrency to detect.
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with factory() as session:
            first = await session.execute(text("SELECT 1"))
            second = await session.execute(text("SELECT 1"))
            assert first.scalar() == 1
            assert second.scalar() == 1
    finally:
        await engine.dispose()
