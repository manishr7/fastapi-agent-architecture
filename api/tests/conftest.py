import logging
from collections.abc import Callable

import pytest
import structlog
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.logging import configure_logging
from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def configured_settings() -> Callable[..., Settings]:
    """Builds one Settings object and configures logging from it.

    Returning the same object callers then use for e.g. a mocked
    `request.app.state.settings` prevents constructing a second, independent
    Settings that can silently drift from what configure_logging() saw.
    """

    def _configure(**overrides: object) -> Settings:
        defaults: dict[str, object] = {"LOG_FORMAT": "json", "LOG_LEVEL": "INFO", "DEBUG": False}
        settings = Settings(**{**defaults, **overrides})
        configure_logging(settings)
        return settings

    return _configure


@pytest.fixture(autouse=True)
def _restore_logging_state() -> None:
    """Tests may call configure_logging() directly; keep that global mutation
    scoped to the test that made it so other tests aren't affected."""
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    yield
    root.handlers = original_handlers
    root.setLevel(original_level)
    structlog.reset_defaults()
