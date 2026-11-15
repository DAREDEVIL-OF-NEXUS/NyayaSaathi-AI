"use client";

import React from "react";
import Link from "next/link";
import { Navbar } from "../../components/Navbar";
import { Scale, ShieldCheck, Heart, Award, BookOpen, Users, ArrowRight } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      <Navbar />

      <main className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold mb-4">
            <Scale className="h-3.5 w-3.5" />
            <span>Mission & Philosophy</span>
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-slate-100 tracking-tight">
            Democratizing Legal Rights for Every Indian Citizen
          </h1>
          <p className="mt-4 text-base text-slate-300 leading-relaxed">
            NyayaSaathi AI (न्यायसाथी AI) was conceived as an engineering capstone at Delhi Technological University (DTU) under the Neural AI Society, designed to bridge the chasm between statutory consumer rights and practical citizen redressal.
          </p>
        </div>

        {/* Narrative Grid */}
        <div className="space-y-10">
          <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h2 className="text-xl font-bold text-amber-400 mb-3">The Problem We Are Solving</h2>
            <p className="text-sm text-slate-300 leading-relaxed space-y-3">
              India boasts one of the most progressive consumer protection frameworks in the world with the enactment of the <strong>Consumer Protection Act, 2019</strong>, the <strong>E-Commerce Rules, 2020</strong>, and the <strong>CCPA Guidelines, 2022</strong>. Yet, over 5.5 lakh consumer disputes remain pending in District, State, and National commissions. The primary barrier is not legal intent, but procedural opacity: consumers do not know whether their grievance qualifies under Section 2(7), which forum holds pecuniary jurisdiction, or how to draft a formal Section 35 petition.
            </p>
          </div>

          <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h2 className="text-xl font-bold text-amber-400 mb-3">The Evidence-First Engineering Principle</h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              Standard commercial LLMs hallucinate plausible-sounding section numbers, invent statutory penalties, and cite non-existent precedents. In legal technology, a single hallucinated citation can lead to a petition being dismissed with costs.
            </p>
            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
                <span className="font-semibold text-emerald-400 block mb-1">✓ Grounded in Verified Gazettes</span>
                Our knowledge base ingests official Ministry of Consumer Affairs Gazette notifications, India Code statutory texts, and NCH procedural guides.
              </div>
              <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
                <span className="font-semibold text-emerald-400 block mb-1">✓ Reflective Answer Verification</span>
                Every generated citation is validated against retrieved source chunks before being rendered. Unverified claims are rejected or flagged.
              </div>
            </div>
          </div>

          <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h2 className="text-xl font-bold text-amber-400 mb-3">Institutional Scope & Limitations</h2>
            <div className="text-sm text-slate-300 leading-relaxed space-y-2">
              <p>NyayaSaathi AI is strictly bounded within Indian Consumer Law, specifically:</p>
              <ul className="list-disc list-inside text-xs text-slate-400 space-y-1 ml-2">
                <li>Consumer Protection Act, 2019 (Act No. 35 of 2019)</li>
                <li>Consumer Protection (E-Commerce) Rules, 2020</li>
                <li>Consumer Protection (Jurisdiction of Commissions) Rules, 2021 (G.S.R. 888(E))</li>
                <li>CCPA Guidelines for Prevention of Misleading Advertisements, 2022</li>
                <li>National Consumer Helpline (NCH 1915) standard procedures</li>
                <li>e-Jagriti (e-Daakhil) digital filing guidelines</li>
              </ul>
              <p className="text-xs text-slate-400 mt-2">
                It deliberately refrains from offering advice on criminal law, motor accident claims (MACT), RTI applications, or general civil litigation outside consumer forums.
              </p>
            </div>
          </div>

          {/* Academic Attribution Card */}
          <div className="p-8 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-amber-950/30 border border-amber-500/20 flex flex-col sm:flex-row items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm mb-1">
                <Award className="h-4 w-4" />
                <span>Delhi Technological University (DTU)</span>
              </div>
              <h3 className="text-lg font-bold text-slate-100">Neural AI Society Engineering Project</h3>
              <p className="text-xs text-slate-400 mt-1">
                Architected and implemented as a full-stack, production-hardened sovereign legal AI system.
              </p>
            </div>
            <Link
              href="/app"
              className="px-6 py-3 rounded-xl font-semibold text-xs text-slate-950 bg-amber-400 hover:bg-amber-300 whitespace-nowrap shadow-lg shadow-amber-500/20 transition-all"
            >
              Start Free Consultation
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 border-t border-slate-900 bg-slate-950 text-xs text-slate-500 text-center">
        NyayaSaathi AI • Indian Consumer Technology Assistant • Not Formal Legal Counsel
      </footer>
    </div>
  );
}
