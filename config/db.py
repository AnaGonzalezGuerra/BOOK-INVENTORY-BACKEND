"""Database configuration and setup."""
from datetime import datetime
from sqlalchemy import Integer, DateTime, create_engine, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from config.config import Settings

settings = Settings()

# ⚡ Engine sincrónico para Alembic (se crea inmediatamente)
# Construir URL sincrónica a partir de settings (reemplazar asyncpg con psycopg2)
SYNC_DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

# Engine async para la aplicación (lazy - se crea cuando se necesita)
_async_engine = None
_async_session_maker = None

def get_async_engine():
    """Get or create the async engine for the application."""
    global _async_engine
    if _async_engine is None:
        database_url = settings.database_url
        _async_engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
        )
    return _async_engine

def get_async_session_maker():
    """Get or create the async session maker."""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(get_async_engine(), expire_on_commit=False)
    return _async_session_maker


# Lazy exports - se crean solo cuando se llaman
engine = get_async_engine
async_session_maker = get_async_session_maker


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"