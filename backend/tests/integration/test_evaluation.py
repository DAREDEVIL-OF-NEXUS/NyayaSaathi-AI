import os
import json
import pytest
from scripts.evaluate_rag import evaluate_retrieval_strategy, load_benchmark_queries
from backend.app.services.rag.retrieval import get_hybrid_retriever
from backend.app.services.rag.generation import get_generation_service

@pytest.fixture(scope="module")
def benchmark_queries():
    queries_path = "./data/evaluation/preliminary_queries.json"
    assert os.path.exists(queries_path), "Benchmark queries file missing"
    return load_benchmark_queries(queries_path)

def test_evaluation_retrieval_metrics(benchmark_queries):
    retriever = get_hybrid_retriever()

    # Evaluate Hybrid strategy
    res_hybrid = evaluate_retrieval_strategy(benchmark_queries, retriever, mode="hybrid", top_k=5)
    
    # Assert quality gates
    assert res_hybrid["recall_at_5"] >= 0.75, f"Hybrid Recall@5 {res_hybrid['recall_at_5']} below 75% threshold"
    assert res_hybrid["mrr"] >= 0.50, f"Hybrid MRR {res_hybrid['mrr']} below 0.50 threshold"
    assert res_hybrid["queries_evaluated"] == len(benchmark_queries)

def test_evaluation_crag_and_disclaimer():
    gen_service = get_generation_service()
    
    # Test sample query
    query = "What is the pecuniary jurisdiction limit for filing a consumer complaint in the District Commission?"
    res = gen_service.generate_response(query=query, top_k=4)

    assert res.summary is not None
    assert len(res.summary) > 20
    assert "District" in res.summary or len(res.applicable_laws) > 0
    assert res.disclaimer is not None
    assert len(res.disclaimer) > 20
    assert res.verification_metadata.get("is_verified", False) is True
