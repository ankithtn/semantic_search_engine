import weaviate
import json

client = weaviate.connect_to_local()

try:
    collections = client.collections.list_all()
    print(f"Collections found: {list(collections.keys())}")

    collection_name = "MedicalPaper" 
    collection = client.collections.get(collection_name)

    # We limit to 5 
    response = collection.query.fetch_objects(
        limit=5,
        include_vector=True
    )

    print(f"\n--- Data in {collection_name} ---")

    for obj in response.objects:
        print(f"\nID: {obj.uuid}")
        print(f"Properties: {json.dumps(obj.properties, indent=2)}")
        
        vector = obj.vector["default"] if isinstance(obj.vector, dict) else obj.vector
        
        if vector:
            print(f"Vector (first 5 dims): {vector[:5]}... (Total dims: {len(vector)})")
        else:
            print("Vector: [No vector stored for this object]")

finally:
    client.close()
