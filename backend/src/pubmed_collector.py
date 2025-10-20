from Bio import Entrez
import json
import time

Entrez.email = "" 

def search_pubmed(query, max_results=500):
    """Search PubMed and get paper IDs"""
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    results = Entrez.read(handle)
    return results["IdList"]

def fetch_abstracts(id_list):
    """Get full abstracts for paper IDs"""
    papers = []
    
    # Processing in batches of 20 (NCBI limit)
    for i in range(0, len(id_list), 20):
        batch = id_list[i:i+20]
        print(f"Processing batch {i//20 + 1}, IDs: {batch[:3]}...")
        
        try:
            handle = Entrez.efetch(db="pubmed", id=batch, rettype="abstract", retmode="xml")
            records = Entrez.read(handle)
            
            # Handling both PubmedArticle and PubmedBookArticle
            articles_to_process = []
            
            if 'PubmedArticle' in records:
                articles_to_process.extend(records['PubmedArticle'])
            if 'PubmedBookArticle' in records:
                articles_to_process.extend(records['PubmedBookArticle'])
            
            print(f"Found {len(articles_to_process)} articles in this batch")
            
            for record in articles_to_process:
                try:
                    # Handle different record structures
                    if 'MedlineCitation' in record:
                        citation = record['MedlineCitation']
                        article = citation['Article']
                        pmid = str(citation['PMID'])
                    elif 'BookDocument' in record:
                        # Handle book articles differently
                        continue
                    else:
                        continue
                    
                    # Extract title
                    title = ""
                    if 'ArticleTitle' in article:
                        title = str(article['ArticleTitle'])
                    
                    # Extract abstract with better error handling
                    abstract_text = ""
                    if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                        abstract_sections = article['Abstract']['AbstractText']
                        if isinstance(abstract_sections, list):
                            abstract_text = " ".join([str(section) for section in abstract_sections])
                        else:
                            abstract_text = str(abstract_sections)
                    
                    # Extract journal info
                    journal = "Unknown"
                    if 'Journal' in article and 'Title' in article['Journal']:
                        journal = str(article['Journal']['Title'])
                    
                    # Only add papers with both title and abstract
                    if title and abstract_text and len(abstract_text) > 50:
                        paper = {
                            'title': title,
                            'abstract': abstract_text,
                            'pmid': pmid,
                            'journal': journal
                        }
                        papers.append(paper)
                        print(f"Added paper: {title[:50]}...")
                
                except Exception as e:
                    print(f"Error processing individual record: {e}")
                    continue
        
        except Exception as e:
            print(f"Error fetching batch: {e}")
            continue
        
        time.sleep(0.5)
    
    return papers

def collect_medical_papers():
    """Main function to collect papers"""
    # Medical topics that usually have good abstracts
    topics = [
        "diabetes treatment",
        "hypertension management", 
        "cancer therapy",
        "mental health intervention",
        "cardiac surgery"
    ]
    
    all_papers = []
    
    for topic in topics:
        print(f"\n--Collecting papers for: {topic} --")
        try:
            ids = search_pubmed(topic, 100)  # 100 papers per topic
            print(f"Found {len(ids)} paper IDs")
            
            if ids:
                papers = fetch_abstracts(ids)
                print(f"Successfully extracted {len(papers)} papers with abstracts")
                all_papers.extend(papers)
            
        except Exception as e:
            print(f"Error with topic '{topic}': {e}")
            continue
    
    return all_papers


if __name__ == "__main__":
    print("Starting medical paper collection...")
    papers = collect_medical_papers()
    
    if papers:
        # Save to file
        with open('medical_papers.json', 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        print(f"\n SUCCESS! Collected {len(papers)} medical papers")
        
      