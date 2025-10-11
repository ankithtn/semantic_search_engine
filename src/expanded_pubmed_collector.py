from Bio import Entrez
import json
import time
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv()

Entrez.email = os.getenv("Email")

def search_pubmed(query, max_results=300):
    """Search Pubmed and get paper IDs"""
    try:
        handle = Entrez.esearch(db = "pubmed", term=query, retmax=max_results)
        results = Entrez.read(handle)
        return results["IdList"]
    except Exception as e:
        print(f"Error Searching for '{query}':{e}")
        return []

def fetch_abstract(id_list):
    """Get full abstracts for paper IDs"""
    papers = []

    # Process in batches of 20
    for i in range(0, len(id_list), 20):
        batch = id_list[i:i+20]

        try:
            handle = Entrez.efetch(db = "pubmed", id=batch, rettype = "abstract", retmode="xml")
            records = Entrez.read(handle)
            
            articles_to_process = []
            if 'PubmedArticle' in records:
                articles_to_process.extend(records['PubmedArticle'])
            
            for record in articles_to_process:
                try:
                    citation = record['MedlineCitation']
                    article = citation['Article']
                    pmid = str(citation['PMID'])

                    title = str(article.get('ArticleTitle', ''))

                    abstract_text = ""
                    if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                        abstract_sections = article['Abstract']['AbstractText']
                        if isinstance(abstract_sections, list):
                            abstract_text = " ".join([str(section) for section in abstract_sections])
                        else:
                            abstract_text = str(abstract_sections)

                    journal = "Unknown"
                    if "Journal" in article and 'Title' in article['Journal']:
                        journal = str(article['Journal']['Title'])
                    
                    # Get publication year
                    pub_year = "Unknown"
                    if 'Journal' in article and 'JournalIssue' in article['Journal']:
                        if 'PubDate' in article['Journal']['JournalIssue']:
                            pub_date = article['Journal']['JournalIssue']['PubDate']
                            pub_year = str(pub_date.get('Year', 'Unknown'))                        

                    if title and abstract_text and len(abstract_text) > 50:
                        paper = {
                            'title': title,
                            'abstract': abstract_text,
                            'pmid': pmid,
                            'journal': journal,
                            'year':pub_year
                        }
                        papers.append(paper)
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error fetching batch:{e}")
            continue

        time.sleep(0.4)
    return papers 

def collect_large_datasets():
    """Collect 3,000-5000 medical papers"""

    # Expanded medical topics - 25 topics * 200 papers = 5000 papers
    topics = [
        # Chronic diseases
        "diabetes mellitus treatment",
        "hypertension management",
        "heart failure therapy",
        "chronic kidney disease",
        "liver cirrhosis",
        

        # Cancer
        "breast cancer treatment",
        "lung cancer therapy",
        "colorectal cancer",
        "prostate cancer",
        "leukemia treatment",

        # Neurological 
        "alzheimer disease",
        "parkinson disease",
        "multiple sclerosis",
        "epilepsy treatment",
        "stroke rehabilitation",

        # Mental health
        "depression treatment",
        "anxiety disorders",
        "schizophrenia therapy",
        "bipolar disorder",
        "post traumatic stress disorder",

        # Infectious diseases
        "tuberculosis treatment",
        "HIV therapy",
        "hepatitis treatment",
        "malaria prevention",
        "COVID-19 treatment"
    ]

    all_papers = []

    print(f"Starting collection of ~{len(topics) * 200} papers...")
    print(f"This will take approximately {len(topics) * 2} minutes\n")
    

    for idx, topic in enumerate(topics, 1):
        print(f"[{idx}/{len(topics)}] Collecting: {topic}")

        try:
            ids = search_pubmed(topic, 200)
            print(f"Found {len(ids)} paper IDs")

            if ids:
                papers = fetch_abstract(ids)
                print(f"Extracted {len(papers)} papers with abstracts")
                all_papers.extend(papers)
            else:
                print(f"No papers found")
        except Exception as e:
            print(f"Error:{e}")
            continue
        
        print(f"Total collected so for: {len(all_papers)}\n")
    return all_papers

if __name__ == "__main__":
    print("="*60)
    print("MEDICAL PAPER COLLECTION - LARGE DATASET")
    print("="*60)

    papers = collect_large_datasets()

    if papers:
        # Remove duplicates by PMID
        unique_papers = {p['pmid']: p for p in papers}.values()
        unique_papers = list(unique_papers)
        
        # Save to file
        filename = 'medical_papers_large.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(unique_papers, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print(f"SUCCESS!")
        print(f"Total papers collected: {len(unique_papers)}")
        print(f"Saved to: {filename}")
        print("="*60)

        # Statistics
        journals = {}
        years = {}
        for paper in unique_papers:
            journals[paper['journal']] = journals.get(paper['journal'], 0) + 1
            years[paper['year']] = years.get(paper['year'], 0) + 1
        
        print(f"\n Top 5 Journals")
        for journal, count in sorted(journals.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"{journal}: {count} papers")

        print(f"\n Year Distribution:")
        for year in sorted(years.keys(), reverse=True)[:5]:
            print(f"{year}:{years[year]} papers")
    else:
        print("\n No papers collected. Check your internet connection.")