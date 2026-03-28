"""Custom exceptions for the application."""
from fastapi import HTTPException


class CustomException(HTTPException):
    """Custom HTTP exception for API errors."""
    
    def __init__(self, status_code: int, message: str, error_code: str = "ERROR"):
        """
        Initialize custom exception.
        
        Args:
            status_code: HTTP status code
            message: Error message (visible to client in Spanish)
            error_code: Internal error code for debugging
        """
        self.error_code = error_code
        detail = {
            "error_code": error_code,
            "message": message
        }
        super().__init__(status_code=status_code, detail=detail)
