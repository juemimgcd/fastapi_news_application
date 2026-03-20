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
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_embedding_model: str = "text-embedding-v4"
    ai_recommendation_candidate_limit: int = 60
    ai_recommendation_profile_history_limit: int = 12
    ai_recommendation_profile_favorite_limit: int = 12
    ai_recommendation_embedding_dimensions: int = 1024
    ai_recommendation_request_timeout: int = 30

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

    @field_validator("qwen_base_url", mode="before")
    @classmethod
    def normalize_qwen_base_url(cls, value):
        if isinstance(value, str):
            return value.strip().rstrip("/")
        return value

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".venv/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()

