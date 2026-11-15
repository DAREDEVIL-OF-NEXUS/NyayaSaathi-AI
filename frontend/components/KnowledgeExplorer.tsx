"use client";

import React, { useState, useEffect } from "react";
import {
  BookOpen,
  Search,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  GitFork,
  Layers,
  Building,
  Scale,
  RefreshCw,
  ChevronRight,
  Database
} from "lucide-react";
import {
  searchKnowledge,
  getGraphEntity,
  getKnowledgeSources,
  getKnowledgeStats
} from "../lib/api";
import { KnowledgeSearchResponse, GraphEntityDetail } from "../types";

export const KnowledgeExplorer: React.FC = () => {
  const [subTab, setSubTab] = useState<"sources" | "search" | "graph">("sources");
  const [manifest, setManifest] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchMode, setSearchMode] = useState("hybrid");
  const [searchResults, setSearchResults] = useState<KnowledgeSearchResponse | null>(null);
  const [searching, setSearching] = useState(false);

  // Graph state
  const [selectedEntityId, setSelectedEntityId] = useState<string>("sec_35_manner_of_complaint");
  const [graphDetail, setGraphDetail] = useState<GraphEntityDetail | null>(null);
  const [loadingGraph, setLoadingGraph] = useState(false);

  const POPULAR_GRAPH_ENTITIES = [
    { id: "sec_35_manner_of_complaint", name: "Section 35 (Manner of Complaint)" },
    { id: "sec_28_district_commission", name: "Section 28 (District Commission)" },
    { id: "rule_4_ecommerce_duties", name: "Rule 4 (E-Commerce Platform Duties)" },
    { id: "rule_7_seller_duties", name: "Rule 7 (Duties of Sellers)" },
    { id: "auth_ccpa", name: "Central Consumer Protection Authority (CCPA)" },
    { id: "portal_nch", name: "National Consumer Helpline (NCH 1915)" }
  ];

  useEffect(() => {
    loadManifestAndStats();
    loadEntityGraph(selectedEntityId);
  }, []);

  const loadManifestAndStats = async () => {
    try {
      const [srcs, st] = await Promise.all([
        getKnowledgeSources().catch(() => null),
        getKnowledgeStats().catch(() => null)
      ]);
      setManifest(srcs);
      setStats(st);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await searchKnowledge(searchQuery, 8, searchMode);
      setSearchResults(res);
    } catch (err: any) {
      alert("Search failed: " + err.message);
    } finally {
      setSearching(false);
    }
  };

  const loadEntityGraph = async (id: string) => {
    setSelectedEntityId(id);
    setLoadingGraph(true);
    try {
      const res = await getGraphEntity(id);
      setGraphDetail(res);
    } catch (err) {
      console.error("Failed to load entity graph:", err);
      setGraphDetail(null);
    } finally {
      setLoadingGraph(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
      {/* Header & Stats Banner */}
      <div className="mb-6 border-b border-slate-800 pb-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Legal Knowledge Base & Graph</h1>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Official Indian Sources
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Curated statutory legislation, Official Gazette regulations, procedural SOPs, and relational legal knowledge graph.
          </p>
        </div>

        {stats && (
          <div className="flex items-center gap-2 text-xs">
            <div className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 flex items-center gap-2">
              <Database className="h-3.5 w-3.5 text-amber-400" />
              <span>Corpus Documents: <strong className="text-slate-100">{stats.official_documents_count}</strong></span>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 flex items-center gap-2">
              <GitFork className="h-3.5 w-3.5 text-blue-400" />
              <span>Graph Entities: <strong className="text-slate-100">{stats.graph_entities_count}</strong></span>
            </div>
          </div>
        )}
      </div>

      {/* Subtab Selector */}
      <div className="flex rounded-xl bg-slate-950 p-1 border border-slate-800 text-xs font-semibold mb-6 max-w-md">
        <button
          onClick={() => setSubTab("sources")}
          className={`flex-1 py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5 ${
            subTab === "sources" ? "bg-slate-800 text-amber-400 shadow-sm" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          <BookOpen className="h-3.5 w-3.5" />
          <span>Official Sources</span>
        </button>
        <button
          onClick={() => setSubTab("search")}
          className={`flex-1 py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5 ${
            subTab === "search" ? "bg-slate-800 text-amber-400 shadow-sm" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          <Search className="h-3.5 w-3.5" />
          <span>Direct Hybrid Search</span>
        </button>
        <button
          onClick={() => setSubTab("graph")}
          className={`flex-1 py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5 ${
            subTab === "graph" ? "bg-slate-800 text-amber-400 shadow-sm" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          <GitFork className="h-3.5 w-3.5" />
          <span>Knowledge Graph</span>
        </button>
      </div>

      {/* Tab 1: Official Sources */}
      {subTab === "sources" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {manifest?.documents?.map((doc: any, dIdx: number) => (
              <div key={dIdx} className="p-5 rounded-2xl bg-slate-950 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between shadow-lg">
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="font-bold text-sm text-slate-100">{doc.title}</div>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0 capitalize ${
                        doc.verification_status === "verified"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                          : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                      }`}
                    >
                      {doc.verification_status}
                    </span>
                  </div>

                  <div className="text-xs text-amber-400/90 font-medium">
                    Category: {doc.category?.replace(/^\d+_/, "").replace(/_/g, " ").toUpperCase()}
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed">
                    {doc.description || "Official legal document integrated into NyayaSaathi AI knowledge base."}
                  </p>

                  <div className="text-[11px] text-slate-500 pt-1">
                    Issuing Authority: <span className="text-slate-300 font-medium">{doc.issuing_authority}</span>
                  </div>
                </div>

                <div className="pt-4 mt-2 border-t border-slate-900 flex items-center justify-between">
                  <span className="text-[10px] text-slate-500 font-mono">
                    Format: {doc.format?.toUpperCase()}
                  </span>
                  {doc.official_source_url && (
                    <a
                      href={doc.official_source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1 font-semibold underline"
                    >
                      <span>Official Source Portal</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Direct Search */}
      {subTab === "search" && (
        <div className="space-y-6">
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search legal provisions (e.g. 'cancellation refund seller', 'Section 35', 'District Commission limit')..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>

            <select
              value={searchMode}
              onChange={(e) => setSearchMode(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-3 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
            >
              <option value="hybrid">Hybrid (Dense E5 + BM25Okapi)</option>
              <option value="hybrid_graph">Hybrid RAG + Knowledge Graph</option>
              <option value="vector_only">Dense Vector Only</option>
              <option value="bm25_only">BM25 Lexical Only</option>
            </select>

            <button
              type="submit"
              disabled={searching || !searchQuery.trim()}
              className="px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-bold text-xs transition-all flex items-center justify-center gap-2 shadow-md shadow-amber-500/10"
            >
              {searching ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              <span>Search Corpus</span>
            </button>
          </form>

          {/* Search Results */}
          {searchResults && (
            <div className="space-y-4">
              <div className="text-xs text-slate-400 font-semibold">
                Found {searchResults.total_found} candidate passages using <span className="text-amber-400 uppercase">{searchResults.mode_used}</span>:
              </div>

              <div className="space-y-3">
                {searchResults.candidates.map((cand, cIdx) => (
                  <div key={cIdx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="font-bold text-amber-300 text-sm">{cand.section_or_rule || "Statutory Provision"}</span>
                        <span className="text-slate-400 font-medium ml-2">— {cand.document_title}</span>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400 font-mono">
                        Score: {cand.score?.toFixed(4)}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-500 font-medium">
                      Authority: {cand.issuing_authority} | Category: {cand.category} | Method: {cand.retrieval_method}
                    </div>

                    <p className="text-slate-300 leading-relaxed font-sans whitespace-pre-wrap bg-slate-900/60 p-3 rounded-lg border border-slate-800/80">
                      {cand.text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Legal Knowledge Graph */}
      {subTab === "graph" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Entity Selector list */}
          <div className="lg:col-span-4 space-y-2">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Key Legal Entities</div>
            {POPULAR_GRAPH_ENTITIES.map((ent) => (
              <button
                key={ent.id}
                onClick={() => loadEntityGraph(ent.id)}
                className={`w-full text-left p-3 rounded-xl border text-xs font-medium transition-all flex items-center justify-between ${
                  selectedEntityId === ent.id
                    ? "bg-slate-900 border-amber-500/50 text-amber-300"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                <span>{ent.name}</span>
                <ChevronRight className="h-4 w-4 shrink-0 text-slate-600" />
              </button>
            ))}
          </div>

          {/* Graph Neighborhood Inspector */}
          <div className="lg:col-span-8 bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-xl">
            {loadingGraph ? (
              <div className="h-64 flex items-center justify-center text-xs text-amber-400 gap-2">
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Traversing 1-hop legal knowledge graph neighborhood...</span>
              </div>
            ) : graphDetail ? (
              <div className="space-y-6">
                {/* Seed Entity Details */}
                <div className="p-4 rounded-xl bg-slate-900 border border-amber-500/30 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="font-bold text-base text-amber-300">{graphDetail.entity.name}</h3>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                      {graphDetail.entity.entity_type}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400">
                    Citation: <strong className="text-slate-200">{graphDetail.entity.canonical_citation}</strong>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">{graphDetail.entity.summary}</p>
                </div>

                {/* Connected 1-hop Neighbors */}
                <div className="space-y-3">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <GitFork className="h-3.5 w-3.5 text-blue-400" />
                    Connected Graph Neighbors ({graphDetail.connected_neighbors.length})
                  </div>

                  {graphDetail.connected_neighbors.length === 0 ? (
                    <div className="text-xs text-slate-500 italic p-4 rounded-xl bg-slate-900/40 border border-slate-800">
                      No connected neighbors found within 1-hop traversal boundary.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {graphDetail.connected_neighbors.map((nb, nIdx) => (
                        <div key={nIdx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1.5">
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-semibold text-slate-200 truncate">{nb.neighbor_name}</span>
                            <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 uppercase">
                              {nb.direction}
                            </span>
                          </div>
                          <div className="text-[11px] text-amber-400 font-mono font-medium">
                            Relationship: {nb.relation_type}
                          </div>
                          <p className="text-slate-400 text-[11px] leading-relaxed line-clamp-3">
                            {nb.summary || "Connected legal entity in knowledge graph."}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-xs text-slate-500">
                <GitFork className="h-10 w-10 text-slate-700 mb-2" />
                <span>Select a legal entity on the left to inspect its graph relationships.</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
