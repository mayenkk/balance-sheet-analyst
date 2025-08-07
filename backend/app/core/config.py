from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Balance Sheet Analyst"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/balance_sheet_db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "ky1qucGOt-uGRNVEbDO7gBcgFSyaHS-bG7K9cO4U5N8")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Groq
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "4000"))
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.3"))

    # Gemini
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "4000"))
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.3"))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB for PDFs
    UPLOAD_DIR: str = "uploads"
    
    # PDF Processing
    PDF_UPLOAD_DIR: str = "pdfs"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_CHUNKS_PER_COMPANY: int = 100
    
    # RAG Settings
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    MAX_CONTEXT_LENGTH: int = 8000
    
    # Company Access Control
    VERTICAL_KEYWORDS: dict = {
        "jio": ["JIO", "telecom", "telecommunications", "digital", "platform"],
        "retail": ["retail", "Reliance Retail", "stores", "commerce"],
        "energy": ["energy", "petroleum", "refinery", "oil", "gas"],
        "chemicals": ["chemicals", "petrochemicals", "polymer"],
        "media": ["media", "entertainment", "broadcasting"],
        "financial": ["financial", "banking", "insurance", "investment"],
        "o2c": ["O2C", "oil to chemicals", "integrated"],
        "oilgas": ["oil & gas", "upstream", "downstream"],
        "newenergy": ["new energy", "renewable", "materials"]
    }
    
    # Pinecone Configuration
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings() 