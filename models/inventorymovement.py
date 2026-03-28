"""Models for inventory movements and related enums."""
import enum
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from config.db import Base

if TYPE_CHECKING:
    from models.inventory import Inventory


class InventoryMovement(Base):
    """Model representing the movement of inventory."""
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    movement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    inventory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('inventorys.id'))
    inventory: Mapped["Inventory"] = relationship(
        "Inventory",
        back_populates="inventory_movements",
        uselist=False
    )


class MovementTypeEnum(str, enum.Enum):
    """Enum representing the type of inventory movement."""
    ADDITION = "addition"
    REMOVAL = "removal"
