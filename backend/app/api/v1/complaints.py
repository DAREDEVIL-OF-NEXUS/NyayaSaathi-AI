import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.entities import ComplaintDraft, User
from backend.app.schemas.complaint import (
    ComplaintClassifyRequest,
    ComplaintClassification,
    ComplaintDraftRequest,
    ComplaintDraftResponse,
)
from backend.app.api.deps import get_optional_current_user
from backend.app.services.complaint.engine import ComplaintEngine

router = APIRouter()
complaint_engine = ComplaintEngine()

@router.post("/complaints/classify", response_model=ComplaintClassification, summary="Classify consumer grievance and pecuniary forum")
def classify_complaint_endpoint(req: ComplaintClassifyRequest):
    return complaint_engine.classify_grievance(
        grievance_description=req.grievance_description,
        transaction_amount=req.transaction_amount or 0.0,
        platform_or_company=req.platform_or_company
    )


@router.post("/complaints/draft", response_model=ComplaintDraftResponse, summary="Generate formal Section 35 consumer complaint draft")
def draft_complaint_endpoint(
    req: ComplaintDraftRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    draft_text, citations = complaint_engine.draft_formal_complaint(req)
    classification = complaint_engine.classify_grievance(
        grievance_description=req.facts_of_case,
        transaction_amount=req.transaction_amount,
        platform_or_company=req.opposite_party_name
    )

    complaint_record = ComplaintDraft(
        id=str(uuid.uuid4()),
        user_id=current_user.id if current_user else None,
        complainant_name=req.complainant_name,
        complainant_contact=req.complainant_contact,
        complainant_address=req.complainant_address,
        opposite_party_name=req.opposite_party_name,
        opposite_party_address=req.opposite_party_address or "Address not provided",
        grievance_category=req.grievance_category or classification.category,
        transaction_amount=req.transaction_amount,
        transaction_date=req.transaction_date,
        relief_claimed=req.relief_sought or "Refund with interest and compensation",
        forum=classification.recommended_forum,
        facts_summary=req.facts_of_case[:500],
        full_draft_text=draft_text,
        citations=citations,
        status="draft",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )

    db.add(complaint_record)
    db.commit()
    db.refresh(complaint_record)

    return ComplaintDraftResponse(
        id=complaint_record.id,
        complainant_name=complaint_record.complainant_name,
        opposite_party_name=complaint_record.opposite_party_name,
        forum=complaint_record.forum,
        grievance_category=complaint_record.grievance_category,
        transaction_amount=complaint_record.transaction_amount,
        full_draft_text=complaint_record.full_draft_text,
        citations=complaint_record.citations or [],
        status=complaint_record.status,
        created_at=complaint_record.created_at
    )


@router.get("/complaints", response_model=List[ComplaintDraftResponse], summary="List all saved complaint drafts")
def list_complaints(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ComplaintDraft)
    if current_user:
        query = query.filter(ComplaintDraft.user_id == current_user.id)
    else:
        query = query.filter(ComplaintDraft.user_id == None)

    drafts = query.order_by(ComplaintDraft.created_at.desc()).all()
    return [
        ComplaintDraftResponse(
            id=d.id,
            complainant_name=d.complainant_name,
            opposite_party_name=d.opposite_party_name,
            forum=d.forum,
            grievance_category=d.grievance_category,
            transaction_amount=d.transaction_amount,
            full_draft_text=d.full_draft_text,
            citations=d.citations or [],
            status=d.status,
            created_at=d.created_at
        )
        for d in drafts
    ]


@router.get("/complaints/{complaint_id}", response_model=ComplaintDraftResponse, summary="Get complaint draft by ID")
def get_complaint(
    complaint_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    d = db.query(ComplaintDraft).filter(ComplaintDraft.id == complaint_id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint draft not found")

    if d.user_id and (not current_user or d.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this complaint draft.")

    return ComplaintDraftResponse(
        id=d.id,
        complainant_name=d.complainant_name,
        opposite_party_name=d.opposite_party_name,
        forum=d.forum,
        grievance_category=d.grievance_category,
        transaction_amount=d.transaction_amount,
        full_draft_text=d.full_draft_text,
        citations=d.citations or [],
        status=d.status,
        created_at=d.created_at
    )


@router.get("/complaints/{complaint_id}/export", summary="Export formal complaint draft as plaintext or downloadable file")
def export_complaint(
    complaint_id: str,
    format: Optional[str] = "download",
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    d = db.query(ComplaintDraft).filter(ComplaintDraft.id == complaint_id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint draft not found")

    if d.user_id and (not current_user or d.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this complaint draft.")

    headers = {}
    if format == "download":
        headers["Content-Disposition"] = f'attachment; filename="formal_complaint_{complaint_id[:8]}.txt"'

    return Response(
        content=d.full_draft_text,
        media_type="text/plain; charset=utf-8",
        headers=headers
    )
