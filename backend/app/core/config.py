"""
Application configuration using Pydantic settings.

This module defines the `Settings` class with environment variables and
provides a global `settings` instance.  Settings are loaded from the
`.env` file (if present) and environment variables at runtime.
"""
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,  # Don't require .env file, read from environment variables only
        env_file_encoding="utf-8",
        case_sensitive=False,  # Allow case-insensitive matching (database_url matches DATABASE_URL)
        extra="ignore"
    )
    
    # Required settings
    database_url: str = Field(..., description="PostgreSQL database connection URL")
    redis_url: str = Field(..., description="Redis connection URL")
    jwt_secret_key: str = Field(..., description="Secret key for JWT tokens (min 32 chars recommended)")
    
    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, v: str) -> str:
        """Warn if JWT secret key is too short, but allow it in development."""
        if len(v) < 32:
            import warnings
            warnings.warn(
                f"JWT_SECRET_KEY is only {len(v)} characters. "
                "For production, use at least 32 characters for security.",
                UserWarning
            )
        return v
    
    # Optional settings with defaults
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440, description="Access token expiration in minutes")
    refresh_token_expire_minutes: int = Field(default=43200, ge=1, description="Refresh token expiration in minutes")
    openai_api_key: str = Field(default="", description="OpenAI API key for embeddings and LLM")
    rag_chunk_size: int = Field(default=512, ge=100, le=2000, description="Text chunk size for RAG")
    rag_overlap: int = Field(default=50, ge=0, le=200, description="Overlap between text chunks")
    log_level: str = Field(default="info", description="Logging level (debug, info, warning, error, critical)")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if v.lower() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.lower()
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"environment must be one of {valid_envs}")
        return v.lower()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()