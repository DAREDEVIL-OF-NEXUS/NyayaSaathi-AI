"use client";

import React from "react";
import Link from "next/link";
import { Navbar } from "../components/Navbar";
import {
  Scale,
  ShieldCheck,
  FileText,
  Search,
  Cpu,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Building2,
  Clock,
  Sparkles,
  Lock,
  Layers,
  FileCheck,
  ChevronRight,
  ExternalLink,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      {/* Navbar */}
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28 border-b border-slate-800/80">
        {/* Glow ambient backgrounds */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-amber-500/10 blur-[130px] rounded-full pointer-events-none" />
        <div className="absolute top-1/3 left-1/4 w-[400px] h-[250px] bg-orange-600/10 blur-[120px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          {/* Official Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/90 border border-amber-500/30 text-amber-300 text-xs font-medium mb-6 shadow-lg shadow-amber-500/5">
            <span className="flex h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
            <span>DTU Neural AI Society • Grounded in Consumer Protection Act, 2019</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-100 max-w-4xl mx-auto leading-[1.15]">
            Empowering Indian Consumers with{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-300 to-orange-400">
              Evidence-First Legal AI
            </span>
          </h1>

          {/* Subheading */}
          <p className="mt-6 text-base sm:text-lg md:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
            Understand your consumer rights, calculate exact pecuniary commission jurisdiction, expose deceptive e-commerce dark patterns, and generate court-ready Section 35 complaints grounded in official Indian legislation.
          </p>

          {/* Call to Actions */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/app"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-semibold text-slate-950 bg-gradient-to-r from-amber-400 via-amber-500 to-orange-500 hover:from-amber-300 hover:to-orange-400 shadow-xl shadow-amber-500/25 flex items-center justify-center gap-2 group transition-all"
            >
              <span>Start Free Consultation</span>
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/architecture"
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-medium text-slate-200 bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 hover:border-slate-600 flex items-center justify-center gap-2 transition-all"
            >
              <Cpu className="h-4 w-4 text-amber-400" />
              <span>Explore Interactive Architecture</span>
            </Link>
          </div>

          {/* Stat Chips */}
          <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
              <div className="text-2xl sm:text-3xl font-bold text-amber-400">78.8%</div>
              <div className="text-xs text-slate-400 mt-1">Hybrid Recall@5 Retrieval</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
              <div className="text-2xl sm:text-3xl font-bold text-slate-100">0.7067</div>
              <div className="text-xs text-slate-400 mt-1">Mean Reciprocal Rank (MRR)</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
              <div className="text-2xl sm:text-3xl font-bold text-emerald-400">100%</div>
              <div className="text-xs text-slate-400 mt-1">Citation Grounding Accuracy</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
              <div className="text-2xl sm:text-3xl font-bold text-amber-400">0 Hallucination</div>
              <div className="text-xs text-slate-400 mt-1">Reflective Verification Gate</div>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-16 md:py-24 border-b border-slate-800/80 bg-slate-900/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h2 className="text-xs font-bold text-amber-400 uppercase tracking-wider">The Problem in Indian Consumer Redressal</h2>
            <p className="mt-2 text-2xl sm:text-3xl font-bold text-slate-100">
              Citizens Face Staggering Friction When Seeking Justice
            </p>
            <p className="mt-3 text-sm sm:text-base text-slate-400">
              India’s consumer protection framework is comprehensive, yet ordinary consumers are deterred by procedural complexity and jurisdictional pitfalls.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all">
              <div className="h-12 w-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mb-4">
                <Clock className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-slate-100">5.5+ Lakh Pending Grievances</h3>
              <p className="mt-2 text-xs sm:text-sm text-slate-400 leading-relaxed">
                Consumer commissions across India face massive backlogs. Citizens often abandon genuine claims because they do not know how to register grievances with the National Consumer Helpline (1915) or e-Jagriti.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all">
              <div className="h-12 w-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-slate-100">Deceptive E-Commerce Dark Patterns</h3>
              <p className="mt-2 text-xs sm:text-sm text-slate-400 leading-relaxed">
                Online marketplaces deploy basket sneaking, drip pricing, hidden delivery fees, and auto-renewals in direct violation of the E-Commerce Rules, 2020 and CCPA 2022 Guidelines.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all">
              <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
                <Building2 className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-slate-100">Pecuniary Jurisdiction Pitfalls</h3>
              <p className="mt-2 text-xs sm:text-sm text-slate-400 leading-relaxed">
                Under CPA 2019 and 2021 Gazette rules, jurisdiction is governed strictly by consideration paid, not compensation claimed. Consumers frequently file before the wrong commission, resulting in dismissals.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 md:py-24 border-b border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h2 className="text-xs font-bold text-amber-400 uppercase tracking-wider">End-to-End Redressal Pipeline</h2>
            <p className="mt-2 text-2xl sm:text-3xl font-bold text-slate-100">
              From Consumer Grievance to Court-Ready Petition
            </p>
            <p className="mt-3 text-sm sm:text-base text-slate-400">
              A 4-stage pipeline that eliminates hallucination and guarantees statutory compliance.
            </p>
          </div>

          <div className="mt-14 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 relative group hover:border-amber-500/50 transition-all">
              <div className="text-3xl font-black text-amber-500/30 group-hover:text-amber-500/60 transition-colors mb-2">01</div>
              <h4 className="text-base font-semibold text-slate-100">Grievance Intake</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Provide details of your transaction, order numbers, dates, and merchant conduct in plain English or Hinglish.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 relative group hover:border-amber-500/50 transition-all">
              <div className="text-3xl font-black text-amber-500/30 group-hover:text-amber-500/60 transition-colors mb-2">02</div>
              <h4 className="text-base font-semibold text-slate-100">Hybrid & Graph Retrieval</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Dense embeddings and BM25 search official Acts, Gazette rules, and CCPA guidelines, augmented by 1-hop legal knowledge graph expansion.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 relative group hover:border-amber-500/50 transition-all">
              <div className="text-3xl font-black text-amber-500/30 group-hover:text-amber-500/60 transition-colors mb-2">03</div>
              <h4 className="text-base font-semibold text-slate-100">CRAG Evaluation</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Corrective RAG assesses evidence sufficiency. Ambiguous queries are rewritten; out-of-scope queries receive safe statutory abstention.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 relative group hover:border-amber-500/50 transition-all">
              <div className="text-3xl font-black text-amber-500/30 group-hover:text-amber-500/60 transition-colors mb-2">04</div>
              <h4 className="text-base font-semibold text-slate-100">Court-Ready Section 35 Draft</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Automated legal synthesis outputs a structured formal petition with prayers, verification clause, and verified citations ready for e-Jagriti filing.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features Grid */}
      <section className="py-16 md:py-24 border-b border-slate-800/80 bg-slate-900/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h2 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Engineered for Indian Law</h2>
            <p className="mt-2 text-2xl sm:text-3xl font-bold text-slate-100">
              Architectural Capabilities Built From Scratch
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
              <div className="h-10 w-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <Search className="h-5 w-5" />
              </div>
              <h4 className="text-base font-semibold text-slate-100">Reciprocal Rank Fusion</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Fuses multilingual-e5-small dense vectors with BM25 keyword matching at k=60, guaranteeing exact statutory tokens (e.g. Rule 4(8), Section 69) are never lost.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
              <div className="h-10 w-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <Layers className="h-5 w-5" />
              </div>
              <h4 className="text-base font-semibold text-slate-100">Legal Knowledge Graph</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                68 nodes and 100 edges linking Acts, Sections, Rules, Authorities, and Remedies with NetworkX bounded 1-hop traversal and source provenance.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
              <div className="h-10 w-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <FileCheck className="h-5 w-5" />
              </div>
              <h4 className="text-base font-semibold text-slate-100">Section 35 Complaint Studio</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Calculates pecuniary limits under 2021 Rules (up to Rs 50L District, Rs 50L to 2Cr State, over Rs 2Cr National) and outputs formal court-ready drafts.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
              <div className="h-10 w-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <FileText className="h-5 w-5" />
              </div>
              <h4 className="text-base font-semibold text-slate-100">Invoice & OCR Analyzer</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Extracts merchant GSTIN, transaction amount, invoice dates, and highlights potential dark pattern discrepancies automatically.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
              <div className="h-10 w-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <Lock className="h-5 w-5" />
              </div>
              <h4 className="text-base font-semibold text-slate-100">RFC 6238 TOTP MFA Security</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Zero-trust authentication with Bcrypt hashing, Time-based OTP (Google Authenticator), and 10 single-use SHA-256 backup recovery codes.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800">
              <div className="h-10 w-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h4 className="text-base font-semibold text-slate-100">Multi-Tenant Isolation</h4>
              <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                Strict foreign-key tenant boundaries and magic-byte PDF validation ensure complete isolation of sensitive consumer evidence.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Teaser Section */}
      <section className="py-16 md:py-20 border-b border-slate-800/80 bg-gradient-to-b from-slate-950 to-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="p-8 sm:p-12 rounded-3xl bg-slate-900/70 border border-slate-700/60 backdrop-blur-md flex flex-col md:flex-row items-center justify-between gap-8 shadow-2xl">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold mb-3">
                <Cpu className="h-3.5 w-3.5" />
                <span>Interactive System Architecture</span>
              </div>
              <h3 className="text-2xl sm:text-3xl font-bold text-slate-100">
                Explore 12 Interactive Architectural Diagrams
              </h3>
              <p className="mt-3 text-sm text-slate-300 leading-relaxed">
                Inspect complete C4 models, Data Flow Diagrams (DFD Levels 0-2), Corrective RAG sequences, Knowledge Graph traversals, and production deployment topologies with client-side Mermaid.js rendering.
              </p>
            </div>
            <Link
              href="/architecture"
              className="px-6 py-3.5 rounded-xl font-semibold text-slate-950 bg-amber-400 hover:bg-amber-300 shadow-lg shadow-amber-500/20 flex items-center gap-2 whitespace-nowrap transition-all"
            >
              <span>View Architecture Portal</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Statutory Disclaimer & Trust Banner */}
      <section className="py-8 bg-slate-950 border-b border-slate-800/80 text-xs text-slate-400">
        <div className="max-w-5xl mx-auto px-4 text-center space-y-2">
          <div className="flex items-center justify-center gap-1.5 text-amber-400 font-semibold">
            <ShieldCheck className="h-4 w-4" />
            <span>STATUTORY MANDATE & CITIZEN ADVISORY</span>
          </div>
          <p className="leading-relaxed">
            NyayaSaathi AI is an automated retrieval-augmented legal research and procedural assistant. It is grounded in the Consumer Protection Act, 2019 and official Gazette notifications. It does not provide formal legal representation or create an attorney-client relationship. For formal judicial filings, refer to e-Jagriti (edaakhil.nic.in) or call the National Consumer Helpline at 1915.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 bg-slate-950 text-xs text-slate-500 border-t border-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-amber-500 flex items-center justify-center text-slate-950 font-bold">
              <Scale className="h-4 w-4" />
            </div>
            <span className="font-semibold text-slate-300">NyayaSaathi AI (न्यायसाथी AI)</span>
            <span>• Delhi Technological University</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <Link href="/about" className="hover:text-amber-400 transition-colors">About</Link>
            <Link href="/how-it-works" className="hover:text-amber-400 transition-colors">How It Works</Link>
            <Link href="/architecture" className="hover:text-amber-400 transition-colors">Architecture</Link>
            <Link href="/app" className="hover:text-amber-400 transition-colors">Workspace</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
