import {
  ChatRequest,
  ChatResponse,
  ConversationSummary,
  MessageItem,
  ComplaintClassification,
  ComplaintDraftRequest,
  ComplaintDraftResponse,
  DocumentAnalysisResponse,
  KnowledgeSearchResponse,
  GraphEntityDetail,
  StructuredLegalResponse,
} from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export function getAuthHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
  const headers: Record<string, string> = { ...extraHeaders };
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("nyayasaathi_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

export async function checkBackendHealth(): Promise<{ status: string }> {
  const res = await fetch("http://localhost:8000/health", { cache: "no-store" });
  if (!res.ok) throw new Error("Backend unavailable");
  return res.json();
}

// ===================== CHAT & CONSULTATION =====================
export async function sendChatQuery(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Chat request failed" }));
    throw new Error(err.detail || "Chat request failed");
  }
  return res.json();
}

export async function streamChatQuery(
  req: ChatRequest,
  onStatus: (status: string) => void,
  onToken: (token: string) => void,
  onComplete: (data: { conversation_id: string; message_id: string; response: StructuredLegalResponse }) => void,
  onError: (error: string) => void
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: getAuthHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(req),
    });

    if (!res.ok || !res.body) {
      throw new Error(`Streaming failed with status: ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data: ")) {
          try {
            const data = JSON.parse(trimmed.slice(6));
            if (data.type === "status") {
              onStatus(data.message);
            } else if (data.type === "token") {
              onToken(data.token);
            } else if (data.type === "complete") {
              onComplete(data);
            }
          } catch (e) {
            console.error("Error parsing SSE JSON:", e);
          }
        }
      }
    }
  } catch (err: any) {
    onError(err.message || "Streaming connection failed");
  }
}

export async function listConversations(): Promise<ConversationSummary[]> {
  const res = await fetch(`${API_BASE}/conversations`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load conversations");
  return res.json();
}

export async function getConversationMessages(conversationId: string): Promise<MessageItem[]> {
  const res = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load messages");
  return res.json();
}

export async function deleteConversation(conversationId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Failed to delete conversation");
}

export async function submitMessageFeedback(messageId: string, rating: number, feedbackText?: string): Promise<void> {
  await fetch(`${API_BASE}/messages/${messageId}/feedback`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ rating, feedback_text: feedbackText }),
  });
}

// ===================== COMPLAINTS ENGINE =====================
export async function classifyComplaint(data: {
  grievance_description: string;
  transaction_amount?: number;
  platform_or_company?: string;
}): Promise<ComplaintClassification> {
  const res = await fetch(`${API_BASE}/complaints/classify`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Grievance classification failed");
  return res.json();
}

export async function generateComplaintDraft(req: ComplaintDraftRequest): Promise<ComplaintDraftResponse> {
  const res = await fetch(`${API_BASE}/complaints/draft`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error("Complaint drafting failed");
  return res.json();
}

export async function listComplaints(): Promise<ComplaintDraftResponse[]> {
  const res = await fetch(`${API_BASE}/complaints`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to list complaints");
  return res.json();
}

export async function getComplaint(id: string): Promise<ComplaintDraftResponse> {
  const res = await fetch(`${API_BASE}/complaints/${id}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load complaint");
  return res.json();
}

export function getComplaintExportUrl(id: string): string {
  return `${API_BASE}/complaints/${id}/export`;
}

// ===================== DOCUMENTS & INVOICES =====================
export async function uploadDocument(file: File): Promise<DocumentAnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Document upload failed");
  }
  return res.json();
}

export async function analyzeTextDirect(text: string, filename?: string): Promise<DocumentAnalysisResponse> {
  const res = await fetch(`${API_BASE}/documents/analyze`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ text, filename }),
  });
  if (!res.ok) throw new Error("Direct text analysis failed");
  return res.json();
}

export async function listDocuments(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/documents`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to list documents");
  return res.json();
}

// ===================== KNOWLEDGE BASE & GRAPH =====================
export async function searchKnowledge(
  query: string,
  top_k: number = 8,
  mode: string = "hybrid"
): Promise<KnowledgeSearchResponse> {
  const res = await fetch(`${API_BASE}/knowledge/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k, mode }),
  });
  if (!res.ok) throw new Error("Knowledge search failed");
  return res.json();
}

export async function getGraphEntity(entityId: string): Promise<GraphEntityDetail> {
  const res = await fetch(`${API_BASE}/knowledge/graph/${encodeURIComponent(entityId)}`);
  if (!res.ok) throw new Error("Graph entity not found");
  return res.json();
}

export async function getKnowledgeSources(): Promise<any> {
  const res = await fetch(`${API_BASE}/knowledge/sources`);
  if (!res.ok) throw new Error("Failed to load official sources manifest");
  return res.json();
}

export async function getKnowledgeStats(): Promise<any> {
  const res = await fetch(`${API_BASE}/knowledge/stats`);
  if (!res.ok) throw new Error("Failed to load knowledge statistics");
  return res.json();
}
