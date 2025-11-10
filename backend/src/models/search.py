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

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    weaviate_connected: bool
    message: str