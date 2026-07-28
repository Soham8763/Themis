import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "THEMIS Compliance Engine"
    ENV: str = "development"
    DEBUG: bool = True

    # Gemini API Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./themis.db"

    # Cache Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_IN_MEMORY_CACHE: bool = True

    # Vector Store
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
