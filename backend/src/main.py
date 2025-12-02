from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config.settings import settings
from .api.routes import router
from .services.search_service import search_service
from .services.llm_service import initialize_llm_service

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
    
    # Initialize LLM service
    print("\n" + "="*50)
    print("Initializing LLM service for RAG...")
    print("="*50)
    llm_service = initialize_llm_service()

    if llm_service:
        print("LLM service initializsed successfully")
        print(f"Model: {llm_service.model}")
        print("RAG capabilities: ENABLED")
    else:
        print("LLM Service initialzation failed")
        print("RAG capabilities: DISABLED")
        print("System will work in search-only mode")
    print("="*50 + "\n")

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
    from .services.llm_service import get_llm_service
    llm_service = get_llm_service()

    return {
        "name": "Semantic Search API",
        "Version": "2.0.0",
        "Status": "running",
        "rag_enabled": llm_service is not None,
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