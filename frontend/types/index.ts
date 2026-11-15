export interface ApplicableLaw {
  act_or_regulation: string;
  section_or_rule: string;
  provision_title: string;
  summary_of_relevance: string;
  is_authoritative: boolean;
  source_url?: string | null;
}

export interface AppropriateForum {
  forum_name: string;
  pecuniary_jurisdiction: string;
  filing_procedure: string;
  official_portal_or_contact: string;
}

export interface LegalCitation {
  citation: string;
  document_title: string;
  category: string;
  source_url: string;
  issuing_authority: string;
  is_authoritative: boolean;
  verification_status: string;
}

export interface StructuredLegalResponse {
  summary: string;
  applicable_laws: ApplicableLaw[];
  consumer_rights: string[];
  recommended_steps: string[];
  appropriate_forums: AppropriateForum[];
  required_documents: string[];
  statutory_timelines: string[];
  disclaimer: string;
  citations: LegalCitation[];
  crag_metadata?: {
    decision?: string;
    confidence_score?: number;
    secondary_retrieval_performed?: boolean;
    final_query?: string;
    missing_aspects?: string[];
  };
  verification_metadata?: {
    is_verified?: boolean;
    citation_precision?: number;
    validated_citations?: string[];
    invalid_citations?: string[];
    hallucination_detected?: boolean;
    verification_notes?: string;
  };
  provider_used?: string;
  model_name?: string;
  clarification_question?: string | null;
}

export interface ChatRequest {
  query: string;
  conversation_id?: string | null;
  mode?: "vector_only" | "bm25_only" | "hybrid" | "hybrid_graph";
  top_k?: number;
  filter_category?: string | null;
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  response: StructuredLegalResponse;
  created_at: string;
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface MessageItem {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  structured_data?: StructuredLegalResponse | null;
  created_at: string;
}

export interface ComplaintClassification {
  category: string;
  confidence: number;
  recommended_forum: string;
  pecuniary_slab: string;
  applicable_provisions: string[];
  suggested_reliefs: string[];
  statutory_limitation: string;
}

export interface ComplaintDraftRequest {
  complainant_name: string;
  complainant_contact: string;
  complainant_address: string;
  opposite_party_name: string;
  opposite_party_address?: string;
  grievance_category?: string;
  transaction_amount: number;
  transaction_date?: string;
  order_or_invoice_number?: string;
  facts_of_case: string;
  relief_sought?: string;
}

export interface ComplaintDraftResponse {
  id: string;
  complainant_name: string;
  opposite_party_name: string;
  forum: string;
  grievance_category: string;
  transaction_amount: number;
  full_draft_text: string;
  citations: any[];
  status: string;
  created_at: string;
}

export interface DocumentAnalysisResponse {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  extracted_text_preview: string;
  merchant_name?: string | null;
  invoice_amount?: number | null;
  invoice_date?: string | null;
  order_or_invoice_id?: string | null;
  product_description?: string | null;
  potential_grievance_indicators: string[];
  suggested_legal_claims: string[];
  created_at: string;
}

export interface KnowledgeSearchResponse {
  query: string;
  total_found: number;
  mode_used: string;
  candidates: any[];
}

export interface GraphEntityDetail {
  entity: {
    id: string;
    entity_type: string;
    name: string;
    canonical_citation: string;
    document_id: string;
    category: string;
    summary: string;
    provenance_chunk_id?: string;
    entity_metadata?: Record<string, any>;
  };
  connected_neighbors: Array<{
    direction: "incoming" | "outgoing";
    relation_type: string;
    neighbor_id: string;
    neighbor_name: string;
    neighbor_type: string;
    summary: string;
  }>;
}
