from fastapi import APIRouter

from app.api.v6.router import router as v6_router

router = APIRouter(prefix="/api")
router.include_router(v6_router)
