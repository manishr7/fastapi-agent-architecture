from typing import Any

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings


def build_database_url(settings: Settings) -> URL:
    """Assemble the connection URL from discrete fields via URL.create().

    Never build this as a formatted/concatenated string — a password
    containing `@`, `:`, `/`, `#`, or `%` would silently misparse. URL.create()
    takes each component literally and needs no manual percent-encoding.
    """
    return URL.create(
        drivername="mysql+asyncmy",
        username=settings.db_user,
        password=settings.db_password.get_secret_value(),
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


def build_ssl_connect_args(settings: Settings) -> dict[str, Any]:
    """asyncmy accepts `ssl` as a dict of {ca, cert, key, ...} file paths.

    Omit the key entirely when no TLS is configured — asyncmy treats a
    missing/falsy `ssl` the same as no TLS, but an empty dict is clearer here
    than passing `ssl=None` explicitly through connect_args.
    """
    ssl_options: dict[str, str] = {}
    if settings.db_ssl_ca is not None:
        ssl_options["ca"] = str(settings.db_ssl_ca)
    if settings.db_ssl_cert is not None:
        ssl_options["cert"] = str(settings.db_ssl_cert)
    if settings.db_ssl_key is not None:
        ssl_options["key"] = str(settings.db_ssl_key)
    return {"ssl": ssl_options} if ssl_options else {}


def create_engine_from_settings(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        build_database_url(settings),
        connect_args=build_ssl_connect_args(settings),
        pool_pre_ping=True,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_recycle=settings.db_pool_recycle,
        echo=settings.debug,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


async def dispose_engine(engine: AsyncEngine) -> None:
    await engine.dispose()
