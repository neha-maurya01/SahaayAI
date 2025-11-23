from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Configuration
    API_VERSION: str = "v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Gemini AI API
    GEMINI_API_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./sahaayai.db"
    
    # Redis Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str
    
    # Twilio (Optional - only needed for real SMS/Voice)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # WhatsApp (Optional - only needed for WhatsApp integration)
    WHATSAPP_BUSINESS_ID: str = ""
    WHATSAPP_API_TOKEN: str = ""
    
    @property
    def twilio_enabled(self) -> bool:
        return bool(self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN)
    
    @property
    def whatsapp_enabled(self) -> bool:
        return bool(self.WHATSAPP_BUSINESS_ID and self.WHATSAPP_API_TOKEN)
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/sahaayai.log"
    
    # Storage
    FILE_STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE_MB: int = 10
    
    # Supported Languages
    SUPPORTED_LANGUAGES: str = "en,hi,bn,ta,te,mr,gu,kn,ml,pa,or,as"
    
    # Default Settings
    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_LITERACY_LEVEL: str = "medium"
    
    # Performance
    MAX_WORKERS: int = 4
    REQUEST_TIMEOUT_SECONDS: int = 30
    CACHE_TTL_SECONDS: int = 3600
    
    # Privacy
    DATA_RETENTION_DAYS: int = 90
    ENABLE_ANALYTICS: bool = True
    ANONYMIZE_LOGS: bool = True
    
    @property
    def supported_languages_list(self) -> List[str]:
        return self.SUPPORTED_LANGUAGES.split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
