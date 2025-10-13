import weaviate
from sentence_transformers import SentenceTransformer
from weaviate.classes.query import MetadataQuery

class MedicalSearchEngine:
    def __init__(self):
        self.client = weaviate.connect_to_local(host = "localhost", port=8080)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self.client.collections.get("MedicalPaper")

    def semantic_search(self, query, limit=10):
        """Pure vector/semantic search"""
        query_vector = self.model.encode(query).tolist()

        response = self.collection.query.near_vector(
            near_vector=query_vector,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )

        return response.objects
    
    def keyword_search(self, query, limit = 10):
       """BM25 keyword search""" 
       response = self.collection.query.bm25(
           query=query,
           limit=limit,
           return_metadata=MetadataQuery(score=True)
       )
       
       return response.objects
    
    def hybrid_search(self, query, limit=10, alpha=0.5):
        """
        Hybrid search combining semantic + keyword
        alpha = 0.5 means equal weight
        alpha = 0.75 means more semantic, less keyword
        alpha - 0.25 means more keyword, less semantic
        """

        query_vector = self.model.encode(query).tolist()

        response = self.collection.query.hybrid(
            query=query,
            vector=query_vector,
            alpha=alpha, # 0 = pure BM25, 1 = pure vector
            limit=limit,
            return_metadata=MetadataQuery(score=True)
        )

        return response.objects
    
    def search_with_filters(self, query, year_from=None, limit = 10):
        """Search with filters (e.g., year)"""
        from weaviate.classes.query import Filter

        query_vector = self.model.encode(query).tolist()

        filters = None
        if year_from:
            filters = Filter.by_property("year").greater_or_equal(str(year_from))
        
        response = self.collection.query.hybrid(
            query=query,
            vector=query_vector,
            filters=filters,
            limit=limit,
            return_metadata=MetadataQuery(score = True)
        )

        return response.objects
    
    def display_results(self, results, show_abstract=True):
        """Pretty print results"""
        if not results:
            print("No results found.")
            return
        
        for i, obj in enumerate(results, 1):
            props = obj.properties

            print(f"\n{'='*80}")
            print(f"Result {i}")
            print(f"{'='*80}")
            print(f"Title: {props['title']}")
            print(f"Journal: {props['journal']}")
            print(f"Year: {props.get('year', 'Unknown')}")
            print(f"PMID: {props['pmid']}")

            #show score if available
            if obj.metadata.score:
                print(f"Score: {obj.metadata.score:.4f}")

            if show_abstract:
                abstract = props['abstract'][:300]
                print(f"\n Abstract: \n{abstract}{'...' if len(props['abstract']) > 300 else ''}")
    
    def compare_search_methods(self, query, limit=5):
        """compare all three search methods"""
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"\n{'='*80}")

        print("\n SEMANTIC SEARCH (pure vector)")
        semantic = self.semantic_search(query, limit)
        self.display_results(semantic, show_abstract=False)

        print("\n\n KEYWORD SEARCH(BM25):")
        keyword = self.keyword_search(query
        , limit)
        self.display_results(keyword, show_abstract=False) 

        print("\n\n HYBRID SEARCH (Best of Both):")
        hybrid = self.hybrid_search(query, limit)
        self.display_results(hybrid, show_abstract=False)
    
    def close(self):
        self.client.close()


# Test the Search Engine
if __name__ == "__main__":
    engine = MedicalSearchEngine()
    
    try:
        # Test Queries
        test_queries = [
            "How to cure diabetes naturally",
            "heart attack prevention",
            "covid vaccine side effects",
            "alzheimer's disease symptoms",
            "cancer immunotherapy"
        ]

        print("TESTING HYBRID SEARCH ENGINE")
        print("="*80)

        for query in test_queries:
            print(f"\n\nSearching: {query}")
            results = engine.semantic_search(query, limit=5, alpha=0.7)
            engine.display_results(results)

            input("\n Press Enter for next query....")
        
        # Compare methods
        print("\n\n" + "="*80)
        print( "COMPARING SEARCH METHODS")  
        print("="*80)
        engine.compare_search_methods("diabetes treatment", limit=3)

    finally:
        engine.close()
