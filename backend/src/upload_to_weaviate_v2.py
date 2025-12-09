import weaviate
from sentence_transformers import SentenceTransformer
import json
from tqdm import tqdm
import time

# Configuration
NEW_DATA_FILE = 'data/medical_papers_100k.json' 
EXISTING_DATA_FILE = 'medical_papes_large.json'
BATCH_SIZE = 100
EMBEDDING_BATCH_SIZE = 32

print("="*70)
print("Weaviate uploader")
print("="*70)

# Initialize embedding model
print("\n Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model Loaded: all-MiniLM-L6-v2")

print("\n Connecting to weaviate...")
client = weaviate.connect_to_local()

if not client.is_ready():
    print("Weaviate is not ready")
    exit(1)

print("Connected to weaviate")

def get_existing_pmids():
    """Get all PMIDs already in weaviate to avoid duplicate"""
    print("\n Checking existing papers in weaviate...")

    try:
        collection = client.collections.get("MedicalPaper")
        existing_pmids = set()

        # Fetch all PMIDs in batches
        offset = 0
        batch_size = 1000

        with tqdm(desc="Scanning database") as pbar:
            while True:
                response = collection.query.fetch_objects(
                    limit=batch_size,
                    offset=offset,
                    return_properties=["pmid"]
                )

                if not response.objects:
                    break

                for obj in response.objects:
                    if obj.properties.get('pmid'):
                        existing_pmids.add(obj.properties['pmid'])
                
                pbar.update(len(response.objects))
                offset += batch_size

                # Stop if it got less than batch_size (end of data)
                if len(response.objects) < batch_size:
                    break

        print(f"Found {len(existing_pmids):,} existing papers in database")
        return existing_pmids
    except Exception as e:
        print(f"Error checking existing papers: {e}")
        return set()
    
def load_papers_from_file(filename):
    """Load papers from json file"""
    print(f"\n Loading papers from {filename}...")

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        print(f"Loaded {len(papers):,} papers from file")
        return papers
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return []
    except Exception as e:
        print(f"Errror loading file: {e}")
        return []
    
def filter_new_papers(papers, existing_pmids):
    """Filter out papers that already exist in Weaviate"""
    print(f"\n Filtering for new papers...")

    new_papers = []
    duplicates = 0

    for paper in papers:
        pmid = paper.get('pmid', '')
        if pmid and pmid not in existing_pmids:
            new_papers.append(paper)
        else:
            duplicates += 1
    
    print(f"Found {len(new_papers):,} new papers to upload")
    print(f"Skipped {duplicates:,} duplicates")

    return new_papers

def upload_papers_batch(papers):
    """Upload papers to weaviate with embeddings in batches"""
    print(f"\n Starting upload of {len(papers):,} papers...")
    print(f"Batch size: {BATCH_SIZE}")
    print("="*70)

    collection = client.collections.get("MedicalPaper")

    successful_uploads = 0
    failed_uploads = 0

    # Process in batches
    total_batches = (len(papers) + BATCH_SIZE - 1) // BATCH_SIZE
    
    with tqdm(total=len(papers), desc="Uploading papers") as pbar:
        for batch_idx in range(0, len(papers), BATCH_SIZE):
            batch = papers[batch_idx:batch_idx + BATCH_SIZE]

            try:
                # Prepare texts for embedding
                texts = []
                for paper in batch:
                    text = f"{paper['title']} {paper['abstract']}"
                    texts.append(text)

                # Generate embeddings in sub-batches for memory efficiency 
                vectors = []
                for j in range(0, len(texts), EMBEDDING_BATCH_SIZE):
                    sub_batch = texts[j:j + EMBEDDING_BATCH_SIZE]
                    sub_vectors = model.encode(sub_batch).tolist()
                    vectors.extend(sub_vectors)
                
                # Prepare objects for weaviate
                with collection.batch.dynamic() as weaviate_batch:
                    for paper, vector in zip(batch, vectors):
                        try:
                            weaviate_batch.add_object(
                                properties={
                                    "title": paper["title"],
                                    "abstract": paper["abstract"],
                                    "pmid": paper.get("pmid", ""),
                                    "journal": paper.get("journal", ""),
                                    "year": paper.get("year", "Unknown")
                                },
                                vector=vector
                            )
                            successful_uploads += 1
                        except Exception as e:
                            failed_uploads += 1
                            continue
                
                pbar.update(len(batch))

                # Progress report every 10 batches
                if (batch_idx // BATCH_SIZE + 1) % 10 == 0:
                    pbar.set_postfix({
                        'success': successful_uploads,
                        'failed': failed_uploads
                    })

            except Exception as e:
                print(f"\n Batch upload error: {e}")
                failed_uploads += len(batch)
                pbar.update(len(batch))
                time.sleep(1)
                continue

    print("\n" + "="*70)
    print("Upload Complete!!")
    print(f"Successfully uploaded: {successful_uploads:,}")
    print(f"Failed: {failed_uploads}")
    print("="*70)

    return successful_uploads, failed_uploads

def verify_upload():
    """Verify final count in Weaviate"""
    print("\n Verifying upload...")

    try:
        collection = client.collections.get("MedicalPaper")
        result = collection.aggregate.over_all(total_count=True)
        total_count = result.total_count
        
        print(f"Total papers in Weaviate: {total_count:,}")
        return total_count
    except Exception as e:
        print(f"Error verifying: {e}")
        return 0
    
def main():
    """Main execution flow"""
    
    # Step 1: Get existing PMIDs from Weaviate
    existing_pmids = get_existing_pmids()
    
    # Step 2: Load new papers from file
    papers = load_papers_from_file(NEW_DATA_FILE)
    
    if not papers:
        print("\n No papers to upload")
        return
    
    # Step 3: Filter out duplicates
    new_papers = filter_new_papers(papers, existing_pmids)
    
    if not new_papers:
        print("\n All papers already in database!")
        verify_upload()
        return
    
    # Step 4: Upload new papers
    successful, failed = upload_papers_batch(new_papers)
    
    # Step 5: Verify final count
    final_count = verify_upload()
    
    # Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Papers in file: {len(papers):,}")
    print(f"Duplicates skipped: {len(papers) - len(new_papers):,}")
    print(f"New papers uploaded: {successful:,}")
    print(f"Upload failures: {failed}")
    print(f"Total in database: {final_count:,}")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    finally:
        print("\n Closing Weaviate connection...")
        client.close()
        print("Done!")