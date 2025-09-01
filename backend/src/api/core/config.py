import os
from pydantic import BaseModel, Field
from typing import List, Optional


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    APP_NAME: str = Field(default="ContentCraft AI Backend", description="Application name.")
    SECRET_KEY: str = Field(default="change-this-secret", description="JWT secret key (set via env).")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, description="JWT access token expiry minutes.")
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm.")
    DATABASE_URL: str = Field(default="sqlite:///./contentcraft.db", description="SQLAlchemy database URL.")
    CORS_ALLOW_ORIGINS: Optional[List[str]] = Field(default=None, description="CORS allow origins list")

    @classmethod
    def from_env(cls) -> "Settings":
        cors = os.getenv("CORS_ALLOW_ORIGINS")
        cors_list = [o.strip() for o in cors.split(",")] if cors else None
        return cls(
            APP_NAME=os.getenv("APP_NAME", "ContentCraft AI Backend"),
            SECRET_KEY=os.getenv("SECRET_KEY", "change-this-secret"),
            ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24))),
            ALGORITHM=os.getenv("ALGORITHM", "HS256"),
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./contentcraft.db"),
            CORS_ALLOW_ORIGINS=cors_list,
        )


settings = Settings.from_env()
