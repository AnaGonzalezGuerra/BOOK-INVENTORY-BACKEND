"""Books Service - Business logic for book operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, asc, desc
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
            if "not null" in str(e.orig).lower():
                raise CustomException(
                    status_code=422,
                    message="Faltan campos obligatorios para crear el libro",
                    error_code="MISSING_FIELDS"
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
                
    async def get_books(
        self,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "id",
        sort_order: str = "asc"
    ) -> list[Book]:
        """
        Retrieve books from the database with pagination and filtering.
        
        Args:
            skip: Number of records to skip (default: 0)
            limit: Number of records to return (default: 50, max: 100)
            sort_by: Field to sort by (default: "id")
            sort_order: Sort order "asc" or "desc" (default: "asc")
            
        Returns:
            List[Book]: A list of book objects
            
        Raises:
            CustomException: If database operation fails or invalid sort field
        """
        try:
            # Validate sort_by field
            valid_sort_fields = ["id", "title", "isbn", "published_date"]
            if sort_by not in valid_sort_fields:
                raise CustomException(
                    status_code=400,
                    message=f"Campo de ordenamiento inválido: {sort_by}. Válidos: {', '.join(valid_sort_fields)}",
                    error_code="INVALID_SORT_FIELD"
                )
            
            # Validate and limit pagination parameters
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            
            # Build query
            query = select(Book)
                        
            # Add sorting
            sort_column = getattr(Book, sort_by, Book.id)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Add pagination
            query = query.offset(skip).limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            books = result.scalars().all()
            
            # Validate if any books found
            if not books:
                raise CustomException(
                    status_code=404,
                    message="No hay libros disponibles con los parámetros especificados",
                    error_code="NO_BOOKS_FOUND"
                )
            
            return list(books)
            
        except Exception as e:
            raise CustomException(
                status_code=500,
                message=f"Error al obtener libros: {str(e)}",
                error_code="GET_BOOKS_ERROR"
            )