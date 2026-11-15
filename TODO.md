# NyayaSaathi AI — Implementation Roadmap & TODOs

## Phase 0: Environment & Base Setup
- [x] Inspect environment (Python 3.11, Node v24, Git detected)
- [x] Initialize Git repository
- [x] Create project directory layout
- [x] Create `.gitignore`, `.env.example`, `LICENSE`, `docker-compose.yml`, CI workflow
- [x] Initialize `PHASE_STATUS.md` and `TODO.md`
- [x] Write initial `README.md` and architecture documentation

## Phase 1: Dataset Acquisition
- [ ] Author official source manifest in `data/manifest/sources.json`
- [ ] Implement `scripts/download_data.py` with checksumming and validation
- [ ] Collect and verify official legal sources (CPA 2019, E-Commerce Rules 2020/2021, Mediation Rules 2020, Redressal Commission Rules 2020/2021, NCH guidelines)
- [ ] Generate missing document report and manual instructions if any

## Phase 2: Document Extraction & Hybrid RAG Infrastructure
- [ ] Implement PyMuPDF extractor and text normalizer
- [ ] Implement legal-aware structure detection (Chapters, Sections, Subsections, Rules, Clauses)
- [ ] Implement semantic parent-child chunking (target 450-600 tokens, overlap 60-80)
- [ ] Implement Sentence Transformers embeddings (`intfloat/multilingual-e5-small`) with prefix support (`passage:` / `query:`)
- [ ] Implement Qdrant vector database storage with local embedded fallback
- [ ] Implement BM25 lexical search with rank fusion (RRF)
- [ ] Implement `scripts/ingest_data.py` and `scripts/rebuild_index.py`
- [ ] Verify retrieval with test queries

## Phase 3: LLM Providers & Citation Validation
- [ ] Implement LLM interface with Gemini SDK adapter
- [ ] Implement OpenRouter OpenAI-compatible adapter
- [ ] Implement provider fallback with transient error/rate-limit handling
- [ ] Implement Pydantic structured response schema
- [ ] Implement citation validation and grounding engine
- [ ] Unit test providers, fallback mechanism, and citation checks

## Phase 4: Backend REST API
- [ ] Author SQLAlchemy models (User, Conversation, Message, Case, Document, Complaint, IngestionJob)
- [ ] Implement FastAPI application with versioned routes (`/api/v1`)
- [ ] Implement streaming chat endpoint (`/chat/stream`)
- [ ] Implement knowledge base search & document endpoints (`/search`, `/documents`, `/sources`)
- [ ] Implement Complaint Studio generation & PDF export (`/complaints/generate`)
- [ ] Implement Document Analyzer for user evidence (`/documents/analyze`)
- [ ] Implement Admin & Health endpoints (`/health`, `/health/providers`, `/admin/status`)

## Phase 5: Frontend Application
- [ ] Configure Next.js frontend with Tailwind CSS, Lucide icons, and modern design system
- [ ] Build Landing Page (explaining RAG architecture, problem statement, official sources)
- [ ] Build AI Assistant interface (multi-turn streaming chat, expandable citations, source previews)
- [ ] Build Legal Knowledge Base explorer (search, browse, section filtering)
- [ ] Build Complaint Studio (structured input, live legal drafting, PDF export)
- [ ] Build Case Management & Document Analyzer
- [ ] Build Admin & System Diagnostic Dashboard

## Phase 6: Evaluation & Testing
- [ ] Create curated evaluation benchmark (50 realistic Indian legal queries)
- [ ] Implement `scripts/evaluate_rag.py` (Recall@5, Recall@10, MRR, Citation Precision, Latency)
- [ ] Run benchmark comparison (Vector-only vs BM25-only vs Hybrid RRF)
- [ ] Execute comprehensive unit and integration test suite

## Phase 7: Deployment & Final Verification
- [ ] Verify Docker container builds (Backend Dockerfile, Frontend Dockerfile)
- [ ] Finalize documentation (`ARCHITECTURE.md`, `RAG_PIPELINE.md`, etc.)
- [ ] Perform end-to-end user journey verification
- [ ] Generate final engineering report
