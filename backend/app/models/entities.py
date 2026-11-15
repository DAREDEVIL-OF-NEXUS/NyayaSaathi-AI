import uuid
import datetime
from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="New Consultation")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(32), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    structured_data = Column(JSON, nullable=True)  # StructuredLegalResponse
    feedback_rating = Column(Integer, nullable=True)  # 1 to 5 stars
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

class ComplaintDraft(Base):
    __tablename__ = "complaint_drafts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complainant_name = Column(String(255), nullable=False)
    complainant_contact = Column(String(128), nullable=False)
    complainant_address = Column(Text, nullable=False)
    opposite_party_name = Column(String(255), nullable=False)
    opposite_party_address = Column(Text, nullable=True)
    grievance_category = Column(String(128), nullable=False)
    transaction_amount = Column(Float, nullable=False, default=0.0)
    transaction_date = Column(String(64), nullable=True)
    relief_claimed = Column(Text, nullable=False)
    forum = Column(String(255), nullable=False)
    facts_summary = Column(Text, nullable=False)
    full_draft_text = Column(Text, nullable=False)
    citations = Column(JSON, default=list)
    status = Column(String(64), default="draft")  # draft, finalized, filed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class DocumentUpload(Base):
    __tablename__ = "document_uploads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(64), nullable=False)
    file_size = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=True)
    extracted_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
