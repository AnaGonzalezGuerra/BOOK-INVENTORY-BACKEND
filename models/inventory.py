"""Model for inventory tracking in the system."""
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from config.db import Base
from models.book import Book
from models.inventorymovement import InventoryMovement


class Inventory(Base):
    """Model representing the inventory of books."""
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey('books.id'))
    book: Mapped["Book"] = relationship(
        "Book",
        back_populates="inventory",
        uselist=False
    )
    inventory_movements: Mapped[list["InventoryMovement"]] = relationship(
        "InventoryMovement",
        back_populates="inventory",
        uselist=True,
        cascade="all, delete-orphan"
    )