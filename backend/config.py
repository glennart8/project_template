"""Centraliserad konfiguration via pydantic-settings."""

from importlib.metadata import PackageNotFoundError, version

from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    APP_VERSION = version("backend")
except PackageNotFoundError:
    APP_VERSION = "0.0.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "MyApp"
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    DEBUG: bool = False


settings = Settings()
