"""Application configuration using pydantic-settings."""

import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv("DATABASE_URL")
    api_key: str = os.getenv("API_KEY")
    debug: bool = False


settings = Settings()
