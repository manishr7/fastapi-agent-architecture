import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.database.base import Base
from app.database.session import build_database_url, build_ssl_connect_args

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

settings = get_settings()
database_url = build_database_url(settings)
# hide_password=False: Alembic needs the real credential to connect, not the
# masked repr `str(url)` would otherwise produce.
config.set_main_option("sqlalchemy.url", database_url.render_as_string(hide_password=False))


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    # Built directly rather than via async_engine_from_config's ini-string
    # parsing, so the same TLS connect_args the app engine uses (session.py)
    # apply here too — one source of truth for how we connect to MySQL.
    connectable = create_async_engine(
        database_url,
        connect_args=build_ssl_connect_args(settings),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
