import pytest
from unittest.mock import MagicMock
from backend.app.services.rag.retrieval import RetrievedCandidate
from backend.app.services.rag.crag import (
    CRAGDecision,
    CRAGEvaluationResult,
    CRAGEvaluator,
    QueryRewriter,
    CRAGPipeline
)

def make_candidate(chunk_id: str, sec: str, text: str, score: float) -> RetrievedCandidate:
    return RetrievedCandidate(
        chunk_id=chunk_id,
        parent_id=None,
        doc_id="cpa_act",
        category="1_statutory",
        document_title="Consumer Protection Act, 2019",
        section_or_rule=sec,
        legal_hierarchy=f"CPA > {sec}",
        text=text,
        score=score,
        retrieval_method="hybrid_rrf",
        source_url="https://indiacode.nic.in",
        issuing_authority="Legislative Dept",
        verification_status="verified_official",
        is_authoritative=True
    )

def test_crag_evaluator_sufficient():
    evaluator = CRAGEvaluator(sufficient_threshold=0.60, insufficient_threshold=0.30)
    candidates = [
        make_candidate(
            "c1",
            "Section 28",
            "Section 28: Establishment of District Commission with pecuniary jurisdiction up to fifty lakh rupees.",
            0.05
        )
    ]
    query = "What is the pecuniary jurisdiction of District Commission up to fifty lakh?"
    res = evaluator.evaluate(query, candidates)

    assert res.decision == CRAGDecision.SUFFICIENT
    assert res.confidence_score >= 0.60
    assert len(res.missing_aspects) == 0

def test_crag_evaluator_insufficient():
    evaluator = CRAGEvaluator(sufficient_threshold=0.60, insufficient_threshold=0.30)
    candidates = []
    query = "Unrelated inquiry about corporate mergers"
    res = evaluator.evaluate(query, candidates)

    assert res.decision == CRAGDecision.INSUFFICIENT
    assert res.confidence_score == 0.0
    assert res.clarification_question is not None

def test_query_rewriter_heuristic():
    rewriter = QueryRewriter()
    query = "Amazon delivered damaged product and refused no refund"
    rewritten = rewriter.rewrite_heuristic(query, ["statutory_timeline"])

    assert "marketplace e-commerce entity" in rewritten
    assert "defective product" in rewritten
    assert "Rule 7" in rewritten
    assert "statutory_timeline" in rewritten

def test_crag_pipeline_sufficient_no_secondary():
    mock_retriever = MagicMock()
    mock_evaluator = MagicMock()
    mock_rewriter = MagicMock()

    cands = [make_candidate("c1", "Section 28", "Jurisdiction details", 0.05)]
    mock_retriever.retrieve.return_value = cands
    mock_evaluator.evaluate.return_value = CRAGEvaluationResult(
        decision=CRAGDecision.SUFFICIENT,
        confidence_score=0.85,
        reasoning="Sufficient evidence.",
        missing_aspects=[]
    )

    pipeline = CRAGPipeline(retriever=mock_retriever, evaluator=mock_evaluator, rewriter=mock_rewriter)
    result = pipeline.run("What is District Commission limit?")

    assert result.decision == CRAGDecision.SUFFICIENT
    assert result.secondary_retrieval_performed is False
    assert mock_retriever.retrieve.call_count == 1
    mock_rewriter.rewrite_with_llm.assert_not_called()

def test_crag_pipeline_partially_sufficient_triggers_secondary():
    mock_retriever = MagicMock()
    mock_evaluator = MagicMock()
    mock_rewriter = MagicMock()

    initial_cands = [make_candidate("c1", "General", "Partial discussion", 0.02)]
    secondary_cands = [make_candidate("c2", "Rule 5", "Grievance redressal within 48 hours", 0.04)]

    mock_retriever.retrieve.side_effect = [initial_cands, secondary_cands]
    mock_rewriter.rewrite_with_llm.return_value = "E-Commerce Rules 2020 Rule 5 grievance officer"

    mock_eval1 = CRAGEvaluationResult(
        decision=CRAGDecision.PARTIALLY_SUFFICIENT,
        confidence_score=0.45,
        reasoning="Partial evidence.",
        missing_aspects=["Rule 5"],
        clarification_question=None
    )
    mock_eval2 = CRAGEvaluationResult(
        decision=CRAGDecision.SUFFICIENT,
        confidence_score=0.80,
        reasoning="Sufficient secondary evidence.",
        missing_aspects=[]
    )
    mock_evaluator.evaluate.side_effect = [mock_eval1, mock_eval2]

    pipeline = CRAGPipeline(retriever=mock_retriever, evaluator=mock_evaluator, rewriter=mock_rewriter)
    result = pipeline.run("Customer care not answering complaint")

    assert result.decision == CRAGDecision.SUFFICIENT
    assert result.secondary_retrieval_performed is True
    assert mock_retriever.retrieve.call_count == 2
    assert len(result.candidates) == 2
