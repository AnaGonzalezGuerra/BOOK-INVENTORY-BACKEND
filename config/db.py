"""Database configuration and setup."""
from datetime import datetime
from sqlalchemy import Integer, DateTime, create_engine, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from config.config import Settings

settings = Settings()
DATABASE_URL = settings.database_url

# We create an asynchronous engine for working with a database

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see the generated SQL queries in the console
    pool_pre_ping=True,  # Check if the connection is alive before using it
)
# Create a session factory to interact with the database
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
# ⚡ Nuevo: engine sincrónico solo para Alembic
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg")
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models"""
    # The class is abstract so that you don't have to create a separate table
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()  # pylint: disable=not-callable
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now()         # pylint: disable=not-callable
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return cls.__name__.lower() + "s"