"use client";

import React, { useState } from "react";
import { Header } from "../components/Header";
import { DisclaimerBanner } from "../components/DisclaimerBanner";
import { ChatInterface } from "../components/ChatInterface";
import { ComplaintDraftStudio } from "../components/ComplaintDraftStudio";
import { InvoiceAnalyzer } from "../components/InvoiceAnalyzer";
import { KnowledgeExplorer } from "../components/KnowledgeExplorer";
import { Scale, Heart } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"chat" | "draft" | "analyze" | "knowledge">("chat");

  return (
    <div className="min-h-screen flex flex-col bg-slate-900 text-slate-100">
      {/* Statutory Disclaimer Notice */}
      <DisclaimerBanner />

      {/* Main Header & Navigation */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Active Tab Workspace */}
      <div className="flex-1 flex flex-col overflow-hidden">
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
      </div>

      {/* Footer */}
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
