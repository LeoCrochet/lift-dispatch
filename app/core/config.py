from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_PROXY_URL: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
