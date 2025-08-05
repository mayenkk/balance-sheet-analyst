from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Balance Sheet Analyst"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/balance_sheet_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.3
    
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
    
    # Vector Database
    CHROMA_PERSIST_DIR: str = "chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
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
        "financial": ["financial", "banking", "insurance", "investment"]
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 