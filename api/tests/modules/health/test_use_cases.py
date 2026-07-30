from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import PersistenceException, ServiceUnavailableException
from app.modules.health.use_cases.check_database_ready import CheckDatabaseReadyUseCase


@pytest.mark.asyncio
async def test_execute_returns_connected_when_repository_succeeds() -> None:
    repository = AsyncMock()
    repository.ping.return_value = None

    result = await CheckDatabaseReadyUseCase(repository=repository).execute()

    assert result.database == "connected"


@pytest.mark.asyncio
async def test_execute_translates_persistence_exception_into_service_unavailable() -> None:
    repository = AsyncMock()
    original_error = PersistenceException(
        code="DATABASE_UNAVAILABLE", log_context={"operation": "ping"}
    )
    repository.ping.side_effect = original_error

    with pytest.raises(ServiceUnavailableException) as exc_info:
        await CheckDatabaseReadyUseCase(repository=repository).execute()

    assert exc_info.value.code == "DATABASE_UNAVAILABLE"
    assert exc_info.value.log_context == {"dependency": "database"}
    assert exc_info.value.__cause__ is original_error
