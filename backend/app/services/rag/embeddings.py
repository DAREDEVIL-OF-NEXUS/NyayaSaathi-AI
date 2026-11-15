import os
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.app.core.config import settings

class EmbeddingService:
    """
    Embedding generation service using intfloat/multilingual-e5-small.
    Enforces strict prefix rules:
      - 'passage: ' for document chunks
      - 'query: ' for user search queries
    Consistently outputs normalized 384-dimensional dense vectors.
    """

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        device = settings.EMBEDDING_DEVICE
        print(f"[EmbeddingService] Loading {settings.EMBEDDING_MODEL} on {device}...")
        self._model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            device=device
        )
        print("[EmbeddingService] Model loaded successfully.")

    def embed_passages(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed document passages with mandatory 'passage: ' prefix and L2 normalization.
        """
        if not texts:
            return []
        prefixed = [f"passage: {t.strip()}" for t in texts]
        embeddings = self._model.encode(
            prefixed,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single search query with mandatory 'query: ' prefix and L2 normalization.
        """
        prefixed = f"query: {query.strip()}"
        embedding = self._model.encode(
            [prefixed],
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return embedding[0].tolist()

    def embed_queries(self, queries: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed multiple search queries with mandatory 'query: ' prefix.
        """
        if not queries:
            return []
        prefixed = [f"query: {q.strip()}" for q in queries]
        embeddings = self._model.encode(
            prefixed,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return embeddings.tolist()

# Global singleton accessor
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
