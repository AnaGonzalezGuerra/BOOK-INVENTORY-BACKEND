"""Configuration settings for the application."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    # Database settings
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 0
    DB_NAME: str = ""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), ".env")
    )

    @property
    def database_url(self) -> str:
        """Construct the database URL from settings."""
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")