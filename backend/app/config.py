"""Application configuration settings using Pydantic Settings."""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Based Smart Allocation Engine for PM Internship Scheme"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./pm_internship.db"

    # Security & Authentication
    SECRET_KEY: str = "pm_internship_super_secret_jwt_key_academic_demo_2026_change_in_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    # Initial Admin Seed
    INITIAL_ADMIN_EMAIL: str = "admin@pm-internship.edu.in"
    INITIAL_ADMIN_PASSWORD: str = "AdminSecurePass@2026"
    INITIAL_ADMIN_NAME: str = "System Super Admin"

    # Uploads
    UPLOAD_DIR: str = "./uploads/resumes"
    MAX_UPLOAD_SIZE_MB: int = 5

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
