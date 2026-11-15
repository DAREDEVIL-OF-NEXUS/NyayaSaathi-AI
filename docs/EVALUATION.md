# NyayaSaathi AI — RAG Evaluation Framework

## 1. Evaluation Methodology
Legal information retrieval requires substantially higher precision than general conversational QA. A single hallucinated section number can mislead a citizen. NyayaSaathi AI incorporates an automated evaluation harness testing:

1. **Retrieval Recall@5 and Recall@10**: Proportion of test queries where statutory ground-truth sections are retrieved in the top 5 and 10 results.
2. **Mean Reciprocal Rank (MRR)**: Evaluates whether the primary applicable statute or rule appears at rank 1 or 2.
3. **Citation Precision**: Proportion of generated citations that match valid retrieved chunks and contain genuine statutory provisions.
4. **Citation Coverage**: Proportion of substantive legal statements in the generated response backed by valid citations.
5. **Answer Faithfulness**: Degree to which the synthesized answer is strictly supported by retrieved passages without extrapolation.
6. **Latency Profiling**: Dense retrieval, BM25 retrieval, RRF fusion, and end-to-end generation timings.

---

## 2. Multi-Strategy Comparative Analysis

The evaluation script (`scripts/evaluate_rag.py`) automatically evaluates three search configurations across the benchmark test suite:
- **Vector-Only**: Dense retrieval using `multilingual-e5-small`.
- **BM25-Only**: Lexical retrieval using Okapi BM25.
- **Hybrid (Dense + BM25 with RRF)**: Reciprocal Rank Fusion (k=60).

Comparative outputs are logged in `data/evaluation/benchmark_results.json` and rendered in the Admin Dashboard.
