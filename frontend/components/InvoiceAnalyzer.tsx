"use client";

import React, { useState } from "react";
import {
  Upload,
  FileText,
  AlertTriangle,
  CheckCircle,
  Building,
  DollarSign,
  Calendar,
  Hash,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  FileSearch
} from "lucide-react";
import { uploadDocument, analyzeTextDirect } from "../lib/api";
import { DocumentAnalysisResponse } from "../types";

interface InvoiceAnalyzerProps {
  onTransferToDraft?: (merchant?: string, amount?: number, date?: string, orderId?: string, narrative?: string) => void;
  onAskAssistant?: (query: string) => void;
}

export const InvoiceAnalyzer: React.FC<InvoiceAnalyzerProps> = ({ onTransferToDraft, onAskAssistant }) => {
  const [tab, setTab] = useState<"upload" | "text">("upload");
  const [file, setFile] = useState<File | null>(null);
  const [rawText, setRawText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<DocumentAnalysisResponse | null>(null);

  const handleFileUpload = async (selectedFile: File) => {
    setFile(selectedFile);
    setAnalyzing(true);
    try {
      const res = await uploadDocument(selectedFile);
      setResult(res);
    } catch (err: any) {
      alert("Document analysis failed: " + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAnalyzeText = async () => {
    if (!rawText.trim()) return;
    setAnalyzing(true);
    try {
      const res = await analyzeTextDirect(rawText, "pasted_invoice.txt");
      setResult(res);
    } catch (err: any) {
      alert("Text analysis failed: " + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleLoadSampleInvoice = () => {
    setRawText(`TAX INVOICE / RETAIL CASH MEMO
Sold By: CloudRetail India Pvt Ltd
Order ID: OD30192840192
Invoice Number: DEL-2023-881920
Invoice Date: 20-10-2023
Customer Name: Priya Sundaram
Product: Apple MacBook Air M2 16GB RAM 512GB SSD
Item Total: ₹1,14,900.00
Platform Convenience Fee: ₹250.00
Delivery & Handling Charges: ₹150.00
Grand Total: ₹1,15,300.00

TERMS & CONDITIONS:
1. Goods once sold cannot be returned under any circumstances. Non-refundable item.
2. In case of customer cancellation before dispatch, a 100% cancellation fee will apply.
3. Warranty claims must be handled directly with manufacturer. Company not liable for in-transit damages.`);
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto w-full">
      {/* Header */}
      <div className="mb-6 border-b border-slate-800 pb-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Smart Invoice & Grievance Analyzer</h1>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              E-Commerce & Receipts
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Extract transaction parameters, detect unfair trade clauses (e.g. no-return clauses, cancellation penalties), and map statutory legal claims.
          </p>
        </div>

        <button
          type="button"
          onClick={handleLoadSampleInvoice}
          className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-amber-300 font-medium transition-colors border border-slate-700"
        >
          Load Sample E-Commerce Invoice
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Section */}
        <div className="lg:col-span-5 space-y-4">
          {/* Tab Selector */}
          <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800 text-xs font-medium">
            <button
              onClick={() => setTab("upload")}
              className={`flex-1 py-1.5 rounded-md transition-colors ${
                tab === "upload" ? "bg-slate-800 text-amber-400 font-semibold" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Upload PDF / TXT
            </button>
            <button
              onClick={() => setTab("text")}
              className={`flex-1 py-1.5 rounded-md transition-colors ${
                tab === "text" ? "bg-slate-800 text-amber-400 font-semibold" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Paste Text / Receipt
            </button>
          </div>

          {tab === "upload" ? (
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                  handleFileUpload(e.dataTransfer.files[0]);
                }
              }}
              className="border-2 border-dashed border-slate-800 hover:border-amber-500/40 rounded-2xl p-8 bg-slate-950/60 text-center flex flex-col items-center justify-center cursor-pointer transition-colors"
              onClick={() => document.getElementById("file-upload-input")?.click()}
            >
              <input
                id="file-upload-input"
                type="file"
                accept=".pdf,.txt,.json,.csv"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileUpload(e.target.files[0]);
                  }
                }}
              />
              <div className="h-12 w-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center mb-3">
                <Upload className="h-6 w-6" />
              </div>
              <div className="text-sm font-semibold text-slate-200 mb-1">
                {file ? file.name : "Click to select or drag & drop invoice"}
              </div>
              <div className="text-xs text-slate-500">Supports PDF, TXT up to 15MB</div>
            </div>
          ) : (
            <div className="space-y-3">
              <textarea
                rows={10}
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="Paste raw invoice text, receipt details, or merchant terms here..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono leading-relaxed"
              />
              <button
                type="button"
                onClick={handleAnalyzeText}
                disabled={analyzing || !rawText.trim()}
                className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-bold text-xs transition-all flex items-center justify-center gap-2 shadow-md shadow-amber-500/10"
              >
                {analyzing ? <RefreshCw className="h-4 w-4 animate-spin" /> : <FileSearch className="h-4 w-4" />}
                <span>Analyze Invoice Content</span>
              </button>
            </div>
          )}

          {analyzing && (
            <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/30 text-amber-300 text-xs flex items-center gap-2.5 animate-pulse">
              <RefreshCw className="h-4 w-4 animate-spin text-amber-400" />
              <span>Scanning document text and checking consumer protection rules...</span>
            </div>
          )}
        </div>

        {/* Results Section */}
        <div className="lg:col-span-7">
          {result ? (
            <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-5 shadow-2xl">
              {/* Top Banner */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-emerald-400" />
                  <span className="font-semibold text-xs text-slate-200">Analysis Completed</span>
                </div>
                <div className="text-[11px] text-slate-500">{result.filename}</div>
              </div>

              {/* Extracted Parameters Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-[10px] text-slate-500 flex items-center gap-1 mb-1">
                    <Building className="h-3 w-3" />
                    <span>Merchant</span>
                  </div>
                  <div className="font-semibold text-slate-200 text-xs truncate">
                    {result.merchant_name || "Not Detected"}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-[10px] text-slate-500 flex items-center gap-1 mb-1">
                    <DollarSign className="h-3 w-3" />
                    <span>Invoice Amount</span>
                  </div>
                  <div className="font-bold text-amber-400 text-xs truncate">
                    {result.invoice_amount ? `₹${result.invoice_amount.toLocaleString()}` : "Not Detected"}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-[10px] text-slate-500 flex items-center gap-1 mb-1">
                    <Calendar className="h-3 w-3" />
                    <span>Date</span>
                  </div>
                  <div className="font-medium text-slate-200 text-xs truncate">
                    {result.invoice_date || "Not Detected"}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-[10px] text-slate-500 flex items-center gap-1 mb-1">
                    <Hash className="h-3 w-3" />
                    <span>Order / Invoice ID</span>
                  </div>
                  <div className="font-mono text-slate-300 text-xs truncate">
                    {result.order_or_invoice_id || "Not Detected"}
                  </div>
                </div>
              </div>

              {/* Grievance Triggers Detected */}
              <div className="space-y-2">
                <div className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                  <ShieldAlert className="h-3.5 w-3.5" />
                  Detected Potential Grievance Red Flags ({result.potential_grievance_indicators.length})
                </div>
                {result.potential_grievance_indicators.length === 0 ? (
                  <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs">
                    No explicit unfair trade terms detected in document text.
                  </div>
                ) : (
                  <div className="space-y-1.5">
                    {result.potential_grievance_indicators.map((ind, i) => (
                      <div key={i} className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                        <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-rose-400" />
                        <span className="font-medium">{ind}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Suggested Statutory Claims */}
              <div className="space-y-2">
                <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <FileText className="h-3.5 w-3.5 text-amber-400" />
                  Applicable Statutory Grounds under Indian Law
                </div>
                <div className="space-y-2">
                  {result.suggested_legal_claims.map((claim, cIdx) => (
                    <div key={cIdx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200">
                      {claim}
                    </div>
                  ))}
                </div>
              </div>

              {/* Extracted Preview */}
              <div className="pt-2 border-t border-slate-800">
                <div className="text-[11px] font-semibold text-slate-400 mb-1">Extracted Text Preview:</div>
                <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-800/80 font-mono text-[11px] text-slate-400 whitespace-pre-wrap max-h-36 overflow-y-auto">
                  {result.extracted_text_preview}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-2 pt-2">
                {onTransferToDraft && (
                  <button
                    onClick={() =>
                      onTransferToDraft(
                        result.merchant_name || undefined,
                        result.invoice_amount || undefined,
                        result.invoice_date || undefined,
                        result.order_or_invoice_id || undefined,
                        `Dispute with ${result.merchant_name || "Seller"} regarding invoice ${result.order_or_invoice_id || ""}: ${result.potential_grievance_indicators.join(", ")}`
                      )
                    }
                    className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs transition-colors shadow-md shadow-amber-500/10"
                  >
                    <span>Populate in Complaint Drafter</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                )}

                {onAskAssistant && (
                  <button
                    onClick={() =>
                      onAskAssistant(
                        `I have an invoice from ${result.merchant_name || "seller"} for ₹${result.invoice_amount || ""}. They have applied terms: ${result.potential_grievance_indicators.join(", ")}. What are my rights?`
                      )
                    }
                    className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-colors border border-slate-700"
                  >
                    <span>Consult Legal Assistant</span>
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full min-h-[400px] flex flex-col items-center justify-center rounded-2xl bg-slate-950 border border-slate-800 p-8 text-center text-slate-500">
              <FileSearch className="h-12 w-12 text-slate-700 mb-3" />
              <div className="font-semibold text-slate-400 mb-1">No Document Analyzed Yet</div>
              <p className="text-xs text-slate-500 max-w-sm">
                Upload a PDF invoice or paste receipt text on the left to extract merchant details, amount, and potential consumer protection red flags.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
