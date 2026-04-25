"""Inventory Controller - HTTP endpoints for inventory operations."""
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_async_session
from models.schemas import InventoryCreate, InventoryResponse, MovementCreate, MovementQuantity, MovementResponse
from services.InventoryService import InventoryService
from utils.custom_exceptions import CustomException

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("", status_code=201)
async def create_inventory(
    inventory_data: InventoryCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)] = None
) -> InventoryResponse:
    """
    Create initial inventory record for a book.
    
    Args:
        inventory_data: InventoryCreate schema with book_id and quantity
        session: AsyncSession injected by FastAPI dependency
        
    Returns:
        InventoryResponse: The created inventory record with ID and timestamps
        
    Raises:
        CustomException: If book not found or inventory already exists
    """
    try:
        service = InventoryService(session)
        created_inventory = await service.create_inventory(
            book_id=inventory_data.book_id,
            quantity=inventory_data.quantity
        )
        return InventoryResponse.model_validate(created_inventory)
        
    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=500,
            message=f"Error inesperado: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )


@router.get("", status_code=200)
async def get_all_inventories(
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of records to return")] = 50,
    session: Annotated[AsyncSession, Depends(get_async_session)] = None
) -> list[InventoryResponse]:
    """
    Retrieve all inventory records with pagination.
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Number of records to return (default: 50, max: 100)
        session: AsyncSession injected by FastAPI dependency
        
    Returns:
        List[InventoryResponse]: List of all inventory records
        
    Raises:
        CustomException: If database operation fails
    """
    try:
        service = InventoryService(session)
        inventories = await service.get_all_inventories(skip=skip, limit=limit)
        return [InventoryResponse.model_validate(inventory) for inventory in inventories]
        
    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=500,
            message=f"Error inesperado: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )


@router.get("/book/{book_id}", status_code=200)
async def get_inventory(
    book_id: Annotated[int, Path(..., gt=0, description="Book ID")],
    session: Annotated[AsyncSession, Depends(get_async_session)] = None
) -> InventoryResponse:
    """
    Get inventory record for a specific book.
    
    Args:
        book_id: ID of the book
        session: AsyncSession injected by FastAPI dependency
        
    Returns:
        InventoryResponse: Inventory information for the book
        
    Raises:
        CustomException: If inventory not found
    """
    try:
        service = InventoryService(session)
        inventory = await service.get_inventory_by_book_id(book_id=book_id)
        return InventoryResponse.model_validate(inventory)
        
    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=500,
            message=f"Error inesperado: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )


@router.post("/book/{book_id}", status_code=200)
async def add_inventory(
    book_id: Annotated[int, Path(..., gt=0, description="Book ID")],
    movement_data: MovementQuantity = None,
    session: Annotated[AsyncSession, Depends(get_async_session)] = None
) -> InventoryResponse:
    """
    Add quantity to book inventory and record movement as 'addition'.
    
    Args:
        book_id: ID of the book
        movement_data: MovementQuantity schema with quantity (movement_type defaults to 'addition')
        session: AsyncSession injected by FastAPI dependency
        
    Returns:
        InventoryResponse: Updated inventory information
        
    Raises:
        CustomException: If inventory not found or operation fails
    """
    try:
        service = InventoryService(session)
        updated_inventory = await service.add_inventory(
            book_id=book_id,
            quantity=movement_data.quantity
        )
        return InventoryResponse.model_validate(updated_inventory)
        
    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=500,
            message=f"Error inesperado: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )


@router.delete("/book/{book_id}", status_code=200)
async def remove_inventory(
    book_id: Annotated[int, Path(..., gt=0, description="Book ID")],
    quantity: Annotated[int, Query(..., gt=0, description="Quantity to remove")] = None,
    session: Annotated[AsyncSession, Depends(get_async_session)] = None
) -> InventoryResponse:
    """
    Remove quantity from book inventory and record movement.
    
    Args:
        book_id: ID of the book
        quantity: Quantity to remove from inventory
        session: AsyncSession injected by FastAPI dependency
        
    Returns:
        InventoryResponse: Updated inventory information
        
    Raises:
        CustomException: If insufficient inventory or inventory not found
    """
    try:
        service = InventoryService(session)
        updated_inventory = await service.remove_inventory(
            book_id=book_id,
            quantity=quantity
        )
        return InventoryResponse.model_validate(updated_inventory)
        
    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=500,
            message=f"Error inesperado: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )


@router.get("/book/{book_id}/movements", status_code=200)
async def get_movements(
    book_id: Annotated[int, Path(..., gt=0, description="Book ID")],
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of records to return")] = 50,
    movement_type: Annotated[str, Query(description="Filter by movement type (addition/removal)")] = None,
    session: Annotated[AsyncSession, Depends(get_async_session)] = None
) -> list[MovementResponse]:
    """
    Get movement history for a book's inventory.
    
    Args:
        book_id: ID of the book
        skip: Number of records to skip (default: 0)
        limit: Number of records to return (default: 50, max: 100)
        movement_type: Optional filter by movement type (addition/removal)
        session: AsyncSession injected by FastAPI dependency
        
    Returns:
        List[MovementResponse]: List of inventory movements
        
    Raises:
        CustomException: If inventory not found or invalid movement type
    """
    try:
        service = InventoryService(session)
        movements = await service.get_movements(
            book_id=book_id,
            skip=skip,
            limit=limit,
            movement_type=movement_type
        )
        return [MovementResponse.model_validate(movement) for movement in movements]
        
    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=500,
            message=f"Error inesperado: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )
