"""Books Service - Business logic for book operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from models.book import Book
from utils.custom_exceptions import CustomException


class BooksService:
    """Service class for book-related operations."""

    def __init__(self, session: AsyncSession):
        """Initialize service with database session."""
        self.session = session

    async def create_book(self, book_data: dict) -> Book:
        """
        Create a new book in the database.
        
        Args:
            book_data: Dictionary with book information (title, isbn, published_date, description)
            
        Returns:
            Book: The created book object with ID and timestamps
            
        Raises:
            CustomException: If ISBN already exists (duplicate) or other validation errors
        """
        try:
            # Create a new Book instance
            new_book = Book(
                title=book_data.get("title"),
                isbn=book_data.get("isbn"),
                published_date=book_data.get("published_date"),
                description=book_data.get("description")
            )

            # Add to session
            self.session.add(new_book)

            # Commit to database
            await self.session.commit()

            # Refresh to get the ID and timestamps from database
            await self.session.refresh(new_book)

            return new_book

        except IntegrityError as e:
            # Handle duplicate ISBN or other constraint violations
            await self.session.rollback()
            
            if "isbn" in str(e.orig).lower():
                raise CustomException(
                    status_code=400,
                    message="El ISBN ya existe en la base de datos",
                    error_code="DUPLICATE_ISBN"
                )
            
            raise CustomException(
                status_code=400,
                message="Error de integridad en la base de datos",
                error_code="INTEGRITY_ERROR"
            )

        except Exception as e:
            await self.session.rollback()
            raise CustomException(
                status_code=500,
                message=f"Error al crear el libro: {str(e)}",
                error_code="CREATE_BOOK_ERROR"
            )