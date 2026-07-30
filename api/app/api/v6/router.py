from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.health.router import router as health_router

router = APIRouter(prefix="/v6")
router.include_router(health_router)
router.include_router(auth_router)
