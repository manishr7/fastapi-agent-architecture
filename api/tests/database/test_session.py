from types import SimpleNamespace

from pydantic import SecretStr

from app.database.session import (
    build_database_url,
    build_ssl_connect_args,
    create_session_factory,
)


def _fake_settings(**overrides: object) -> SimpleNamespace:
    defaults: dict[str, object] = {
        "db_user": "root",
        "db_password": SecretStr("root"),
        "db_host": "localhost",
        "db_port": 3306,
        "db_name": "app_db",
        "db_ssl_ca": None,
        "db_ssl_cert": None,
        "db_ssl_key": None,
    }
    return SimpleNamespace(**{**defaults, **overrides})


def test_build_database_url_uses_mysql_asyncmy_driver() -> None:
    url = build_database_url(_fake_settings())

    assert url.drivername == "mysql+asyncmy"
    assert url.username == "root"
    assert url.host == "localhost"
    assert url.port == 3306
    assert url.database == "app_db"


def test_build_database_url_never_mangles_special_character_password() -> None:
    # The exact concern this function exists to solve: @, :, /, #, % in a
    # hand-formatted DSN string would silently misparse. URL.create() takes
    # each component literally.
    raw_password = "p@ss:word/with#chars%here"
    settings = _fake_settings(db_password=SecretStr(raw_password))

    url = build_database_url(settings)

    assert url.password == raw_password
    # Rendering to a string must not raise, and must not contain the raw
    # unescaped password (confirming URL.create() actually did the
    # percent-encoding rather than passing it through unchanged).
    assert raw_password not in str(url)


def test_build_ssl_connect_args_empty_when_no_tls_configured() -> None:
    assert build_ssl_connect_args(_fake_settings()) == {}


def test_build_ssl_connect_args_ca_only() -> None:
    settings = _fake_settings(db_ssl_ca="/path/to/ca.pem")

    assert build_ssl_connect_args(settings) == {"ssl": {"ca": "/path/to/ca.pem"}}


def test_build_ssl_connect_args_mutual_tls() -> None:
    settings = _fake_settings(
        db_ssl_ca="/path/to/ca.pem",
        db_ssl_cert="/path/to/client-cert.pem",
        db_ssl_key="/path/to/client-key.pem",
    )

    assert build_ssl_connect_args(settings) == {
        "ssl": {
            "ca": "/path/to/ca.pem",
            "cert": "/path/to/client-cert.pem",
            "key": "/path/to/client-key.pem",
        }
    }


def test_create_session_factory_disables_expire_on_commit_and_autoflush() -> None:
    # expire_on_commit=False: 05-sqlalchemy-part-1.md — repositories should
    # return fully usable domain entities without relying on expiration.
    # autoflush=False / autocommit=False: no implicit flush or transaction
    # behavior; the use case controls exactly when persistence happens.
    factory = create_session_factory(engine=None)

    assert factory.kw["expire_on_commit"] is False
    assert factory.kw["autoflush"] is False
    assert factory.kw["autocommit"] is False
