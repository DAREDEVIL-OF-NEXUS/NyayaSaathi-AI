"use client";

import React, { useState, useEffect } from "react";
import {
  FileText,
  Building,
  CheckCircle,
  Copy,
  Download,
  AlertCircle,
  RefreshCw,
  FolderOpen,
  Sparkles,
  ChevronRight
} from "lucide-react";
import {
  classifyComplaint,
  generateComplaintDraft,
  listComplaints,
  getComplaintExportUrl
} from "../lib/api";
import {
  ComplaintClassification,
  ComplaintDraftRequest,
  ComplaintDraftResponse
} from "../types";

export const ComplaintDraftStudio: React.FC = () => {
  const [formData, setFormData] = useState<ComplaintDraftRequest>({
    complainant_name: "",
    complainant_contact: "",
    complainant_address: "",
    opposite_party_name: "",
    opposite_party_address: "",
    grievance_category: "",
    transaction_amount: 0,
    transaction_date: "",
    order_or_invoice_number: "",
    facts_of_case: "",
    relief_sought: ""
  });

  const [classification, setClassification] = useState<ComplaintClassification | null>(null);
  const [generatedDraft, setGeneratedDraft] = useState<ComplaintDraftResponse | null>(null);
  const [savedDrafts, setSavedDrafts] = useState<ComplaintDraftResponse[]>([]);
  const [classifying, setClassifying] = useState(false);
  const [drafting, setDrafting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showSaved, setShowSaved] = useState(false);

  useEffect(() => {
    loadSavedDrafts();
  }, []);

  const loadSavedDrafts = async () => {
    try {
      const data = await listComplaints();
      setSavedDrafts(data);
    } catch (err) {
      console.error("Failed to load drafts:", err);
    }
  };

  const handleClassify = async () => {
    if (!formData.facts_of_case.trim()) {
      alert("Please provide the facts of the dispute before classifying.");
      return;
    }
    setClassifying(true);
    try {
      const result = await classifyComplaint({
        grievance_description: formData.facts_of_case,
        transaction_amount: formData.transaction_amount,
        platform_or_company: formData.opposite_party_name
      });
      setClassification(result);
      if (!formData.grievance_category) {
        setFormData(prev => ({ ...prev, grievance_category: result.category }));
      }
    } catch (err: any) {
      alert("Classification failed: " + err.message);
    } finally {
      setClassifying(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.complainant_name || !formData.opposite_party_name || !formData.facts_of_case) {
      alert("Please fill in required complainant, opposite party, and dispute facts.");
      return;
    }
    setDrafting(true);
    try {
      const draft = await generateComplaintDraft(formData);
      setGeneratedDraft(draft);
      loadSavedDrafts();
    } catch (err: any) {
      alert("Drafting failed: " + err.message);
    } finally {
      setDrafting(false);
    }
  };

  const handleCopy = () => {
    if (generatedDraft) {
      navigator.clipboard.writeText(generatedDraft.full_draft_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleFillSample = () => {
    setFormData({
      complainant_name: "Rahul Verma",
      complainant_contact: "+91-9876543210 / rahul.verma@example.com",
      complainant_address: "Flat 402, Shanti Vihar, Rohini Sector 14, Delhi 110085",
      opposite_party_name: "Flipkart Internet Pvt Ltd & Seller CloudRetail",
      opposite_party_address: "Buildings Alyssa, Begonia & Clover, Embassy Tech Village, Bengaluru 560103",
      grievance_category: "E-Commerce Delivery & Return Grievance",
      transaction_amount: 32500,
      transaction_date: "12-10-2023",
      order_or_invoice_number: "OD402910391039",
      facts_of_case: "The Complainant purchased a 55-inch Smart LED TV on the Opposite Party platform on 12-10-2023 for Rs 32,500. Upon delivery on 16-10-2023, the parcel was unboxed in presence of technician and found to have a shattered screen. The Complainant immediately raised a return request within the 7-day return window. The Opposite Party arbitrarily rejected the return citing policy exclusions, despite photographic evidence. Multiple emails and NCH complaints yielded no redressal.",
      relief_sought: "Full refund of Rs 32,500 with 18% p.a. interest, Rs 30,000 as compensation for harassment and mental agony, and Rs 15,000 towards litigation costs."
    });
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
      {/* Studio Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Formal Complaint Drafting Studio</h1>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Section 35, CPA 2019
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Generate legally structured petitions for filing before District or State Consumer Disputes Redressal Commissions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleFillSample}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-amber-300 font-medium transition-colors border border-slate-700"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Load Sample Data</span>
          </button>
          <button
            type="button"
            onClick={() => setShowSaved(!showSaved)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 font-medium transition-colors border border-slate-700"
          >
            <FolderOpen className="h-3.5 w-3.5" />
            <span>Saved Drafts ({savedDrafts.length})</span>
          </button>
        </div>
      </div>

      {/* Saved Drafts Accordion */}
      {showSaved && (
        <div className="mb-6 p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Saved Complaint Petitions</div>
          {savedDrafts.length === 0 ? (
            <div className="text-xs text-slate-500 italic">No saved complaints found.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {savedDrafts.map(draft => (
                <div
                  key={draft.id}
                  onClick={() => setGeneratedDraft(draft)}
                  className="p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-amber-500/40 cursor-pointer text-xs space-y-1 transition-all"
                >
                  <div className="font-semibold text-slate-200 truncate">{draft.complainant_name} vs {draft.opposite_party_name}</div>
                  <div className="text-amber-400 font-medium text-[11px]">{draft.forum}</div>
                  <div className="text-slate-400 text-[10px] truncate">{draft.grievance_category} — ₹{draft.transaction_amount.toLocaleString()}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form: Inputs */}
        <div className="lg:col-span-6 space-y-4">
          <form onSubmit={handleGenerate} className="space-y-4">
            {/* Complainant Card */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <div className="text-xs font-bold text-amber-400 uppercase tracking-wider">1. Complainant (Consumer) Details</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Full Legal Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.complainant_name}
                    onChange={e => setFormData({ ...formData, complainant_name: e.target.value })}
                    placeholder="e.g. Rahul Verma"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Contact Phone / Email *</label>
                  <input
                    type="text"
                    required
                    value={formData.complainant_contact}
                    onChange={e => setFormData({ ...formData, complainant_contact: e.target.value })}
                    placeholder="+91-XXXXXXXXXX / email"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Residential Address with PIN Code *</label>
                <input
                  type="text"
                  required
                  value={formData.complainant_address}
                  onChange={e => setFormData({ ...formData, complainant_address: e.target.value })}
                  placeholder="Address for correspondence"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>

            {/* Opposite Party Card */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <div className="text-xs font-bold text-amber-400 uppercase tracking-wider">2. Opposite Party (Respondent) Details</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Opposite Party / Company Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.opposite_party_name}
                    onChange={e => setFormData({ ...formData, opposite_party_name: e.target.value })}
                    placeholder="e.g. Amazon / Cloudtail / Samsung"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Registered Address / Branch</label>
                  <input
                    type="text"
                    value={formData.opposite_party_address}
                    onChange={e => setFormData({ ...formData, opposite_party_address: e.target.value })}
                    placeholder="Opposite party address"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>
            </div>

            {/* Dispute Financials & Facts */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
              <div className="text-xs font-bold text-amber-400 uppercase tracking-wider">3. Transaction & Dispute Details</div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Amount Paid (₹) *</label>
                  <input
                    type="number"
                    min="0"
                    step="any"
                    required
                    value={formData.transaction_amount || ""}
                    onChange={e => setFormData({ ...formData, transaction_amount: parseFloat(e.target.value) || 0 })}
                    placeholder="e.g. 35000"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Transaction Date</label>
                  <input
                    type="text"
                    value={formData.transaction_date}
                    onChange={e => setFormData({ ...formData, transaction_date: e.target.value })}
                    placeholder="DD-MM-YYYY"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Invoice / Order ID</label>
                  <input
                    type="text"
                    value={formData.order_or_invoice_number}
                    onChange={e => setFormData({ ...formData, order_or_invoice_number: e.target.value })}
                    placeholder="Order ID / Ref #"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs text-slate-400">Chronological Facts of Dispute *</label>
                  <button
                    type="button"
                    onClick={handleClassify}
                    disabled={classifying || !formData.facts_of_case}
                    className="text-[11px] text-amber-400 hover:text-amber-300 font-semibold flex items-center gap-1 transition-colors"
                  >
                    {classifying ? <RefreshCw className="h-3 w-3 animate-spin" /> : <Building className="h-3 w-3" />}
                    <span>Check Forum & Jurisdiction</span>
                  </button>
                </div>
                <textarea
                  required
                  rows={4}
                  value={formData.facts_of_case}
                  onChange={e => setFormData({ ...formData, facts_of_case: e.target.value })}
                  placeholder="State the facts in chronological order: date of purchase, defect/service failure, communication with opposite party, and refusal of resolution..."
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 focus:outline-none focus:border-amber-500 leading-relaxed"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Specific Relief Sought (Prayer Clause)</label>
                <input
                  type="text"
                  value={formData.relief_sought}
                  onChange={e => setFormData({ ...formData, relief_sought: e.target.value })}
                  placeholder="e.g. Full refund with interest, compensation for harassment, litigation costs"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>

            {/* Classification Feedback Card */}
            {classification && (
              <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/30 text-xs space-y-2">
                <div className="font-bold text-amber-400 flex items-center gap-1.5">
                  <Building className="h-3.5 w-3.5" />
                  Statutory Jurisdiction Determination
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                  <div>
                    <span className="text-slate-500">Grievance Category: </span>
                    <span className="text-slate-200 font-medium">{classification.category}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Pecuniary Slab: </span>
                    <span className="text-slate-200 font-medium">{classification.pecuniary_slab}</span>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-slate-500">Competent Forum: </span>
                    <span className="text-amber-300 font-bold">{classification.recommended_forum}</span>
                  </div>
                </div>
                <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-800">
                  Statutory Limitation: {classification.statutory_limitation}
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={drafting}
              className="w-full py-3 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-bold text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-amber-500/10"
            >
              {drafting ? <RefreshCw className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
              <span>Generate Section 35 Consumer Complaint Petition</span>
            </button>
          </form>
        </div>

        {/* Right Preview: Generated Petition */}
        <div className="lg:col-span-6 flex flex-col h-[750px] bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
          {/* Preview Toolbar */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-900/50">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
              <FileText className="h-4 w-4 text-amber-400" />
              <span>Formal Petition Preview</span>
            </div>

            {generatedDraft && (
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleCopy}
                  className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-[11px] text-slate-200 transition-colors border border-slate-700"
                >
                  {copied ? <CheckCircle className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                  <span>{copied ? "Copied!" : "Copy"}</span>
                </button>
                <a
                  href={getComplaintExportUrl(generatedDraft.id)}
                  download
                  className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-[11px] text-slate-950 font-semibold transition-colors shadow-sm"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>Download .txt</span>
                </a>
              </div>
            )}
          </div>

          {/* Petition Document Text */}
          <div className="flex-1 p-6 overflow-y-auto font-mono text-xs leading-relaxed text-slate-200 bg-slate-950 select-text whitespace-pre-wrap">
            {generatedDraft ? (
              generatedDraft.full_draft_text
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center text-slate-500 font-sans px-6">
                <FileText className="h-12 w-12 text-slate-700 mb-3" />
                <div className="font-semibold text-slate-400 mb-1">No Complaint Draft Generated Yet</div>
                <p className="text-xs text-slate-500 max-w-sm">
                  Complete the dispute details on the left and click "Generate Section 35 Consumer Complaint Petition" to view the formal legal draft.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
