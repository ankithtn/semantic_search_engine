from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config.settings import settings
from .api.routes import router
from .services.search_service import search_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown"""
    # startup
    print("Starting semantic search API...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Weaviate: {settings.WEAVIATE_HOST}:{settings.WEAVIATE_PORT}")

    # Check Weaviate connection
    if search_service.is_connected():
        total_docs = search_service.get_total_documents()
        print(f"Connected to weaviate -{total_docs} documents indexed")
    else:
        print("Warning: Weavaite connection failed")

    yield

    # Shutdown
    print("Shutting down semantic search API...")
    search_service.close()

# Create FastAPI app
app = FastAPI(
    title="Semantic Search API",
    description="Medical research papers semantic search engine",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers
app.include_router(router, prefix="/api", tags=["search"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Semantic Search API",
        "Version": "1.0.0",
        "Status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )