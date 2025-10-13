from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Truth Net Server"
    environment: str = "development"
    api_v1_prefix: str = "/v1"
    database_url: str = "postgresql+psycopg://truthnet:truthnet@localhost:5432/truthnet"
    redis_url: str = "redis://localhost:6379/0"
    search_url: str = "http://localhost:7700"
    search_api_key: str | None = None
    storage_path: Path = Path("./storage")

    # Database pool configuration
    db_pool_size: int = Field(default=5, description="Base connection pool size")
    db_max_overflow: int = Field(default=10, description="Max overflow connections")
    db_pool_recycle: int = Field(default=3600, description="Recycle connections after N seconds")
    db_pool_pre_ping: bool = Field(default=True, description="Test connections before using")

    jwt_secret: str = Field(
        "dev-secret-key-do-not-use-in-production-change-this-immediately",
        min_length=32
    )
    jwt_algorithm: str = "HS256"
    access_token_exp_minutes: int = 60
    refresh_token_exp_minutes: int = 60 * 24 * 30

    # CORS configuration
    allow_origins: list[str] = Field(
        default=["http://localhost:1420", "tauri://localhost"],
        description="Allowed CORS origins. Override with comma-separated string in TRUTHNET_ALLOW_ORIGINS"
    )
    allowed_hosts: list[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts for production. Use '*' to allow all (not recommended)"
    )

    @field_validator("allow_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Parse comma-separated origins string from env."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_hosts(cls, v):
        """Parse comma-separated hosts string from env."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str, info) -> str:
        if info.data.get("environment") == "production" and "dev-secret" in v:
            raise ValueError(
                "Must set TRUTHNET_JWT_SECRET in production. "
                "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v

    model_config = SettingsConfigDict(env_file=".env", env_prefix="TRUTHNET_", case_sensitive=False)


settings = Settings()
