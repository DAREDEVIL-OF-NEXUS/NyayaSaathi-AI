from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.services.rag.retrieval import RetrievedCandidate
from backend.app.services.graph.models import LegalEntity, LegalRelationship

class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(10, ge=1, le=50)
    mode: str = Field("hybrid", description="vector_only, bm25_only, hybrid, or hybrid_graph")
    filter_category: Optional[str] = None

class KnowledgeSearchResponse(BaseModel):
    query: str
    total_found: int
    mode_used: str
    candidates: List[RetrievedCandidate]

class GraphEntityDetail(BaseModel):
    entity: LegalEntity
    connected_neighbors: List[Dict[str, Any]]
