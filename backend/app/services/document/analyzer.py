import re
import os
import uuid
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import fitz  # pymupdf

from backend.app.schemas.document import DocumentAnalysisResponse
from backend.app.services.rag.extraction import DocumentExtractor
from backend.app.services.llm.base import BaseLLMClient
from backend.app.services.llm.fallback import get_llm_manager

class DocumentAnalyzer:
    """
    Analyzes uploaded receipts, invoices, delivery proofs, and consumer communications.
    Extracts transaction parameters, detects potential grievance flags, and maps
    applicable provisions under Indian consumer law.
    """

    KNOWN_MERCHANTS = [
        "Amazon", "Flipkart", "Meesho", "Myntra", "Reliance Digital", "Croma",
        "Tata Cliq", "Nykaa", "Zomato", "Swiggy", "Blinkit", "Zepto", "MakeMyTrip",
        "Yatra", "Cleartrip", "Samsung", "Apple", "Xiaomi", "OnePlus", "Dell", "HP",
        "Airtel", "Jio", "Vodafone Idea", "Uber", "Ola", "Paytm"
    ]

    GRIEVANCE_TRIGGERS = [
        ("No return policy / Non-refundable clause", ["no return", "non refundable", "non-refundable", "cannot be returned", "no exchange"]),
        ("Unilateral cancellation penalty", ["cancellation fee", "cancellation charge", "100% cancellation", "non-cancellable"]),
        ("Exclusion of warranty or liability", ["sold as is", "no warranty", "at buyer risk", "company not liable", "no responsibility"]),
        ("Misleading pricing / Hidden platform charges", ["convenience fee", "handling charge", "packaging fee", "hidden charge", "extra fee"]),
        ("Unreasonable delivery timeline / Delay", ["delayed", "delayed delivery", "dispatch pending", "transit delay"]),
        ("Damaged or tampered goods received", ["damaged", "tampered", "seal broken", "defective item", "wrong item"])
    ]

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client

    def extract_text_from_file(self, file_path: str, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            try:
                doc = fitz.open(file_path)
                parts = []
                for page in doc:
                    text = page.get_text("text")
                    cleaned = DocumentExtractor.clean_text(text)
                    if cleaned:
                        parts.append(cleaned)
                doc.close()
                return "\n\n".join(parts)
            except Exception as e:
                return f"[PDF Extraction Error: {str(e)}]"
        elif ext in [".txt", ".md", ".json", ".csv"]:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return DocumentExtractor.clean_text(f.read())
            except Exception as e:
                return f"[Text Extraction Error: {str(e)}]"
        else:
            return f"[Unsupported file type {ext} for direct text extraction]"

    def extract_text_from_bytes(self, content: bytes, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            try:
                doc = fitz.open(stream=content, filetype="pdf")
                parts = []
                for page in doc:
                    text = page.get_text("text")
                    cleaned = DocumentExtractor.clean_text(text)
                    if cleaned:
                        parts.append(cleaned)
                doc.close()
                return "\n\n".join(parts)
            except Exception as e:
                return f"[PDF Extraction Error: {str(e)}]"
        elif ext in [".txt", ".md", ".json", ".csv"]:
            try:
                raw_text = content.decode("utf-8", errors="ignore")
                return DocumentExtractor.clean_text(raw_text)
            except Exception as e:
                return f"[Text Extraction Error: {str(e)}]"
        else:
            return f"[Unsupported file type {ext} for direct text extraction]"

    def parse_heuristics(self, text: str) -> Dict[str, Any]:
        """
        Regex and rule-based heuristic extraction for transaction documents.
        """
        data: Dict[str, Any] = {
            "merchant_name": None,
            "invoice_amount": None,
            "invoice_date": None,
            "order_or_invoice_id": None,
            "product_description": None,
            "potential_grievance_indicators": [],
            "suggested_legal_claims": []
        }

        # 1. Merchant Detection
        for merchant in self.KNOWN_MERCHANTS:
            if re.search(r"\b" + re.escape(merchant) + r"\b", text, re.IGNORECASE):
                data["merchant_name"] = merchant
                break

        if not data["merchant_name"]:
            # Check first 5 lines for company name heuristic
            lines = [line.strip() for line in text.split("\n") if line.strip()][:6]
            for line in lines:
                if any(kw in line.lower() for kw in ["pvt", "ltd", "enterprises", "retail", "technologies", "services", "store"]):
                    data["merchant_name"] = line[:60]
                    break

        # 2. Amount Detection
        amount_patterns = [
            r"(?:Grand\s*Total|Total\s*Amount|Net\s*Amount|Amount\s*Payable|Invoice\s*Total|Total)[:\s]*(?:₹|Rs\.?|INR)?\s*([0-9,]+(?:\.[0-9]{2})?)",
            r"(?:₹|Rs\.?|INR)\s*([0-9,]+(?:\.[0-9]{2})?)"
        ]
        for pat in amount_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            if matches:
                # Pick the match that looks like a plausible invoice total
                for m in matches:
                    try:
                        clean_num = m.replace(",", "")
                        val = float(clean_num)
                        if val > 0 and (data["invoice_amount"] is None or val > data["invoice_amount"]):
                            data["invoice_amount"] = val
                    except ValueError:
                        continue
                if data["invoice_amount"] is not None:
                    break

        # 3. Date Detection
        date_patterns = [
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
            r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
            r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b"
        ]
        for pat in date_patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                data["invoice_date"] = match.group(1)
                break

        # 4. Order / Invoice ID
        id_patterns = [
            r"(?:Order\s*(?:ID|No\.?|Number)|Invoice\s*(?:ID|No\.?|Number)|Ref\s*(?:ID|No\.?))[:\s]*([A-Za-z0-9\-#_]+)",
            r"\b(OD\d{12,20})\b",  # Flipkart order pattern
            r"\b(\d{3}-\d{7}-\d{7})\b"  # Amazon order pattern
        ]
        for pat in id_patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                data["order_or_invoice_id"] = match.group(1).strip()
                break

        # 5. Product Description heuristic
        desc_patterns = [
            r"(?:Item\s*Description|Description\s*of\s*Goods|Product\s*Name|Item)[:\s]*([^\n]+)",
            r"(?:Description)[:\s]*([^\n]+)"
        ]
        for pat in desc_patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                data["product_description"] = match.group(1).strip()[:150]
                break

        # 6. Grievance Indicators
        lower_text = text.lower()
        for label, keywords in self.GRIEVANCE_TRIGGERS:
            if any(kw in lower_text for kw in keywords):
                data["potential_grievance_indicators"].append(label)

        # 7. Suggested Legal Claims
        if any("no return" in ind.lower() or "cancellation" in ind.lower() for ind in data["potential_grievance_indicators"]):
            data["suggested_legal_claims"].append(
                "Rule 5(3)(b) & Rule 7, Consumer Protection (E-Commerce) Rules, 2020: Prohibition of arbitrary cancellation charges and mandate for return of goods"
            )
        if any("misleading" in ind.lower() or "hidden" in ind.lower() for ind in data["potential_grievance_indicators"]):
            data["suggested_legal_claims"].append(
                "Section 2(47), CPA 2019 & CCPA Guidelines 2022: Unfair Trade Practice regarding misleading pricing and undisclosed fees"
            )
        if any("damaged" in ind.lower() or "tampered" in ind.lower() for ind in data["potential_grievance_indicators"]):
            data["suggested_legal_claims"].append(
                "Section 2(34) & Section 84, CPA 2019: Product Liability for defective or damaged goods delivered to consumer"
            )
        if not data["suggested_legal_claims"]:
            data["suggested_legal_claims"].append(
                "Section 2(11), CPA 2019: Deficiency in service for failure to fulfill agreed terms of transaction"
            )

        return data

    def analyze_document(
        self,
        doc_id: str,
        filename: str,
        file_path: Optional[str] = None,
        file_bytes: Optional[bytes] = None,
        file_size: int = 0
    ) -> DocumentAnalysisResponse:
        """
        Extracts document text and generates structured grievance analysis.
        """
        if file_bytes:
            text = self.extract_text_from_bytes(file_bytes, filename)
            size = len(file_bytes) if file_size == 0 else file_size
        elif file_path and os.path.exists(file_path):
            text = self.extract_text_from_file(file_path, filename)
            size = os.path.getsize(file_path) if file_size == 0 else file_size
        else:
            text = "[Error: No document content available]"
            size = 0

        parsed = self.parse_heuristics(text)
        preview = (text[:400] + "...") if len(text) > 400 else text

        return DocumentAnalysisResponse(
            id=doc_id,
            filename=filename,
            file_type=Path(filename).suffix.lower() or "unknown",
            file_size=size,
            extracted_text_preview=preview,
            merchant_name=parsed["merchant_name"],
            invoice_amount=parsed["invoice_amount"],
            invoice_date=parsed["invoice_date"],
            order_or_invoice_id=parsed["order_or_invoice_id"],
            product_description=parsed["product_description"],
            potential_grievance_indicators=parsed["potential_grievance_indicators"],
            suggested_legal_claims=parsed["suggested_legal_claims"],
            created_at=datetime.datetime.utcnow()
        )
