# NyayaSaathi AI — Empirical RAG Evaluation & Benchmarking Report

**Date Generated:** 2026-11-15 12:12:21 UTC  
**Embedding Model:** `intfloat/multilingual-e5-small`  
**Fusion Method:** Reciprocal Rank Fusion (RRF, $k=60$)  
**Knowledge Graph:** NetworkX Bounded Traversal ($hops=1$)  

---

## 1. Executive Summary

This evaluation benchmarks the NyayaSaathi AI Retrieval-Augmented Generation pipeline across 15 curated Indian Consumer Protection test queries covering statutory legislation, regulatory rules, National Consumer Helpline procedures, and CCPA guidelines.

### Key Findings:
- **Hybrid RAG + Legal Knowledge Graph** achieved superior performance over standalone vector and BM25 configurations.
- **Reciprocal Rank Fusion (RRF)** effectively mitigates vector false-positives on legal section numbers and BM25 sensitivity to synonym phrasing.
- **Corrective RAG (CRAG)** successfully identifies evidence sufficiency and prevents ungrounded synthesis.
- **Reflection-Based Answer Verification** enforces a 100% citation ground-truth validation rate and statutory disclaimer compliance.

---

## 2. Multi-Strategy Retrieval Benchmark (Top-10 Candidates)

| Retrieval Strategy | Recall@3 | Recall@5 | Recall@10 | MRR | Category Match | Avg Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **VECTOR_ONLY** | 86.7% | 93.3% | 100.0% | 0.8430 | 73.3% | 81.9 ms |
| **BM25_ONLY** | 73.3% | 86.7% | 86.7% | 0.6889 | 53.3% | 6.83 ms |
| **HYBRID** | 100.0% | 100.0% | 100.0% | 0.8778 | 73.3% | 161.31 ms |
| **HYBRID_GRAPH** | 100.0% | 100.0% | 100.0% | 0.8778 | 73.3% | 193.77 ms |

---

## 3. Corrective RAG (CRAG) & Verification Metrics

- **Queries Sampled for Generation:** 8
- **CRAG Outcomes:** `SUFFICIENT`: 8, `PARTIALLY_SUFFICIENT`: 0, `INSUFFICIENT`: 0
- **Average Citation Precision:** 100.0%
- **Statutory Disclaimer Enforcement:** 100.0%

---

## 4. Empirical Performance Analysis

### Why Hybrid RAG Outperforms Dense Vector Alone
Dense embedding models like `intfloat/multilingual-e5-small` excel at semantic matching (e.g. mapping 'broken laptop delivered' to 'defective goods and product liability'). However, in statutory law, precise tokens like *'Section 35'*, *'Rule 2'*, or *'1915'* are critical. BM25 guarantees that specific statutory identifiers are never lost, while RRF fuses both ranks without requiring arbitrary threshold calibration.

### Role of Legal Knowledge Graph
Graph traversal adds 1-hop semantic enrichment: when a candidate chunk citing *Rule 2 of the 2021 Jurisdiction Rules* is retrieved, the graph automatically attaches the relationship `(GOVERNS) -> District Consumer Disputes Redressal Commission`, providing the LLM with connected institutional context without expanding the candidate set unnecessarily.

---

## 5. Verification Gate Status

| Quality Gate | Threshold | Achieved | Status |
| :--- | :---: | :---: | :---: |
| Hybrid Recall@5 | $\ge 75.0\%$ | 100.0% | PASSED |
| Mean Reciprocal Rank (MRR) | $\ge 0.50$ | 0.8778 | PASSED |
| Citation Precision | $\ge 80.0\%$ | 100.0% | PASSED |
| Mandatory Disclaimer Compliance | $100.0\%$ | 100.0% | PASSED |
