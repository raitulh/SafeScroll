from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    app_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    auto_create_db: bool = False
    database_url: str = "postgresql+asyncpg://safescroll:safescroll@localhost:5432/safescroll"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    jwt_secret: str = Field(min_length=16, default="development-only-change-me")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 30

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:1.7b"
    ollama_timeout_seconds: float = 35.0
    safescroll_mode: str = "zero"
    local_model_enabled: bool = True

    web_risk_enabled: bool = False
    web_risk_api_key: str | None = None
    web_risk_threat_types: str = "SOCIAL_ENGINEERING,MALWARE,UNWANTED_SOFTWARE"

    rate_limit_per_minute: int = 60
    scan_max_chars: int = 12000
    image_max_bytes: int = 8_000_000

    sentry_dsn: str | None = None
    metrics_enabled: bool = True
    otel_service_name: str = "safescroll-api"

    rules_signing_public_key_b64: str | None = None
    rules_require_signature: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    def validate_security(self) -> None:
        if self.app_env.lower() == "production" and self.jwt_secret == "development-only-change-me":
            raise ValueError("JWT_SECRET must be changed in production.")
        if self.app_env.lower() == "production" and len(self.jwt_secret.encode()) < 32:
            raise ValueError("JWT_SECRET must be at least 32 bytes in production.")

    @property
    def cors_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

    @property
    def web_risk_types(self) -> list[str]:
        return [x.strip() for x in self.web_risk_threat_types.split(",") if x.strip()]

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
settings.validate_security()
