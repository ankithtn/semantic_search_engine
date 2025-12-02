from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SearchMode(str, Enum):
    """Search mode options"""
    HYBRID = "hybrid"
    SEMANTIC = "semantic"
    KEYWORD = "keyword"

class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, max_length=500, description="search_query")
    mode: SearchMode = Field(SearchMode.HYBRID, description="search_mode")
    limit: int = Field(default=10, ge=1, le=100, description="Number of results to return")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "diabetes treatment",
                "mode": "hybrid",
                "limit": 10
            }
        }
class SearchResult(BaseModel):
    """Individual search result model"""
    title: str
    abstract: str
    pmid: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[str] = None
    score: Optional[float] = None

    class Config:
        json_schema_extra = {
           "example": {
               "title": "Diabetes Management Through Diet and Exercise",
               "abstract": "Type 2 diabetes affects millions worldwide...",
               "pmid": "12345678",
               "journal": "Journal of Diabetes Care",
               "year": "2023",
               "Score": 0.95
           } 
        }
class SearchResponse(BaseModel):
    """Search response model"""
    results: List[SearchResult]
    total_count: int
    query: str
    mode: str
    search_time: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "results": [],
                "total_count": 245,
                "query": "diabetes treatment",
                "mode": "hybrid",
                "search_time": 0.43
            }
        }

# New modles for RAG

class AIAnswer(BaseModel):
    """AI-generated answer model"""
    answer: str = Field(..., description="AI-generated answer with citations")
    model: str = Field(..., description="LLM model used")
    tokens_used: int = Field(0, description="Number of tokens used")
    generation_time: float = Field(..., description="Time taken to generate answer in seconds")
    error: Optional[str] = Field(None, description="Error message if generation failed")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on recent research, diabetes treatments include...[1][2]",
                "model": "llama-3.1-70b-versatile",
                "tokens_used": 856,
                "generation_time": 1.234,
                "error": None
            }
        }

class UnifiedSearchResponse(BaseModel):
    """
    Unified response containing both search results AND AI-generated answer
    This is the NEW response format that includes RAG capabilities
    """
    # Original search fields
    query:str = Field(..., description="Original user query")
    mode:str = Field(...,description="Search mode used (semantic/hybrid/keyword)")

    # Search results
    results: List[SearchResult] = Field(..., description="List of retrieved papers")
    total_count: int = Field(..., description="Total number of results")
    search_time: float = Field(..., description="Time taken for search in seconds")

    # AI-generated answer
    ai_answer: Optional[AIAnswer] = Field(None, description="AI-generated answer based on retrieved papers")

    # Metadata
    papers_analyzed: int = Field(0, description="Number of papers sent to LLM")
    rag_enabled: bool = Field(True, description="whether RAG was used")
    
    class config:
        json_schema_extra = {
            "example": {
                "query": "What are the latest diabetes treatment",
                "mode": "hybrid",
                "results": [],
                "total_count": 10,
                "search_time": 0.234,
                "ai_answer": {
                    "answer": "Recent treatments include...[1][2]",
                    "model": "llama-3.1-70b-versatile",
                    "tokens_used": 856,
                    "generation_time": 1.234
                },
                "papers_analyzed": 5,
                "rag_enabled": True
            }
        }

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    weaviate_connected: bool
    message: str