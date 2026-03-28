"""Books Controller - HTTP endpoints for book operations."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_async_session
from models.schemas import BookCreate, BookResponse
from services.BooksService import BooksService
from utils.custom_exceptions import CustomException

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/CreateBook", status_code=201, response_model=BookResponse)
async def create_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_async_session)
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
        
        # ✅ Convert ORM model to Pydantic response model
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


