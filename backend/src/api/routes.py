from fastapi import APIRouter, HTTPException, status
from typing import List 

from ..models.search import SearchRequest, SearchResponse, HealthResponse
from ..services.search_service import search_service

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """
    Search for medical papers
    
    -**query**: Search query string(required)
    -**mode**: Search mode - hybrid, semantic, or keyword(default: hybrid)
    -**limit**: Number of results to return (default: 10, max: 100)
    
    Returns list of matching papers with relevance scores
    """
    try:
        # Validate query
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        #perform search
        results, search_time = search_service.search(
            query=request.query.strip(),
            mode=request.mode,
            limit=request.limit
        )

        # Build response
        response = SearchResponse(
            results=results,
            total_count=len(results),
            query=request.query,
            mode=request.mode.value,
            search_time = round(search_time, 3)   
        )

        return response
    
    except Exception as e:
        print(f"Search API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns API and weaviate connection status
    """
    weaviate_connected = search_service.is_connected()
    if weaviate_connected:
        total_docs = search_service.get_total_documents()
        message = f"API is healthy. {total_docs} documents indexed in Weaviate."
    else:
        message = "API is running but Weaviate connection failed"
    
    return HealthResponse(
        status="healthy" if weaviate_connected else "degraded",
        weaviate_connected=weaviate_connected,
        message=message
    )

@router.get("/stats")
async def get_status():
    """
    Get search engine statistics
    Returns total document count and collection info
    """
    try:
        total_docs = search_service.get_total_documents()

        return {
            "total_documents": total_docs,
            "collection_name": "MedicalPaper",
            "Status": "active"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )