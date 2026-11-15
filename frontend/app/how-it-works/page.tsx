"use client";

import React from "react";
import Link from "next/link";
import { Navbar } from "../../components/Navbar";
import {
  Scale,
  ArrowRight,
  Search,
  Cpu,
  FileText,
  Send,
  CheckCircle,
  HelpCircle,
  Layers,
  ShieldAlert,
} from "lucide-react";

export default function HowItWorksPage() {
  const steps = [
    {
      num: "01",
      title: "Grievance Intake & Invoice Ingestion",
      desc: "Consumers describe their grievance in natural language or upload proof of purchase (tax invoices, warranty cards, receipt PDFs). The document engine validates magic bytes, prevents directory traversal, and extracts merchant details, GSTIN, and transaction dates.",
      tag: "Intake Stage",
      icon: FileText,
    },
    {
      num: "02",
      title: "Hybrid Retrieval with Reciprocal Rank Fusion",
      desc: "The query undergoes parallel lexical (BM25) and dense vector (multilingual-e5-small) retrieval across verified statutory chunks. RRF fusion (k=60) merges both ranks to guarantee precise statutory token matching without losing semantic intent.",
      tag: "Retrieval Stage",
      icon: Search,
    },
    {
      num: "03",
      title: "Legal Knowledge Graph Traversal",
      desc: "Candidate chunks are linked into the in-memory NetworkX knowledge graph. A bounded 1-hop expansion attaches governing authorities, statutory remedies, and cross-referenced procedural sections (e.g. connecting Rule 2 to District Commission via GOVERNS).",
      tag: "Graph Enrichment",
      icon: Layers,
    },
    {
      num: "04",
      title: "Corrective RAG (CRAG) Sufficiency Gate",
      desc: "Before prompting the generative model, the CRAG evaluator classifies retrieval outcomes into SUFFICIENT, PARTIALLY_SUFFICIENT, or INSUFFICIENT. Ambiguous inputs trigger query reformulation; out-of-scope queries (criminal, motor accidents) receive safe statutory abstention.",
      tag: "CRAG Gate",
      icon: Cpu,
    },
    {
      num: "05",
      title: "Reflective Citation Verification & Disclaimer Gate",
      desc: "The generation output undergoes post-hoc reflection: every cited section, rule, and authority is verified against retrieved ground truth chunks. Citations must meet a 100% precision gate, and mandatory statutory disclaimers are appended.",
      tag: "Verification Stage",
      icon: CheckCircle,
    },
    {
      num: "06",
      title: "Section 35 Formal Complaint Studio & Export",
      desc: "The complaint engine computes pecuniary jurisdiction strictly under the 2021 Rules (up to Rs 50L District, Rs 50L to 2Cr State, over Rs 2Cr National) based on consideration paid. It outputs a complete formal petition formatted with facts, prayers, and verification clause ready for e-Jagriti.",
      tag: "Redressal Stage",
      icon: Send,
    },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      <Navbar />

      <main className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold mb-4">
            <Cpu className="h-3.5 w-3.5" />
            <span>Process & Technology</span>
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-slate-100 tracking-tight">
            How NyayaSaathi AI Resolves Grievances
          </h1>
          <p className="mt-4 text-base text-slate-300 leading-relaxed">
            An engineered, multi-stage legal intelligence pipeline that converts natural language consumer complaints into court-ready legal drafts with zero hallucination.
          </p>
        </div>

        {/* Steps Stack */}
        <div className="space-y-6">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={step.num}
                className="p-6 sm:p-8 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col sm:flex-row gap-6 items-start"
              >
                <div className="h-12 w-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 shrink-0 font-bold text-lg">
                  <Icon className="h-6 w-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-xs font-bold text-amber-500 uppercase tracking-wider">{step.tag}</span>
                    <span className="text-xs text-slate-500">• Step {step.num}</span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-100">{step.title}</h3>
                  <p className="mt-2 text-xs sm:text-sm text-slate-300 leading-relaxed">{step.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Final CTA */}
        <div className="mt-14 p-8 rounded-3xl bg-gradient-to-r from-amber-500/10 via-slate-900 to-slate-900 border border-amber-500/30 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div>
            <h3 className="text-xl font-bold text-slate-100">Ready to resolve your grievance?</h3>
            <p className="text-xs text-slate-400 mt-1">Start a free, confidential consultation with zero setup.</p>
          </div>
          <Link
            href="/app"
            className="px-6 py-3 rounded-xl font-semibold text-xs text-slate-950 bg-amber-400 hover:bg-amber-300 shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all whitespace-nowrap"
          >
            <span>Launch Consultation</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </main>

      <footer className="py-6 border-t border-slate-900 bg-slate-950 text-xs text-slate-500 text-center">
        NyayaSaathi AI • Grounded in Official Indian Government Legislation
      </footer>
    </div>
  );
}
