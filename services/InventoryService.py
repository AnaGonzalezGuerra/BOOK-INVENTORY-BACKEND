"""Inventory Service - Business logic for inventory operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from models.inventory import Inventory
from models.inventorymovement import InventoryMovement, MovementTypeEnum
from models.book import Book
from utils.custom_exceptions import CustomException


class InventoryService:
    """Service class for inventory-related operations."""

    def __init__(self, session: AsyncSession):
        """Initialize service with database session."""
        self.session = session

    async def create_inventory(self, book_id: int, quantity: int) -> Inventory:
        """
        Create initial inventory record for a book.
        
        Args:
            book_id: ID of the book
            quantity: Initial inventory quantity
            
        Returns:
            Inventory: The created inventory object
            
        Raises:
            CustomException: If book doesn't exist or inventory already exists
        """
        try:
            # Verify book exists
            book_query = select(Book).where(Book.id == book_id)
            result = await self.session.execute(book_query)
            book = result.scalar_one_or_none()
            
            if not book:
                raise CustomException(
                    status_code=404,
                    message=f"Libro con ID {book_id} no encontrado",
                    error_code="BOOK_NOT_FOUND"
                )
            
            # Check if inventory already exists
            inventory_query = select(Inventory).where(Inventory.book_id == book_id)
            result = await self.session.execute(inventory_query)
            existing_inventory = result.scalar_one_or_none()
            
            if existing_inventory:
                raise CustomException(
                    status_code=400,
                    message=f"El libro {book_id} ya tiene inventario registrado",
                    error_code="INVENTORY_ALREADY_EXISTS"
                )
            
            # Create new inventory
            new_inventory = Inventory(
                book_id=book_id,
                stock=quantity
            )
            
            self.session.add(new_inventory)
            
            # Create movement record
            movement = InventoryMovement(
                inventory=new_inventory,
                movement_type=MovementTypeEnum.CREATION.value,
                quantity=quantity
            )
            
            self.session.add(movement)
            
            await self.session.commit()
            await self.session.refresh(new_inventory)
            
            return new_inventory
            
        except CustomException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise CustomException(
                status_code=500,
                message=f"Error al crear inventario: {str(e)}",
                error_code="CREATE_INVENTORY_ERROR"
            )

    async def get_all_inventories(self, skip: int = 0, limit: int = 50) -> list[Inventory]:
        """
        Retrieve all inventories with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List[Inventory]: List of inventory objects
            
        Raises:
            CustomException: If database operation fails
        """
        try:
            # Validate pagination
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            
            # Build and execute query
            query = select(Inventory).offset(skip).limit(limit)
            result = await self.session.execute(query)
            inventories = result.scalars().all()
            
            if not inventories:
                raise CustomException(
                    status_code=404,
                    message="No hay inventarios disponibles",
                    error_code="NO_INVENTORIES_FOUND"
                )
            
            return list(inventories)
            
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(
                status_code=500,
                message=f"Error al obtener inventarios: {str(e)}",
                error_code="GET_INVENTORIES_ERROR"
            )

    async def get_inventory_by_book_id(self, book_id: int) -> Inventory:
        """
        Get inventory record for a specific book.
        
        Args:
            book_id: ID of the book
            
        Returns:
            Inventory: The inventory object
            
        Raises:
            CustomException: If inventory not found or database error
        """
        try:
            query = select(Inventory).where(Inventory.book_id == book_id)
            result = await self.session.execute(query)
            inventory = result.scalar_one_or_none()
            
            if not inventory:
                raise CustomException(
                    status_code=404,
                    message=f"Inventario para el libro {book_id} no encontrado",
                    error_code="INVENTORY_NOT_FOUND"
                )
            
            return inventory
            
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(
                status_code=500,
                message=f"Error al obtener inventario: {str(e)}",
                error_code="GET_INVENTORY_ERROR"
            )

    async def add_inventory(self, book_id: int, quantity: int) -> Inventory:
        """
        Add quantity to book inventory and record movement.
        
        Args:
            book_id: ID of the book
            quantity: Quantity to add
            
        Returns:
            Inventory: Updated inventory object
            
        Raises:
            CustomException: If inventory not found or operation fails
        """
        try:
            # Get current inventory
            inventory = await self.get_inventory_by_book_id(book_id)
            
            # Update stock level
            inventory.stock += quantity
            
            # Create movement record
            movement = InventoryMovement(
                inventory_id=inventory.id,
                movement_type=MovementTypeEnum.ADDITION.value,
                quantity=quantity
            )
            
            self.session.add(movement)
            await self.session.commit()
            await self.session.refresh(inventory)
            
            return inventory
            
        except CustomException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise CustomException(
                status_code=500,
                message=f"Error al agregar inventario: {str(e)}",
                error_code="ADD_INVENTORY_ERROR"
            )

    async def remove_inventory(self, book_id: int, quantity: int) -> Inventory:
        """
        Remove quantity from book inventory and record movement.
        
        Args:
            book_id: ID of the book
            quantity: Quantity to remove
            
        Returns:
            Inventory: Updated inventory object
            
        Raises:
            CustomException: If insufficient inventory or inventory not found
        """
        try:
            # Get current inventory
            inventory = await self.get_inventory_by_book_id(book_id)
            
            # Validate sufficient stock
            if inventory.stock < quantity:
                raise CustomException(
                    status_code=400,
                    message=f"Inventario insuficiente. Disponible: {inventory.stock}, Solicitado: {quantity}",
                    error_code="INSUFFICIENT_INVENTORY"
                )
            
            # Update stock level
            inventory.stock -= quantity
            
            # Create movement record
            movement = InventoryMovement(
                inventory_id=inventory.id,
                movement_type=MovementTypeEnum.REMOVAL.value,
                quantity=quantity
            )
            
            self.session.add(movement)
            await self.session.commit()
            await self.session.refresh(inventory)
            
            return inventory
            
        except CustomException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise CustomException(
                status_code=500,
                message=f"Error al remover inventario: {str(e)}",
                error_code="REMOVE_INVENTORY_ERROR"
            )

    async def get_movements(
        self,
        book_id: int,
        skip: int = 0,
        limit: int = 50,
        movement_type: str = None
    ) -> list[InventoryMovement]:
        """
        Get movement history for a book's inventory.
        
        Args:
            book_id: ID of the book
            skip: Number of records to skip
            limit: Number of records to return
            movement_type: Optional filter by movement type (creation/addition/removal)
            
        Returns:
            List[InventoryMovement]: List of movements
            
        Raises:
            CustomException: If inventory not found or invalid movement type
        """
        try:
            # Validate pagination
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            
            # Get inventory first
            inventory = await self.get_inventory_by_book_id(book_id)
            
            # Validate movement_type if provided
            valid_types = [e.value for e in MovementTypeEnum]
            if movement_type and movement_type not in valid_types:
                raise CustomException(
                    status_code=400,
                    message=f"Tipo de movimiento inválido. Válidos: {', '.join(valid_types)}",
                    error_code="INVALID_MOVEMENT_TYPE"
                )
            
            # Build query
            query = select(InventoryMovement).where(
                InventoryMovement.inventory_id == inventory.id
            )
            
            if movement_type:
                query = query.where(InventoryMovement.movement_type == movement_type)
            
            query = query.offset(skip).limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            movements = result.scalars().all()
            
            if not movements:
                raise CustomException(
                    status_code=404,
                    message=f"No hay movimientos para el libro {book_id}",
                    error_code="NO_MOVEMENTS_FOUND"
                )
            
            return list(movements)
            
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(
                status_code=500,
                message=f"Error al obtener movimientos: {str(e)}",
                error_code="GET_MOVEMENTS_ERROR"
            )
