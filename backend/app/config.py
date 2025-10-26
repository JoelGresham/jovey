"""
Configuration Management
Loads environment variables and provides configuration settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application settings
    app_name: str = "Jovey API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True

    # Supabase configuration
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    # Anthropic Claude API
    anthropic_api_key: str

    # JWT configuration
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS origins (optional - will use defaults if not set)
    cors_origins: Optional[str] = None

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string or use defaults"""
        if self.cors_origins:
            return [origin.strip() for origin in self.cors_origins.split(',')]
        return ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
