# ADR-003: Hierarchical Legal Parent-Child Chunking

## Status
Accepted

## Context
Statutory documents (Acts, Rules, Guidelines) possess strict hierarchical structures: Act -> Chapter -> Section -> Subsection -> Clause. Naive fixed-character chunking splits legal definitions mid-sentence and severs the relationship between a penalty clause and its governing section.

## Decision
Implement a legal-aware chunking pipeline:
1. Regex-driven statutory boundary detection (`Section [0-9]+`, `Rule [0-9]+`, `CHAPTER [IVXLCDM]+`).
2. Parent chunks correspond to complete statutory sections or administrative chapters (up to 2000 characters).
3. Child chunks represent individual subsections or clauses (300-600 characters) with 50-character overlap.
4. Each child chunk inherits full document metadata: `document_id`, `category`, `act_name`, `section_or_rule`, `issuing_authority`, and SHA-256 document hash.

## Consequences
- **Positive:** Enables child-level precision during vector retrieval while retaining parent context for LLM prompt synthesis.
- **Positive:** Zero orphan chunks; exact statutory provenance is preserved for citation validation.
