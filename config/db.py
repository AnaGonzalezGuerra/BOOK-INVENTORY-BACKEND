"""Database configuration and setup."""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from config import Settings

settings = Settings()
DATABASE_URL = settings.database_url

# We create an asynchronous engine for working with a database
engine = create_async_engine(url=DATABASE_URL)
# Create a session factory to interact with the database
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models"""
    # The class is abstract so that you don't have to create a separate table
    __abstract__ = True
