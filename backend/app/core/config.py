"""Application configuration using Pydantic settings."""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/getanswers",
        description="PostgreSQL async database URL (postgresql+asyncpg://...)"
    )

    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )

    # JWT Configuration
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-use-a-long-random-string",
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    MAGIC_LINK_EXPIRE_MINUTES: int = 15

    # OAuth Configuration (Gmail) - Optional for initial setup
    GMAIL_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="Google OAuth Client ID for Gmail integration"
    )
    GMAIL_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="Google OAuth Client Secret for Gmail integration"
    )

    # Anthropic Configuration - Optional for initial setup
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude integration"
    )

    # GetMailer Configuration (transactional emails: magic links, notifications, digests)
    # GetMailer is our internal email solution built on AWS SES
    # NOT for user emails - those go through Gmail/Outlook OAuth
    GETMAILER_API_KEY: Optional[str] = Field(
        default=None,
        description="GetMailer API key for transactional emails"
    )
    GETMAILER_URL: str = Field(
        default="https://api.getmailer.io",
        description="GetMailer API base URL"
    )
    EMAIL_FROM: str = Field(
        default="noreply@getanswers.co",
        description="Email address to send from (must be verified in GetMailer)"
    )

    # Application Configuration
    APP_URL: str = Field(
        default="http://localhost:5073",
        description="Frontend application URL for magic links"
    )

    # Environment
    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment (development, staging, production)"
    )

    # Version
    VERSION: str = Field(
        default="0.1.0",
        description="Application version"
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # Error Tracking
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking (optional)"
    )

    # CORS Settings
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5073", "http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure the database URL uses the asyncpg driver."""
        if "postgresql://" in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://")
        elif "postgres://" in v:
            v = v.replace("postgres://", "postgresql+asyncpg://")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


# Global settings instance
settings = Settings()
