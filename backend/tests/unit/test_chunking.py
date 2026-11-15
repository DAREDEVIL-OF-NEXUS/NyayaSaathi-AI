import pytest
from backend.app.services.rag.extraction import ExtractedDocument
from backend.app.services.rag.chunking import LegalChunker, LegalChunk

SAMPLE_LEGAL_TEXT = """
CHAPTER IV
CONSUMER DISPUTES REDRESSAL COMMISSION

Section 28. Establishment of District Consumer Disputes Redressal Commission.
(1) The State Government shall, by notification, establish a District Consumer Disputes Redressal Commission, to be known as the District Commission, in each district of the State.
(2) The District Commission shall have jurisdiction to entertain complaints where the value of the goods or services paid as consideration does not exceed fifty lakh rupees.

Section 41. Appeal against order of District Commission.
Any person aggrieved by an order made by the District Commission may prefer an appeal against such order to the State Commission on the grounds of facts or law within a period of forty-five days from the date of the order.

CHAPTER V
MEDIATION

Section 74. Consumer Mediation Cell.
(1) The State Government shall establish a consumer mediation cell to be attached to each of the District Commissions and the State Commissions.
"""

def test_legal_chunker_provisions():
    chunker = LegalChunker(target_chunk_tokens=100, max_chunk_tokens=200, overlap_tokens=20)
    provisions = chunker.split_into_legal_provisions(SAMPLE_LEGAL_TEXT)

    assert len(provisions) >= 3
    sec_28 = next((p for p in provisions if "Section 28" in (p.get("section_or_rule") or "")), None)
    assert sec_28 is not None
    assert "IV" in sec_28["chapter"]
    assert "District Commission" in sec_28["text"]

    sec_41 = next((p for p in provisions if "Section 41" in (p.get("section_or_rule") or "")), None)
    assert sec_41 is not None
    assert "IV" in sec_41["chapter"]

    sec_74 = next((p for p in provisions if "Section 74" in (p.get("section_or_rule") or "")), None)
    assert sec_74 is not None
    assert "V" in sec_74["chapter"]

def test_parent_child_chunking():
    doc = ExtractedDocument(
        doc_id="cpa_2019_test",
        title="Consumer Protection Act, 2019",
        category="statutory",
        source_url="https://indiacode.nic.in",
        issuing_authority="Legislative Department",
        verification_status="verified_official",
        is_authoritative=True,
        text=SAMPLE_LEGAL_TEXT
    )

    chunker = LegalChunker(target_chunk_tokens=50, max_chunk_tokens=100, overlap_tokens=10)
    parents, children = chunker.chunk_document(doc)

    assert len(parents) >= 3
    assert len(children) >= len(parents)

    # Verify parent chunk properties
    for parent in parents:
        assert parent.is_parent is True
        assert parent.parent_id is None
        assert parent.doc_id == "cpa_2019_test"
        assert parent.is_authoritative is True
        assert parent.source_url == "https://indiacode.nic.in"

    # Verify child chunk properties and parent linking
    parent_ids = {p.chunk_id for p in parents}
    for child in children:
        assert child.is_parent is False
        assert child.parent_id in parent_ids
        assert child.doc_id == "cpa_2019_test"
        assert child.token_count <= 200
        assert child.legal_hierarchy != ""
