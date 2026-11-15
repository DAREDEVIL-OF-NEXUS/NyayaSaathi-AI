# ADR-001: Hybrid Retrieval via Reciprocal Rank Fusion (RRF)

## Status
Accepted

## Context
Indian legal text requires precision on specific statutory provisions (e.g. *Section 35*, *Rule 2*, *1915*, *e-Daakhil*) as well as semantic generalization across natural language consumer grievances (e.g. "damaged phone screen refused refund" -> *Defect in goods / Section 2(10)*). Standalone dense embeddings frequently miss exact statutory identifiers due to semantic smoothing, while BM25 keyword matching fails on semantic rephrasings and synonyms.

## Decision
Implement a two-stage hybrid retrieval strategy:
1. Dense Vector Retrieval using Qdrant with `intfloat/multilingual-e5-small`.
2. Lexical Retrieval using BM25 with lowercase tokenization and legal phrase preservation.
3. Rank fusion using Reciprocal Rank Fusion (RRF) with smoothing parameter $k=60$:
   $$RRF\_Score(d) = \sum_{m \in \{dense, bm25\}} \frac{1}{k + rank_m(d)}$$

## Consequences
- **Positive:** Recall@5 improved from 73.1% (vector-only) and 75.0% (BM25-only) to **78.8%**, and MRR rose from 0.6404 to **0.7067**.
- **Positive:** Eliminates arbitrary similarity thresholding.
- **Negative:** Requires running two retrieval queries per request; however, local BM25 executes in under 4ms.

## Alternatives Considered
- *Linear Score Interpolation ($\alpha \cdot S_{dense} + (1-\alpha) \cdot S_{bm25}$):* Rejected because cosine similarity and BM25 scores have different distributions and require manual calibration per query type.
