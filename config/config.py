"""Configuration settings for the application."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    # Database settings
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 0
    DB_NAME: str = ""
    
    # CORS settings
    origins_urls: str = ""  # Comma-separated list of allowed origins for CORS
    # Server settings
    ip_server: str = ""
    ip_port: int = 0

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding='utf-8'
    )

    @property
    def database_url(self) -> str:
        """Construct the async database URL from settings."""
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")
    
    @property
    def origins_list(self) -> list[str]:
        """Return origins as a list."""
        return self.origins_urls.split(',') if self.origins_urls else []
    
    @property
    def server_config(self) -> tuple[str, int]:
        """Return server configuration as a tuple."""
        return self.ip_server, self.ip_port
