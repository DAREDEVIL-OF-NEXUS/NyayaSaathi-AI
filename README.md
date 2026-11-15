# NyayaSaathi AI (न्यायसाथी AI)

[![CI Pipeline](https://github.com/DAREDEVIL-OF-NEXUS/NyayaSaathi-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/DAREDEVIL-OF-NEXUS/NyayaSaathi-AI)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js: 14+](https://img.shields.io/badge/next.js-14+-black.svg)](https://nextjs.org/)
[![Vector DB: Qdrant](https://img.shields.io/badge/Vector%20DB-Qdrant-red.svg)](https://qdrant.tech/)

> **A Production-Grade Retrieval-Augmented Generation (RAG) & Legal Knowledge Graph Platform for Indian Consumer Protection and Grievance Redressal.**  
> Built for **Neural AI Society, Delhi Technological University (DTU)**.

---

## 🏛️ Executive Summary

NyayaSaathi AI (न्यायसाथी AI) is an intelligent, context-grounded legal technology assistant for Indian consumers. When facing defective products, e-commerce refund refusals, deficient services, misleading advertisements, or arbitrary cancellation penalties, consumers often struggle to navigate statutory remedies under the **Consumer Protection Act, 2019**, the **Consumer Protection (E-Commerce) Rules, 2020**, and statutory procedures under the **National Consumer Helpline (NCH 1915)** and **Consumer Disputes Redressal Commissions (District, State, and National)**.

NyayaSaathi AI solves this through a multi-tier RAG and Legal Knowledge Graph architecture:
1. **Zero Statutory Hallucinations**: Grounded strictly in official Indian legislation, statutory rules, and administrative gazettes.
2. **Hybrid RAG + Knowledge Graph**: Dense embeddings (`intfloat/multilingual-e5-small`) combined with Okapi BM25, fused via Reciprocal Rank Fusion ($k=60$) and enriched with a NetworkX-based legal knowledge graph.
3. **Corrective RAG (CRAG)**: Evaluates evidence sufficiency (`SUFFICIENT`, `PARTIALLY_SUFFICIENT`, `INSUFFICIENT`) and rewrites queries for targeted secondary retrieval when necessary.
4. **Reflection-Based Answer Verification**: Programmatically extracts and cross-validates citations against retrieved chunks, detecting speculative statements and enforcing mandatory disclaimers.
5. **Section 35 Complaint Drafting Studio**: Automatically determines pecuniary jurisdiction and generates formal consumer complaint petitions ready for filing on e-Daakhil / e-Jagriti.
6. **Smart Invoice & Grievance Analyzer**: Scans uploaded receipts/invoices (PDF/TXT), extracts key transaction parameters, and flags unfair trade terms.

---

## 📐 System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   Next.js 14 Frontend (App Router)                     │
│  - Consultation Chat  - Complaint Studio  - Invoice Analyzer  - Graph  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST / SSE Stream
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend (v1 API)                        │
└───────┬───────────────────────────┬────────────────────────────┬───────┘
        │                           │                            │
        ▼                           ▼                            ▼
┌──────────────────┐    ┌────────────────────────┐      ┌────────────────┐
│   Hybrid RAG     │    │   Corrective RAG       │      │ Relational DB  │
│  - Dense: Qdrant │    │   (CRAG) Pipeline      │      │ (Postgres/     │
│  - Sparse: BM25  │    │  - Evaluator           │      │  SQLite)       │
│  - RRF (k=60)    │    │  - Query Rewriter      │      │ - Cases        │
└───────┬──────────┘    └───────────┬────────────┘      │ - Sessions     │
        │                           │                   │ - Drafts       │
        ▼                           ▼                   └────────────────┘
┌──────────────────┐    ┌────────────────────────┐
│  Legal Knowledge │    │   LLM Provider Manager │
│  Graph Engine    │    │  - Gemini 1.5 Flash    │
│  - NetworkX      │    │  - OpenRouter Fallback │
│  - 1-Hop Bounded │    │  - Reflection Verifier │
└──────────────────┘    └────────────────────────┘
```

---

## 📊 Empirical RAG Evaluation Benchmark

Evaluated across **15 benchmark Indian Consumer Protection queries** covering statutory legislation, regulatory rules, and administrative procedures:

| Retrieval Strategy | Recall@3 | Recall@5 | Recall@10 | MRR | Category Match | Avg Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **BM25 Lexical** | 73.3% | 86.7% | 86.7% | 0.6889 | 80.0% | 6.8 ms |
| **Dense Vector (E5)** | 86.7% | 93.3% | 100.0% | 0.8430 | 93.3% | 81.9 ms |
| **Hybrid (RRF $k=60$)** | **100.0%** | **100.0%** | **100.0%** | **0.8778** | **100.0%** | 161.3 ms |
| **Hybrid + Knowledge Graph** | **100.0%** | **100.0%** | **100.0%** | **0.8778** | **100.0%** | 193.8 ms |

### Quality Gates Verified:
- **Citation Precision**: `100.0%` (Zero hallucinated sections)
- **Statutory Disclaimer Compliance**: `100.0%`
- **Mean Reciprocal Rank (MRR)**: `0.8778` (Primary statutory provision at Rank 1 in 88% of queries)

Detailed evaluation findings are recorded in [`docs/RAG_EVALUATION_REPORT.md`](docs/RAG_EVALUATION_REPORT.md).

---

## 🚀 Quick Start

### Option A: Local Development Setup

#### 1. Clone & Configure
```bash
git clone https://github.com/DAREDEVIL-OF-NEXUS/NyayaSaathi-AI.git
cd NyayaSaathi-AI
cp .env.example .env
```
*(Optionally provide your `GEMINI_API_KEY` or `OPENROUTER_API_KEY` in `.env`. Hermetic mock providers run automatically in dev mode if keys are omitted).*

#### 2. Backend Setup
```bash
# Using uv (recommended) or standard venv
uv venv
.\.venv\Scripts\activate      # Windows
source .venv/bin/activate     # Linux / macOS

uv pip install -r backend/requirements.txt

# Run the test suite (all 45 tests)
uv run pytest backend/tests -v

# Start FastAPI server
uv run uvicorn backend.app.main:app --reload --port 8000
```
Backend Swagger API will be live at: `http://localhost:8000/docs`.

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000` to interact with NyayaSaathi AI.

---

### Option B: Docker Compose Deployment

To spin up the entire multi-container stack (FastAPI backend, PostgreSQL, Qdrant vector database, and Next.js frontend):

```bash
docker compose up --build -d
```

- **Frontend App**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Qdrant Vector DB**: `http://localhost:6333`
- **PostgreSQL**: `localhost:5432`

---

## 📚 Official Ingested Legal Sources

NyayaSaathi AI operates exclusively on verified Indian government legal documentation:
1. **Consumer Protection Act, 2019** (Act No. 35 of 2019, Ministry of Law and Justice / India Code)
2. **Consumer Protection (E-Commerce) Rules, 2020** (Official Gazette G.S.R. 452(E), Dept of Consumer Affairs)
3. **Consumer Protection (Jurisdiction of Commissions) Rules, 2021** (Official Gazette G.S.R. 888(E))
4. **CCPA Guidelines for Prevention of Misleading Advertisements, 2022** (Central Authority)
5. **National Consumer Helpline (NCH) Standard Operating Procedures & FAQs** (consumerhelpline.gov.in)
6. **e-Jagriti / e-Daakhil Redressal Guidelines** (edaakhil.nic.in)

Source provenance details and SHA-256 hashes are tracked in [`data/manifest/sources.json`](data/manifest/sources.json).

---

## ⚖️ Mandatory Statutory Notice

> **IMPORTANT DISCLAIMER**: NyayaSaathi AI (न्यायसाथी AI) provides automated legal information and procedural assistance based on public Indian consumer statutes and administrative guidance. It **does not** constitute formal legal advice, representation, or an attorney-client relationship under the Advocates Act, 1961. For active disputes or judicial filings, citizens are advised to seek counsel from an enrolled advocate or register a grievance with the **National Consumer Helpline (Toll-Free 1915 / SMS 8800001915)**.
