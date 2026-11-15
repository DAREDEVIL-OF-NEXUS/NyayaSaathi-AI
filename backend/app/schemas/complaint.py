import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ComplaintClassifyRequest(BaseModel):
    grievance_description: str = Field(..., min_length=5, description="Consumer grievance narrative")
    transaction_amount: Optional[float] = Field(0.0, ge=0.0, description="Amount paid or transaction value in INR")
    platform_or_company: Optional[str] = Field(None, description="Opposite party / company name")

class ComplaintClassification(BaseModel):
    category: str
    confidence: float
    recommended_forum: str
    pecuniary_slab: str
    applicable_provisions: List[str] = Field(default_factory=list)
    suggested_reliefs: List[str] = Field(default_factory=list)
    statutory_limitation: str = "2 years from cause of action"

class ComplaintDraftRequest(BaseModel):
    complainant_name: str = Field(..., min_length=2)
    complainant_contact: str = Field(..., min_length=5)
    complainant_address: str = Field(..., min_length=5)
    opposite_party_name: str = Field(..., min_length=2)
    opposite_party_address: Optional[str] = Field("Address not provided", min_length=2)
    grievance_category: Optional[str] = Field(None)
    transaction_amount: float = Field(0.0, ge=0.0)
    transaction_date: Optional[str] = Field(None)
    order_or_invoice_number: Optional[str] = Field(None)
    facts_of_case: str = Field(..., min_length=15, description="Chronological facts of dispute")
    relief_sought: Optional[str] = Field(None, description="Specific damages/relief claimed")

class ComplaintDraftResponse(BaseModel):
    id: str
    complainant_name: str
    opposite_party_name: str
    forum: str
    grievance_category: str
    transaction_amount: float
    full_draft_text: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    status: str
    created_at: datetime.datetime
