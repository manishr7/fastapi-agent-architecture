from app.core.exceptions import PersistenceException, ServiceUnavailableException
from app.modules.health.domain.readiness import ReadinessResult
from app.modules.health.repositories.health_repository import HealthRepository


class CheckDatabaseReadyUseCase:
    """Verifies that the application can reach the database."""

    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    async def execute(self) -> ReadinessResult:
        try:
            await self._repository.ping()
        except PersistenceException as exc:
            raise ServiceUnavailableException(
                message="Database is not available",
                code="DATABASE_UNAVAILABLE",
                log_context={"dependency": "database"},
            ) from exc
        return ReadinessResult(database="connected")
