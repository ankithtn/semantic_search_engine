import weaviate
from sentence_transformers import SentenceTransformer
from weaviate.classes.query import MetadataQuery
from typing import List, Dict, Any
import time

from ..models.search import SearchResult, SearchMode
from ..config.settings import settings

class SearchService:
    """Service for handling serach operations with weaviate"""

    def __init__(self):
        self.client = None
        self.model = None
        self.collection = None
        self._initialize()

    def _initialize(self):
        """Initialize Weaviate client and embedding model"""
        try:
            # Connect to Weaviate
            self.client = weaviate.connect_to_local(
                host=settings.WEAVIATE_HOST,
                port=settings.WEAVIATE_PORT
            )

            # Load embedding model
            print("Loading embedding model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Embedding model loaded successfully.")

            # Get Collection 
            self.collection = self.client.collections.get("MedicalPaper")
            
            print("Weaviate connection established successfully.")
        except Exception as e:
            print(f"Error initializing search servie: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if Weaviate is connected"""
        try:
            return self.client.is_ready()
        except:
            return False
        
    def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.HYBRID,
        limit: int = 10
    )  -> tuple[list[SearchResult], float]:
        """
        Perform search based on mode

        Args:
            query: Search query string
            mode: Search mode (hybrid, semantic, or keyword)
            limit: Number of  results to return

        Returns:
            Tuple of (results list, search time in seconds)
        """
        start_time = time.time()

        try:
            if mode == SearchMode.SEMANTIC:
                results = self._semantic_search(query, limit)
            elif mode == SearchMode.KEYWORD:
                results = self._keyword_search(query, limit)
            else:
                results = self._hybrid_search(query, limit)
            
            search_time = time.time() - start_time

            # convert to SearchResult models
            search_results = self._format_results(results)

            return search_results, search_time
        
        except Exception as e:
            print(f"Search error: {e}")
            raise Exception(f"Search failed: {str(e)}")
    
    def _semantic_search(self, query: str, limit: int) -> List[Any]:
        """Pure vector/semanitc search"""
        query_vector = self.model.encode(query).tolist()

        response = self.collection.query.near_vector(
            near_vector=query_vector,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )

        return response.objects
    
    def _keyword_search(self, query: str, limit: int) -> List[Any]:
        """BM25 keyword search"""
        response = self.collection.query.bm25(
            query=query,
            limit=limit,
            return_metadata=MetadataQuery(score=True)
        )
            
        return response.objects
    
    def _hybrid_search(self, query: str, limit: int, alpha: float = 0.7) -> List[Any]:
        """
        Hybrid search combining semantic + keyword
        alpha = 0.7 mean 70% semantic, 30% keyword
        """

        query_vector = self.model.encode(query).tolist()

        response = self.collection.query.hybrid(
            query = query,
            vector=query_vector,
            alpha=alpha,
            limit=limit,
            return_metadata=MetadataQuery(score=True)
        )

        return response.objects
    
    def _format_results(self, results: List[Any]) -> List[SearchResult]:
        """Format Weaviate results to searchresult models"""
        formatted_results = []

        for obj in results:
            props = obj.properties

            # Get score (from distance or score metadata)
            score = None
            if hasattr(obj.metadata, 'score') and obj.metadata.score:
                score = obj.metadata.score
            elif hasattr(obj.metadata, 'distance') and obj.metadata.distance:
                # Convert distance to similarity score
                score = 1 - obj.metadata.distance
            
            # Create searchresult
            result = SearchResult(
                title=props.get('title', ''),
                abstract=props.get('abstract', ''),
                pmid=props.get('pmid', ''),
                journal=props.get('journal', ''),
                year=props.get('year', ''),
                score=score
            )

            formatted_results.append(result)
        
        return formatted_results
    
    def get_total_documents(self) -> int:
        """Get total number of documents in collection"""
        try:
            response = self.collection.aggregate.over_all(total_count=True)
            return response.total_count
        except:
            return 0
        
    def close(self):
        """Close Weaviate connection"""
        if self.client:
            self.client.close()

# Global instance 
search_service = SearchService()



      





