# NyayaSaathi AI (न्यायसाथी AI) — REST API Documentation (v1)

NyayaSaathi AI provides a production-grade REST API and Server-Sent Events (SSE) streaming interface for Indian Consumer Protection consultation, grievance classification, formal petition drafting, and legal knowledge base traversal.

- **Base URL:** `http://localhost:8000/api/v1`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 1. System Endpoints

### `GET /health`
Returns high-level system health and service version.

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "timestamp": "2026-11-15T17:30:00.000000",
  "service": "NyayaSaathi AI",
  "version": "1.0.0"
}
```

### `GET /ready`
Readiness probe verifying relational database connectivity, embedding model, and LLM providers.

**Response `200 OK`:**
```json
{
  "status": "ready",
  "database_connected": true,
  "environment": "development",
  "embedding_model": "intfloat/multilingual-e5-small",
  "llm_primary_provider": "gemini",
  "llm_fallback_provider": "openrouter",
  "timestamp": "2026-11-15T17:30:00.000000"
}
```

---

## 2. Chat & Legal Consultation

### `POST /api/v1/chat`
Submits a consumer query to the Corrective RAG (CRAG) pipeline, retrieves statutory provisions and knowledge graph relationships, queries the resilient LLM, verifies citations against context, and returns a structured response.

**Request Body:**
```json
{
  "query": "Seller delivered damaged product on Flipkart and refused refund.",
  "conversation_id": null,
  "mode": "hybrid_graph",
  "top_k": 6,
  "filter_category": "2_regulatory_ccpa"
}
```

**Response `200 OK`:**
```json
{
  "conversation_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "message_id": "1c2d3e4f-5a6b-7c8d-9e0f-1a2b3c4d5e6f",
  "response": {
    "summary": "Under Rule 4 & 5 of the Consumer Protection (E-Commerce) Rules, 2020...",
    "applicable_laws": [
      {
        "act_or_regulation": "Consumer Protection (E-Commerce) Rules, 2020",
        "section_or_rule": "Rule 4 & 5",
        "provision_title": "Duties of e-commerce entities",
        "summary_of_relevance": "Mandates transparent return and refund policies for e-commerce entities.",
        "is_authoritative": true,
        "source_url": "https://consumeraffairs.nic.in"
      }
    ],
    "consumer_rights": ["Right to be protected against unfair trade practices", "Right to seek redressal"],
    "recommended_steps": [
      "Lodge an official grievance on National Consumer Helpline (NCH 1915).",
      "Issue a formal legal notice to the opposite party.",
      "File a complaint on e-Daakhil if unresolved within 15 days."
    ],
    "appropriate_forums": [
      {
        "forum_name": "District Consumer Disputes Redressal Commission",
        "pecuniary_jurisdiction": "Up to Rs 50,00,000",
        "filing_procedure": "File via e-Daakhil portal or submit physical petition under Section 35.",
        "official_portal_or_contact": "https://edaakhil.nic.in"
      }
    ],
    "required_documents": [
      "Purchase invoice / consideration proof",
      "Photographs of damaged goods"
    ],
    "statutory_timelines": [
      "Limitation period of 2 years from date of cause of action (Section 69, CPA 2019)"
    ],
    "disclaimer": "This information is generated for educational purposes and does not constitute formal legal representation.",
    "citations": [
      {
        "citation": "Consumer Protection (E-Commerce) Rules, 2020",
        "document_title": "Consumer Protection (E-Commerce) Rules, 2020",
        "category": "2_regulatory_ccpa",
        "source_url": "https://consumeraffairs.nic.in",
        "issuing_authority": "Ministry of Consumer Affairs",
        "is_authoritative": true,
        "verification_status": "verified"
      }
    ],
    "crag_metadata": {
      "decision": "SUFFICIENT",
      "confidence_score": 0.85
    },
    "verification_metadata": {
      "is_verified": true,
      "citation_precision": 1.0,
      "validated_citations": ["Consumer Protection (E-Commerce) Rules, 2020"],
      "invalid_citations": [],
      "hallucination_detected": false
    },
    "provider_used": "gemini",
    "model_name": "gemini-1.5-flash"
  },
  "created_at": "2026-11-15T17:30:00.000000"
}
```

### `POST /api/v1/chat/stream`
Server-Sent Events (SSE) streaming endpoint. Yields progress updates, generated token slices, and the final structured payload.

```text
data: {"type": "status", "stage": "crag_retrieval", "message": "Retrieving statutory provisions..."}

data: {"type": "token", "token": "Under Rule 4 "}

data: {"type": "complete", "conversation_id": "...", "message_id": "...", "response": {...}}
```

### `GET /api/v1/conversations`
Lists saved consultation sessions with message counts and last update timestamps.

### `GET /api/v1/conversations/{id}`
Returns all messages associated with a consultation session.

### `DELETE /api/v1/conversations/{id}`
Deletes a consultation session and its associated messages.

### `POST /api/v1/messages/{id}/feedback`
Records 1 to 5 star rating and feedback comments.

---

## 3. Consumer Grievance & Complaints Engine

### `POST /api/v1/complaints/classify`
Classifies a consumer grievance description into one of 4 statutory categories and computes the competent forum based on the pecuniary claim.

**Request Body:**
```json
{
  "grievance_description": "Purchased a refrigerator for Rs 42,000 which caught fire due to manufacturing defect.",
  "transaction_amount": 42000.0,
  "platform_or_company": "Samsung India"
}
```

**Response `200 OK`:**
```json
{
  "category": "Defective Product & Product Liability",
  "confidence": 0.90,
  "recommended_forum": "District Consumer Disputes Redressal Commission",
  "pecuniary_slab": "Up to ₹50,00,000 (Fifty Lakh Rupees)",
  "applicable_provisions": [
    "Section 2(34) Product Liability, Consumer Protection Act, 2019",
    "Section 84 Liability of Product Manufacturer"
  ],
  "suggested_reliefs": [
    "Replacement with non-defective product or full refund",
    "Damages for loss caused by defective product"
  ],
  "statutory_limitation": "2 years from date of cause of action (Section 69, CPA 2019)"
}
```

### `POST /api/v1/complaints/draft`
Generates a formal legal consumer complaint petition formatted in accordance with Section 35 of the CPA 2019 and persists it to the database.

**Request Body:**
```json
{
  "complainant_name": "Rahul Verma",
  "complainant_contact": "+91-9876543210",
  "complainant_address": "42 Connaught Place, New Delhi 110001",
  "opposite_party_name": "CloudRetail India Pvt Ltd",
  "opposite_party_address": "Buildings Alyssa, Embassy Tech Village, Bengaluru",
  "transaction_amount": 32500.0,
  "transaction_date": "12-10-2023",
  "order_or_invoice_number": "OD402910391039",
  "facts_of_case": "The complainant purchased a 55-inch Smart TV... shattered screen upon delivery...",
  "relief_sought": "Full refund of Rs 32,500 with interest and Rs 25,000 for mental harassment."
}
```

### `GET /api/v1/complaints`
Lists all saved complaint drafts.

### `GET /api/v1/complaints/{id}`
Returns details of a specific complaint draft.

### `GET /api/v1/complaints/{id}/export`
Exports the complaint petition as a downloadable plaintext (`.txt`) file.

---

## 4. Document Ingestion & Invoice Analysis

### `POST /api/v1/documents/upload`
Uploads a receipt/invoice (PDF, TXT) up to 15MB, extracts text, identifies merchant details, flags unfair contract clauses, and maps statutory legal claims.

### `POST /api/v1/documents/analyze`
Directly analyzes text provided in JSON without file upload.

### `GET /api/v1/documents`
Lists uploaded documents.

---

## 5. Knowledge Base & Legal Knowledge Graph

### `POST /api/v1/knowledge/search`
Direct search across the legal corpus with configurable modes (`hybrid`, `hybrid_graph`, `vector_only`, `bm25_only`).

### `GET /api/v1/knowledge/graph/{entity_id}`
Returns entity details and its bounded 1-hop connected neighbors (`REFERENCES`, `GOVERNS`, `ISSUED_BY`, `DEFINES`).

### `GET /api/v1/knowledge/sources`
Returns the curated official sources manifest (`data/manifest/sources.json`).

### `GET /api/v1/knowledge/stats`
Returns live statistics on total documents, graph entities, edges, and embedding models.
