import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from backend.app.services.rag.extraction import ExtractedDocument
from backend.app.core.config import settings

@dataclass
class LegalChunk:
    chunk_id: str
    parent_id: Optional[str]
    doc_id: str
    category: str
    document_title: str
    chapter: Optional[str]
    section_or_rule: Optional[str]
    legal_hierarchy: str
    text: str
    token_count: int
    source_url: str
    issuing_authority: str
    verification_status: str
    is_authoritative: bool
    is_parent: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class LegalChunker:
    CHAPTER_PATTERN = re.compile(r'^(?:CHAPTER|PART)\s+([IVXLCDM\d]+[A-Z]?)(?:[\s:—–-]+([^\r\n]+))?', re.IGNORECASE | re.MULTILINE)
    SECTION_PATTERN = re.compile(r'^(?:Section|Sec\.)\s+(\d+[A-Z]?)\.?\s*([^\r\n.—–]+)?[.—–]', re.IGNORECASE | re.MULTILINE)
    RULE_PATTERN = re.compile(r'^(?:Rule|Guideline)\s+(\d+[A-Z]?)\.?\s*([^\r\n.—–]+)?[.—–]', re.IGNORECASE | re.MULTILINE)

    def __init__(self, target_chunk_tokens: int = 500, max_chunk_tokens: int = 750, overlap_tokens: int = 75):
        self.target_tokens = target_chunk_tokens
        self.max_tokens = max_chunk_tokens
        self.overlap_tokens = overlap_tokens

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return max(1, len(text.split()))

    def split_into_legal_provisions(self, text: str) -> List[Dict[str, Any]]:
        lines = text.split('\n')
        provisions: List[Dict[str, Any]] = []
        current_chapter: Optional[str] = None
        current_provision: Optional[str] = None
        current_heading: Optional[str] = None
        current_lines: List[str] = []

        for line in lines:
            trimmed = line.strip()
            chap_match = self.CHAPTER_PATTERN.match(trimmed)
            if chap_match:
                if current_provision and current_lines:
                    prov_text = '\n'.join(current_lines).strip()
                    if prov_text:
                        provisions.append({
                            'chapter': current_chapter,
                            'section_or_rule': current_provision,
                            'heading': current_heading,
                            'text': prov_text
                        })
                    current_lines = []
                    current_provision = None
                    current_heading = None
                chap_num = chap_match.group(1)
                chap_title = chap_match.group(2) or ''
                current_chapter = f'Chapter {chap_num}: {chap_title.strip()}'.strip(': ')

            sec_match = self.SECTION_PATTERN.match(trimmed)
            rule_match = self.RULE_PATTERN.match(trimmed)

            if sec_match or rule_match:
                if current_provision and current_lines:
                    prov_text = '\n'.join(current_lines).strip()
                    if prov_text:
                        provisions.append({
                            'chapter': current_chapter,
                            'section_or_rule': current_provision,
                            'heading': current_heading,
                            'text': prov_text
                        })
                    current_lines = []

                if sec_match:
                    sec_num = sec_match.group(1)
                    sec_heading = sec_match.group(2) or ''
                    current_provision = f'Section {sec_num}'
                    current_heading = sec_heading.strip()
                else:
                    rule_num = rule_match.group(1)
                    rule_heading = rule_match.group(2) or ''
                    current_provision = f'Rule {rule_num}'
                    current_heading = rule_heading.strip()

            current_lines.append(line)

        if current_lines:
            prov_text = '\n'.join(current_lines).strip()
            if prov_text:
                provisions.append({
                    'chapter': current_chapter,
                    'section_or_rule': current_provision or 'General Provisions',
                    'heading': current_heading or '',
                    'text': prov_text
                })
        return provisions

    def chunk_provision(self, doc: ExtractedDocument, provision: Dict[str, Any], parent_chunk_id: str) -> List[LegalChunk]:
        text = provision['text']
        total_tokens = self.estimate_tokens(text)
        sec_name = provision.get('section_or_rule', 'General')
        chapter = provision.get('chapter')

        if total_tokens <= self.max_tokens:
            chunk_id = f'{parent_chunk_id}_c1'
            return [LegalChunk(
                chunk_id=chunk_id,
                parent_id=parent_chunk_id,
                doc_id=doc.doc_id,
                category=doc.category,
                document_title=doc.title,
                chapter=chapter,
                section_or_rule=sec_name,
                legal_hierarchy=f'{doc.title} > {chapter or ""} > {sec_name}'.replace(' >  >', ' >').strip(' >'),
                text=text,
                token_count=total_tokens,
                source_url=doc.source_url,
                issuing_authority=doc.issuing_authority,
                verification_status=doc.verification_status,
                is_authoritative=doc.is_authoritative,
                is_parent=False,
                metadata={**doc.metadata, 'heading': provision.get('heading', ''), 'is_monolithic_section': True}
            )]

        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks: List[LegalChunk] = []
        current_batch: List[str] = []
        current_count = 0
        child_idx = 1

        for p in paragraphs:
            p_tokens = self.estimate_tokens(p)
            if current_count + p_tokens > self.target_tokens and current_batch:
                batch_text = '\n\n'.join(current_batch)
                chunk_id = f'{parent_chunk_id}_c{child_idx}'
                chunks.append(LegalChunk(
                    chunk_id=chunk_id,
                    parent_id=parent_chunk_id,
                    doc_id=doc.doc_id,
                    category=doc.category,
                    document_title=doc.title,
                    chapter=chapter,
                    section_or_rule=sec_name,
                    legal_hierarchy=f'{doc.title} > {chapter or ""} > {sec_name} (Part {child_idx})'.replace(' >  >', ' >').strip(' >'),
                    text=batch_text,
                    token_count=self.estimate_tokens(batch_text),
                    source_url=doc.source_url,
                    issuing_authority=doc.issuing_authority,
                    verification_status=doc.verification_status,
                    is_authoritative=doc.is_authoritative,
                    is_parent=False,
                    metadata={**doc.metadata, 'heading': provision.get('heading', ''), 'part_number': child_idx}
                ))
                child_idx += 1
                current_batch = [p]
                current_count = p_tokens
            else:
                current_batch.append(p)
                current_count += p_tokens

        if current_batch:
            batch_text = '\n\n'.join(current_batch)
            chunk_id = f'{parent_chunk_id}_c{child_idx}'
            chunks.append(LegalChunk(
                chunk_id=chunk_id,
                parent_id=parent_chunk_id,
                doc_id=doc.doc_id,
                category=doc.category,
                document_title=doc.title,
                chapter=chapter,
                section_or_rule=sec_name,
                legal_hierarchy=f'{doc.title} > {chapter or ""} > {sec_name} (Part {child_idx})'.replace(' >  >', ' >').strip(' >'),
                text=batch_text,
                token_count=self.estimate_tokens(batch_text),
                source_url=doc.source_url,
                issuing_authority=doc.issuing_authority,
                verification_status=doc.verification_status,
                is_authoritative=doc.is_authoritative,
                is_parent=False,
                metadata={**doc.metadata, 'heading': provision.get('heading', ''), 'part_number': child_idx}
            ))
        return chunks

    def chunk_document(self, doc: ExtractedDocument) -> Tuple[List[LegalChunk], List[LegalChunk]]:
        provisions = self.split_into_legal_provisions(doc.text)
        parent_chunks: List[LegalChunk] = []
        child_chunks: List[LegalChunk] = []

        for idx, prov in enumerate(provisions, start=1):
            sec_clean = re.sub(r'[^a-zA-Z0-9]', '_', prov.get('section_or_rule', f'p{idx}')).lower().strip('_')
            parent_id = f'{doc.doc_id}_{sec_clean}'

            parent_chunk = LegalChunk(
                chunk_id=parent_id,
                parent_id=None,
                doc_id=doc.doc_id,
                category=doc.category,
                document_title=doc.title,
                chapter=prov.get('chapter'),
                section_or_rule=prov.get('section_or_rule'),
                legal_hierarchy=f'{doc.title} > {prov.get("chapter") or ""} > {prov.get("section_or_rule")}'.replace(' >  >', ' >').strip(' >'),
                text=prov['text'],
                token_count=self.estimate_tokens(prov['text']),
                source_url=doc.source_url,
                issuing_authority=doc.issuing_authority,
                verification_status=doc.verification_status,
                is_authoritative=doc.is_authoritative,
                is_parent=True,
                metadata={**doc.metadata, 'heading': prov.get('heading', '')}
            )
            parent_chunks.append(parent_chunk)
            children = self.chunk_provision(doc, prov, parent_id)
            child_chunks.extend(children)

        return parent_chunks, child_chunks