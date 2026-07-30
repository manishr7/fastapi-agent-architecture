from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PersistenceException


class HealthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def ping(self) -> None:
        """Execute a lightweight query to verify database connectivity."""
        try:
            await self._session.execute(text("SELECT 1"))
        except (SQLAlchemyError, OSError, RuntimeError) as exc:
            raise PersistenceException(
                message="Database connectivity check failed",
                code="DATABASE_UNAVAILABLE",
                log_context={"operation": "ping"},
            ) from exc
