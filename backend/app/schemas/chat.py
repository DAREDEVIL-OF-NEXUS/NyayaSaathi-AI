import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.services.rag.generation import StructuredLegalResponse

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Consumer grievance or legal question")
    conversation_id: Optional[str] = Field(None, description="Existing conversation UUID or None to create new")
    mode: Optional[str] = Field("hybrid_graph", description="Retrieval mode: vector_only, bm25_only, hybrid, or hybrid_graph")
    top_k: Optional[int] = Field(6, ge=1, le=20, description="Max candidate chunks to retrieve")
    filter_category: Optional[str] = Field(None, description="Filter to specific legal category")

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: StructuredLegalResponse
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    message_count: int

class MessageItem(BaseModel):
    id: str
    role: str
    content: str
    structured_data: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime

class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="1 to 5 star rating")
    feedback_text: Optional[str] = Field(None, max_length=1000)
