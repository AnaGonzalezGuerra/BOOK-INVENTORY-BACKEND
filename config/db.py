"""Database configuration and setup."""
from datetime import datetime
from sqlalchemy import Integer, DateTime, create_engine, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from config.config import Settings

settings = Settings()

# ⚡ Synchronous engine for Alembic (created immediately)
# Build synchronous URL from settings (replace asyncpg with psycopg2)

SYNC_DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

# lazy engine for the application (created on demand)
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


# lazy export 
engine = get_async_engine
async_session_maker = get_async_session_maker


async def get_async_session() -> AsyncSession:
    """Dependency for FastAPI to inject async session into routes."""
    async_session = get_async_session_maker()
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


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