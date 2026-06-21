"""
InterviewGPT — Application Configuration
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "InterviewGPT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://interviewgpt:interviewgpt_secret@localhost:5432/interviewgpt"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Ollama Local LLM
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    USE_OLLAMA: bool = True

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8100
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # Faster Whisper
    WHISPER_MODEL_SIZE: str = "small"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate(self) -> None:
        """Validate critical environment configuration and raise helpful errors."""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is required")

        if not self.DEBUG:
            if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY == "change-me-in-production":
                raise ValueError("JWT_SECRET_KEY is not set or is using the insecure default. Set JWT_SECRET_KEY in your environment.")

        if self.USE_OLLAMA and not self.OLLAMA_URL:
            raise ValueError("USE_OLLAMA is True but OLLAMA_URL is not configured.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    try:
        settings.validate()
    except Exception:
        # Do not swallow validation errors — raise them so startup fails fast with a clear message
        raise
    return settings
