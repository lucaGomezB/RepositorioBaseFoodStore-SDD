# Configuration management using pydantic settings
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/foodstore_db"

    # Security - JWT
    SECRET_KEY: str = "your-super-secret-key-min-32-chars-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes for access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 days for refresh token

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # MercadoPago (optional for setup)
    MERCADOPAGO_ACCESS_TOKEN: str = ""
    MERCADOPAGO_PUBLIC_KEY: str = ""
    MERCADOPAGO_WEBHOOK_SECRET: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    # Environment
    ENVIRONMENT: str = "development"

    # Rate Limiting
    RATE_LIMIT_LOGIN_REQUESTS: int = 5  # Max requests per window
    RATE_LIMIT_LOGIN_WINDOW: int = 15   # Window in minutes

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()