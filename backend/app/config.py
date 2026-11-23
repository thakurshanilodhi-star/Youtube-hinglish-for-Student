"""Application configuration and environment variables."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "HinglishDub"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/hinglish_dub")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # AI APIs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")

    # Storage
    S3_BUCKET: str = os.getenv("S3_BUCKET", "hinglish-dub-storage")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    LOCAL_STORAGE_PATH: str = os.getenv("LOCAL_STORAGE_PATH", "/tmp/hinglish-dub")

    # Processing
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "large-v3")
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    CHUNK_DURATION: int = int(os.getenv("CHUNK_DURATION", "10"))  # seconds

    # Live Stream
    LIVE_BUFFER_SECONDS: int = int(os.getenv("LIVE_BUFFER_SECONDS", "3"))
    LIVE_RECONNECT_ATTEMPTS: int = int(os.getenv("LIVE_RECONNECT_ATTEMPTS", "5"))

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
