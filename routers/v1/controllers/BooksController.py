"""Books Controller - HTTP endpoints for book operations."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_async_session
from models.schemas import BookCreate, BookResponse
from services.BooksService import BooksService
from utils.custom_exceptions import CustomException

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/CreateBook", status_code=201)
async def create_book(
    book_data: BookCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> BookResponse:
    """
    Create a new book in the inventory system.
    
    Args:
        book_data: BookCreate schema with title, isbn, published_date, description
        session: AsyncSession injected by FastAPI dependency
        
    Returns:
        BookResponse: The created book with ID and timestamps
        
    Raises:
        CustomException: If validation fails or duplicate ISBN
    """
    try:
        # Initialize service with the session
        service = BooksService(session)
        
        # Convert Pydantic model to dict for service
        book_dict = book_data.model_dump()
        
        # Call service to create book
        created_book = await service.create_book(book_dict)
        
        # Convert ORM model to Pydantic response model
        return BookResponse.model_validate(created_book)
        
    except CustomException:
        # Re-raise custom exceptions
        raise
    except Exception as e:
        raise CustomException(
            status_code=500,
            message=f"Error inesperado: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )

@router.get("/GetBooks", status_code=200)
async def get_books(
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of records to return")] = 50,
    sort_by: Annotated[str, Query(description="Field to sort by (id, title, isbn, published_date)")] = "id",
    sort_order: Annotated[str, Query(pattern="^(asc|desc)$", description="Sort order")] = "asc",
    session: Annotated[AsyncSession, Depends(get_async_session)] = None
) -> list[BookResponse]:
    """
    Retrieve all books with pagination, filtering, and sorting.
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Number of records to return (default: 50, max: 100)
        sort_by: Field to sort by (default: id)
        sort_order: Sort order "asc" or "desc" (default: asc)
        search: Optional search string to filter by title or ISBN
        session: AsyncSession injected by FastAPI dependency
        
    Returns:
        List[BookResponse]: List of books matching the criteria
        
    Raises:
        CustomException: If database operation fails
    """
    try:
        service = BooksService(session)
        books = await service.get_books(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return [BookResponse.model_validate(book) for book in books]
        
    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=500,
            message=f"Error inesperado: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )

@router.get("/GetBooksById/{book_id}", status_code=200)
async def get_book_by_id(
    book_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> BookResponse:
    """
    Retrieve a single book by its ID.
    
    Args:
        book_id: The ID of the book to retrieve
        session: AsyncSession injected by FastAPI dependency
        
    Returns:
        BookResponse: The book with the specified ID
        
    Raises:
        CustomException: If book not found or database operation fails
    """
    try:
        service = BooksService(session)
        book = await service.get_book_by_id(book_id)
        if not book:
            raise CustomException(
                status_code=404,
                message=f"Libro con ID {book_id} no encontrado",
                error_code="BOOK_NOT_FOUND"
            )
        return BookResponse.model_validate(book)
        
    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=500,
            message=f"Error inesperado: {str(e)}",
            error_code="UNEXPECTED_ERROR"
        )