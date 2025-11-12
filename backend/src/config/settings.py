from dotenv import load_dotenv
import os

# Load environment variables 
load_dotenv()

class Settings:
    """Application settings """

    # Weaviate settings
    WEAVIATE_HOST: str = os.getenv("WEAVIATE_HOST", "localhost")
    WEAVIATE_PORT: int = int(os.getenv("WEAVIATE_PORT", "8080"))

    #Application Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "True"

    # CORS settings
    ALLOWED_ORIGINS = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"  # Allowed all origins (DEVELOPMENT ONLY!)
    ]

    # Search settings
    DEFAULT_SEARCH_LIMIT = 10
    MAX_SEARCH_LIMIT = 100
    DEFAULT_ALPHA = 0.7 # Hybrid search alpha (0.7 = 70% semantic)

    # Collection name
    COLLECTION_NAME = "MedicalPaper"

settings = Settings()