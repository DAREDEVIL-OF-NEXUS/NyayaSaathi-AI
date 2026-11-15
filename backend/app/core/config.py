import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Environment
    APP_ENV: str = 'development'
    LOG_LEVEL: str = 'INFO'
    SECRET_KEY: str = 'nyayasaathi-default-dev-secret-key-change-in-production-0123456789'

    # Server & Security
    HOST: str = '0.0.0.0'
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ['http://localhost:3000', 'http://127.0.0.1:3000']
    SECURE_COOKIES: bool = False
    COOKIE_DOMAIN: str = ''

    # JWT Authentication
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MFA_TEMP_TOKEN_EXPIRE_MINUTES: int = 5

    # Brevo Transactional Email
    BREVO_API_KEY: str = ''
    BREVO_SENDER_EMAIL: str = 'notifications@nyayasaathi.ai'
    BREVO_SENDER_NAME: str = 'NyayaSaathi AI'
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15
    FRONTEND_URL: str = 'http://localhost:3000'

    # Database
    DATABASE_URL: str = 'sqlite:///./data/nyayasaathi.db'

    # Qdrant Vector Store
    QDRANT_URL: str = ''
    QDRANT_API_KEY: str = ''
    QDRANT_STORAGE_PATH: str = './data/qdrant_db'
    QDRANT_COLLECTION_NAME: str = 'nyayasaathi_legal_corpus'

    # Embeddings
    EMBEDDING_MODEL: str = 'intfloat/multilingual-e5-small'
    EMBEDDING_DEVICE: str = 'cpu'
    EMBEDDING_DIMENSION: int = 384

    # Chunking & RAG Parameters
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 75
    MAX_CHUNK_SIZE: int = 750
    RETRIEVAL_TOP_K: int = 10
    RRF_K: int = 60

    # Legal Knowledge Graph Parameters
    GRAPH_MAX_HOPS: int = 1
    GRAPH_MAX_ENRICHED_NODES: int = 3

    # File Storage Paths
    RAW_DATA_DIR: str = './data/raw'
    PROCESSED_DATA_DIR: str = './data/processed'
    MANIFEST_PATH: str = './data/manifest/sources.json'
    UPLOAD_DIR: str = './data/uploads'
    MAX_UPLOAD_SIZE_MB: int = 15

    # LLM Providers
    LLM_PRIMARY_PROVIDER: str = 'gemini'
    LLM_FALLBACK_PROVIDER: str = 'openrouter'
    GEMINI_API_KEY: str = ''
    GEMINI_MODEL: str = 'gemini-1.5-flash'
    OPENROUTER_API_KEY: str = ''
    OPENROUTER_MODEL: str = 'meta-llama/llama-3.1-8b-instruct:free'
    OPENROUTER_BASE_URL: str = 'https://openrouter.ai/api/v1'

    # Corrective RAG (CRAG) Parameters
    CRAG_SUFFICIENT_THRESHOLD: float = 0.65
    CRAG_INSUFFICIENT_THRESHOLD: float = 0.35
    CRAG_MAX_SECONDARY_RETRIEVALS: int = 1

    # Reflection-Based Answer Verification Parameters
    VERIFICATION_ENABLED: bool = True
    MIN_CITATION_CONFIDENCE: float = 0.80

settings = Settings()
