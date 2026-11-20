"""
Application configuration loaded from environment variables / .env file.
"""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME:  str  = "Traffic Black Spot Prediction API"
    APP_ENV:   str  = "development"
    DEBUG:     bool = True

    # Model paths (relative to backend/ directory)
    MODEL_PATH:     Path = Path("models/best_model.pkl")
    METADATA_PATH:  Path = Path("models/model_metadata.json")
    ALL_MODELS_DIR: Path = Path("models/all_models")

    # API server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # CORS — React Vite dev server + production frontend
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "https://your-app.vercel.app",
    ]

    # Rate limiting
    RATE_LIMIT:  str = "100/minute"
    BATCH_LIMIT: int = 500

    # Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600

    # Bengaluru coordinate bounds
    LAT_MIN: float = 12.75
    LAT_MAX: float = 13.18
    LNG_MIN: float = 77.38
    LNG_MAX: float = 77.82

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
