from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fastapi_reviews"
    env: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    api_prefix: str = "/api"

    cors_origins: str = ""

    async_database_url: str
    redis_url: str

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"release", "prod", "production", "false", "0", "off", "no"}:
                return False
            if lowered in {"debug", "development", "dev", "true", "1", "on", "yes"}:
                return True
        return value

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".venv/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()

