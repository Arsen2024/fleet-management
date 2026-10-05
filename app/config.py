import os

from pydantic_settings import BaseSettings, SettingsConfigDict

ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")

ENV_FILES = {
    "sandbox": ".env.sandbox",
    "production": ".env.production",
}

env_file = ENV_FILES.get(ENVIRONMENT)

if env_file is None:
    raise ValueError(f"Unsupported ENVIRONMENT: {ENVIRONMENT}")


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
