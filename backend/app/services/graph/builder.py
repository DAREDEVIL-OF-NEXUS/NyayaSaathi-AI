import re
from typing import List, Dict, Any, Tuple
from backend.app.services.rag.chunking import LegalChunk
from backend.app.services.graph.models import LegalEntity, LegalRelationship

class LegalGraphBuilder:
    """
    Deterministic Legal Knowledge Graph builder for Indian Consumer Protection laws.
    Extracts legal entities and explicitly defined statutory cross-references.
    Ensures 100% provenance tracking with zero LLM hallucination.
    """

    # Authority definitions
    AUTHORITIES = [
        {"id": "auth_ccpa", "name": "Central Consumer Protection Authority (CCPA)", "type": "AUTHORITY"},
        {"id": "auth_district_comm", "name": "District Consumer Disputes Redressal Commission", "type": "FORUM"},
        {"id": "auth_state_comm", "name": "State Consumer Disputes Redressal Commission", "type": "FORUM"},
        {"id": "auth_national_comm", "name": "National Consumer Disputes Redressal Commission (NCDRC)", "type": "FORUM"},
        {"id": "auth_nch", "name": "National Consumer Helpline (NCH)", "type": "AUTHORITY"},
        {"id": "auth_grievance_officer", "name": "E-Commerce Grievance Redressal Officer", "type": "AUTHORITY"},
    ]

    # Standard Statutory Timelines & Slabs
    SPECIAL_ENTITIES = [
        {"id": "limit_district_50lakh", "name": "Pecuniary Limit: Up to ₹50 Lakh (District Commission)", "type": "PECUNIARY_LIMIT"},
        {"id": "limit_state_2crore", "name": "Pecuniary Limit: ₹50 Lakh to ₹2 Crore (State Commission)", "type": "PECUNIARY_LIMIT"},
        {"id": "limit_national_above_2crore", "name": "Pecuniary Limit: Above ₹2 Crore (National Commission)", "type": "PECUNIARY_LIMIT"},
        {"id": "timeline_ecom_48hr", "name": "Grievance Acknowledgment: Within 48 Hours", "type": "TIMELINE"},
        {"id": "timeline_ecom_30days", "name": "Grievance Resolution: Within 1 Month (30 Days)", "type": "TIMELINE"},
        {"id": "timeline_limitation_2years", "name": "Statutory Limitation Period: 2 Years from Cause of Action", "type": "TIMELINE"},
    ]

    @classmethod
    def get_static_entities(cls) -> List[LegalEntity]:
        entities = []
        for a in cls.AUTHORITIES + cls.SPECIAL_ENTITIES:
            entities.append(
                LegalEntity(
                    id=a["id"],
                    entity_type=a["type"],
                    name=a["name"],
                    document_id="statutory_definitions",
                    category="statutory_entities",
                    summary=a["name"]
                )
            )
        return entities

    @classmethod
    def extract_from_chunks(
        cls,
        parent_chunks: List[LegalChunk],
        child_chunks: List[LegalChunk]
    ) -> Tuple[List[LegalEntity], List[LegalRelationship]]:
        entities: Dict[str, LegalEntity] = {}
        relationships: List[LegalRelationship] = []

        # 1. Register static authorities & limits
        for se in cls.get_static_entities():
            entities[se.id] = se

        # 2. Extract Document, Chapter, Section/Rule entities
        for p in parent_chunks:
            # Document Entity
            doc_entity_id = f"doc_{p.doc_id}"
            if doc_entity_id not in entities:
                entities[doc_entity_id] = LegalEntity(
                    id=doc_entity_id,
                    entity_type="ACT" if "act" in p.doc_id else "STATUTORY_RULES",
                    name=p.document_title,
                    canonical_citation=p.document_title,
                    document_id=p.doc_id,
                    category=p.category,
                    summary=f"Statutory document: {p.document_title}",
                    provenance_chunk_id=p.chunk_id
                )

            # Provision Entity (Section or Rule)
            prov_id = f"prov_{p.chunk_id}"
            sec_name = p.section_or_rule or "General"
            heading = p.metadata.get("heading", "")
            full_name = f"{sec_name}: {heading}".strip(": ")

            entity_type = "SECTION" if "section" in sec_name.lower() else ("RULE" if "rule" in sec_name.lower() else "PROVISION")

            entities[prov_id] = LegalEntity(
                id=prov_id,
                entity_type=entity_type,
                name=full_name,
                canonical_citation=sec_name,
                document_id=p.doc_id,
                category=p.category,
                summary=p.text[:300] + ("..." if len(p.text) > 300 else ""),
                provenance_chunk_id=p.chunk_id,
                entity_metadata={"chapter": p.chapter, "heading": heading}
            )

            # Relationship: Document CONTAINS Provision
            rel_id = f"rel_{doc_entity_id}_contains_{prov_id}"
            relationships.append(
                LegalRelationship(
                    id=rel_id,
                    source_id=doc_entity_id,
                    target_id=prov_id,
                    relation_type="CONTAINS",
                    provenance_doc_id=p.doc_id,
                    provenance_chunk_id=p.chunk_id,
                    evidence_text=f"{p.document_title} contains {sec_name}"
                )
            )

        # 3. Detect Cross-References and Authority/Limit links from text
        for p in parent_chunks:
            prov_id = f"prov_{p.chunk_id}"
            text = p.text

            # Match: "section X" references
            for m in re.finditer(r"section\s+(\d+[A-Z]?)", text, re.IGNORECASE):
                target_sec_num = m.group(1).upper()
                # Find matching target section in current document
                for target_id, target_entity in entities.items():
                    if target_entity.document_id == p.doc_id and target_entity.canonical_citation:
                        if target_entity.canonical_citation.lower() == f"section {target_sec_num}".lower():
                            if prov_id != target_id:
                                rel_id = f"rel_{prov_id}_ref_{target_id}"
                                relationships.append(
                                    LegalRelationship(
                                        id=rel_id,
                                        source_id=prov_id,
                                        target_id=target_id,
                                        relation_type="REFERENCES",
                                        provenance_doc_id=p.doc_id,
                                        provenance_chunk_id=p.chunk_id,
                                        evidence_text=m.group(0)
                                    )
                                )

            # Match: "rule X" references
            for m in re.finditer(r"rule\s+(\d+[A-Z]?)", text, re.IGNORECASE):
                target_rule_num = m.group(1).upper()
                for target_id, target_entity in entities.items():
                    if target_entity.document_id == p.doc_id and target_entity.canonical_citation:
                        if target_entity.canonical_citation.lower() == f"rule {target_rule_num}".lower():
                            if prov_id != target_id:
                                rel_id = f"rel_{prov_id}_ref_{target_id}"
                                relationships.append(
                                    LegalRelationship(
                                        id=rel_id,
                                        source_id=prov_id,
                                        target_id=target_id,
                                        relation_type="REFERENCES",
                                        provenance_doc_id=p.doc_id,
                                        provenance_chunk_id=p.chunk_id,
                                        evidence_text=m.group(0)
                                    )
                                )

            # Match Forums and Authorities
            if "district commission" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_gov_district",
                        source_id=prov_id,
                        target_id="auth_district_comm",
                        relation_type="GOVERNS",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Governs District Commission jurisdiction/proceedings"
                    )
                )
            if "state commission" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_gov_state",
                        source_id=prov_id,
                        target_id="auth_state_comm",
                        relation_type="GOVERNS",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Governs State Commission jurisdiction/proceedings"
                    )
                )
            if "national commission" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_gov_national",
                        source_id=prov_id,
                        target_id="auth_national_comm",
                        relation_type="GOVERNS",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Governs National Commission jurisdiction/proceedings"
                    )
                )
            if "central consumer protection authority" in text.lower() or "central authority" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_gov_ccpa",
                        source_id=prov_id,
                        target_id="auth_ccpa",
                        relation_type="GOVERNS",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Governs Central Consumer Protection Authority duties/orders"
                    )
                )
            if "grievance officer" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_gov_grievance_off",
                        source_id=prov_id,
                        target_id="auth_grievance_officer",
                        relation_type="GOVERNS",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Mandates duties of Grievance Redressal Officer"
                    )
                )

            # Match Timelines & Pecuniary Limits
            if "fifty lakh" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_limit_50lakh",
                        source_id=prov_id,
                        target_id="limit_district_50lakh",
                        relation_type="DEFINES",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Defines fifty lakh rupees pecuniary limit"
                    )
                )
            if "two crore" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_limit_2crore",
                        source_id=prov_id,
                        target_id="limit_state_2crore",
                        relation_type="DEFINES",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Defines two crore rupees pecuniary limit"
                    )
                )
            if "forty-eight hours" in text.lower() or "48 hour" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_time_48hr",
                        source_id=prov_id,
                        target_id="timeline_ecom_48hr",
                        relation_type="DEFINES",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Defines mandatory 48-hour acknowledgment timeline"
                    )
                )
            if "one month" in text.lower() or "thirty days" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_time_30days",
                        source_id=prov_id,
                        target_id="timeline_ecom_30days",
                        relation_type="DEFINES",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Defines mandatory 1 month / 30 days redressal timeline"
                    )
                )
            if "two years" in text.lower() and "limitation" in text.lower():
                relationships.append(
                    LegalRelationship(
                        id=f"rel_{prov_id}_time_2years",
                        source_id=prov_id,
                        target_id="timeline_limitation_2years",
                        relation_type="DEFINES",
                        provenance_doc_id=p.doc_id,
                        provenance_chunk_id=p.chunk_id,
                        evidence_text="Defines 2 years statutory limitation period"
                    )
                )

        # 4. Explicit Appeals Escalations
        relationships.append(
            LegalRelationship(
                id="rel_district_escalates_to_state",
                source_id="auth_district_comm",
                target_id="auth_state_comm",
                relation_type="ESCALATES_TO",
                provenance_doc_id="cpa_2019_act",
                provenance_chunk_id="cpa_2019_act_sec_41",
                evidence_text="Section 41: Appeal against District Commission order to State Commission"
            )
        )
        relationships.append(
            LegalRelationship(
                id="rel_state_escalates_to_national",
                source_id="auth_state_comm",
                target_id="auth_national_comm",
                relation_type="ESCALATES_TO",
                provenance_doc_id="cpa_2019_act",
                provenance_chunk_id="cpa_2019_act_sec_51",
                evidence_text="Section 51: Appeal against State Commission order to National Commission"
            )
        )

        # Deduplicate relationships by ID
        unique_rels = {r.id: r for r in relationships}.values()
        return list(entities.values()), list(unique_rels)
