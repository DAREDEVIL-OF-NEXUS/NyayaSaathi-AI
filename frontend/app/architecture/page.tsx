"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Navbar } from "../../components/Navbar";
import {
  Cpu,
  Layers,
  Copy,
  Check,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  BookOpen,
  ArrowRight,
  ShieldCheck,
  Code2,
} from "lucide-react";
import mermaid from "mermaid";

interface ArchitectureDiagram {
  id: string;
  number: string;
  title: string;
  category: "C4 & System" | "Data Flow (DFD)" | "Workflows & Sequences" | "Deployment & State";
  summary: string;
  tradeoffs: string;
  code: string;
}

const DIAGRAMS: ArchitectureDiagram[] = [
  {
    id: "system-context",
    number: "01",
    title: "System Context Diagram (C4 Context)",
    category: "C4 & System",
    summary: "Illustrates NyayaSaathi AI within the broader ecosystem of Indian consumers, official government portals (e-Jagriti, NCH 1915, CCPA, India Code), LLM providers, and transactional email infrastructure.",
    tradeoffs: "Provides complete boundary clarity without exposing internal micro-components. External dependencies are isolated via resilient fallbacks.",
    code: `flowchart TD
    Consumer["Indian Consumer / Citizen"]
    Advocate["Consumer Advocate / Legal Aid"]

    subgraph NyayaSaathiSystem["NyayaSaathi AI Platform (न्यायसाथी AI)"]
        WebUI["Next.js 14 Web Application (Glassmorphism UI)"]
        BackendAPI["FastAPI Production Backend Gateway"]
        RAGCore["Hybrid RAG & Legal Knowledge Graph Core"]
        AuthCore["Zero-Trust Auth & RFC 6238 TOTP MFA"]
    end

    subgraph IndianGovt["Official Indian Government & Legal Infrastructure"]
        IndiaCode["India Code Statutory Portal (CPA 2019)"]
        NCH["National Consumer Helpline (1915 / INGRAM)"]
        eJagriti["e-Jagriti (e-Daakhil) Filing Portal"]
        CCPA["Central Consumer Protection Authority (CCPA)"]
    end

    subgraph ExternalServices["External Infrastructure Providers"]
        Gemini["Google Gemini API (Primary LLM)"]
        OpenRouter["OpenRouter API (Resilient Fallback LLM)"]
        Brevo["Brevo API (Transactional Email & 2FA OTP)"]
    end

    Consumer -->|Consults rights & drafts complaint| WebUI
    Advocate -->|Validates citations & jurisdiction| WebUI
    WebUI -->|REST & SSE Streams| BackendAPI
    BackendAPI --> RAGCore
    BackendAPI --> AuthCore

    RAGCore -.->|Ingests official gazettes| IndiaCode
    RAGCore -.->|Procedural SOPs| NCH
    RAGCore -.->|Filing guidelines| eJagriti
    RAGCore -.->|Misleading ads guidelines| CCPA

    RAGCore -->|Structured Prompts| Gemini
    Gemini -.->|Failover on rate limit| OpenRouter
    AuthCore -->|Sends OTP & alerts| Brevo`
  },
  {
    id: "high-level-arch",
    number: "02",
    title: "High-Level Architecture Diagram",
    category: "C4 & System",
    summary: "Depicts the multi-tier separation between the Next.js presentation layer, the FastAPI application gateway, domain engines, and the persistence & vector layer.",
    tradeoffs: "Decouples vector operations, graph traversal, and relational persistence. Allows independent scaling of frontend and backend services.",
    code: `flowchart LR
    subgraph ClientLayer["Presentation Layer (Client)"]
        Browser["Next.js 14 Client Router"]
        ChatUI["AI Consultation UI"]
        DraftUI["Section 35 Drafting Studio"]
        OCRUI["Invoice OCR Analyzer"]
        GraphUI["Legal Knowledge Explorer"]
    end

    subgraph GatewayLayer["Application Gateway"]
        FastAPI["FastAPI ASGI Server (Uvicorn)"]
        CORS["CORS & Host Filtering"]
        RateLimit["SlowAPI Rate Limiter"]
        AuthMiddleware["JWT & Session Validator"]
    end

    subgraph ServiceLayer["Domain Services & Engines"]
        RetrievalSvc["Hybrid Retriever (BM25 + Dense)"]
        CRAGSvc["Corrective RAG (CRAG) Evaluator"]
        GraphSvc["NetworkX Legal Graph Engine"]
        DraftEngine["Pecuniary Complaint Engine"]
        LLMManager["Resilient LLM Manager"]
        VerifierSvc["Reflection Answer Verifier"]
    end

    subgraph PersistenceLayer["Data & Vector Persistence"]
        Qdrant[("Qdrant Vector DB (Dense Embeddings)")]
        BM25Index[("BM25 In-Memory Inverted Index")]
        PostgreSQL[("PostgreSQL 16 (Users, Drafts, Audit)")]
        LocalUploads[("Sandboxed PDF Storage")]
    end

    Browser --> FastAPI
    FastAPI --> CORS --> RateLimit --> AuthMiddleware
    AuthMiddleware --> ServiceLayer

    RetrievalSvc --> Qdrant
    RetrievalSvc --> BM25Index
    GraphSvc --> PostgreSQL
    DraftEngine --> PostgreSQL
    LLMManager --> VerifierSvc`
  },
  {
    id: "low-level-components",
    number: "03",
    title: "Low-Level Component Architecture Diagram",
    category: "C4 & System",
    summary: "Detailed internal class and module decomposition within the FastAPI backend, detailing dependencies between security, extraction, RAG, and complaints.",
    tradeoffs: "High cohesion and low coupling ensure individual engines (e.g. ComplaintEngine) can be unit-tested without external network dependencies.",
    code: `classDiagram
    class FastAPIApp {
        +include_router(auth_router)
        +include_router(chat_router)
        +include_router(complaints_router)
        +include_router(documents_router)
        +include_router(knowledge_router)
    }

    class HybridRetriever {
        -DenseRetriever dense_retriever
        -BM25Retriever bm25_retriever
        +retrieve(query, top_k, mode) List~LegalChunk~
        +reciprocal_rank_fusion(dense_ranks, bm25_ranks, k) List~LegalChunk~
    }

    class CRAGPipeline {
        -HybridRetriever retriever
        -LegalGraphEngine graph_engine
        +evaluate_retrieval(query, candidates) CRAGDecision
        +rewrite_query(query) str
        +run(query) Tuple~List~LegalChunk~, CRAGMetadata~
    }

    class LegalGraphEngine {
        -nx.DiGraph graph
        +hydrate_from_db(session)
        +traverse_1hop(candidates) List~GraphContext~
        +get_entity_subgraph(entity_id) dict
    }

    class ComplaintEngine {
        +classify_grievance(desc, amount, merchant) ComplaintClassification
        +generate_draft(req, citations) ComplaintDraft
        -calculate_pecuniary_forum(consideration_paid) str
    }

    class ResilientLLMManager {
        -GeminiProvider primary
        -OpenRouterProvider fallback
        +generate_structured(prompt, schema) dict
        +generate_stream(prompt) AsyncIterator~str~
    }

    class AnswerVerifier {
        +verify_citations(text, candidates) VerificationResult
        +enforce_statutory_disclaimer(text) str
    }

    FastAPIApp --> HybridRetriever
    FastAPIApp --> ComplaintEngine
    CRAGPipeline --> HybridRetriever
    CRAGPipeline --> LegalGraphEngine
    FastAPIApp --> ResilientLLMManager
    ResilientLLMManager --> AnswerVerifier`
  },
  {
    id: "c4-container",
    number: "04",
    title: "C4 Container Diagram",
    category: "C4 & System",
    summary: "Shows execution containers, networks, port boundaries, and communication protocols (HTTPS, JSON REST, SSE streams) across the production deployment.",
    tradeoffs: "Qdrant and PostgreSQL are strictly isolated on the internal bridge network nyayasaathi_internal, eliminating direct host attack surface.",
    code: `flowchart TD
    subgraph Host["Host Environment (Docker Compose Boundary)"]
        subgraph PublicFacing["Public Network Exposure"]
            WebContainer["frontend Container (Next.js 14, Node 20, Port 3000)"]
            APIContainer["backend Container (FastAPI, Python 3.11, Port 8000)"]
        end

        subgraph InternalNetwork["Internal Isolated Bridge (nyayasaathi_internal)"]
            DBContainer["postgres Container (PostgreSQL 16, Port 5432)"]
            VectorContainer["qdrant Container (Qdrant Vector Store, Port 6333)"]
            VolumeData[("Docker Volume: postgres_data")]
            VolumeQdrant[("Docker Volume: qdrant_data")]
        end
    end

    User(["End User Web Browser"]) -->|HTTPS:3000| WebContainer
    WebContainer -->|REST & SSE:8000| APIContainer

    APIContainer -->|SQL / Connection Pool:5432| DBContainer
    APIContainer -->|gRPC / REST:6333| VectorContainer

    DBContainer --- VolumeData
    VectorContainer --- VolumeQdrant`
  },
  {
    id: "c4-component-rag",
    number: "05",
    title: "C4 Component Diagram (RAG & Knowledge Core)",
    category: "C4 & System",
    summary: "Deep dive into the retrieval-augmented generation sub-system: document extraction, chunk normalization, embeddings, RRF, CRAG decision gate, and verification.",
    tradeoffs: "Modular pipeline allows benchmarking each component independently (e.g. comparing dense vs hybrid vs hybrid+graph).",
    code: `flowchart TB
    UserQuery["Consumer Grievance Query"] --> Tokenizer["e5-small Query Formatter (query: prefix)"]

    subgraph IngestionPipeline["Document Processing (Offline / Upload)"]
        RawDoc["Official PDF / Text Document"] --> Extractor["PyMuPDF / Normalizer"]
        Extractor --> ChunkSplitter["Parent-Child Hierarchical Chunker"]
        ChunkSplitter --> VectorEncoder["e5-small Embedder (passage: prefix)"]
        ChunkSplitter --> BM25Builder["BM25 Lexical Inverted Index"]
    end

    subgraph HybridEngine["Hybrid Retrieval Engine"]
        Tokenizer --> DenseSearch["Qdrant Vector Retrieval (Top-10)"]
        UserQuery --> BM25Search["BM25 Lexical Match (Top-10)"]
        DenseSearch & BM25Search --> RRF["Reciprocal Rank Fusion (k=60)"]
    end

    subgraph GraphEnrichment["Legal Knowledge Graph"]
        RRF --> GraphLookup["1-Hop NetworkX Expansion"]
        GraphLookup --> GraphAugmented["Candidates + Connected Authorities/Remedies"]
    end

    subgraph CRAGDecision["Corrective RAG Gate"]
        GraphAugmented --> SufficiencyCheck{"Evidence Evaluation"}
        SufficiencyCheck -->|SUFFICIENT| Generator["Prompt Synthesizer"]
        SufficiencyCheck -->|PARTIALLY_SUFFICIENT| Rewriter["Query Reformulation & 2nd Retrieval"]
        Rewriter --> Generator
        SufficiencyCheck -->|INSUFFICIENT| Abstain["Safe Legal Abstention & Referral"]
    end

    Generator --> LLM["Resilient LLM (Gemini / OpenRouter)"]
    LLM --> VerificationGate["Reflection-Based Answer Verifier"]
    VerificationGate --> FinalResponse["Verified Structured Legal Response"]`
  },
  {
    id: "dfd-level-0",
    number: "06",
    title: "Data Flow Diagram Level 0 (Context DFD)",
    category: "Data Flow (DFD)",
    summary: "Context-level data flow representing inputs and outputs between the consumer, NyayaSaathi AI, government databases, and external notifications.",
    tradeoffs: "High-level abstraction for stakeholder review, regulatory compliance verification, and institutional privacy audits.",
    code: `flowchart LR
    Consumer["Indian Consumer"]
    Platform["(0.0) NyayaSaathi AI Platform"]
    IndiaCode["Official India Code Portal"]
    NCHPortal["National Consumer Helpline"]
    BrevoSystem["Brevo Email Service"]

    Consumer -->|1. Grievance facts, invoice, query| Platform
    Platform -->|2. Rights consultation, legal provisions, draft petition| Consumer

    IndiaCode -->|3. Official CPA 2019 statutory texts & gazettes| Platform
    NCHPortal -->|4. Grievance escalation workflows & contact SOPs| Platform

    Platform -->|5. MFA OTP & verification tokens| BrevoSystem
    BrevoSystem -->|6. Transactional notification| Consumer`
  },
  {
    id: "dfd-level-1",
    number: "07",
    title: "Data Flow Diagram Level 1 (Pipeline DFD)",
    category: "Data Flow (DFD)",
    summary: "Sub-processes representing the transformation of user queries into categorized grievances, retrieved statutory chunks, and drafted petitions.",
    tradeoffs: "Isolates data stores (Users, Knowledge, Drafts) and maps explicit data exchange between distinct processing modules.",
    code: `flowchart TD
    User["Consumer"] -->|Query / Document| P1["(1.0) Auth & Input Sanitization"]
    P1 -->|Sanitized Input| P2["(2.0) Hybrid Legal Retrieval"]

    subgraph DataStores["Data Stores"]
        D1[("D1: User Accounts & Sessions")]
        D2[("D2: Official Legal Knowledge Chunks")]
        D3[("D3: Legal Entities & Relationships")]
        D4[("D4: Complaint Drafts & Filings")]
    end

    P1 <--> D1
    D2 -->|Indexed Chunks| P2
    P2 -->|Candidate Provisions| P3["(3.0) Graph Context Expansion"]
    D3 -->|Relationships (GOVERNS, AMENDS)| P3
    P3 -->|Enriched Legal Evidence| P4["(4.0) CRAG Evidence Evaluation"]

    P4 -->|Sufficient Evidence| P5["(5.0) Response Synthesis & Drafting"]
    P5 -->|Synthesized Draft| P6["(6.0) Citation Verification Gate"]
    P6 -->|Verified Legal Draft| D4
    P6 -->|Court-Ready Petition| User`
  },
  {
    id: "dfd-level-2",
    number: "08",
    title: "Data Flow Diagram Level 2 (CRAG & Verification DFD)",
    category: "Data Flow (DFD)",
    summary: "Granular data flow inside the Corrective RAG evaluation loop and post-generation reflection-based citation verification gate.",
    tradeoffs: "Demonstrates exactly how hallucinated statutory citations are captured, filtered, and prevented from reaching citizen users.",
    code: `flowchart TD
    EvidenceIn["Evidence Candidates + Graph Context"] --> P41["(4.1) Keyword & Category Match Scoring"]
    P41 --> P42["(4.2) Confidence Classification"]

    P42 -->|Score >= 0.65| PathSufficient["Classification: SUFFICIENT"]
    P42 -->|0.35 <= Score < 0.65| PathPartial["Classification: PARTIALLY_SUFFICIENT"]
    P42 -->|Score < 0.35| PathInsufficient["Classification: INSUFFICIENT"]

    PathPartial --> P43["(4.3) LLM Query Reformulation"]
    P43 --> P44["(4.4) Secondary Lexical / Dense Query"]
    P44 --> MergeEvidence["Merged Filtered Evidence"]

    PathSufficient --> MergeEvidence
    PathInsufficient --> EmitAbstention["Generate Safe Statutory Abstention"]

    MergeEvidence --> LLMSynthesis["(5.1) Grounded Generation Prompt"]
    LLMSynthesis --> RawGeneration["Raw LLM Output Stream"]

    RawGeneration --> P61["(6.1) Regex Citation Extraction"]
    P61 --> P62["(6.2) Ground Truth Chunk Cross-Check"]
    P62 -->|Matched Citations| P63["(6.3) Append Statutory Disclaimers"]
    P62 -->|Unmatched Citations| RedactHallucination["(6.4) Redact or Regenerate"]
    RedactHallucination --> P63
    P63 --> VerifiedOutput["Delivered Legal Response"]`
  },
  {
    id: "seq-rag-traversal",
    number: "09",
    title: "Hybrid RAG & Knowledge Graph Traversal Sequence",
    category: "Workflows & Sequences",
    summary: "End-to-end runtime sequence diagram of a consumer consultation query passing through parallel retrieval, RRF ranking, graph expansion, and generation.",
    tradeoffs: "Parallel retrieval in threads yields <35ms combined latency before calling LLM APIs.",
    code: `sequenceDiagram
    autonumber
    actor Consumer as Citizen / Consumer
    participant API as FastAPI Gateway
    participant Retriever as HybridRetriever
    participant Qdrant as Qdrant Vector DB
    participant BM25 as BM25 Index
    participant Graph as LegalGraphEngine
    participant CRAG as CRAG Evaluator
    participant LLM as Gemini / OpenRouter
    participant Verifier as AnswerVerifier

    Consumer->>API: POST /api/v1/chat (query)
    API->>Retriever: retrieve(query, top_k=8, mode="hybrid_graph")
    
    par Dense Vector Search
        Retriever->>Qdrant: Search embeddings (query: <text>)
        Qdrant-->>Retriever: Top-10 Vector Matches
    and Lexical Keyword Match
        Retriever->>BM25: Query inverted index (BM25Okapi)
        BM25-->>Retriever: Top-10 Lexical Matches
    end

    Retriever->>Retriever: Reciprocal Rank Fusion (k=60)
    Retriever->>Graph: traverse_1hop(top_candidates)
    Graph-->>Retriever: Connected Entities (Authorities, Commissions, Remedies)
    Retriever-->>API: Enriched Legal Candidates

    API->>CRAG: evaluate_retrieval(query, candidates)
    CRAG-->>API: Decision (SUFFICIENT)

    API->>LLM: generate_response(prompt, candidates)
    LLM-->>API: Raw Response Text & Claims

    API->>Verifier: verify_citations(text, candidates)
    Verifier-->>API: Verified (100% Precision) + Disclaimer

    API-->>Consumer: Structured Legal Response + Verified Sources`
  },
  {
    id: "seq-auth-mfa",
    number: "10",
    title: "Authentication, MFA TOTP & Session Security Sequence",
    category: "Workflows & Sequences",
    summary: "Zero-trust identity workflow including email OTP verification, Bcrypt password authentication, RFC 6238 TOTP challenge, and single-use backup recovery codes.",
    tradeoffs: "Stateless 15-minute JWTs are decoupled from long-lived revokable session hashes, ensuring immediate session revocation capability.",
    code: `sequenceDiagram
    autonumber
    actor User as Consumer
    participant API as /api/v1/auth
    participant DB as PostgreSQL
    participant Email as BrevoEmailService
    participant App as Authenticator App (TOTP)

    Note over User, API: 1. Registration & Verification
    User->>API: POST /signup (email, password, name)
    API->>DB: Store User (is_verified=False, Bcrypt hash)
    API->>Email: send_verification_email(6-digit OTP)
    Email-->>User: Delivery of Verification Code
    User->>API: POST /verify-email (code)
    API->>DB: Set is_verified=True

    Note over User, API: 2. MFA TOTP Enrollment
    User->>API: POST /mfa/setup (Bearer Token)
    API-->>User: TOTP Secret, Provisioning URI & QR Code
    User->>App: Scan QR Code
    App-->>User: 6-Digit Time-Based OTP
    User->>API: POST /mfa/verify (secret, code)
    API->>DB: Enable MFA & Save 10 Hashed Backup Codes
    API-->>User: 10 Plaintext Backup Codes (One-time download)

    Note over User, API: 3. Sign In with 2FA Challenge
    User->>API: POST /signin (email, password)
    API->>DB: Verify Bcrypt password & check MFA status
    API-->>User: mfa_required=True, mfa_temp_token
    User->>App: Read 6-Digit Code (or use Backup Code)
    User->>API: POST /mfa/challenge (mfa_temp_token, code)
    API->>DB: Validate TOTP timestamp or mark backup code used
    API->>DB: Create UserSession (refresh_token_hash)
    API-->>User: Access Token (JWT 15m) + httpOnly Refresh Cookie`
  },
  {
    id: "state-complaint-drafting",
    number: "11",
    title: "Section 35 Complaint Drafting & Jurisdiction State Machine",
    category: "Deployment & State",
    summary: "State machine depicting the classification of pecuniary jurisdiction under the 2021 Rules (G.S.R. 888(E)) and formal court petition drafting.",
    tradeoffs: "Enforces consideration-paid rule at the model boundary, preventing jurisdictional misfilings before consumer commissions.",
    code: `stateDiagram-v2
    [*] --> GrievanceIntake

    state GrievanceIntake {
        [*] --> ExtractTransaction
        ExtractTransaction --> ValidateConsiderationPaid
    }

    state PecuniaryAssessment {
        [*] --> CheckConsiderationAmount
        CheckConsiderationAmount --> DistrictForum: Consideration <= ₹50 Lakhs (Rule 2a)
        CheckConsiderationAmount --> StateForum: Consideration > ₹50L and <= ₹2 Crores (Rule 2b)
        CheckConsiderationAmount --> NationalForum: Consideration > ₹2 Crores (Rule 2c)
    }

    GrievanceIntake --> PecuniaryAssessment

    state FormalDraftSynthesis {
        DistrictForum --> DraftPetition: District Consumer Disputes Redressal Commission
        StateForum --> DraftPetition: State Consumer Disputes Redressal Commission
        NationalForum --> DraftPetition: National Consumer Disputes Redressal Commission (NCDRC)
        
        DraftPetition --> FormatSections: Memorandum of Parties & Facts
        FormatSections --> AttachReliefs: Consideration Refund + Section 39 Damages
        AttachReliefs --> VerificationClause: Rule 35 Mandatory Affidavit
    }

    PecuniaryAssessment --> FormalDraftSynthesis
    FormalDraftSynthesis --> CitationValidation
    
    state CitationValidation {
        [*] --> CheckGrounding
        CheckGrounding --> ApprovedForFiling: 100% Citations Verified
        CheckGrounding --> FlaggedReview: Unverified Citations Present
    }

    ApprovedForFiling --> ExportPDF: Download Court-Ready Petition
    ExportPDF --> [*]`
  },
  {
    id: "deployment-topology",
    number: "12",
    title: "Production Deployment & Network Topology Diagram",
    category: "Deployment & State",
    summary: "Physical and containerized deployment architecture showcasing Docker isolation, non-root users, volume persistence, and secret boundaries.",
    tradeoffs: "Principle of least privilege: Backend runs as appuser (UID 1001), frontend as nextjs (UID 1001), zero database credentials exposed in public images.",
    code: `flowchart TD
    subgraph Internet["Public Internet"]
        Users["Citizen Web Browsers"]
    end

    subgraph Edge["Edge Layer (Reverse Proxy / Load Balancer)"]
        Nginx["TLS Terminator & Host Routing"]
    end

    subgraph DockerBridge["Isolated Docker Network (nyayasaathi_internal)"]
        subgraph WebContainer["Container: frontend (Node.js 20 Non-Root)"]
            NextServer["Next.js 14 SSR / SSG (Port 3000)"]
        end

        subgraph APIContainer["Container: backend (Python 3.11 Non-Root)"]
            Uvicorn["FastAPI ASGI Server (Port 8000)"]
            Worker1["Async Worker Pool"]
            Worker2["In-Memory BM25 Index"]
            Worker3["In-Memory NetworkX Graph"]
        end

        subgraph StorageLayer["Data & Persistence Layer"]
            PostgreSQL["Container: postgres:16-alpine (Port 5432)"]
            Qdrant["Container: qdrant/qdrant:latest (Port 6333)"]
        end
    end

    subgraph HostVolumes["Host Persistent Storage"]
        PGVolume[("/var/lib/postgresql/data")]
        QdrantVolume[("/qdrant/storage")]
        UploadsVolume[("./data/uploads/sandboxed")]
    end

    Users -->|HTTPS / WSS| Nginx
    Nginx -->|Proxy HTTP :3000| NextServer
    NextServer -->|Internal REST :8000| Uvicorn
    Nginx -.->|Direct API Access :8000| Uvicorn

    Uvicorn --> Worker1
    Worker1 -->|TCP Connection Pool| PostgreSQL
    Worker1 -->|REST / gRPC| Qdrant
    Worker1 -->|File I/O Sandboxed| UploadsVolume

    PostgreSQL --- PGVolume
    Qdrant --- QdrantVolume`
  }
];

export default function ArchitecturePage() {
  const [selectedId, setSelectedId] = useState<string>("system-context");
  const [copied, setCopied] = useState<boolean>(false);
  const [zoom, setZoom] = useState<number>(1);
  const [activeCategory, setActiveCategory] = useState<string>("All");
  const diagramRef = useRef<HTMLDivElement>(null);

  const currentDiagram = DIAGRAMS.find((d) => d.id === selectedId) || DIAGRAMS[0];

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      themeVariables: {
        darkMode: true,
        background: "#090d16",
        primaryColor: "#f59e0b",
        primaryTextColor: "#ffffff",
        primaryBorderColor: "#d97706",
        lineColor: "#f59e0b",
        secondaryColor: "#1e293b",
        tertiaryColor: "#0f172a",
      },
      securityLevel: "loose",
      fontFamily: "ui-sans-serif, system-ui, sans-serif",
    });

    const renderCurrent = async () => {
      if (diagramRef.current) {
        diagramRef.current.innerHTML = "";
        try {
          const uniqueId = `mermaid-${currentDiagram.id}-${Date.now()}`;
          const { svg } = await mermaid.render(uniqueId, currentDiagram.code);
          if (diagramRef.current) {
            diagramRef.current.innerHTML = svg;
          }
        } catch (err) {
          console.error("Mermaid render error:", err);
          if (diagramRef.current) {
            diagramRef.current.innerHTML = `<pre class="text-xs text-rose-400 p-4 font-mono">${currentDiagram.code}</pre>`;
          }
        }
      }
    };

    renderCurrent();
  }, [currentDiagram]);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(currentDiagram.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const categories = ["All", "C4 & System", "Data Flow (DFD)", "Workflows & Sequences", "Deployment & State"];
  const filteredDiagrams = activeCategory === "All"
    ? DIAGRAMS
    : DIAGRAMS.filter((d) => d.category === activeCategory);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold mb-2">
                <Cpu className="h-3.5 w-3.5" />
                <span>Interactive Technical Blueprint</span>
              </div>
              <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-slate-100 tracking-tight">
                System Architecture & Verification Models
              </h1>
              <p className="mt-1 text-xs sm:text-sm text-slate-400">
                12 client-side rendered Mermaid.js diagrams detailing C4 models, DFD levels 0–2, CRAG decision logic, knowledge graph traversal, and deployment topologies.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Link
                href="/app"
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20 transition-all flex items-center gap-1.5"
              >
                <span>Open Workspace</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>

          {/* Category Filter Pills */}
          <div className="mt-6 flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                  activeCategory === cat
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                    : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Main Grid: Sidebar + Canvas */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Sidebar List */}
          <div className="lg:col-span-4 space-y-2">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider px-2 mb-3">
              Architectural Diagrams ({filteredDiagrams.length})
            </div>
            <div className="space-y-1.5 max-h-[600px] overflow-y-auto pr-1">
              {filteredDiagrams.map((d) => {
                const isSelected = d.id === selectedId;
                return (
                  <button
                    key={d.id}
                    onClick={() => {
                      setSelectedId(d.id);
                      setZoom(1);
                    }}
                    className={`w-full text-left p-3 rounded-xl border transition-all flex items-start gap-3 ${
                      isSelected
                        ? "bg-slate-900 border-amber-500/50 shadow-md shadow-amber-500/5"
                        : "bg-slate-900/40 border-slate-800/80 hover:bg-slate-900 hover:border-slate-700"
                    }`}
                  >
                    <span
                      className={`text-xs font-black px-1.5 py-0.5 rounded ${
                        isSelected
                          ? "bg-amber-500 text-slate-950"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {d.number}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className={`text-xs font-semibold truncate ${isSelected ? "text-amber-400" : "text-slate-200"}`}>
                        {d.title}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate mt-0.5">{d.category}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Canvas & Details */}
          <div className="lg:col-span-8 space-y-4">
            {/* Diagram Title & Toolbar Card */}
            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                    Diagram {currentDiagram.number}
                  </span>
                  <span className="text-xs text-slate-400">{currentDiagram.category}</span>
                </div>
                <h2 className="text-base sm:text-lg font-bold text-slate-100 mt-1">{currentDiagram.title}</h2>
              </div>

              {/* Controls */}
              <div className="flex items-center gap-1.5 self-end sm:self-auto">
                <button
                  onClick={() => setZoom((z) => Math.min(z + 0.15, 2.0))}
                  title="Zoom In"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  <ZoomIn className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setZoom((z) => Math.max(z - 0.15, 0.5))}
                  title="Zoom Out"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  <ZoomOut className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setZoom(1)}
                  title="Reset Zoom"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  <RotateCcw className="h-4 w-4" />
                </button>
                <button
                  onClick={handleCopyCode}
                  title="Copy Mermaid Code"
                  className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-amber-400 font-medium transition-colors"
                >
                  {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                  <span>{copied ? "Copied" : "Copy Code"}</span>
                </button>
              </div>
            </div>

            {/* Mermaid Render Canvas */}
            <div className="p-4 sm:p-6 rounded-2xl bg-slate-950/80 border border-slate-800 min-h-[440px] flex items-center justify-center overflow-auto shadow-inner">
              <div
                ref={diagramRef}
                style={{ transform: `scale(${zoom})`, transformOrigin: "top center", transition: "transform 0.2s ease-out" }}
                className="w-full flex justify-center text-slate-100"
              />
            </div>

            {/* Description & Trade-offs Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400 mb-1.5">
                  <BookOpen className="h-3.5 w-3.5" />
                  <span>Architectural Overview</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{currentDiagram.summary}</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 mb-1.5">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  <span>Technology Trade-Offs & Rationale</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{currentDiagram.tradeoffs}</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="py-6 border-t border-slate-900 bg-slate-950 text-xs text-slate-500 text-center">
        NyayaSaathi AI Architecture Portal • 12 Verified Mermaid.js Systems Models
      </footer>
    </div>
  );
}
