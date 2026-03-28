"""Pydantic schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class BookCreate(BaseModel):
    """Schema for creating a new book."""
    title: str = Field(..., min_length=1, max_length=255, description="Book title")
    isbn: str = Field(..., min_length=10, max_length=13, description="ISBN-10 or ISBN-13")
    published_date: datetime = Field(..., description="Publication date")
    description: Optional[str] = Field(None, description="Book description")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "El Quijote",
                "isbn": "9788467039568",
                "published_date": "2023-01-15T00:00:00",
                "description": "Novela de aventuras"
            }
        }


class BookResponse(BaseModel):
    """Schema for book response."""
    id: int
    title: str
    isbn: str
    published_date: datetime
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Permite convertir objetos ORM a Pydantic
