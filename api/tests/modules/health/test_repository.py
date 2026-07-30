from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import PersistenceException
from app.modules.health.repositories.health_repository import HealthRepository


@pytest.mark.asyncio
async def test_ping_succeeds_when_database_reachable() -> None:
    session = AsyncMock()

    await HealthRepository(session=session).ping()

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_ping_translates_database_failure_into_persistence_exception() -> None:
    session = AsyncMock()
    original_error = RuntimeError("connection refused")
    session.execute.side_effect = original_error

    with pytest.raises(PersistenceException) as exc_info:
        await HealthRepository(session=session).ping()

    assert exc_info.value.code == "DATABASE_UNAVAILABLE"
    assert exc_info.value.log_context == {"operation": "ping"}
    # Exception chaining (`raise ... from exc`) must be preserved so the
    # global handler's cause_type/cause_message reflect the real failure —
    # 12-errors.md's "Exception Chaining".
    assert exc_info.value.__cause__ is original_error
