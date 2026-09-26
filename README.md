# SemSearchNet

A semantic search engine for medical research papers, combining vector search over PubMed abstracts with a Retrieval-Augmented Generation (RAG) layer that turns search results into a cited, AI-generated answer.

The system collects abstracts from PubMed, embeds them with a sentence-transformer model, stores them in [Weaviate](https://weaviate.io/), and exposes semantic, keyword (BM25), and hybrid search through a FastAPI backend. Every search can optionally be passed through an LLM (via [Groq](https://groq.com/)) to produce a synthesized answer with inline `[1][2]`-style citations back to the source papers.

## Features

- **Three search modes** — pure vector (semantic), BM25 (keyword), and a weighted hybrid of both
- **RAG-powered answers** — top results are fed to an LLM (Llama 3.3 70B via Groq) which generates a cited answer; falls back gracefully to search-only mode if no LLM key is configured
- **PubMed data pipeline** — resumable collector (via Biopython/Entrez) that can pull 100k+ abstracts across ~150 medical topics, with checkpointing and duplicate (PMID) detection
- **Vector store** — [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) sentence-transformer embeddings, self-provided into Weaviate (no built-in vectorizer module needed)
- **FastAPI backend** — typed request/response models (Pydantic), auto-generated OpenAPI docs, health/stats endpoints
- **React frontend** — mode switcher, expandable result cards, and a dedicated AI-answer panel, built with Vite + Tailwind CSS

## Architecture

```
PubMed (NCBI Entrez)
       │  pubmed_collector / expanded_pubmed_collector_v2.py
       ▼
 medical_papers*.json (title, abstract, pmid, journal, year)
       │  upload_to_weaviate(_v2).py
       │  → embeds each paper with all-MiniLM-L6-v2
       ▼
   Weaviate ("MedicalPaper" collection)
       │  semantic / BM25 / hybrid query
       ▼
 FastAPI  (search_service.py) ──► optional ──► llm_service.py ──► Groq API
       │                                                              │
       ▼                                                              ▼
  papers list  ◄──────────────────────────────────  AI answer + citations
       │
       ▼
  React frontend (SemSearchNet UI)
```

## Tech Stack

**Backend**

| Component | Library |
|---|---|
| API framework | FastAPI + Uvicorn |
| Vector database | Weaviate (`weaviate-client` v4) |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| LLM / RAG | Groq API (`llama-3.3-70b-versatile` by default) |
| Data collection | Biopython (`Bio.Entrez`, PubMed) |
| Config | `python-dotenv` |

**Frontend**

| Component | Library |
|---|---|
| Framework | React 19 + Vite |
| Styling | Tailwind CSS (+ shadcn/ui config, `class-variance-authority`, `tailwind-merge`) |
| HTTP client | Axios |
| Icons | lucide-react |

## Project Structure

```
semantic_search_engine/
├── backend/
│   ├── requirements.txt
│   ├── run.sh                        # starts uvicorn dev server
│   ├── data/                         # data files (gitignored, kept via .gitignore exception)
│   └── src/
│       ├── main.py                   # FastAPI app, lifespan startup, CORS
│       ├── api/routes.py             # /search, /search/legacy, /health, /stats
│       ├── models/search.py          # Pydantic request/response schemas
│       ├── config/settings.py        # env-driven settings (Weaviate, Groq, CORS)
│       ├── services/
│       │   ├── search_service.py     # Weaviate connection + semantic/keyword/hybrid search
│       │   └── llm_service.py        # Groq RAG answer generation
│       ├── pubmed_collector.py               # original/simple PubMed collector
│       ├── expanded_pubmed_collector.py      # intermediate collector
│       ├── expanded_pubmed_collector_v2.py   # resumable, checkpointed 100k-paper collector
│       ├── medical_data_topics.py            # ~150 PubMed search topics used by the collector
│       ├── upload_to_weaviate.py             # (v1) creates schema + uploads embeddings
│       ├── upload_to_weaviate_v2.py          # (v2) incremental/dedup upload to existing schema
│       ├── hybrid_search.py, search.py       # standalone CLI scripts used during development
│       └── data_viewer.py                   # quick CLI inspector for the Weaviate collection
└── frontend/
    └── src/
        ├── App.jsx                   # active entry point (see index.html → main.jsx)
        ├── api/searchAPI.js          # axios client for the backend API
        ├── hooks/useSearch.js        # search state + API call orchestration
        └── components/               # SearchBar, ModeSelector, ResultCard, ResultsList,
                                       # AIAnswerCard, LoadingSpinner, ErrorMessage
```

> Note: `frontend/src` also contains `App.tsx` / `main.tsx`, leftovers from the original Vite TypeScript template. `index.html` loads `main.jsx`, so `App.jsx` is the file that's actually in use.

## Prerequisites

- Python 3.9+
- Node.js (18+ recommended) and npm
- Docker, to run a local Weaviate instance
- A [Groq API key](https://console.groq.com/) — optional; without it the API still runs in search-only mode
- (Optional) your own email address for NCBI Entrez, only needed if you re-run the data collection scripts

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/ankithtn/semantic_search_engine.git
cd semantic_search_engine
```

### 2. Start Weaviate

The repo doesn't ship a `docker-compose.yml`, so run Weaviate directly. `weaviate-client==4.17.0` requires **Weaviate server 1.27.0 or newer**, and the client uses gRPC on port `50051`:

```bash
docker run -d --name weaviate \
  -p 8080:8080 -p 50051:50051 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=none \
  -v weaviate_data:/var/lib/weaviate \
  cr.weaviate.io/semitechnologies/weaviate:1.27.0
```

`DEFAULT_VECTORIZER_MODULE=none` is used because the app generates and supplies its own embeddings (`Configure.Vectors.self_provided()`).

### 3. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install groq                # used by llm_service.py but not listed in requirements.txt
```

Create `backend/.env`:

```env
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8080
WEAVIATE_GRPC_PORT=50051

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=2000
GROQ_TEMPERATURE=0.3

ENVIRONMENT=development
DEBUG=True
```

Create the Weaviate schema and load some data (see [Populating the Database](#populating-the-database) below), then start the API:

```bash
bash run.sh
# equivalent to:
# uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

### 4. Frontend setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

```bash
npm run dev
```

The app runs at `http://localhost:5173` by default.

## Populating the Database

The `data/` folder is gitignored (except for `.gitignore` itself), so no paper data ships with the repo — the database starts empty and needs to be seeded:

1. **Collect papers from PubMed**
   ```bash
   cd backend
   python -m src.expanded_pubmed_collector_v2
   ```
   Set `Entrez.email` (via the `EMAIL` env var or by editing the script) before running, per [NCBI's usage policy](https://www.ncbi.nlm.nih.gov/books/NBK25497/). This script is resumable — it writes a `collection_checkpoint.json` and can be safely stopped and restarted, searching the topics in `medical_data_topics.py` until it reaches `TARGET_PAPERS` (100,000 by default) new papers.
   Simpler runs are available in `pubmed_collector.py` (a handful of hardcoded topics, ~500 papers) if you just want a small dataset to test with.

2. **Create the schema and upload embeddings**
   ```bash
   python -m src.upload_to_weaviate      # first run: creates the "MedicalPaper" collection, then embeds + uploads
   # or, for incremental/deduped loads against an existing collection:
   python -m src.upload_to_weaviate_v2
   ```
   Both scripts load `all-MiniLM-L6-v2`, embed each paper's `title + abstract`, and upload in batches. Check the `NEW_DATA_FILE` / `EXISTING_DATA_FILE` constants at the top of each script and point them at your collected JSON file(s) before running.

3. **(Optional) Inspect the collection**
   ```bash
   python -m src.data_viewer
   ```

## API Reference

All endpoints are mounted under `/api`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/search` | Unified endpoint — runs a search and also generates an AI answer (if the LLM service is available) |
| `POST` | `/api/search/legacy` | Search only, no AI answer (kept for backward compatibility) |
| `GET` | `/api/health` | Connectivity status for Weaviate and the LLM service |
| `GET` | `/api/stats` | Total indexed document count and collection info |
| `GET` | `/` | API metadata (name, version, RAG status, links to docs) |
| `GET` | `/docs` | Auto-generated OpenAPI/Swagger docs |

**Search request body:**

```json
{
  "query": "diabetes treatment",
  "mode": "hybrid",
  "limit": 10
}
```

`mode` is one of `semantic`, `keyword`, or `hybrid` (default). `limit` accepts 1–100.

**Unified search response (abridged):**

```json
{
  "query": "diabetes treatment",
  "mode": "hybrid",
  "results": [ { "title": "...", "abstract": "...", "pmid": "...", "journal": "...", "year": "...", "score": 0.87 } ],
  "total_count": 10,
  "search_time": 0.234,
  "ai_answer": {
    "answer": "Recent treatments include...[1][2]",
    "model": "llama-3.3-70b-versatile",
    "tokens_used": 856,
    "generation_time": 1.234
  },
  "papers_analyzed": 5,
  "rag_enabled": true
}
```

## Search Modes

| Mode | How it works |
|---|---|
| `semantic` | Pure vector search (`near_vector`) using the query's sentence-transformer embedding |
| `keyword` | BM25 full-text search over titles/abstracts |
| `hybrid` | Weaviate's hybrid query, combining vector and BM25 with `alpha=0.7` (70% semantic / 30% keyword weighting) |

## Environment Variables

**Backend (`backend/.env`)**

| Variable | Default | Purpose |
|---|---|---|
| `WEAVIATE_HOST` | `localhost` | Weaviate host |
| `WEAVIATE_PORT` | `8080` | Weaviate REST port |
| `WEAVIATE_GRPC_PORT` | `50051` | Weaviate gRPC port |
| `GROQ_API_KEY` | *(none)* | Required for AI-answer generation; without it the app runs search-only |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model used for answer generation |
| `GROQ_MAX_TOKENS` | `2000` | Max tokens per generated answer |
| `GROQ_TEMPERATURE` | `0.3` | Sampling temperature |
| `ENVIRONMENT` | `development` | Free-form environment label |
| `DEBUG` | `True` | Enables uvicorn `--reload`-style behavior |

**Frontend (`frontend/.env`)**

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Base URL of the backend API |
| `VITE_API_TIMEOUT` | `30000` | Request timeout (ms) |

## Notes

- `backend/requirements.txt` doesn't list the `groq` package, even though `llm_service.py` imports it — install it separately (`pip install groq`) or add it to `requirements.txt`.
- `hybrid_search.py` and `search.py` at the top of `backend/src/` are standalone exploratory CLI scripts used while building the search logic; the actual API uses `services/search_service.py`. `api.py`, `models.py`, and `services.py` are empty legacy stub files from an earlier project layout.
- No `LICENSE` file is currently included in the repository.

## License

No license file is currently present in this repository. Add one (e.g. MIT, Apache-2.0) if you intend for others to reuse this code.
