import pytest
from backend.app.services.rag.retrieval import get_hybrid_retriever

def test_live_hybrid_retrieval_pecuniary_jurisdiction():
    retriever = get_hybrid_retriever()
    query = "pecuniary jurisdiction of District Commission"
    results = retriever.retrieve(query, top_k=3, mode="hybrid_graph")

    assert len(results) > 0
    top = results[0]
    assert top.chunk_id != ""
    assert top.retrieval_method == "hybrid_rrf"
    assert top.score > 0
    assert "District Commission" in top.text or "jurisdiction" in top.text.lower()
    assert top.source_url is not None
    assert top.is_authoritative in [True, False]

    # Verify graph context enrichment
    assert len(top.graph_context) > 0
    target_names = [gc.target_name for gc in top.graph_context]
    assert any("District" in name or "Pecuniary" in name or "Consumer" in name for name in target_names)

def test_live_retrieval_ecommerce_timeline():
    retriever = get_hybrid_retriever()
    query = "grievance officer acknowledgment 48 hours e-commerce"
    results = retriever.retrieve(query, top_k=3, mode="hybrid")

    assert len(results) > 0
    found_ecommerce = any("commerce" in r.document_title.lower() or "48" in r.text or "grievance" in r.text.lower() for r in results)
    assert found_ecommerce is True

def test_live_retrieval_nch_helpline():
    retriever = get_hybrid_retriever()
    query = "National Consumer Helpline toll-free number 1915"
    results = retriever.retrieve(query, top_k=3, mode="hybrid")

    assert len(results) > 0
    found_nch = any("1915" in r.text or "helpline" in r.text.lower() for r in results)
    assert found_nch is True

def test_live_retrieval_category_filter():
    retriever = get_hybrid_retriever()
    query = "duties of sellers and marketplace"
    results = retriever.retrieve(
        query,
        top_k=2,
        mode="hybrid",
        filter_category="2_regulatory_ccpa"
    )

    for r in results:
        assert r.category == "2_regulatory_ccpa"
