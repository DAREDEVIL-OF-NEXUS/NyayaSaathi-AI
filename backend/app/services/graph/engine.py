from typing import List, Dict, Any, Optional, Set
import networkx as nx
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.core.config import settings
from backend.app.services.graph.models import (
    LegalEntityModel, LegalRelationshipModel, LegalEntity, LegalRelationship, GraphEnrichedContext
)

class LegalGraphEngine:
    """
    NetworkX in-memory legal knowledge graph with persistent relational storage.
    Enforces bounded 1-hop traversal with strict neighbor limits.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LegalGraphEngine, cls).__new__(cls)
            cls._instance._init_graph()
        return cls._instance

    def _init_graph(self):
        # Create database tables if not exist
        Base.metadata.create_all(bind=engine)
        self.graph = nx.DiGraph()
        self.entities: Dict[str, LegalEntity] = {}
        self.load_from_db()

    def sync_to_db(self, entities: List[LegalEntity], relationships: List[LegalRelationship]):
        """
        Persists extracted legal entities and relationships to the relational database.
        """
        db: Session = SessionLocal()
        try:
            # Upsert entities
            for e in entities:
                existing = db.query(LegalEntityModel).filter(LegalEntityModel.id == e.id).first()
                if not existing:
                    db.add(LegalEntityModel(
                        id=e.id,
                        entity_type=e.entity_type,
                        name=e.name,
                        canonical_citation=e.canonical_citation,
                        document_id=e.document_id,
                        category=e.category,
                        summary=e.summary,
                        provenance_chunk_id=e.provenance_chunk_id,
                        entity_metadata=e.entity_metadata
                    ))
                else:
                    existing.name = e.name
                    existing.summary = e.summary
                    existing.entity_metadata = e.entity_metadata

            # Upsert relationships
            for r in relationships:
                existing_rel = db.query(LegalRelationshipModel).filter(LegalRelationshipModel.id == r.id).first()
                if not existing_rel:
                    db.add(LegalRelationshipModel(
                        id=r.id,
                        source_id=r.source_id,
                        target_id=r.target_id,
                        relation_type=r.relation_type,
                        provenance_doc_id=r.provenance_doc_id,
                        provenance_chunk_id=r.provenance_chunk_id,
                        evidence_text=r.evidence_text,
                        relationship_metadata=r.relationship_metadata
                    ))

            db.commit()
            print(f"[LegalGraphEngine] Synced {len(entities)} entities and {len(relationships)} relationships to DB.")
        except Exception as ex:
            db.rollback()
            print(f"[LegalGraphEngine] Error syncing graph to DB: {ex}")
            raise
        finally:
            db.close()

        # Re-hydrate in-memory NetworkX DiGraph
        self.load_from_db()

    def load_from_db(self):
        """
        Hydrates NetworkX DiGraph from relational database storage.
        """
        db: Session = SessionLocal()
        try:
            self.graph.clear()
            self.entities.clear()

            db_entities = db.query(LegalEntityModel).all()
            for e in db_entities:
                entity = LegalEntity(
                    id=e.id,
                    entity_type=e.entity_type,
                    name=e.name,
                    canonical_citation=e.canonical_citation,
                    document_id=e.document_id,
                    category=e.category,
                    summary=e.summary,
                    provenance_chunk_id=e.provenance_chunk_id,
                    entity_metadata=e.entity_metadata or {}
                )
                self.entities[e.id] = entity
                self.graph.add_node(
                    e.id,
                    entity_type=e.entity_type,
                    name=e.name,
                    document_id=e.document_id,
                    provenance_chunk_id=e.provenance_chunk_id
                )

            db_rels = db.query(LegalRelationshipModel).all()
            for r in db_rels:
                if self.graph.has_node(r.source_id) and self.graph.has_node(r.target_id):
                    self.graph.add_edge(
                        r.source_id,
                        r.target_id,
                        relation_type=r.relation_type,
                        provenance_chunk_id=r.provenance_chunk_id,
                        evidence_text=r.evidence_text
                    )

            print(f"[LegalGraphEngine] Graph hydrated: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")
        finally:
            db.close()

    def bounded_traverse(
        self,
        seed_entity_ids: List[str],
        max_hops: int = 1,
        max_enriched_nodes: int = 3
    ) -> List[GraphEnrichedContext]:
        """
        Executes bounded 1-hop traversal from seed entities.
        Returns connected legal provisions (e.g. governing forum, statutory limitation, penalties)
        strictly capped at max_enriched_nodes to avoid context bloating.
        """
        max_hops = min(max_hops, settings.GRAPH_MAX_HOPS)
        max_enriched = min(max_enriched_nodes, settings.GRAPH_MAX_ENRICHED_NODES)

        enriched: List[GraphEnrichedContext] = []
        visited: Set[str] = set(seed_entity_ids)

        for seed_id in seed_entity_ids:
            if not self.graph.has_node(seed_id):
                continue

            # Outgoing edges (e.g. Section REFERENCES Section, or Section DEFINES Limit)
            for neighbor in self.graph.successors(seed_id):
                if neighbor not in visited and len(enriched) < max_enriched:
                    edge_data = self.graph.get_edge_data(seed_id, neighbor)
                    target_entity = self.entities.get(neighbor)
                    if target_entity:
                        enriched.append(
                            GraphEnrichedContext(
                                seed_entity_id=seed_id,
                                neighbor_entity_id=neighbor,
                                relation_type=edge_data.get("relation_type", "RELATED_TO"),
                                target_name=target_entity.name,
                                summary=target_entity.summary,
                                provenance_chunk_id=target_entity.provenance_chunk_id
                            )
                        )
                        visited.add(neighbor)

            # Incoming edges of high significance (e.g. Pecuniary Limit GOVERNED by Rule)
            for predecessor in self.graph.predecessors(seed_id):
                if predecessor not in visited and len(enriched) < max_enriched:
                    edge_data = self.graph.get_edge_data(predecessor, seed_id)
                    source_entity = self.entities.get(predecessor)
                    if source_entity:
                        enriched.append(
                            GraphEnrichedContext(
                                seed_entity_id=seed_id,
                                neighbor_entity_id=predecessor,
                                relation_type=f"REVERSE_{edge_data.get('relation_type', 'RELATED_TO')}",
                                target_name=source_entity.name,
                                summary=source_entity.summary,
                                provenance_chunk_id=source_entity.provenance_chunk_id
                            )
                        )
                        visited.add(predecessor)

            if len(enriched) >= max_enriched:
                break

        return enriched

def get_graph_engine() -> LegalGraphEngine:
    return LegalGraphEngine()
