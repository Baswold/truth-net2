from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Truth Net Server"
    environment: str = "development"
    api_v1_prefix: str = "/v1"
    database_url: str = "postgresql+psycopg://truthnet:truthnet@localhost:5432/truthnet"
    redis_url: str = "redis://localhost:6379/0"
    search_url: str = "http://localhost:7700"
    storage_path: Path = Path("./storage")

    jwt_secret: str = Field("change-me-to-a-long-secret", min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_exp_minutes: int = 60
    refresh_token_exp_minutes: int = 60 * 24 * 30

    allow_origins: list[str] = ["http://localhost:1420", "tauri://localhost"]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="TRUTHNET_", case_sensitive=False)


settings = Settings()
