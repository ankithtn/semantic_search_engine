import weaviate
from weaviate.classes.query import MetadataQuery
from sentence_transformers import SentenceTransformer
import json


class MedicalSearchEngine:
    def __init__(self):
        self.client = weaviate.connect_to_local()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def search(self, query, limit=10):
        """Perform semantic search"""
        print(f"Searching for: {query}")

        with weaviate.connect_to_local() as self.client:
            # Create query embedding
            query_vector = self.model.encode(query).tolist()

            # Get Collection
            collection = self.client.collections.get("MedicalPaper")

            #search Weaviate
            response= (
                collection.query
                .near_vector(
                    near_vector=query_vector,
                    limit=limit,
                    return_properties=["title", "abstract", "pmid", "journal"],
                    return_metadata=MetadataQuery(distance=True)   
                )
            )
            
            # Format results to match old structure
            results = []
            
            for obj in response.objects:
                res = obj.properties
                res['_additional'] = {'distance': obj.metadata.distance}
                results.append(res)
            return results


    def display_results(self, results):
        """Pretty print search results"""
        if not results:
            print("No results found.")
            return
            
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {result['title']}")
            print(f"Journal: {result['journal']}")
            print(f"PMID: {result['pmid']}")
            
            # Show similarity score if available
            if '_additional' in result and 'distance' in result['_additional']:
                similarity = 1 - result['_additional']['distance']
                print(f" Similarity: {similarity:.3f}")
            
            # Show first 300 chars of abstract
            abstract = result['abstract'][:300]
            print(f" Abstract: {abstract}{'...' if len(result['abstract']) > 300 else ''}")
            print("-" * 80)

# Test search engine
if __name__ == "__main__":
    search_engine = MedicalSearchEngine()
    
    # Test queries
    test_queries = [
        "diabetes treatment diet exercise",
        "covid vaccine effectiveness",
        "heart disease prevention",
        "cancer immunotherapy",
        "mental health depression"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        results = search_engine.search(query, limit=3)
        search_engine.display_results(results)
        
        input("Press Enter for next query...")
