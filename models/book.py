"""Model for books in the inventory system."""
from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from config.db import Base


class Book(Base):
    """Model representing a book in the database."""
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    published_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    inventory: Mapped["Inventory"] = relationship(
        "Inventory",
        back_populates="book",
        uselist=False,
        cascade="all, delete-orphan"
    )