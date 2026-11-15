# ADR-006: Reflection-Based Citation Verification & Statutory Guardrails

## Status
Accepted

## Context
LLMs frequently hallucinate statutory sections, penalties, or case law that look plausible but are legally invalid. Generated responses must strictly ground every factual claim in verified knowledge base chunks.

## Decision
Implement a reflection-based post-generation verification stage (`AnswerVerifier`):
1. Extract all citation markers (e.g. `[Doc 1]`, `Section 35`, `Rule 2`).
2. Verify each citation against the actual text of retrieved candidate chunks.
3. Compute `citation_precision`:
   $$\text{Precision} = \frac{\text{Verified Citations}}{\text{Total Citations Claimed}}$$
4. If invalid citations exceed tolerance, regenerate response with corrective instructions or redact hallucinated claims.
5. Guarantee statutory disclaimer presence in 100% of generated responses.

## Consequences
- **Positive:** Benchmark achieves 100% citation precision and 100% disclaimer compliance.
- **Positive:** Provides users with verifiable audit trails linked directly to official statutory texts.
