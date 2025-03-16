from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")
    WHATSAPP_ACCOUNT_SID: str = os.getenv("WHATSAPP_ACCOUNT_SID")
    WHATSAPP_AUTH_TOKEN: str = os.getenv("WHATSAPP_AUTH_TOKEN")
    WHATSAPP_PHONE_NUMBER: str = os.getenv("WHATSAPP_PHONE_NUMBER")

    # Google Cloud APIs
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_CALENDAR_API_KEY: str = os.getenv("GOOGLE_CALENDAR_API_KEY")
    GOOGLE_DOCS_API_KEY: str = os.getenv("GOOGLE_DOCS_API_KEY")
    GOOGLE_SEARCH_API_KEY: str = os.getenv("GOOGLE_SEARCH_API_KEY")

    # Text-to-Speech
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "azure")
    AZURE_TTS_KEY: Optional[str] = os.getenv("AZURE_TTS_KEY")
    AZURE_TTS_REGION: Optional[str] = os.getenv("AZURE_TTS_REGION")
    AMAZON_POLLY_KEY: Optional[str] = os.getenv("AMAZON_POLLY_KEY")
    ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 