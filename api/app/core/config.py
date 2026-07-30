from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="fastapi-agent-architecture", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")

    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=3306, alias="DB_PORT")
    db_name: str = Field(default="fastapi_agent_architecture", alias="DB_NAME")
    db_user: str = Field(default="root", alias="DB_USER")
    db_password: SecretStr = Field(default="root", alias="DB_PASSWORD")
    # Optional TLS. Set DB_SSL_CA alone for server-only verification, or all
    # three for mutual TLS. Full standards: 05-sqlalchemy-part-1.md.
    db_ssl_ca: Path | None = Field(default=None, alias="DB_SSL_CA")
    db_ssl_cert: Path | None = Field(default=None, alias="DB_SSL_CERT")
    db_ssl_key: Path | None = Field(default=None, alias="DB_SSL_KEY")

    cors_origins: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
    )
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    db_pool_recycle: int = Field(default=3600, alias="DB_POOL_RECYCLE")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_max_connections: int = Field(default=20, alias="REDIS_MAX_CONNECTIONS")
    redis_socket_timeout: float = Field(default=5.0, alias="REDIS_SOCKET_TIMEOUT")
    redis_connect_timeout: float = Field(default=5.0, alias="REDIS_CONNECT_TIMEOUT")
    log_level: LogLevel = Field(default="INFO", alias="LOG_LEVEL")
    log_format: Literal["json", "console"] | None = Field(default=None, alias="LOG_FORMAT")

    @model_validator(mode="after")
    def _validate_db_ssl_config(self) -> "Settings":
        if bool(self.db_ssl_cert) != bool(self.db_ssl_key):
            raise ValueError(
                "DB_SSL_CERT and DB_SSL_KEY must both be set (mutual TLS) "
                "or both left unset — a client cert is unusable without its key."
            )
        for name, path in (
            ("DB_SSL_CA", self.db_ssl_ca),
            ("DB_SSL_CERT", self.db_ssl_cert),
            ("DB_SSL_KEY", self.db_ssl_key),
        ):
            if path is not None and not path.is_file():
                raise ValueError(f"{name} is set to '{path}' but that file does not exist")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def resolved_log_format(self) -> Literal["json", "console"]:
        if self.log_format is not None:
            return self.log_format
        return "console" if self.debug else "json"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
