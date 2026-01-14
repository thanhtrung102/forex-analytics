"""Application configuration settings."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Forex Prediction API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./forex.db"

    # Security
    secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # ML Models
    model_path: str = "./models"

    # API
    api_prefix: str = "/api"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        url = self.database_url
        # Handle Railway/Render postgres:// URLs
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
