import weaviate
from weaviate.classes.config import Configure, Property, DataType
from sentence_transformers import SentenceTransformer
import json
from tqdm import tqdm

# Initialize embedding model
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to Weaviate (local Docker) 
with weaviate.connect_to_local() as client:
    print("Connected to Weaviate!")

def create_schema(client):
    # Delete existing collection if it exists
    if client.collections.exists("MedicalPaper"):
        client.collections.delete("MedicalPaper")
        print("Deleted existing collection")

    # Define collection configuration
    client.collections.create(
        name="MedicalPaper",
        description="Medical research papers and abstracts",
        vector_config=Configure.Vectors.self_provided(),  # We provide our own embeddings
        properties=[
            Property(
                name="title", 
                data_type=DataType.TEXT, 
                description="Paper title"
            ),
            Property(
                name="abstract", 
                data_type=DataType.TEXT, 
                description="Paper abstract content"
            ),
            Property(
                name="pmid", 
                data_type=DataType.TEXT, 
                description="PubMed ID"
            ),
            Property(
                name="journal", 
                data_type=DataType.TEXT, 
                description="Journal name"
            ),
        ]
    )
    print("Schema or collection created!")

def upload_papers(client):
    """Upload papers with embeddings to Weaviate"""
    # Load collected papers
    with open('medical_papers_large.json', 'r', encoding='utf-8') as f:
        papers = json.load(f)

    print(f"Uploading {len(papers)} papers to Weaviate...")
    successful_uploads = 0
    collection = client.collections.get("MedicalPaper")

    # Configure batch 
    with collection.batch.dynamic() as batch:
        for paper in tqdm(papers, desc="Creating embeddings and uploading"):
            try:
                # Create text for embedding (title + abstract)
                text_for_embedding = f"{paper['title']} {paper['abstract']}"

                # Generate embedding
                vector = model.encode(text_for_embedding).tolist()

                # Add to batch
                batch.add_object(
                    properties={
                        "title": paper["title"],
                        "abstract": paper["abstract"],
                        "pmid": paper["pmid"],
                        "journal": paper["journal"],
                        "year": paper.get("year", "Unkown")
                    },
                    vector=vector
                )
                successful_uploads += 1
            except Exception as e:
                print(f"Error uploading paper: {e}")
                continue
    print(f"Successfully uploaded {successful_uploads} papers!")
    return successful_uploads



if __name__ == "__main__":
    # Use context manager for Weaviate client
    with weaviate.connect_to_local() as client:
        print("Setting up Weaviate schema...")
        create_schema(client)

        print("\nUploading papers with embeddings...")
        count = upload_papers(client)

        # Test the upload
        collection = client.collections.get("MedicalPaper")
        result = collection.aggregate.over_all(total_count=True)
        total_count = result.total_count
        print(f" Vector Database contains {total_count} papers!")