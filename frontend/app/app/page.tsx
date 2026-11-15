"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Navbar } from "../../components/Navbar";
import { Header } from "../../components/Header";
import { DisclaimerBanner } from "../../components/DisclaimerBanner";
import { ChatInterface } from "../../components/ChatInterface";
import { ComplaintDraftStudio } from "../../components/ComplaintDraftStudio";
import { InvoiceAnalyzer } from "../../components/InvoiceAnalyzer";
import { KnowledgeExplorer } from "../../components/KnowledgeExplorer";
import { Scale } from "lucide-react";

function WorkspaceContent() {
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("tab") as "chat" | "draft" | "analyze" | "knowledge" | null;
  const [activeTab, setActiveTab] = useState<"chat" | "draft" | "analyze" | "knowledge">(initialTab || "chat");

  useEffect(() => {
    if (initialTab && ["chat", "draft", "analyze", "knowledge"].includes(initialTab)) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

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
