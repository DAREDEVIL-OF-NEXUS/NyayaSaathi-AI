import pytest
from unittest.mock import MagicMock
from backend.app.services.rag.chunking import LegalChunk
from backend.app.services.rag.retrieval import (
    BM25Retriever,
    RetrievedCandidate,
    HybridRetriever
)

def test_bm25_tokenize():
    text = "Section 28(1): District Commission pecuniary jurisdiction up to Rs 50 lakh."
    tokens = BM25Retriever.tokenize(text)
    assert "section" in tokens
    assert "28" in tokens
    assert "district" in tokens
    assert "commission" in tokens
    assert "pecuniary" in tokens
    assert "50" in tokens

def test_bm25_search_sparse(tmp_path):
    index_file = tmp_path / "test_bm25.pkl"
    retriever = BM25Retriever(index_path=str(index_file))

    chunk1 = LegalChunk(
        chunk_id="c1",
        parent_id=None,
        doc_id="doc1",
        category="statutory",
        document_title="CPA 2019",
        chapter=None,
        section_or_rule="Section 28",
        legal_hierarchy="CPA > Section 28",
        text="District Commission pecuniary limit up to fifty lakh rupees.",
        token_count=10,
        source_url="http://example.com",
        issuing_authority="Auth",
        verification_status="verified_official",
        is_authoritative=True
    )
    chunk2 = LegalChunk(
        chunk_id="c2",
        parent_id=None,
        doc_id="doc1",
        category="statutory",
        document_title="CPA 2019",
        chapter=None,
        section_or_rule="Section 41",
        legal_hierarchy="CPA > Section 41",
        text="Appeal to State Commission within forty-five days.",
        token_count=8,
        source_url="http://example.com",
        issuing_authority="Auth",
        verification_status="verified_official",
        is_authoritative=True
    )

    retriever.build_index([chunk1, chunk2])

    results = retriever.search_sparse("pecuniary limit District Commission", top_k=1)
    assert len(results) == 1
    assert results[0].chunk_id == "c1"
    assert results[0].section_or_rule == "Section 28"

def test_reciprocal_rank_fusion():
    retriever = HybridRetriever.__new__(HybridRetriever)
    retriever.rrf_k = 60

    cand1 = RetrievedCandidate(
        chunk_id="c1", parent_id=None, doc_id="d1", category="cat", document_title="Doc",
        section_or_rule="Sec 1", legal_hierarchy="Doc > Sec 1", text="Text 1", score=0.9,
        retrieval_method="dense", source_url="url", issuing_authority="auth",
        verification_status="verified", is_authoritative=True
    )
    cand2 = RetrievedCandidate(
        chunk_id="c2", parent_id=None, doc_id="d1", category="cat", document_title="Doc",
        section_or_rule="Sec 2", legal_hierarchy="Doc > Sec 2", text="Text 2", score=0.8,
        retrieval_method="dense", source_url="url", issuing_authority="auth",
        verification_status="verified", is_authoritative=True
    )
    cand3 = RetrievedCandidate(
        chunk_id="c3", parent_id=None, doc_id="d1", category="cat", document_title="Doc",
        section_or_rule="Sec 3", legal_hierarchy="Doc > Sec 3", text="Text 3", score=0.7,
        retrieval_method="sparse", source_url="url", issuing_authority="auth",
        verification_status="verified", is_authoritative=True
    )

    # Dense ranked: [c1 (rank 1), c2 (rank 2)]
    # Sparse ranked: [c2 (rank 1), c3 (rank 2)]
    # RRF score for c1 = 1 / (60 + 1) = 1/61 = 0.01639
    # RRF score for c2 = 1 / (60 + 2) + 1 / (60 + 1) = 1/62 + 1/61 = 0.01613 + 0.01639 = 0.03252
    # RRF score for c3 = 1 / (60 + 2) = 1/62 = 0.01613
    # Therefore, c2 MUST be ranked 1st!

    dense_results = [cand1, cand2]
    sparse_results = [cand2, cand3]

    fused = retriever.reciprocal_rank_fusion(dense_results, sparse_results, top_k=2)

    assert len(fused) == 2
    assert fused[0].chunk_id == "c2"
    assert pytest.approx(fused[0].score, 0.0001) == (1.0 / 61 + 1.0 / 62)
    assert fused[1].chunk_id == "c1"
    assert pytest.approx(fused[1].score, 0.0001) == 1.0 / 61
