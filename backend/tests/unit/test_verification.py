import pytest
from backend.app.services.rag.retrieval import RetrievedCandidate
from backend.app.services.rag.verification import ReflectionVerifier, MANDATORY_DISCLAIMER

def make_candidate(chunk_id: str, sec: str, text: str) -> RetrievedCandidate:
    return RetrievedCandidate(
        chunk_id=chunk_id,
        parent_id=None,
        doc_id="doc1",
        category="statutory",
        document_title="CPA 2019",
        section_or_rule=sec,
        legal_hierarchy=f"CPA > {sec}",
        text=text,
        score=0.05,
        retrieval_method="hybrid_rrf",
        source_url="https://indiacode.nic.in",
        issuing_authority="Legislative Dept",
        verification_status="verified_official",
        is_authoritative=True
    )

def test_extract_citations():
    verifier = ReflectionVerifier()
    text = "Under Section 28 and Rule 5, the consumer may file an appeal as per Section 41."
    citations = verifier.extract_citations_from_text(text)
    assert "Section 28" in citations
    assert "Rule 5" in citations
    assert "Section 41" in citations

def test_verify_all_valid_citations():
    verifier = ReflectionVerifier()
    cands = [
        make_candidate("c1", "Section 28", "District Commission jurisdiction under Section 28."),
        make_candidate("c2", "Rule 5", "Grievance redressal officer obligations under Rule 5.")
    ]
    answer = (
        "Under Section 28, you can approach the District Commission. "
        "Also Rule 5 mandates grievance acknowledgment. "
        "Disclaimer: This is not formal legal advice."
    )
    res = verifier.verify("How to file?", answer, cands)

    assert res.is_verified is True
    assert res.hallucination_detected is False
    assert res.citation_precision == 1.0
    assert "Section 28" in res.validated_citations
    assert "Rule 5" in res.validated_citations
    assert len(res.invalid_citations) == 0

def test_verify_hallucinated_citation_detected():
    verifier = ReflectionVerifier()
    cands = [
        make_candidate("c1", "Section 28", "District Commission jurisdiction under Section 28.")
    ]
    # Answer hallucinates Section 999 which does NOT exist in CPA 2019 or retrieved context
    answer = (
        "Under Section 28 and Section 999, the consumer is entitled to immediate 10x compensation. "
        "Disclaimer: This is not formal legal advice."
    )
    res = verifier.verify("What is compensation?", answer, cands)

    assert res.is_verified is False
    assert res.hallucination_detected is True
    assert "Section 999" in res.invalid_citations
    assert res.citation_precision < 1.0

def test_verify_speculative_claim_detected():
    verifier = ReflectionVerifier()
    cands = [
        make_candidate("c1", "Section 28", "District Commission proceedings.")
    ]
    answer = (
        "Under Section 28 you can file. The courts always rule in favor of the consumer and you are 100% guaranteed to win. "
        "Disclaimer: This is not formal legal advice."
    )
    res = verifier.verify("Can I win?", answer, cands)

    assert res.is_verified is False
    assert res.hallucination_detected is True
    assert len(res.unsupported_claims) >= 1

def test_missing_disclaimer_sanitization():
    verifier = ReflectionVerifier()
    cands = [
        make_candidate("c1", "Section 28", "District Commission jurisdiction under Section 28.")
    ]
    # No disclaimer in generated text
    answer = "Under Section 28, you can approach the District Commission."
    res = verifier.verify("Where to file?", answer, cands)

    assert res.disclaimer_present is True
    assert res.sanitized_text is not None
    assert "Disclaimer:" in res.sanitized_text
    assert "not formal legal advice" in res.sanitized_text.lower()
