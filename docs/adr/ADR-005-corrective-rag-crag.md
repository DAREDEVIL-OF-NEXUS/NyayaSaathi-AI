# ADR-005: Corrective RAG (CRAG) with Evidence Sufficiency Assessment

## Status
Accepted

## Context
Standard RAG pipelines blindly feed retrieved documents to the generator even when the retrieval is irrelevant, out-of-scope, or insufficient. In legal advisory applications, generating ungrounded advice poses unacceptable risks of misleading consumers.

## Decision
Implement a formal Corrective RAG (CRAG) pipeline:
1. Evaluator assesses retrieved evidence across three quality dimensions: keyword relevance, category alignment, and score confidence.
2. Three-way classification:
   - `SUFFICIENT`: Confidence $\ge 0.65$; directly feeds the generator.
   - `PARTIALLY_SUFFICIENT`: Confidence between $0.35$ and $0.65$; triggers LLM query rewriting and secondary retrieval before merging.
   - `INSUFFICIENT`: Confidence $< 0.35$ or out-of-scope; halts generation and returns safe legal abstention with referral to official bodies (e.g. NCH 1915 or legal counsel).

## Consequences
- **Positive:** Prevents hallucinated statutory provisions for ungrounded or off-topic queries.
- **Positive:** Triggers automated query reformulation for ambiguous consumer phrasing.
