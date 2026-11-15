import pytest
from backend.app.services.rag.generation import RAGGenerationService, StructuredLegalResponse
from backend.app.services.llm.fallback import ResilientLLMManager, MockLLMClient
from backend.app.services.rag.crag import get_crag_pipeline
from backend.app.services.rag.verification import get_reflection_verifier

def test_live_rag_generation_flow():
    # Construct mock LLM responding with structured JSON valid against retrieved context
    canned_json = {
        "summary": "Under Rule 2 of the Consumer Protection (Jurisdiction of the District Commission, the State Commission and the National Commission) Rules, 2021, the District Commission has pecuniary jurisdiction up to fifty lakh rupees.",
        "applicable_laws": [
            {
                "act_or_regulation": "Consumer Protection (Jurisdiction) Rules, 2021",
                "section_or_rule": "Rule 2",
                "provision_title": "Pecuniary Jurisdiction",
                "summary_of_relevance": "Sets District Commission threshold up to Rs 50 Lakh"
            }
        ],
        "consumer_rights": ["Right to seek redressal against unfair trade practices"],
        "recommended_steps": [
            "Calculate actual consideration paid excluding compensation claim.",
            "If value does not exceed Rs 50 Lakh, file complaint before District Consumer Commission."
        ],
        "appropriate_forums": [
            {
                "forum_name": "District Consumer Disputes Redressal Commission",
                "pecuniary_jurisdiction": "Up to Rs 50,00,000",
                "filing_procedure": "File online via e-Daakhil portal or submit physical petition.",
                "official_portal_or_contact": "https://edaakhil.nic.in"
            }
        ],
        "required_documents": [
            "Purchase invoice / consideration proof",
            "Proof of defect or deficiency",
            "Copy of legal notice sent to seller"
        ],
        "statutory_timelines": [
            "Limitation period of 2 years from date of cause of action"
        ],
        "disclaimer": "Disclaimer: This is not formal legal advice."
    }

    mock_llm = MockLLMClient(
        canned_response="Summary of jurisdiction rules.",
        canned_json=canned_json
    )
    llm_manager = ResilientLLMManager(
        primary_provider="mock",
        fallback_provider="mock",
        primary_client=mock_llm,
        fallback_client=mock_llm
    )

    service = RAGGenerationService(
        crag_pipeline=get_crag_pipeline(),
        llm_manager=llm_manager,
        verifier=get_reflection_verifier()
    )

    query = "What is the pecuniary jurisdiction limit for filing in District Commission?"
    response = service.generate_response(query, top_k=3, mode="hybrid_graph")

    assert isinstance(response, StructuredLegalResponse)
    assert response.summary != ""
    assert "District Commission" in response.summary or "Rule 2" in response.summary
    assert len(response.applicable_laws) >= 1
    assert len(response.appropriate_forums) >= 1
    assert len(response.citations) >= 1
    assert response.disclaimer != ""
    assert response.crag_metadata["decision"] in ["SUFFICIENT", "PARTIALLY_SUFFICIENT"]
    assert response.verification_metadata["is_verified"] is True
    assert response.verification_metadata["hallucination_detected"] is False

def test_rag_generation_insufficient_query():
    service = RAGGenerationService(
        crag_pipeline=get_crag_pipeline(),
        llm_manager=ResilientLLMManager(
            primary_provider="mock",
            fallback_provider="mock",
            primary_client=MockLLMClient(),
            fallback_client=MockLLMClient()
        ),
        verifier=get_reflection_verifier()
    )

    # Empty query or completely unrelated query that returns no legal match
    query = "zzzzqwerty12345 non-existent random query"
    response = service.generate_response(query, top_k=3)

    assert isinstance(response, StructuredLegalResponse)
    assert response.crag_metadata["decision"] == "INSUFFICIENT"
    assert response.clarification_question is not None
    assert response.verification_metadata["is_verified"] is False
