from dotenv import load_dotenv
import os

# Load environment variables 
load_dotenv()

class Settings:
    """Application settings """

    # Weaviate settings
    WEAVIATE_HOST: str = os.getenv("WEAVIATE_HOST", "localhost")
    WEAVIATE_PORT: int = int(os.getenv("WEAVIATE_PORT", "8080"))
    WEAVIATE_GRPC_PORT: int = int(os.getenv("WEAVIATE_GRPC_PORT", 50051))

    #Application Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "True"

    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    
    # CORS settings
    ALLOWED_ORIGINS = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"  # Allowed all origins (FOr DEVELOPMENT ONLY!)
    ]

    # Groq API settings (New)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", 2000))
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", 0.3))
    

    # Search settings
    DEFAULT_SEARCH_LIMIT = 10
    MAX_SEARCH_LIMIT = 100
    DEFAULT_ALPHA = 0.7 # Hybrid search alpha (0.7 = 70% semantic)

    # Collection name
    COLLECTION_NAME = "MedicalPaper"

settings = Settings()