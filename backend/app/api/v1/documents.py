import os
import uuid
import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.entities import DocumentUpload
from backend.app.schemas.document import DocumentAnalysisResponse
from backend.app.services.document.analyzer import DocumentAnalyzer

router = APIRouter()
analyzer = DocumentAnalyzer()

class DirectAnalyzeRequest(BaseModel):
    text: str
    filename: Optional[str] = "input_text.txt"

@router.post("/documents/upload", response_model=DocumentAnalysisResponse, summary="Upload an invoice/receipt and analyze consumer claims")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    contents = await file.read()
    file_size = len(contents)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    doc_id = str(uuid.uuid4())
    safe_filename = Path(file.filename or "upload.pdf").name
    dest_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{safe_filename}")

    with open(dest_path, "wb") as f:
        f.write(contents)

    analysis = analyzer.analyze_document(
        doc_id=doc_id,
        filename=safe_filename,
        file_bytes=contents,
        file_size=file_size
    )

    doc_record = DocumentUpload(
        id=doc_id,
        filename=safe_filename,
        file_path=dest_path,
        file_type=Path(safe_filename).suffix.lower() or "unknown",
        file_size=file_size,
        extracted_text=analysis.extracted_text_preview,
        extracted_metadata={
            "merchant_name": analysis.merchant_name,
            "invoice_amount": analysis.invoice_amount,
            "invoice_date": analysis.invoice_date,
            "order_or_invoice_id": analysis.order_or_invoice_id,
            "product_description": analysis.product_description,
            "potential_grievance_indicators": analysis.potential_grievance_indicators,
            "suggested_legal_claims": analysis.suggested_legal_claims
        },
        created_at=datetime.datetime.utcnow()
    )

    db.add(doc_record)
    db.commit()

    return analysis


@router.post("/documents/analyze", response_model=DocumentAnalysisResponse, summary="Analyze extracted text directly without file upload")
def analyze_text_direct(req: DirectAnalyzeRequest):
    doc_id = str(uuid.uuid4())
    filename = req.filename or "direct_text.txt"
    return analyzer.analyze_document(
        doc_id=doc_id,
        filename=filename,
        file_bytes=req.text.encode("utf-8"),
        file_size=len(req.text)
    )


@router.get("/documents", summary="List all uploaded documents")
def list_uploaded_documents(db: Session = Depends(get_db)):
    docs = db.query(DocumentUpload).order_by(DocumentUpload.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "created_at": d.created_at,
            "metadata": d.extracted_metadata
        }
        for d in docs
    ]


@router.get("/documents/{document_id}", summary="Get uploaded document details")
def get_document_details(document_id: str, db: Session = Depends(get_db)):
    d = db.query(DocumentUpload).filter(DocumentUpload.id == document_id).first()
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return {
        "id": d.id,
        "filename": d.filename,
        "file_path": d.file_path,
        "file_type": d.file_type,
        "file_size": d.file_size,
        "extracted_text_preview": d.extracted_text,
        "metadata": d.extracted_metadata,
        "created_at": d.created_at
    }
