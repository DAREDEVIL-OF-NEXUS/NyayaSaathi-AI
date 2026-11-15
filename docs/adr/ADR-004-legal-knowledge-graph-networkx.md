# ADR-004: Lightweight Legal Knowledge Graph via NetworkX & Relational Backing

## Status
Accepted

## Context
Legal provisions cross-reference one another continuously (e.g. *Section 35* references *Section 34* for jurisdiction and *Section 37* for mediation). A dedicated graph database (e.g. Neo4j) introduces heavy deployment overhead and operational complexity.

## Decision
Implement a lightweight in-process legal knowledge graph using Python `NetworkX` backed by PostgreSQL / SQLite tables:
1. Tables: `legal_entities` and `legal_relationships`.
2. Explicit entities: `Act`, `Chapter`, `Section`, `Rule`, `Authority`, `Remedy`, `Commission`.
3. Bounded 1-hop traversal: When hybrid retrieval identifies candidate legal chunks, the graph expands connected entities (e.g. linking *Rule 2* to *District Commission* via `GOVERNS`).
4. Graph provenance is attached to the candidate context passed to LLM generation.

## Consequences
- **Positive:** Zero external graph database infrastructure required; instant hydration into memory (<5ms).
- **Positive:** Enforces strict domain relations (`CONTAINS`, `REFERENCES`, `DEFINES`, `AMENDS`, `GOVERNS`, `ESCALATES_TO`).
- **Negative:** Limited to sub-graph traversals; complex multi-hop graph algorithms must be bounded to avoid latency.
