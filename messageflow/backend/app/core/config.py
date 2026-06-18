from pydantic import BaseSettings, Field, AnyHttpUrl
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30, env="REFRESH_TOKEN_EXPIRE_DAYS")

    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(..., env="CELERY_RESULT_BACKEND")

    WHATSAPP_API_BASE: Optional[str] = Field(None, env="WHATSAPP_API_BASE")
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = Field(None, env="WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_BUSINESS_ID: Optional[str] = Field(None, env="WHATSAPP_BUSINESS_ID")
    WHATSAPP_ACCESS_TOKEN: Optional[str] = Field(None, env="WHATSAPP_ACCESS_TOKEN")

    SMTP_HOST: Optional[str] = Field(None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(None, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(None, env="SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = Field(None, env="EMAIL_FROM")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
