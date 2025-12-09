from fastapi import APIRouter, HTTPException, status
from typing import List 

from ..models.search import (
    SearchRequest, 
    SearchResponse,
    UnifiedSearchResponse,
    AIAnswer,    
    HealthResponse 
)
from ..services.search_service import search_service
from ..services.llm_service import get_llm_service


router = APIRouter()

@router.post("/search", response_model=UnifiedSearchResponse)
async def unified_search(request: SearchRequest):
    """
    UNIFIED RAG-ENABLED SEARCH ENDPOINT

    This endpoint combines traditional search with AI-powered answer generation.
    For every query, it:
    1. Retrieves relevant papers using selected mode (semantic/hybrid/keyword)
    2. Autmatically generates an AI answer based on retrieved papers
    3. Returns Both the papers list and the AI-generated answer
    
    Args:
        -query: Search query string(required)
        -mode: Search mode - hybrid, semantic, or keyword(default: hybrid)
        -limit: Number of results to return (default: 10, max: 100)
    
    Returns:
        list of matching papers with papers, AI answer, and metdata
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

        # Generate AI answer using LLM
        llm_service = get_llm_service()
        ai_answer = None
        papers_analyzed = 0
        
        if llm_service and len(results) > 0:
            try:
                print(f"Generating AI answer from top {min(10, len(results))} papers...")

                # Generate anwer from top 5 papers
                llm_response = llm_service.generate_answer(
                    query = request.query.strip(),
                    papers=results[:10],
                    max_papers=10
                )

                ai_answer = AIAnswer(
                    answer=llm_response["answer"],
                    model=llm_response["model"],
                    tokens_used=llm_response.get("tokens_used", 0),
                    generation_time=llm_response["generation_time"],
                    error=llm_response.get("error")
                )
                papers_analyzed = min(5, len(results))

                print(f"AI answer generated in {llm_response['generation_time']:.2f}s")
                print(f"  Model: {llm_response['model']}")
                print(f"  Tokens: {llm_response.get('tokens_used', 0)}")
            
            except Exception as e:
                print(f"LLM generation failed: {e}")
                # if crashed - just return results without AI answer
                ai_answer = AIAnswer(
                    answer=f"AI answer generation is currently unavailable: {str(e)}",
                    model="error",
                    tokens_used=0,
                    generation_time=0.0,
                    error=str(e)
                )
        elif not llm_service:
            print("LLM service not available - returning search results only")
        elif len(results) == 0:
            print(" No papers found - cannot generate AI answer")


        # Build response
        response = UnifiedSearchResponse(
            query=request.query,
            mode=request.mode.value,
            results=results,
            total_count=len(results),
            search_time=round(search_time, 3),
            ai_answer=ai_answer,
            papers_analyzed=papers_analyzed,
            rag_enabled=llm_service is not None 
        )
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Search API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
    
# LEGACY ENDPOINT -  for backward compatibility
@router.post("/search/legacy", response_model=SearchResponse)
async def legacy_search(request: SearchRequest):
    """
    Legacy search endpoint without RAG (for backward compatibility)
    Returns only papers list without AI-generated answer
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        results, search_time = search_service.search(
            query=request.query.strip(),
            mode=request.mode,
            limit=request.limit
        )

        response = SearchResponse(
            results=results,
            total_count=len(results),
            query=request.query,
            mode=request.mode.value,
            search_time=round(search_time, 3)   
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
    Returns API, weaviate, and LLM connection status
    """
    weaviate_connected = search_service.is_connected()
    llm_service = get_llm_service()
    llm_connected = llm_service is not None

    if weaviate_connected and llm_connected:
        total_docs = search_service.get_total_documents()
        message = f"API is healthy. {total_docs} documents indexed. RAG enabled"
        status_text = "healthy"
    elif weaviate_connected and not llm_connected:
        total_docs = search_service.get_total_documents()
        message = f"API is running. {total_docs} documents indexed. RAG disabled(LLM not available)"
        status_text = "degraded"
    else:
        message = "API is running but weaviate connection failed"
        status_text = "degraded"

    return HealthResponse(
        status=status_text,
        weaviate_connected=weaviate_connected,
        llm_connected=llm_connected,
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
        llm_service = get_llm_service

        return {
            "total_documents": total_docs,
            "collection_name": "MedicalPaper",
            "Status": "active",
            "rag_enabled": llm_service is not None,
            "llm_model": llm_service.model if llm_service else None
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )