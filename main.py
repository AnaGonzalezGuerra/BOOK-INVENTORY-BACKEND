"""Main application entry point."""
# General libraries

# FastAPI associated libraries
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# My imports
from routers.v1.routers import api_router
from config.config import Settings
# Import all models to register them with SQLAlchemy before app starts
from models import Book, Inventory, InventoryMovement
from utils.custom_exceptions import CustomException

settings = Settings()

app = FastAPI(docs_url="/docs", redoc_url="/redoc")
origins = settings.origins_list
ip_server, ip_port = settings.server_config


# EXCEPTION HANDLER para errores de validación Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Convert Pydantic validation errors to our custom error format.
    
    Maps field validation errors to our CustomException with 422 status.
    """
    errors = exc.errors()
    
    # Extract field names and messages
    missing_fields = []
    for error in errors:
        field_name = error["loc"][-1]  # Get the last element (field name)
        msg = error["msg"]
        missing_fields.append(f"{field_name}: {msg}")
    
    # Raise custom exception with our format
    raise CustomException(
        status_code=422,
        message="Campos inválidos o faltantes: " + ", ".join(missing_fields),
        error_code="VALIDATION_ERROR"
    )


app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include the API routes, with a prefix to version the API as v1.
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
   
    uvicorn.run("main:app", host=ip_server, port=ip_port, reload=True)
