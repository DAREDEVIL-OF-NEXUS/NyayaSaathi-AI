"use client";

import React, { useEffect, useState } from "react";
import { Scale, MessageSquare, FileText, Upload, BookOpen, ShieldCheck, Activity } from "lucide-react";
import { checkBackendHealth } from "../lib/api";

interface HeaderProps {
  activeTab: "chat" | "draft" | "analyze" | "knowledge";
  setActiveTab: (tab: "chat" | "draft" | "analyze" | "knowledge") => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");

  useEffect(() => {
    let mounted = true;
    checkBackendHealth()
      .then(() => mounted && setBackendStatus("online"))
      .catch(() => mounted && setBackendStatus("offline"));

    const interval = setInterval(() => {
      checkBackendHealth()
        .then(() => mounted && setBackendStatus("online"))
        .catch(() => mounted && setBackendStatus("offline"));
    }, 15000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Identity */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-amber-500 via-orange-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20">
              <Scale className="h-6 w-6 text-slate-950" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-slate-100 tracking-tight">NyayaSaathi AI</span>
                <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  न्यायसाथी
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Indian Consumer Protection & Grievance AI Platform</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1 sm:gap-2">
            <button
              onClick={() => setActiveTab("chat")}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === "chat"
                  ? "bg-slate-800 text-amber-400 border border-slate-700 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
              }`}
            >
              <MessageSquare className="h-4 w-4" />
              <span>Consultation</span>
            </button>

            <button
              onClick={() => setActiveTab("draft")}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === "draft"
                  ? "bg-slate-800 text-amber-400 border border-slate-700 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Complaint Drafter</span>
            </button>

            <button
              onClick={() => setActiveTab("analyze")}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === "analyze"
                  ? "bg-slate-800 text-amber-400 border border-slate-700 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
              }`}
            >
              <Upload className="h-4 w-4" />
              <span>Invoice Analyzer</span>
            </button>

            <button
              onClick={() => setActiveTab("knowledge")}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === "knowledge"
                  ? "bg-slate-800 text-amber-400 border border-slate-700 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
              }`}
            >
              <BookOpen className="h-4 w-4" />
              <span className="hidden md:inline">Knowledge Base</span>
              <span className="md:hidden">Corpus</span>
            </button>
          </nav>

          {/* System Status Pill */}
          <div className="hidden lg:flex items-center gap-2 text-xs">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800">
              <span
                className={`h-2 w-2 rounded-full ${
                  backendStatus === "online"
                    ? "bg-emerald-500 animate-pulse"
                    : backendStatus === "checking"
                    ? "bg-amber-500 animate-pulse"
                    : "bg-rose-500"
                }`}
              />
              <span className="text-slate-400 capitalize">
                {backendStatus === "online" ? "API Live" : backendStatus === "checking" ? "Connecting" : "API Offline"}
              </span>
            </div>
            <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>CPA 2019 Grounded</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
