"""Main API router - Combines all v1 endpoints."""
from fastapi import APIRouter
from routers.v1.controllers.BooksController import router as books_router

api_router = APIRouter()

# Include books router
api_router.include_router(books_router)