import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey, UniqueConstraint
from pydantic import BaseModel, Field
from backend.app.core.database import Base

# SQLAlchemy Models
class LegalEntityModel(Base):
    __tablename__ = "legal_entities"

    id = Column(String(128), primary_key=True)
    entity_type = Column(String(64), nullable=False, index=True)
    name = Column(String(256), nullable=False, index=True)
    canonical_citation = Column(String(256), nullable=True)
    document_id = Column(String(128), nullable=False, index=True)
    category = Column(String(64), nullable=False)
    summary = Column(Text, nullable=True)
    provenance_chunk_id = Column(String(128), nullable=True)
    entity_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class LegalRelationshipModel(Base):
    __tablename__ = "legal_relationships"

    id = Column(String(128), primary_key=True)
    source_id = Column(String(128), ForeignKey("legal_entities.id"), nullable=False, index=True)
    target_id = Column(String(128), ForeignKey("legal_entities.id"), nullable=False, index=True)
    relation_type = Column(String(64), nullable=False, index=True)
    provenance_doc_id = Column(String(128), nullable=False)
    provenance_chunk_id = Column(String(128), nullable=False)
    evidence_text = Column(Text, nullable=True)
    relationship_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("source_id", "target_id", "relation_type", name="uq_legal_rel"),
    )

# Pydantic Schemas
class LegalEntity(BaseModel):
    id: str
    entity_type: str
    name: str
    canonical_citation: Optional[str] = None
    document_id: str
    category: str
    summary: Optional[str] = None
    provenance_chunk_id: Optional[str] = None
    entity_metadata: Dict[str, Any] = Field(default_factory=dict)

class LegalRelationship(BaseModel):
    id: str
    source_id: str
    target_id: str
    relation_type: str
    provenance_doc_id: str
    provenance_chunk_id: str
    evidence_text: Optional[str] = None
    relationship_metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEnrichedContext(BaseModel):
    seed_entity_id: str
    neighbor_entity_id: str
    relation_type: str
    target_name: str
    summary: Optional[str] = None
    provenance_chunk_id: Optional[str] = None
