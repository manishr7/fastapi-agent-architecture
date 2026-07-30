from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.core.config import Settings, get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.database.session import (
    create_engine_from_settings,
    create_session_factory,
    dispose_engine,
)
from app.infrastructure.redis.client import create_redis_client, dispose_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings: Settings = app.state.settings
    configure_logging(settings)
    engine = create_engine_from_settings(settings)
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    app.state.redis = create_redis_client(settings)
    yield
    await dispose_redis(app.state.redis)
    app.state.redis = None
    await dispose_engine(app.state.engine)
    app.state.engine = None
    app.state.session_factory = None


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        # Always False, independent of settings.debug: Starlette's
        # ServerErrorMiddleware uses this flag to render raw HTML stack
        # traces directly to HTTP clients when a bug escapes our own
        # exception handlers. settings.debug controls internal verbosity
        # (log format, SQL echo, traceback-in-logs via
        # unhandled_exception_handler, which always logs exc_info
        # regardless) — it must never also control what a client can see.
        debug=False,
        lifespan=lifespan,
    )
    app.state.settings = settings
    # CORS first (inner); RequestContextMiddleware last so it is outermost and
    # every request — including CORS short-circuits — gets tracing + access log.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
