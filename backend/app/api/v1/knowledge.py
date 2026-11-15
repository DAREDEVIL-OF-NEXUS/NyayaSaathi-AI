import json
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.core.config import settings
from backend.app.schemas.knowledge import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    GraphEntityDetail,
)
from backend.app.services.rag.retrieval import get_hybrid_retriever, HybridRetriever
from backend.app.services.graph.engine import get_graph_engine, LegalGraphEngine

router = APIRouter()

@router.post("/knowledge/search", response_model=KnowledgeSearchResponse, summary="Direct hybrid search across legal knowledge base")
def search_knowledge_endpoint(
    req: KnowledgeSearchRequest,
    retriever: HybridRetriever = Depends(get_hybrid_retriever)
):
    candidates = retriever.retrieve(
        query=req.query,
        top_k=req.top_k,
        mode=req.mode,
        filter_category=req.filter_category
    )

    return KnowledgeSearchResponse(
        query=req.query,
        total_found=len(candidates),
        mode_used=req.mode,
        candidates=candidates
    )


@router.get("/knowledge/graph/{entity_id}", response_model=GraphEntityDetail, summary="Get legal entity and its bounded 1-hop knowledge graph neighborhood")
def get_graph_entity_detail(
    entity_id: str,
    graph_engine: LegalGraphEngine = Depends(get_graph_engine)
):
    entity = graph_engine.entities.get(entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Legal entity '{entity_id}' not found in knowledge graph")

    neighbors = []
    # Successors
    if graph_engine.graph.has_node(entity_id):
        for succ in graph_engine.graph.successors(entity_id):
            edge_data = graph_engine.graph.get_edge_data(entity_id, succ) or {}
            target = graph_engine.entities.get(succ)
            neighbors.append({
                "direction": "outgoing",
                "relation_type": edge_data.get("relation_type", "RELATED_TO"),
                "neighbor_id": succ,
                "neighbor_name": target.name if target else succ,
                "neighbor_type": target.entity_type if target else "unknown",
                "summary": target.summary if target else ""
            })

        for pred in graph_engine.graph.predecessors(entity_id):
            edge_data = graph_engine.graph.get_edge_data(pred, entity_id) or {}
            source = graph_engine.entities.get(pred)
            neighbors.append({
                "direction": "incoming",
                "relation_type": edge_data.get("relation_type", "RELATED_TO"),
                "neighbor_id": pred,
                "neighbor_name": source.name if source else pred,
                "neighbor_type": source.entity_type if source else "unknown",
                "summary": source.summary if source else ""
            })

    return GraphEntityDetail(
        entity=entity,
        connected_neighbors=neighbors
    )


@router.get("/knowledge/sources", summary="List official legal sources and verification metadata from manifest")
def list_official_sources():
    if not os.path.exists(settings.MANIFEST_PATH):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sources manifest not found on disk")

    try:
        with open(settings.MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        return manifest_data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error reading sources manifest: {str(e)}")


@router.get("/knowledge/stats", summary="Get knowledge base and legal knowledge graph statistics")
def get_knowledge_stats(
    graph_engine: LegalGraphEngine = Depends(get_graph_engine)
):
    total_docs = 0
    if os.path.exists(settings.MANIFEST_PATH):
        try:
            with open(settings.MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                total_docs = len(manifest_data.get("documents", []))
        except Exception:
            pass

    return {
        "graph_entities_count": len(graph_engine.entities),
        "graph_edges_count": graph_engine.graph.number_of_edges(),
        "official_documents_count": total_docs,
        "max_hops_configured": settings.GRAPH_MAX_HOPS,
        "embedding_model": settings.EMBEDDING_MODEL
    }
