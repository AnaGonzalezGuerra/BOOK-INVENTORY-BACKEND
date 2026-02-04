"""Main application entry point."""
from config.config import Settings

settings = Settings()

if __name__ == "__main__":
    print("DB URL =>", settings.database_url)
    print("DB HOST =>", settings.DB_HOST)
