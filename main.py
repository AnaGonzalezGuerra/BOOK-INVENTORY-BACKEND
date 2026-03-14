"""Main application entry point."""
# General libraries

# FastAPI associated libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# My imports
from routers.v1.routers import api_router
from config.config import Settings

settings = Settings()

app = FastAPI(docs_url="/docs", redoc_url="/redoc")
origins = settings.origins_list
ip_server, ip_port = settings.server_config

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
