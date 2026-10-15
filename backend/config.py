"""Centraliserad konfiguration via pydantic-settings.

Ordning: miljövariabel → .env i projektroten → standardvärdet nedan.
Ogiltiga värden stoppar uppstarten i stället för att märkas i drift.
"""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Literal, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    APP_VERSION = version("backend")
except PackageNotFoundError:
    APP_VERSION = "0.0.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Projektroten, oavsett vilken katalog appen startas från.
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "MyApp"
    ENVIRONMENT: Literal["development", "production"] = "development"
    DATABASE_URL: str = "postgresql+psycopg://app:app@localhost:5432/app"
    DEBUG: bool = False

    # app_proxy: identiteten kommer i headers från Entra Application Proxy.
    # mock: en fast användare, för utveckling utan proxy.
    AUTH_MODE: Literal["app_proxy", "mock"] = "app_proxy"
    MOCK_USER: str = "DEVUSER"
    MOCK_GROUPS: list[str] = []

    @model_validator(mode="after")
    def _no_mock_in_production(self) -> Self:
        if self.ENVIRONMENT == "production" and self.AUTH_MODE != "app_proxy":
            raise ValueError("AUTH_MODE måste vara app_proxy när ENVIRONMENT=production.")
        return self


settings = Settings()
