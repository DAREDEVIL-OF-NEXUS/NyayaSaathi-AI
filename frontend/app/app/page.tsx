"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Navbar } from "../../components/Navbar";
import { Header } from "../../components/Header";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import { ChatInterface } from "../../components/ChatInterface";
import { ComplaintDraftStudio } from "../../components/ComplaintDraftStudio";
import { InvoiceAnalyzer } from "../../components/InvoiceAnalyzer";
import { KnowledgeExplorer } from "../../components/KnowledgeExplorer";
import {
  Scale,
  Lock,
  ShieldAlert,
  ArrowRight,
  UserPlus,
  LogIn,
  CheckCircle2,
  FileCheck,
  Building,
} from "lucide-react";
import { getStoredToken } from "../../lib/auth";

function WorkspaceContent() {
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("tab") as "chat" | "draft" | "analyze" | "knowledge" | null;
  const [activeTab, setActiveTab] = useState<"chat" | "draft" | "analyze" | "knowledge">(initialTab || "chat");
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    setIsAuthenticated(Boolean(token));
  }, []);

  useEffect(() => {
    if (initialTab && ["chat", "draft", "analyze", "knowledge"].includes(initialTab)) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  // Loading state while checking token
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center text-xs text-amber-400">
          Checking authentication status...
        </div>
      </div>
    );
  }

  // If NOT authenticated, enforce Sign Up & Sign In Gate
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
        <Navbar />
        <DisclaimerBanner />

        <main className="flex-1 flex items-center justify-center p-4">
          <div className="w-full max-w-lg p-8 sm:p-10 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-2xl backdrop-blur-md text-center">
            {/* Lock Emblem */}
            <div className="h-16 w-16 rounded-3xl bg-gradient-to-br from-amber-500/20 via-amber-500/10 to-transparent border border-amber-500/30 flex items-center justify-center mx-auto mb-6 text-amber-400 shadow-lg shadow-amber-500/10">
              <Lock className="h-8 w-8" />
            </div>

            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold mb-3">
              <ShieldAlert className="h-3.5 w-3.5" />
              <span>Confidential Citizen Workspace</span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight">
              Sign In Required to Access Legal Workspace
            </h1>

            <p className="mt-3 text-xs sm:text-sm text-slate-300 leading-relaxed max-w-md mx-auto">
              To protect personal grievance details, guarantee multi-tenant data isolation, and draft court-ready Section 35 petitions, you must sign in or register your citizen account.
            </p>

            {/* Action Buttons */}
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                href="/signin"
                className="w-full sm:w-1/2 py-3 px-4 rounded-xl text-xs font-semibold text-slate-950 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 shadow-md shadow-amber-500/20 flex items-center justify-center gap-2 transition-all"
              >
                <LogIn className="h-4 w-4" />
                <span>Sign In to Account</span>
              </Link>
              <Link
                href="/signup"
                className="w-full sm:w-1/2 py-3 px-4 rounded-xl text-xs font-semibold text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 flex items-center justify-center gap-2 transition-all"
              >
                <UserPlus className="h-4 w-4 text-amber-400" />
                <span>Create New Account</span>
              </Link>
            </div>

            {/* Protected Workspace Feature Highlights */}
            <div className="mt-8 pt-6 border-t border-slate-800/80 text-left space-y-2.5">
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Included in Your Verified Citizen Account:
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-300">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  <span>Confidential Case History</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  <span>Section 35 Formal Petitions</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  <span>Invoice & Receipt OCR Analysis</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  <span>Two-Factor Authentication (MFA)</span>
                </div>
              </div>
            </div>

            {/* Public Links */}
            <div className="mt-6 text-xs text-slate-500">
              Exploring the technology first? Check our{" "}
              <Link href="/architecture" className="text-amber-400 hover:underline">
                12 System Architecture Diagrams
              </Link>{" "}
              or read{" "}
              <Link href="/how-it-works" className="text-amber-400 hover:underline">
                How It Works
              </Link>.
            </div>
          </div>
        </main>

        <footer className="py-4 border-t border-slate-900 bg-slate-950 text-xs text-slate-500 text-center">
          NyayaSaathi AI • Indian Consumer Technology Platform • Grounded in Consumer Protection Act, 2019
        </footer>
      </div>
    );
  }

  // Authenticated: Render Full Workspace
  return (
    <div className="min-h-screen flex flex-col bg-slate-900 text-slate-100">
      <Navbar />
      <DisclaimerBanner />
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1 flex flex-col overflow-hidden">
        {activeTab === "chat" && <ChatInterface />}
        {activeTab === "draft" && <ComplaintDraftStudio />}
        {activeTab === "analyze" && (
          <InvoiceAnalyzer
            onTransferToDraft={(merchant, amount, date, orderId, narrative) => {
              setActiveTab("draft");
            }}
            onAskAssistant={(query) => {
              setActiveTab("chat");
            }}
          />
        )}
        {activeTab === "knowledge" && <KnowledgeExplorer />}
      </main>
      <footer className="border-t border-slate-800 bg-slate-950 py-3 px-4 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-1.5">
            <Scale className="h-3.5 w-3.5 text-amber-500" />
            <span className="font-semibold text-slate-400">NyayaSaathi AI (न्यायसाथी AI)</span>
            <span>— Indian Consumer Legal Technology Assistant</span>
          </div>
          <div className="text-[11px] text-slate-500">
            Delhi Technological University • Neural AI Society • Grounded in Consumer Protection Act, 2019
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function WorkspaceApp() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-xs text-amber-400">Loading Workspace...</div>}>
      <WorkspaceContent />
    </Suspense>
  );
}
