from Bio import Entrez
import json 
import time
from tqdm import tqdm
import os
from dotenv import load_dotenv
from medical_data_topics import vast_med_topics

load_dotenv

# Configuration
Entrez.email = os.getenv("EMAIL", "ankithtn2003@gmail.com")

# Target and files
TARGET_PAPERS =  100000
EXISTING_DATA_FILE = 'medical_papers_large.json'
NEW_DATA_FILE = 'medical_papers_100k.json'
CHECKPOINT_FILE = 'collection_checkpoint.json'
BATCH_SAVE_INTERVAL = 5000

MEDICAL_TOPICS = vast_med_topics

def load_existing_pmids():
    """Load PMIDs from existing data to avoid duplicates"""
    existing_pmids = set()

    if os.path.exists(EXISTING_DATA_FILE):
        print(f" Loading existing data from {EXISTING_DATA_FILE}...")
        try:
            with open(EXISTING_DATA_FILE, 'r', encoding='utf-8') as f:
                existing_papers = json.load(f)
                existing_pmids = {paper['pmid'] for paper in existing_papers if 'pmid' in paper}
                print(f" Found {len(existing_pmids)} existing PMIDs")
        except Exception as e:
            print(f"Error laoding existing data: {e}")
    
    return existing_pmids

def load_checkpoint():
    """Load checkpoint if exists"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                checkpoint = json.load(f)
                print(f" Resuming from checkpoint: {checkpoint['papers_collected']} papers collected")
                return checkpoint
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
    
    return {
        'papers_collected': 0,
        'last_topic_index': 0,
        'collected_pmids': []
    }

def save_checkpoint(checkpoint):
    """Save checkpoint"""
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    except Exception as e:
        print(f"Error saving checkpoint: {e}")


def search_pubmed(query, max_results=500):
    """Search Pubmed and get paper IDs"""
    try:
        handle = Entrez.esearch(
            db = "pubmed",
            term=query,
            retmax=max_results,
            sort="relevance"
        )
        results = Entrez.read(handle)
        handle.close()
        return results['IdList']
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return []
    

def fetch_abstracts(id_list, existing_pmids):
    """Get full abstracts for paper IDs, skip existing PMIDs"""
    papers = []

    # Filter out already collected PMIDs
    new_ids = [pmid for pmid in id_list if pmid not in existing_pmids]

    if not new_ids:
        return papers
    
    # Process in batches of 50
    for i in range(0, len(new_ids), 50):
        batch = new_ids[i:i+50]

        try:
            handle = Entrez.efetch(
                db="pubmed",
                id=batch,
                rettype="abstract",
                retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()

            # Process articles
            articles_to_process = []
            if 'PubmedArticle' in records:
                articles_to_process.extend(records['PubmedArticle'])

            for record in articles_to_process:
                try:
                    citation = record['MedlineCitation']
                    article = citation['Article']
                    pmid = str(citation['PMID'])

                    # Skip if already exists
                    if pmid in existing_pmids:
                        continue

                    title = str(article.get('ArticleTitle', ''))

                    # Extract abstract
                    abstract_text = ""
                    if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                        abstract_sections = article['Abstract']['AbstractText']
                        if isinstance(abstract_sections, list):
                            abstract_text = " ".join([str(section) for section in abstract_sections])
                        else:
                            abstract_text = str(abstract_sections)
                    
                    # Extract journal
                    journal = "Unknown"
                    if "Journal" in article and 'Title' in article['Journal']:
                        journal = str(article['Journal']['Title'])
                    
                    # Get publication year
                    pub_year = "Unknown"
                    if 'Journal' in article and 'JournalIssue' in article['Journal']:
                        if 'PubDate' in article['Journal']['JournalIssue']:
                            pub_date = article['Journal']['JournalIssue']['PubDate']
                            pub_year = str(pub_date.get('Year', 'Unknown'))
                    
                    # Only add if has good content
                    if title and abstract_text and len(abstract_text) > 50:
                        paper = {
                            'title': title,
                            'abstract': abstract_text,
                            'pmid': pmid,
                            'journal': journal,
                            'year': pub_year
                        }
                        papers.append(paper)
                        existing_pmids.add(pmid) 

                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error fetching batch: {e}")
            continue

        # Rate limiting
        time.sleep(0.5)

    return papers


def collect_papers_to_target():
    """Collect papers until target is reached"""
    
    # Load existing PMIDs to avoid duplicates
    existing_pmids = load_existing_pmids()
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    
    all_papers = []
    papers_collected = checkpoint['papers_collected']
    start_topic_index = checkpoint['last_topic_index']
    
    # Add previously collected PMIDs from checkpoint
    for pmid in checkpoint.get('collected_pmids', []):
        existing_pmids.add(pmid)
    
    print("\n" + "="*70)
    print(" MEDICAL PAPER COLLECTION - TARGET: 100K+ PAPERS")
    print("="*70)
    print(f"Already collected: {len(existing_pmids):,} papers")
    print(f"Target NEW papers: {TARGET_PAPERS:,}")
    print(f"Topics to search: {len(MEDICAL_TOPICS)}")
    print("="*70 + "\n")
    
    for idx, topic in enumerate(MEDICAL_TOPICS):
        # Skip already processed topics
        if idx < start_topic_index:
            continue
        
        # Check if target reached
        if papers_collected >= TARGET_PAPERS:
            print(f"\nTARGET REACHED! Collected {papers_collected:,} NEW papers")
            break
        
        print(f"\n[{idx+1}/{len(MEDICAL_TOPICS)}] Searching: {topic}")
        
        try:
            # Search with higher limit for 100K collection
            ids = search_pubmed(topic, max_results=500)
            print(f"Found {len(ids)} paper IDs")
            
            if ids:
                papers = fetch_abstracts(ids, existing_pmids)
                
                if papers:
                    all_papers.extend(papers)
                    papers_collected += len(papers)
                    
                    print(f"Extracted {len(papers)} NEW papers with abstracts")
                    print(f"Progress: {papers_collected:,} / {TARGET_PAPERS:,} ({papers_collected/TARGET_PAPERS*100:.1f}%)")
                    
                    # Update checkpoint
                    checkpoint['papers_collected'] = papers_collected
                    checkpoint['last_topic_index'] = idx
                    checkpoint['collected_pmids'] = list(existing_pmids)
                    save_checkpoint(checkpoint)
                    
                    # Save intermediate results every 5K papers
                    if papers_collected % BATCH_SAVE_INTERVAL == 0:
                        print(f"\n💾 Checkpoint: Saving {len(all_papers):,} papers...")
                        save_papers_to_file(all_papers, NEW_DATA_FILE)
                else:
                    print(f"No new papers extracted (all duplicates)")
            else:
                print(f"No papers found")
                
        except Exception as e:
            print(f" Error: {e}")
            continue
    
    return all_papers

def save_papers_to_file(papers, filename):
    """Save papers to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(papers):,} papers to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")

def print_statistics(papers):
    """Print collection statistics"""
    print("\n" + "="*70)
    print("COLLECTION STATISTICS")
    print("="*70)
    
    # Journal stats
    journals = {}
    for paper in papers:
        journal = paper.get('journal', 'Unknown')
        journals[journal] = journals.get(journal, 0) + 1
    
    print(f"\nTop 10 Journals:")
    for journal, count in sorted(journals.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f" {journal}: {count:,} papers")
    
    # Year stats
    years = {}
    for paper in papers:
        year = paper.get('year', 'Unknown')
        years[year] = years.get(year, 0) + 1
    
    print(f"\nYear Distribution (Top 10):")
    for year in sorted(years.keys(), reverse=True)[:10]:
        print(f"   {year}: {years[year]:,} papers")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("MEDICAL PAPER COLLECTION - ENHANCED VERSION")
    print("="*70)
    
    papers = collect_papers_to_target()
    
    if papers:
        # Save final results
        print(f"\nSaving final dataset...")
        save_papers_to_file(papers, NEW_DATA_FILE)
        
        # Print statistics
        print_statistics(papers)
        
        print("\n" + "="*70)
        print("SUCCESS!")
        print(f"New papers file: {NEW_DATA_FILE}")
        print(f"Original papers: {EXISTING_DATA_FILE}")
        print(f"Total NEW papers: {len(papers):,}")
        print("="*70)
        
        # Clean up checkpoint
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
            print("Checkpoint file removed")
    else:
        print("\nNo papers collected. Check your internet connection.")