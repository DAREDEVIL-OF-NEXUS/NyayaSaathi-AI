import pytest
from backend.app.services.rag.chunking import LegalChunk
from backend.app.services.graph.builder import LegalGraphBuilder
from backend.app.services.graph.engine import LegalGraphEngine, get_graph_engine
from backend.app.services.graph.models import LegalEntity, LegalRelationship

def test_static_entities_structure():
    static_entities = LegalGraphBuilder.get_static_entities()
    ids = {e.id for e in static_entities}
    assert "auth_district_comm" in ids
    assert "auth_state_comm" in ids
    assert "auth_national_comm" in ids
    assert "auth_ccpa" in ids
    assert "limit_district_50lakh" in ids
    assert "timeline_ecom_48hr" in ids
    assert "timeline_ecom_30days" in ids

def test_graph_builder_provenance_and_extraction():
    parent_chunk = LegalChunk(
        chunk_id="cpa_sec_28",
        parent_id=None,
        doc_id="cpa_2019_act",
        category="1_statutory",
        document_title="Consumer Protection Act, 2019",
        chapter="CHAPTER IV",
        section_or_rule="Section 28",
        legal_hierarchy="Consumer Protection Act, 2019 > CHAPTER IV > Section 28",
        text="Section 28. Establishment of District Commission. The District Commission shall entertain complaints where value does not exceed fifty lakh rupees.",
        token_count=35,
        source_url="https://indiacode.nic.in",
        issuing_authority="Legislative Department",
        verification_status="verified_official",
        is_authoritative=True,
        is_parent=True,
        metadata={"heading": "Establishment of District Commission"}
    )

    child_chunk = LegalChunk(
        chunk_id="cpa_sec_28_c1",
        parent_id="cpa_sec_28",
        doc_id="cpa_2019_act",
        category="1_statutory",
        document_title="Consumer Protection Act, 2019",
        chapter="CHAPTER IV",
        section_or_rule="Section 28",
        legal_hierarchy="Consumer Protection Act, 2019 > CHAPTER IV > Section 28",
        text="The District Commission shall entertain complaints where value does not exceed fifty lakh rupees.",
        token_count=20,
        source_url="https://indiacode.nic.in",
        issuing_authority="Legislative Department",
        verification_status="verified_official",
        is_authoritative=True,
        is_parent=False
    )

    entities, relationships = LegalGraphBuilder.extract_from_chunks([parent_chunk], [child_chunk])

    # Check entities
    entity_ids = {e.id for e in entities}
    assert "doc_cpa_2019_act" in entity_ids
    assert "prov_cpa_sec_28" in entity_ids

    # Check provenance
    sec_entity = next(e for e in entities if e.id == "prov_cpa_sec_28")
    assert sec_entity.provenance_chunk_id == "cpa_sec_28"
    assert sec_entity.canonical_citation == "Section 28"

    # Check relationships
    rel_types = {r.relation_type for r in relationships}
    assert "CONTAINS" in rel_types
    assert "GOVERNS" in rel_types
    assert "DEFINES" in rel_types

    # Verify provenance for every single relationship
    for r in relationships:
        assert r.provenance_doc_id is not None
        assert r.provenance_chunk_id is not None
        assert r.evidence_text != ""

def test_bounded_graph_traversal():
    engine = get_graph_engine()

    # Verify that graph is hydrated
    assert engine.graph.number_of_nodes() > 0
    assert engine.graph.number_of_edges() > 0

    # Test bounded 1-hop traversal with strict limit of 2
    seed_nodes = [nid for nid in engine.graph.nodes if "prov_" in nid or "auth_" in nid]
    assert len(seed_nodes) > 0

    seed = seed_nodes[0]
    contexts = engine.bounded_traverse(seed_entity_ids=[seed], max_hops=1, max_enriched_nodes=2)
    assert len(contexts) <= 2
    for ctx in contexts:
        assert ctx.seed_entity_id == seed
        assert ctx.neighbor_entity_id != ""
        assert ctx.relation_type != ""
        assert ctx.target_name != ""

    # Test unknown entity returns empty list without error
    empty_res = engine.bounded_traverse(seed_entity_ids=["non_existent_entity_xyz"], max_hops=1, max_enriched_nodes=3)
    assert empty_res == []
