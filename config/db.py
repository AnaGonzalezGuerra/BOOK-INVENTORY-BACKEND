"""Database configuration and setup."""
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text, func
from sqlalchemy import ForeignKey, relationship
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
import enum

from config import Settings

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


class Book(Base):
    """Model representing a book in the database."""
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    published_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(Text)
   
    inventory: Mapped["Inventory"] = relationship(
        "Inventory",
        back_populates="Book",
        uselist=False,  # Each book has one inventory record
        cascade="all, delete-orphan"
    )


class Inventory(Base):
    """Model representing the inventory of books."""
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey('books.id'))
   
    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="Inventory",
        uselist=False  # Each book has one inventory record
        
    )
    
    inventoryMovements: Mapped[list["InventoryMovement"]] = relationship(
        "InventoryMovement",
        back_populates="Inventory",
        uselist=True,  # Each inventory can have multiple movements
        cascade="all, delete-orphan"
    )


class InventoryMovement(Base):
    """Model representing the movement of inventory."""
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    # movement_type examples: e.g., 'addition', 'removal'
    movement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    inventory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('inventorys.id'))
    
    inventory: Mapped["Inventory"] = relationship(
        "Inventory",
        back_populates="InventoryMovement",
        uselist=False  # Each inventory movement belongs to one inventory
       
    )
    

class MovementTypeEnum(str, enum.Enum):
    """Enum representing the type of inventory movement."""
    ADDITION = "addition"
    REMOVAL = "removal"

