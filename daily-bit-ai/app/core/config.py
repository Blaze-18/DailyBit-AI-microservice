import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # DB configuration
    CHROMA_DB_PATH: str = "./chroma_db"

    # Model Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2" # Updated embedding model

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

settings = Settings()
