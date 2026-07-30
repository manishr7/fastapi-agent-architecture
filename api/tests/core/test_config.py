from pathlib import Path

import pytest

from app.core.config import Settings

# Settings fields use Field(alias="ENV_VAR_NAME") without populate_by_name,
# so construction must use the alias (the env var name), not the Python
# attribute name — Settings(db_ssl_cert=...) is silently dropped by
# extra="ignore" rather than raising, which would make these tests pass
# without actually exercising anything.


def test_settings_constructs_with_no_environment_at_all() -> None:
    # Every field has a working default — CI runs the whole suite with no
    # .env file and no environment variables set, and Settings() must not
    # require either.
    settings = Settings(_env_file=None)

    assert settings.app_name == "fastapi-agent-architecture"
    assert settings.db_host == "localhost"
    assert settings.debug is False


def test_ssl_cert_without_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="must both be set"):
        Settings(_env_file=None, DB_SSL_CERT="/nonexistent/cert.pem")


def test_ssl_key_without_cert_is_rejected() -> None:
    with pytest.raises(ValueError, match="must both be set"):
        Settings(_env_file=None, DB_SSL_KEY="/nonexistent/key.pem")


def test_ssl_path_that_does_not_exist_is_rejected(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.pem"

    with pytest.raises(ValueError, match="does not exist"):
        Settings(_env_file=None, DB_SSL_CA=str(missing))


def test_ssl_mutual_tls_with_real_files_succeeds(tmp_path: Path) -> None:
    cert = tmp_path / "client-cert.pem"
    key = tmp_path / "client-key.pem"
    cert.write_text("fake cert")
    key.write_text("fake key")

    settings = Settings(_env_file=None, DB_SSL_CERT=str(cert), DB_SSL_KEY=str(key))

    assert settings.db_ssl_cert == cert
    assert settings.db_ssl_key == key


def test_cors_origin_list_strips_and_splits() -> None:
    settings = Settings(_env_file=None, CORS_ORIGINS="http://a.com, http://b.com ,")

    assert settings.cors_origin_list == ["http://a.com", "http://b.com"]


@pytest.mark.parametrize(
    ("debug", "log_format", "expected"),
    [
        (False, None, "json"),
        (True, None, "console"),
        (False, "console", "console"),
        (True, "json", "json"),
    ],
)
def test_resolved_log_format(debug: bool, log_format: str | None, expected: str) -> None:
    kwargs: dict[str, object] = {"DEBUG": debug}
    if log_format is not None:
        kwargs["LOG_FORMAT"] = log_format
    settings = Settings(_env_file=None, **kwargs)

    assert settings.resolved_log_format == expected
