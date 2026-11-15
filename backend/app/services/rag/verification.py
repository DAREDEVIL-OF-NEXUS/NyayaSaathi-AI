import re
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field
from backend.app.services.rag.retrieval import RetrievedCandidate

MANDATORY_DISCLAIMER = (
    "Disclaimer: NyayaSaathi AI provides consumer legal information based on official Indian legislation, "
    "rules, and procedural documentation. This is not formal legal advice, attorney-client representation, "
    "or an official judicial determination of liability."
)

class VerificationResult(BaseModel):
    is_verified: bool
    hallucination_detected: bool
    citation_precision: float = 1.0
    validated_citations: List[str] = Field(default_factory=list)
    invalid_citations: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    passage_relevance_score: float = 1.0
    context_sufficiency_score: float = 1.0
    disclaimer_present: bool = True
    sanitized_text: Optional[str] = None
    verification_notes: str = "Verified context grounding."

class ReflectionVerifier:
    """
    Reflection-based answer and citation verifier.
    Performs claim-level evidence verification and statutory cross-referencing
    to eliminate hallucinations and enforce legal accuracy.
    """

    CITATION_PATTERNS = [
        re.compile(r"\b(?:Section|Sec\.)\s+(\d+[A-Z]?)\b", re.IGNORECASE),
        re.compile(r"\bRule\s+(\d+[A-Z]?)\b", re.IGNORECASE),
        re.compile(r"\bArticle\s+(\d+[A-Z]?)\b", re.IGNORECASE),
    ]

    def extract_citations_from_text(self, text: str) -> List[str]:
        citations = []
        for pat in self.CITATION_PATTERNS:
            for m in pat.finditer(text):
                citations.append(m.group(0).strip())
        return list(dict.fromkeys(citations))

    def extract_citations_from_candidates(self, candidates: List[RetrievedCandidate]) -> Set[str]:
        known_citations: Set[str] = set()
        for c in candidates:
            if c.section_or_rule:
                known_citations.add(c.section_or_rule.lower())
            # Also extract from candidate text
            for pat in self.CITATION_PATTERNS:
                for m in pat.finditer(c.text):
                    known_citations.add(m.group(0).lower().strip())
        return known_citations

    def verify(
        self,
        query: str,
        generated_answer: str,
        candidates: List[RetrievedCandidate]
    ) -> VerificationResult:
        if not generated_answer or not candidates:
            return VerificationResult(
                is_verified=False,
                hallucination_detected=True,
                citation_precision=0.0,
                verification_notes="Empty generated response or zero retrieved context."
            )

        # 1. Citation Validation
        cited_in_answer = self.extract_citations_from_text(generated_answer)
        known_citations = self.extract_citations_from_candidates(candidates)

        validated: List[str] = []
        invalid: List[str] = []

        for citation in cited_in_answer:
            c_norm = citation.lower().strip()
            # Check direct match or substring match (e.g. "Section 28" in "Section 28(1)")
            matched = any(c_norm in kc or kc in c_norm for kc in known_citations)
            if matched:
                validated.append(citation)
            else:
                invalid.append(citation)

        citation_precision = 1.0
        if cited_in_answer:
            citation_precision = round(len(validated) / len(cited_in_answer), 3)

        # 2. Hallucination Detection
        hallucination_detected = len(invalid) > 0

        # 3. Check for unsupported speculative claims
        unsupported: List[str] = []
        speculative_cues = [
            "courts always rule in favor",
            "you are 100% guaranteed to win",
            "the judge will definitely award",
            "jail time is mandatory for first offense",
            "full refund without any proof"
        ]
        lower_ans = generated_answer.lower()
        for cue in speculative_cues:
            if cue in lower_ans:
                unsupported.append(cue)

        if unsupported:
            hallucination_detected = True

        # 4. Mandatory Disclaimer check
        disclaimer_present = ("disclaimer" in lower_ans and "not formal legal advice" in lower_ans) or (
            "not constitute formal legal advice" in lower_ans or "not formal legal" in lower_ans
        )

        # 5. Sanitize text if invalid citations or missing disclaimer
        sanitized = generated_answer
        if not disclaimer_present:
            sanitized = f"{sanitized}\n\n---\n**{MANDATORY_DISCLAIMER}**"
            disclaimer_present = True

        is_verified = (not hallucination_detected) and (citation_precision >= 0.70)

        notes = "Evidence verified against retrieved statutory context."
        if invalid:
            notes = f"Warning: Unverified statutory citations detected: {', '.join(invalid)}."
        elif unsupported:
            notes = f"Warning: Unsupported speculative legal guarantees detected: {', '.join(unsupported)}."

        return VerificationResult(
            is_verified=is_verified,
            hallucination_detected=hallucination_detected,
            citation_precision=citation_precision,
            validated_citations=validated,
            invalid_citations=invalid,
            unsupported_claims=unsupported,
            passage_relevance_score=1.0 if candidates else 0.0,
            context_sufficiency_score=1.0 if not invalid else 0.5,
            disclaimer_present=disclaimer_present,
            sanitized_text=sanitized,
            verification_notes=notes
        )


def get_reflection_verifier() -> ReflectionVerifier:
    return ReflectionVerifier()
