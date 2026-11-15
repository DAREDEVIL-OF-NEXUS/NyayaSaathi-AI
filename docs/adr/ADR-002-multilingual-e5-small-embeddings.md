# ADR-002: Selection of multilingual-e5-small Embedding Model

## Status
Accepted

## Context
Indian consumer protection involves statutory texts written in legal English and potential citizen queries expressed in mixed Indian English or Romanized vernacular terms. The model must run efficiently on local CPU infrastructure (development and evaluation) while retaining strong semantic clustering across 512-token contexts.

## Decision
Adopt `intfloat/multilingual-e5-small` (12 layers, 384 hidden dimensions, ~117M parameters):
- Asymmetric query/passage prefixing is strictly enforced: `query: <text>` for inference and `passage: <text>` for chunk ingestion.
- Normalization of cosine embeddings in Qdrant collection vectors.

## Consequences
- **Positive:** Low CPU memory footprint (~470MB) with fast inference (<30ms per batch).
- **Positive:** Pre-trained on 94 languages including Hindi and Indian English legal corpora.
- **Negative:** Context limited to 512 tokens, requiring parent-child chunking.
