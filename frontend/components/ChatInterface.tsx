"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Send,
  PlusCircle,
  Trash2,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Star,
  Shield,
  Layers,
  FileCheck,
  Clock,
  Building,
  HelpCircle,
  Sparkles,
  RefreshCw
} from "lucide-react";
import {
  sendChatQuery,
  streamChatQuery,
  listConversations,
  getConversationMessages,
  deleteConversation,
  submitMessageFeedback
} from "../lib/api";
import {
  ConversationSummary,
  MessageItem,
  StructuredLegalResponse,
  ChatRequest
} from "../types";

export const ChatInterface: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamStatus, setStreamStatus] = useState<string | null>(null);
  const [mode, setMode] = useState<"hybrid_graph" | "hybrid" | "vector_only" | "bm25_only">("hybrid_graph");
  const [filterCategory, setFilterCategory] = useState<string | null>(null);
  const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({});
  const [userRatings, setUserRatings] = useState<Record<string, number>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested starter queries
  const SUGGESTED_QUERIES = [
    "Seller refuses refund for damaged TV received from Flipkart order",
    "Flight cancelled by airline and only offering credit shell voucher",
    "E-commerce app charged hidden dark-pattern convenience fee at checkout",
    "What is the pecuniary jurisdiction limit for District Consumer Commission?"
  ];

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (currentConversationId) {
      loadMessages(currentConversationId);
    } else {
      setMessages([]);
    }
  }, [currentConversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamStatus]);

  const loadConversations = async () => {
    try {
      const data = await listConversations();
      setConversations(data);
      if (data.length > 0 && !currentConversationId) {
        setCurrentConversationId(data[0].id);
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  };

  const loadMessages = async (id: string) => {
    try {
      const data = await getConversationMessages(id);
      setMessages(data);
    } catch (err) {
      console.error("Failed to load messages:", err);
    }
  };

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setQuery("");
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteConversation(id);
      const remaining = conversations.filter(c => c.id !== id);
      setConversations(remaining);
      if (currentConversationId === id) {
        setCurrentConversationId(remaining.length > 0 ? remaining[0].id : null);
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  const handleSubmit = async (e?: React.FormEvent, overrideQuery?: string) => {
    if (e) e.preventDefault();
    const queryToSend = overrideQuery || query;
    if (!queryToSend.trim() || loading) return;

    const userMsgId = "user-" + Date.now();
    const newUserMsg: MessageItem = {
      id: userMsgId,
      role: "user",
      content: queryToSend,
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, newUserMsg]);
    setQuery("");
    setLoading(true);
    setStreamStatus("Initializing CRAG pipeline and retrieving official legal sources...");

    const req: ChatRequest = {
      query: queryToSend,
      conversation_id: currentConversationId,
      mode: mode,
      top_k: 6,
      filter_category: filterCategory
    };

    try {
      await streamChatQuery(
        req,
        (statusMsg) => {
          setStreamStatus(statusMsg);
        },
        (token) => {
          // Token update handling
        },
        (completeData) => {
          setStreamStatus(null);
          setCurrentConversationId(completeData.conversation_id);
          const asstMsg: MessageItem = {
            id: completeData.message_id,
            role: "assistant",
            content: completeData.response.summary,
            structured_data: completeData.response,
            created_at: new Date().toISOString()
          };
          setMessages(prev => [...prev, asstMsg]);
          setLoading(false);
          loadConversations();
        },
        (err) => {
          console.error("Stream error, falling back to direct POST:", err);
          sendChatQuery(req)
            .then(res => {
              setStreamStatus(null);
              setCurrentConversationId(res.conversation_id);
              const asstMsg: MessageItem = {
                id: res.message_id,
                role: "assistant",
                content: res.response.summary,
                structured_data: res.response,
                created_at: res.created_at
              };
              setMessages(prev => [...prev, asstMsg]);
              setLoading(false);
              loadConversations();
            })
            .catch(postErr => {
              setStreamStatus(null);
              setLoading(false);
              alert("Consultation failed: " + postErr.message);
            });
        }
      );
    } catch (err: any) {
      setStreamStatus(null);
      setLoading(false);
      console.error(err);
    }
  };

  const handleFeedback = async (messageId: string, rating: number) => {
    try {
      await submitMessageFeedback(messageId, rating);
      setUserRatings(prev => ({ ...prev, [messageId]: rating }));
    } catch (err) {
      console.error("Feedback failed:", err);
    }
  };

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Sidebar: Conversation History */}
      <aside className="w-72 bg-slate-950 border-r border-slate-800 flex flex-col hidden md:flex">
        <div className="p-4 border-b border-slate-800">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold text-sm transition-all shadow-md shadow-amber-500/10"
          >
            <PlusCircle className="h-4 w-4" />
            <span>New Consultation</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          <div className="text-xs font-semibold text-slate-500 px-3 py-2 uppercase tracking-wider">
            Previous Consultations
          </div>
          {conversations.length === 0 ? (
            <div className="text-xs text-slate-500 px-3 py-4 italic">No previous sessions yet</div>
          ) : (
            conversations.map(conv => (
              <div
                key={conv.id}
                onClick={() => setCurrentConversationId(conv.id)}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-lg text-sm cursor-pointer transition-colors ${
                  currentConversationId === conv.id
                    ? "bg-slate-800 text-amber-300 font-medium border border-slate-700/60"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                <div className="truncate flex-1 pr-2">
                  <div className="truncate text-xs font-medium text-slate-200">{conv.title}</div>
                  <div className="text-[10px] text-slate-500">{conv.message_count} messages</div>
                </div>
                <button
                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 text-slate-500 transition-opacity"
                  title="Delete consultation"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main Chat Workspace */}
      <main className="flex-1 flex flex-col bg-slate-900 overflow-hidden">
        {/* Messages Feed */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto text-center px-4">
              <div className="h-16 w-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4 shadow-xl">
                <Shield className="h-8 w-8" />
              </div>
              <h2 className="text-2xl font-bold text-slate-100 tracking-tight mb-2">
                Consumer Legal Consultation
              </h2>
              <p className="text-sm text-slate-400 mb-8 max-w-lg leading-relaxed">
                Ground your consumer grievance in the Consumer Protection Act, 2019, E-Commerce Rules, 2020, and National Consumer Helpline procedures.
              </p>

              {/* Starter Query Prompts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
                {SUGGESTED_QUERIES.map((sq, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSubmit(undefined, sq)}
                    className="p-3.5 rounded-xl bg-slate-950/70 hover:bg-slate-800 border border-slate-800 hover:border-amber-500/40 text-xs text-slate-300 transition-all flex items-start gap-2.5 shadow-sm group"
                  >
                    <Sparkles className="h-4 w-4 text-amber-400/70 shrink-0 mt-0.5 group-hover:text-amber-400" />
                    <span>{sq}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map(msg => (
              <div key={msg.id} className="max-w-4xl mx-auto w-full">
                {msg.role === "user" ? (
                  <div className="flex justify-end">
                    <div className="max-w-xl bg-amber-500 text-slate-950 px-4 py-3 rounded-2xl rounded-tr-sm font-medium text-sm shadow-md">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col gap-4 bg-slate-950/80 border border-slate-800/80 rounded-2xl p-5 sm:p-6 shadow-xl">
                    {/* Header Badges */}
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-xs text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Shield className="h-3.5 w-3.5" />
                          NyayaSaathi Verified Analysis
                        </span>
                        {msg.structured_data?.crag_metadata && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                            CRAG: {msg.structured_data.crag_metadata.decision || "SUFFICIENT"}
                          </span>
                        )}
                        {msg.structured_data?.verification_metadata?.is_verified && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 flex items-center gap-1">
                            <FileCheck className="h-3 w-3" />
                            Grounded
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-500">
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </div>
                    </div>

                    {/* Clarification Alert if insufficient */}
                    {msg.structured_data?.clarification_question && (
                      <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-2.5">
                        <HelpCircle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                        <div>
                          <div className="font-semibold text-amber-300 mb-0.5">Additional Details Required:</div>
                          {msg.structured_data.clarification_question}
                        </div>
                      </div>
                    )}

                    {/* Summary */}
                    <div className="text-sm text-slate-200 leading-relaxed font-normal">
                      {msg.structured_data?.summary || msg.content}
                    </div>

                    {/* Applicable Statutory Provisions */}
                    {msg.structured_data?.applicable_laws && msg.structured_data.applicable_laws.length > 0 && (
                      <div className="space-y-2.5 pt-2">
                        <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Layers className="h-3.5 w-3.5" />
                          Applicable Statutory Provisions
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                          {msg.structured_data.applicable_laws.map((law, lIdx) => (
                            <div key={lIdx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs flex flex-col justify-between">
                              <div>
                                <div className="font-semibold text-amber-300 mb-1">
                                  {law.section_or_rule}: {law.provision_title}
                                </div>
                                <div className="text-[11px] text-slate-400 font-medium mb-1.5">{law.act_or_regulation}</div>
                                <div className="text-slate-300 text-[11px] leading-relaxed">{law.summary_of_relevance}</div>
                              </div>
                              {law.source_url && (
                                <a
                                  href={law.source_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="mt-2 text-[10px] text-amber-400/80 hover:text-amber-300 flex items-center gap-1 underline"
                                >
                                  <span>Official Gazette Source</span>
                                  <ExternalLink className="h-2.5 w-2.5" />
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Consumer Rights Chips */}
                    {msg.structured_data?.consumer_rights && msg.structured_data.consumer_rights.length > 0 && (
                      <div className="pt-2">
                        <div className="text-xs font-semibold text-slate-400 mb-2">Statutory Consumer Rights:</div>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.structured_data.consumer_rights.map((cr, cIdx) => (
                            <span key={cIdx} className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] text-slate-300 font-medium">
                              ✓ {cr}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recommended Action Steps */}
                    {msg.structured_data?.recommended_steps && msg.structured_data.recommended_steps.length > 0 && (
                      <div className="space-y-2 pt-2">
                        <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          Recommended Step-by-Step Action
                        </div>
                        <div className="space-y-1.5">
                          {msg.structured_data.recommended_steps.map((step, sIdx) => (
                            <div key={sIdx} className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800/80 text-xs text-slate-200 flex items-start gap-2.5">
                              <span className="h-4 w-4 rounded-full bg-amber-500/20 text-amber-400 font-bold text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                                {sIdx + 1}
                              </span>
                              <span>{step}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Appropriate Forums & Pecuniary Jurisdictions */}
                    {msg.structured_data?.appropriate_forums && msg.structured_data.appropriate_forums.length > 0 && (
                      <div className="space-y-2 pt-2">
                        <div className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
                          <Building className="h-3.5 w-3.5" />
                          Competent Grievance Redressal Forums:
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {msg.structured_data.appropriate_forums.map((forum, fIdx) => (
                            <div key={fIdx} className="p-3 rounded-lg bg-slate-900/70 border border-slate-800 text-xs">
                              <div className="font-semibold text-slate-200 mb-0.5">{forum.forum_name}</div>
                              <div className="text-[11px] text-amber-400 mb-1">Jurisdiction: {forum.pecuniary_jurisdiction}</div>
                              <div className="text-[11px] text-slate-400 mb-1.5">{forum.filing_procedure}</div>
                              {forum.official_portal_or_contact && (
                                <span className="text-[10px] text-slate-500 block truncate">
                                  Portal: {forum.official_portal_or_contact}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Statutory Timelines & Required Documents */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                      {msg.structured_data?.statutory_timelines && msg.structured_data.statutory_timelines.length > 0 && (
                        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                          <div className="font-semibold text-amber-400 flex items-center gap-1.5 mb-1.5">
                            <Clock className="h-3.5 w-3.5" />
                            Statutory Timelines:
                          </div>
                          <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px]">
                            {msg.structured_data.statutory_timelines.map((tl, tIdx) => (
                              <li key={tIdx}>{tl}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {msg.structured_data?.required_documents && msg.structured_data.required_documents.length > 0 && (
                        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                          <div className="font-semibold text-slate-300 flex items-center gap-1.5 mb-1.5">
                            <FileCheck className="h-3.5 w-3.5" />
                            Required Evidentiary Documents:
                          </div>
                          <ul className="list-disc list-inside space-y-1 text-slate-400 text-[11px]">
                            {msg.structured_data.required_documents.map((rd, rIdx) => (
                              <li key={rIdx}>{rd}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Citations & Source Provenance Drawer */}
                    {msg.structured_data?.citations && msg.structured_data.citations.length > 0 && (
                      <div className="border-t border-slate-800/80 pt-3">
                        <button
                          onClick={() => setExpandedCitations(prev => ({ ...prev, [msg.id]: !prev[msg.id] }))}
                          className="flex items-center justify-between w-full text-xs text-slate-400 hover:text-slate-200 transition-colors"
                        >
                          <span className="flex items-center gap-1.5 font-medium">
                            <Layers className="h-3.5 w-3.5 text-amber-400" />
                            Verified Citations & Provenance ({msg.structured_data.citations.length})
                          </span>
                          {expandedCitations[msg.id] ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                        </button>

                        {expandedCitations[msg.id] && (
                          <div className="mt-2.5 space-y-2">
                            {msg.structured_data.citations.map((cite, cIdx) => (
                              <div key={cIdx} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs flex items-start justify-between gap-3">
                                <div>
                                  <div className="font-medium text-slate-200">{cite.citation}</div>
                                  <div className="text-[11px] text-slate-400">{cite.document_title} — {cite.issuing_authority}</div>
                                </div>
                                <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 shrink-0 capitalize">
                                  {cite.verification_status}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Response Footer: Feedback & Disclaimer */}
                    <div className="border-t border-slate-800/80 pt-3 flex flex-wrap items-center justify-between gap-2 text-xs">
                      {/* Feedback rating */}
                      <div className="flex items-center gap-2">
                        <span className="text-slate-500 text-[11px]">Was this helpful?</span>
                        <div className="flex items-center gap-1">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <button
                              key={star}
                              onClick={() => handleFeedback(msg.id, star)}
                              className={`p-0.5 hover:text-amber-400 transition-colors ${
                                (userRatings[msg.id] || msg.structured_data?.verification_metadata?.is_verified ? star : 0) <= (userRatings[msg.id] || 0)
                                  ? "text-amber-400"
                                  : "text-slate-600"
                              }`}
                            >
                              <Star className="h-3.5 w-3.5 fill-current" />
                            </button>
                          ))}
                        </div>
                      </div>

                      <div className="text-[10px] text-slate-500 italic">
                        {msg.structured_data?.provider_used && `Provider: ${msg.structured_data.provider_used}`}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}

          {/* Real-time Streaming Pulse Indicator */}
          {streamStatus && (
            <div className="max-w-4xl mx-auto w-full">
              <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-950/80 border border-amber-500/30 text-amber-300 text-xs animate-pulse">
                <RefreshCw className="h-4 w-4 animate-spin text-amber-400" />
                <span>{streamStatus}</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/90 backdrop-blur">
          <div className="max-w-4xl mx-auto space-y-2.5">
            {/* Controls Bar: Mode selector & Category Filter */}
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
              <div className="flex items-center gap-2">
                <span className="text-slate-400 text-[11px]">Retrieval Mode:</span>
                <select
                  value={mode}
                  onChange={(e: any) => setMode(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-md px-2 py-1 text-slate-200 text-xs focus:outline-none focus:border-amber-500"
                >
                  <option value="hybrid_graph">Hybrid RAG + Knowledge Graph (Recommended)</option>
                  <option value="hybrid">Hybrid RAG (Vector + BM25)</option>
                  <option value="vector_only">Dense Vector Search (E5)</option>
                  <option value="bm25_only">Lexical BM25 Search</option>
                </select>
              </div>

              <div className="flex items-center gap-1.5">
                {["all", "ecommerce", "defective_goods", "service_deficiency", "misleading_ads"].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setFilterCategory(cat === "all" ? null : cat)}
                    className={`px-2 py-0.5 rounded-full text-[10px] font-medium transition-colors ${
                      (cat === "all" && filterCategory === null) || filterCategory === cat
                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                        : "bg-slate-900 text-slate-400 hover:text-slate-300 border border-slate-800"
                    }`}
                  >
                    {cat === "all" ? "All Categories" : cat.replace("_", " ")}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="flex items-center gap-2">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                placeholder="Describe your consumer grievance (e.g. refused refund, broken delivery, misleading charge)..."
                rows={1}
                disabled={loading}
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 resize-none"
              />
              <button
                type="submit"
                disabled={!query.trim() || loading}
                className="px-4 py-3 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-bold transition-all flex items-center justify-center shrink-0 shadow-md shadow-amber-500/10"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
};
