from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_DIR = Path(__file__).resolve().parents[1]


class TelemetrySettings(BaseSettings):
    database_url: str
    fleet_management_url: str
    service_api_key: str
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=SERVICE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = TelemetrySettings()
