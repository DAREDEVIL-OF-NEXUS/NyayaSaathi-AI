import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class DocumentAnalysisResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    extracted_text_preview: str
    merchant_name: Optional[str] = None
    invoice_amount: Optional[float] = None
    invoice_date: Optional[str] = None
    order_or_invoice_id: Optional[str] = None
    product_description: Optional[str] = None
    potential_grievance_indicators: List[str] = Field(default_factory=list)
    suggested_legal_claims: List[str] = Field(default_factory=list)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
