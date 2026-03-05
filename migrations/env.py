import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection

from alembic import context

# My imports
from config.db import Base, sync_engine, settings, engine
from models.book import Book
from models.inventory import Inventory
from models.inventorymovement import InventoryMovement

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
print(f"📋 Tablas detectadas: {list(Base.metadata.tables.keys())}")
print()
print("🔍 DEBUG - Variables de Configuración:")
print(f"  DB_USER: {settings.DB_USER}")
print(f"  DB_PASSWORD: {'*' * len(settings.DB_PASSWORD) if settings.DB_PASSWORD else '(vacío)'}")
print(f"  DB_HOST: {settings.DB_HOST}")
print(f"  DB_PORT: {settings.DB_PORT}")
print(f"  DB_NAME: {settings.DB_NAME}")
print()
print(f"🔗 DATABASE URL: {settings.database_url}")
print()


def run_migrations_offline() -> None:
    url = str(sync_engine.url)
    print(url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    async with engine().connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
