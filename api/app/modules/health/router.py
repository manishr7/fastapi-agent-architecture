from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.modules.health.repositories.health_repository import HealthRepository
from app.modules.health.schemas.health import HealthData, ReadyData
from app.modules.health.use_cases.check_database_ready import CheckDatabaseReadyUseCase
from app.shared.responses.envelope import ApiResponse, success_response

router = APIRouter(tags=["Health"])


def _get_health_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HealthRepository:
    return HealthRepository(session=session)


def _get_check_database_ready(
    repository: Annotated[HealthRepository, Depends(_get_health_repository)],
) -> CheckDatabaseReadyUseCase:
    return CheckDatabaseReadyUseCase(repository=repository)


@router.get(
    "/health",
    summary="Liveness check",
    description="Returns OK when the API process is running. No I/O.",
    response_model=ApiResponse[HealthData],
)
async def liveness() -> ApiResponse[HealthData]:
    return success_response(HealthData(status="ok"))


@router.get(
    "/ready",
    summary="Readiness check",
    description="Verifies database connectivity via CheckDatabaseReadyUseCase.",
    response_model=ApiResponse[ReadyData],
)
async def readiness(
    use_case: Annotated[CheckDatabaseReadyUseCase, Depends(_get_check_database_ready)],
) -> ApiResponse[ReadyData]:
    result = await use_case.execute()
    return success_response(ReadyData(status="ok", database=result.database))
