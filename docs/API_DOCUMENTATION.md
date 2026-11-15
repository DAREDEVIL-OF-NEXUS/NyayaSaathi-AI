# NyayaSaathi AI — REST API Documentation (v1)

Base URL: `/api/v1`

---

## 1. System & Health

### `GET /health`
Returns system status, active database dialect, vector index status, and memory stats.

### `GET /health/providers`
Tests connectivity and quota for Google Gemini and OpenRouter adapters.

---

## 2. Chat & Assistant

### `POST /chat`
Execute a non-streaming grounded multi-turn conversation.

### `POST /chat/stream`
Server-Sent Events (SSE) streaming endpoint emitting markdown tokens, citations, and metadata.

---

## 3. Search & Legal Knowledge Base

### `POST /search`
Execute hybrid RRF search across official legislation.

### `GET /documents`
List all ingested statutory documents with metadata, checksums, and chunk counts.

### `GET /sources/{chunk_id}`
Retrieve full text, parent chapter, statutory section, and official citation metadata for a specific chunk.

---

## 4. Grievance Redressal & Drafting

### `POST /complaints/generate`
Draft a formal consumer complaint compliant with Consumer Disputes Redressal Commission norms.

### `POST /documents/analyze`
Extract transactional details, identify defect categories, and flag missing evidentiary documents from uploaded receipts or customer service chats.
