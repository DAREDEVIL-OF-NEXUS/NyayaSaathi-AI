# NyayaSaathi AI (न्यायसाथी AI)

[![CI Pipeline](https://github.com/neural-ai-society/NyayaSaathi-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/neural-ai-society/NyayaSaathi-AI)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js: 14+](https://img.shields.io/badge/next.js-14+-black.svg)](https://nextjs.org/)
[![Vector DB: Qdrant](https://img.shields.io/badge/Vector%20DB-Qdrant-red.svg)](https://qdrant.tech/)

> **A Production-Grade Retrieval-Augmented Generation (RAG) Platform for Indian Consumer Protection and Legal Grievance Redressal.**
> Built for **Neural AI Society, Delhi Technological University (DTU)**.

---

## 🏛️ Executive Summary

NyayaSaathi AI bridges the gap between everyday Indian consumers and the complex legal landscape of consumer rights. Millions of consumers face e-commerce fraud, unfair trade practices, misleading advertisements, and deficient services, but struggle to identify applicable remedies under the **Consumer Protection Act, 2019**, the **Consumer Protection (E-Commerce) Rules, 2020**, and statutory procedures under the National Consumer Helpline (NCH) and Consumer Disputes Redressal Commissions (District, State, and National).

NyayaSaathi AI provides a reliable, context-grounded AI assistant that:
1. **Never hallucinates legal provisions**: Strictly grounds answers in official Indian legislation, statutory rules, and administrative gazettes.
2. **Employs Hybrid RAG**: Combines semantic embeddings (`multilingual-e5-small`) with BM25 lexical retrieval fused via Reciprocal Rank Fusion (RRF).
3. **Validates All Citations**: Verifies that every cited statutory section, rule, and paragraph exists in retrieved context with strict sentence-level grounding.
4. **Drafts Structured Grievances**: Generates legally structured complaints ready for filing before the National Consumer Helpline (NCH) or e-Daakhil / e-Jagriti consumer forums with PDF export.
5. **Maintains Complete Data Isolation**: Ensures user evidence and private documents remain segregated and are never indexed into the public legal knowledge base.

---

## 📐 High-Level Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │          Next.js Frontend (App Router)       │
                  │  (Chat Assistant, Knowledge Base, Complaint) │
                  └──────────────────────┬───────────────────────┘
                                         │ REST / SSE Stream
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │              FastAPI Backend                 │
                  └──────────────┬───────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────────────┐
         ▼                       ▼                               ▼
┌──────────────────┐    ┌──────────────────┐           ┌──────────────────┐
│  Hybrid RAG      │    │  LLM Orchestrator│           │  Relational DB   │
│  Engine          │    │  (Gemini + Fall- │           │  (PostgreSQL /   │
│  - Dense: Qdrant │    │   back OpenRouter│           │   SQLite)        │
│  - Sparse: BM25  │    │  - Pydantic Valid│           │  Cases, Chat,    │
│  - RRF Fusion    │    │  - Citation Check│           │  User Docs       │
└──────────────────┘    └──────────────────┘           └──────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Docker & Docker Compose (optional, standalone local mode supported out of the box)

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/neural-ai-society/NyayaSaathi-AI.git
cd NyayaSaathi-AI

# Create your local environment configuration
cp .env.example .env
```
Edit `.env` and provide your `GEMINI_API_KEY` (or `OPENROUTER_API_KEY`).

### 3. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# Run database migrations and seed official knowledge base
python ../scripts/download_data.py
python ../scripts/ingest_data.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000` to interact with NyayaSaathi AI.

---

## 📚 Legal Scope & Official Sources

NyayaSaathi AI operates exclusively on vetted, official Indian legal documentation:
- **Consumer Protection Act, 2019** (Act No. 35 of 2019, Ministry of Law and Justice / India Code)
- **Consumer Protection (E-Commerce) Rules, 2020** (G.S.R. 452(E), Department of Consumer Affairs)
- **Consumer Protection (E-Commerce) Amendment Rules, 2021**
- **Consumer Protection (Mediation) Rules, 2020**
- **Consumer Protection (Consumer Disputes Redressal Commissions) Rules, 2020**
- **Consumer Protection (Jurisdiction of Commissions) Rules, 2021**
- **Central Consumer Protection Authority (CCPA) Guidelines for Prevention of Misleading Advertisements, 2022**
- **National Consumer Helpline (NCH) Standard Operating Procedures & FAQs**

*Disclaimer: NyayaSaathi AI provides informational and procedural assistance grounded in official Indian legal texts. It does not provide formal legal representation, attorney-client privileged counsel, or judicial determination of liability.*
