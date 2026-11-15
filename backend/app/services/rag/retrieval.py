import os
import json
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from rank_bm25 import BM25Okapi

from backend.app.core.config import settings
from backend.app.services.rag.chunking import LegalChunk
from backend.app.services.rag.embeddings import get_embedding_service
from backend.app.services.graph.engine import get_graph_engine
from backend.app.services.graph.models import GraphEnrichedContext

@dataclass
class RetrievedCandidate:
    chunk_id: str
    parent_id: Optional[str]
    doc_id: str
    category: str
    document_title: str
    section_or_rule: Optional[str]
    legal_hierarchy: str
    text: str
    score: float
    retrieval_method: str  # "dense", "sparse", "hybrid_rrf", "graph_enriched"
    source_url: str
    issuing_authority: str
    verification_status: str
    is_authoritative: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    graph_context: List[GraphEnrichedContext] = field(default_factory=list)

_shared_qdrant_client = None

def get_shared_qdrant_client() -> QdrantClient:
    global _shared_qdrant_client
    if _shared_qdrant_client is None:
        if settings.QDRANT_URL and settings.QDRANT_URL.startswith("http"):
            try:
                c = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY or None,
                    timeout=1.0
                )
                c.get_collections()
                print(f"[QdrantVectorStore] Connected to remote Qdrant at {settings.QDRANT_URL}")
                _shared_qdrant_client = c
            except Exception as e:
                print(f"[QdrantVectorStore] Remote Qdrant unreachable ({e}). Falling back to embedded local storage.")
                os.makedirs(settings.QDRANT_STORAGE_PATH, exist_ok=True)
                _shared_qdrant_client = QdrantClient(path=settings.QDRANT_STORAGE_PATH)
        else:
            os.makedirs(settings.QDRANT_STORAGE_PATH, exist_ok=True)
            _shared_qdrant_client = QdrantClient(path=settings.QDRANT_STORAGE_PATH)
            print(f"[QdrantVectorStore] Using local embedded storage at {settings.QDRANT_STORAGE_PATH}")
    return _shared_qdrant_client

class QdrantVectorStore:
    """
    Qdrant vector database client. Supports remote server (Docker)
    with seamless local embedded disk storage fallback (./data/qdrant_db).
    Uses a singleton client to avoid Windows file lock contention on .lock.
    """

    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.dim = settings.EMBEDDING_DIMENSION
        self.client = get_shared_qdrant_client()
        self._ensure_collection()

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self.dim,
                    distance=qmodels.Distance.COSINE
                )
            )
            print(f"[QdrantVectorStore] Created collection: {self.collection_name}")

    def upsert_chunks(self, chunks: List[LegalChunk], embeddings: List[List[float]]):
        if not chunks:
            return

        points = []
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            # Deterministic integer ID or stable UUID from chunk_id
            point_id = abs(hash(chunk.chunk_id)) % (10**12)
            payload = {
                "chunk_id": chunk.chunk_id,
                "parent_id": chunk.parent_id,
                "doc_id": chunk.doc_id,
                "category": chunk.category,
                "document_title": chunk.document_title,
                "chapter": chunk.chapter,
                "section_or_rule": chunk.section_or_rule,
                "legal_hierarchy": chunk.legal_hierarchy,
                "text": chunk.text,
                "token_count": chunk.token_count,
                "source_url": chunk.source_url,
                "issuing_authority": chunk.issuing_authority,
                "verification_status": chunk.verification_status,
                "is_authoritative": chunk.is_authoritative,
                "metadata": chunk.metadata
            }
            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=emb,
                    payload=payload
                )
            )

        # Batch upsert
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"[QdrantVectorStore] Upserted {len(points)} vector points.")

    def search_dense(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_category: Optional[str] = None
    ) -> List[RetrievedCandidate]:
        query_filter = None
        if filter_category:
            query_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="category",
                        match=qmodels.MatchValue(value=filter_category)
                    )
                ]
            )

        if hasattr(self.client, "query_points"):
            res = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k,
                query_filter=query_filter
            )
            results = res.points
        else:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=query_filter
            )

        candidates = []
        for r in results:
            payload = r.payload or {}
            candidates.append(
                RetrievedCandidate(
                    chunk_id=payload.get("chunk_id", ""),
                    parent_id=payload.get("parent_id"),
                    doc_id=payload.get("doc_id", ""),
                    category=payload.get("category", ""),
                    document_title=payload.get("document_title", ""),
                    section_or_rule=payload.get("section_or_rule"),
                    legal_hierarchy=payload.get("legal_hierarchy", ""),
                    text=payload.get("text", ""),
                    score=float(r.score),
                    retrieval_method="dense",
                    source_url=payload.get("source_url", ""),
                    issuing_authority=payload.get("issuing_authority", ""),
                    verification_status=payload.get("verification_status", "unverified"),
                    is_authoritative=payload.get("is_authoritative", False),
                    metadata=payload.get("metadata", {})
                )
            )
        return candidates


class BM25Retriever:
    """
    Lexical BM25 retriever for exact statutory number and phrasing lookup.
    """

    def __init__(self, index_path: str = "./data/processed/bm25_index.pkl"):
        self.index_path = Path(index_path)
        self.corpus_chunks: List[LegalChunk] = []
        self.bm25: Optional[BM25Okapi] = None
        self.load_index()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        # Legal-aware lowercase tokenization preserving section and rule numbers
        import re
        tokens = re.findall(r"\b[a-zA-Z0-9]+(?:[-_][a-zA-Z0-9]+)*\b", text.lower())
        return tokens

    def build_index(self, chunks: List[LegalChunk]):
        self.corpus_chunks = chunks
        tokenized_corpus = [self.tokenize(c.text + " " + (c.section_or_rule or "")) for c in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, "wb") as f:
            pickle.dump((self.corpus_chunks, self.bm25), f)
        print(f"[BM25Retriever] Built and saved BM25 index with {len(chunks)} chunks.")

    def load_index(self):
        if self.index_path.exists():
            try:
                with open(self.index_path, "rb") as f:
                    self.corpus_chunks, self.bm25 = pickle.load(f)
                print(f"[BM25Retriever] Loaded BM25 index with {len(self.corpus_chunks)} chunks.")
            except Exception as e:
                print(f"[BM25Retriever] Could not load BM25 index ({e}). Rebuild required.")

    def search_sparse(
        self,
        query: str,
        top_k: int = 10,
        filter_category: Optional[str] = None
    ) -> List[RetrievedCandidate]:
        if not self.bm25 or not self.corpus_chunks:
            return []

        tokens = self.tokenize(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        candidates = []
        for idx in top_indices:
            chunk = self.corpus_chunks[idx]
            chunk_tokens = set(self.tokenize(chunk.text + " " + (chunk.section_or_rule or "")))
            if not any(t in chunk_tokens for t in tokens):
                continue
            if filter_category and chunk.category != filter_category:
                continue

            candidates.append(
                RetrievedCandidate(
                    chunk_id=chunk.chunk_id,
                    parent_id=chunk.parent_id,
                    doc_id=chunk.doc_id,
                    category=chunk.category,
                    document_title=chunk.document_title,
                    section_or_rule=chunk.section_or_rule,
                    legal_hierarchy=chunk.legal_hierarchy,
                    text=chunk.text,
                    score=float(scores[idx]),
                    retrieval_method="sparse",
                    source_url=chunk.source_url,
                    issuing_authority=chunk.issuing_authority,
                    verification_status=chunk.verification_status,
                    is_authoritative=chunk.is_authoritative,
                    metadata=chunk.metadata
                )
            )
            if len(candidates) >= top_k:
                break

        return candidates


class HybridRetriever:
    """
    Coordinates Dense Vector (Qdrant) + Sparse Lexical (BM25) search.
    Merges candidates via Reciprocal Rank Fusion (RRF).
    Selectively enriches top candidates with bounded Legal Knowledge Graph neighbors.
    """

    def __init__(self):
        self.vector_store = QdrantVectorStore()
        self.bm25_retriever = BM25Retriever()
        self.embedding_service = get_embedding_service()
        self.graph_engine = get_graph_engine()
        self.rrf_k = settings.RRF_K

    def reciprocal_rank_fusion(
        self,
        dense_results: List[RetrievedCandidate],
        sparse_results: List[RetrievedCandidate],
        top_k: int = 10
    ) -> List[RetrievedCandidate]:
        """
        Calculates RRF score:
        RRF_Score(d) = sum_{m in {dense, sparse}} 1 / (k + rank_m(d))
        """
        rrf_scores: Dict[str, float] = {}
        candidate_map: Dict[str, RetrievedCandidate] = {}

        # Dense ranks
        for rank, cand in enumerate(dense_results, start=1):
            cid = cand.chunk_id
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))
            candidate_map[cid] = cand

        # Sparse ranks
        for rank, cand in enumerate(sparse_results, start=1):
            cid = cand.chunk_id
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))
            if cid not in candidate_map:
                candidate_map[cid] = cand

        # Sort descending by fused RRF score
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        fused: List[RetrievedCandidate] = []
        for cid in sorted_cids[:top_k]:
            base_cand = candidate_map[cid]
            fused.append(
                RetrievedCandidate(
                    chunk_id=base_cand.chunk_id,
                    parent_id=base_cand.parent_id,
                    doc_id=base_cand.doc_id,
                    category=base_cand.category,
                    document_title=base_cand.document_title,
                    section_or_rule=base_cand.section_or_rule,
                    legal_hierarchy=base_cand.legal_hierarchy,
                    text=base_cand.text,
                    score=rrf_scores[cid],
                    retrieval_method="hybrid_rrf",
                    source_url=base_cand.source_url,
                    issuing_authority=base_cand.issuing_authority,
                    verification_status=base_cand.verification_status,
                    is_authoritative=base_cand.is_authoritative,
                    metadata=base_cand.metadata
                )
            )

        return fused

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        mode: str = "hybrid",  # "vector_only", "bm25_only", "hybrid", "hybrid_graph"
        filter_category: Optional[str] = None
    ) -> List[RetrievedCandidate]:
        """
        Modular retrieval entry point supporting vector-only, bm25-only,
        hybrid, and hybrid+graph execution.
        """
        # Vector-only branch
        if mode == "vector_only":
            query_vec = self.embedding_service.embed_query(query)
            return self.vector_store.search_dense(query_vec, top_k=top_k, filter_category=filter_category)

        # BM25-only branch
        if mode == "bm25_only":
            return self.bm25_retriever.search_sparse(query, top_k=top_k, filter_category=filter_category)

        # Hybrid execution
        query_vec = self.embedding_service.embed_query(query)
        dense_cands = self.vector_store.search_dense(query_vec, top_k=top_k * 2, filter_category=filter_category)
        sparse_cands = self.bm25_retriever.search_sparse(query, top_k=top_k * 2, filter_category=filter_category)

        fused_cands = self.reciprocal_rank_fusion(dense_cands, sparse_cands, top_k=top_k)

        # Optional Graph Enrichment
        if mode in ["hybrid_graph", "hybrid"]:
            # Extract seed entity IDs from top candidates
            seed_entities = []
            for c in fused_cands[:3]:
                if c.parent_id:
                    seed_entities.append(f"prov_{c.parent_id}")
                else:
                    seed_entities.append(f"prov_{c.chunk_id}")

            graph_contexts = self.graph_engine.bounded_traverse(
                seed_entity_ids=seed_entities,
                max_hops=settings.GRAPH_MAX_HOPS,
                max_enriched_nodes=settings.GRAPH_MAX_ENRICHED_NODES
            )

            # Attach graph context to candidate records
            for cand in fused_cands:
                cand.graph_context = graph_contexts

        return fused_cands

# Global accessor with singleton pattern
_shared_hybrid_retriever = None

def get_hybrid_retriever() -> HybridRetriever:
    global _shared_hybrid_retriever
    if _shared_hybrid_retriever is None:
        _shared_hybrid_retriever = HybridRetriever()
    return _shared_hybrid_retriever
