import re
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import fitz  # pymupdf
from bs4 import BeautifulSoup

@dataclass
class ExtractedDocument:
    doc_id: str
    title: str
    category: str
    source_url: str
    issuing_authority: str
    verification_status: str
    is_authoritative: bool
    text: str
    pages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DocumentExtractor:
    """
    Production-grade document extraction for Indian legal texts.
    Supports PDF, HTML, and Text formats with legal-aware text cleaning.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        text = text.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"xxxGID[HE]xxx", "", text)
        text = re.sub(r"[-_]{4,}", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        return text.strip()

    @classmethod
    def extract_pdf(cls, file_path: Path, metadata: Dict[str, Any]) -> ExtractedDocument:
        doc = fitz.open(str(file_path))
        pages_text: List[str] = []
        full_text_parts: List[str] = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            raw_page_text = page.get_text("text")
            cleaned_page = cls.clean_text(raw_page_text)
            if cleaned_page:
                pages_text.append(cleaned_page)
                full_text_parts.append(f"--- [Page {page_idx + 1}] ---\n{cleaned_page}")

        doc.close()
        combined_text = "\n\n".join(full_text_parts)

        return ExtractedDocument(
            doc_id=metadata.get("document_id", file_path.stem),
            title=metadata.get("title", file_path.stem),
            category=metadata.get("category", "unclassified"),
            source_url=metadata.get("official_source_url", ""),
            issuing_authority=metadata.get("issuing_authority", ""),
            verification_status=metadata.get("verification_status", "unverified"),
            is_authoritative=metadata.get("is_authoritative_for_rag", False),
            text=combined_text,
            pages=pages_text,
            metadata={
                **metadata,
                "page_count": len(pages_text),
                "file_format": "pdf",
                "file_name": file_path.name
            }
        )

    @classmethod
    def extract_html(cls, file_path: Path, metadata: Dict[str, Any]) -> ExtractedDocument:
        raw_html = file_path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(raw_html, "html.parser")

        for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "svg"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        cleaned_text = cls.clean_text(text)

        return ExtractedDocument(
            doc_id=metadata.get("document_id", file_path.stem),
            title=metadata.get("title", soup.title.string.strip() if soup.title and soup.title.string else file_path.stem),
            category=metadata.get("category", "unclassified"),
            source_url=metadata.get("official_source_url", ""),
            issuing_authority=metadata.get("issuing_authority", ""),
            verification_status=metadata.get("verification_status", "unverified"),
            is_authoritative=metadata.get("is_authoritative_for_rag", False),
            text=cleaned_text,
            pages=[cleaned_text],
            metadata={
                **metadata,
                "file_format": "html",
                "file_name": file_path.name
            }
        )

    @classmethod
    def extract_text(cls, file_path: Path, metadata: Dict[str, Any]) -> ExtractedDocument:
        raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
        cleaned = cls.clean_text(raw_text)

        return ExtractedDocument(
            doc_id=metadata.get("document_id", file_path.stem),
            title=metadata.get("title", file_path.stem),
            category=metadata.get("category", "unclassified"),
            source_url=metadata.get("official_source_url", ""),
            issuing_authority=metadata.get("issuing_authority", ""),
            verification_status=metadata.get("verification_status", "unverified"),
            is_authoritative=metadata.get("is_authoritative_for_rag", False),
            text=cleaned,
            pages=[cleaned],
            metadata={
                **metadata,
                "file_format": "txt",
                "file_name": file_path.name
            }
        )

    @classmethod
    def extract(cls, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> ExtractedDocument:
        meta = metadata or {}
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return cls.extract_pdf(file_path, meta)
        elif ext in [".html", ".htm"]:
            return cls.extract_html(file_path, meta)
        elif ext in [".txt", ".md"]:
            return cls.extract_text(file_path, meta)
        else:
            raise ValueError(f"Unsupported file format: {ext} for file {file_path}")
