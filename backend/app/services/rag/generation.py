import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.services.rag.retrieval import RetrievedCandidate
from backend.app.services.rag.crag import CRAGPipeline, get_crag_pipeline, CRAGDecision
from backend.app.services.rag.verification import ReflectionVerifier, get_reflection_verifier, MANDATORY_DISCLAIMER
from backend.app.services.llm.fallback import ResilientLLMManager, get_llm_manager

logger = logging.getLogger(__name__)

class ApplicableLaw(BaseModel):
    act_or_regulation: str
    section_or_rule: str
    provision_title: str
    summary_of_relevance: str
    is_authoritative: bool = True
    source_url: Optional[str] = None

class AppropriateForum(BaseModel):
    forum_name: str
    pecuniary_jurisdiction: str
    filing_procedure: str
    official_portal_or_contact: str

class LegalCitation(BaseModel):
    citation: str
    document_title: str
    category: str
    source_url: str
    issuing_authority: str
    is_authoritative: bool
    verification_status: str

class StructuredLegalResponse(BaseModel):
    summary: str
    applicable_laws: List[ApplicableLaw] = Field(default_factory=list)
    consumer_rights: List[str] = Field(default_factory=list)
    recommended_steps: List[str] = Field(default_factory=list)
    appropriate_forums: List[AppropriateForum] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    statutory_timelines: List[str] = Field(default_factory=list)
    disclaimer: str = MANDATORY_DISCLAIMER
    citations: List[LegalCitation] = Field(default_factory=list)
    crag_metadata: Dict[str, Any] = Field(default_factory=dict)
    verification_metadata: Dict[str, Any] = Field(default_factory=dict)
    provider_used: str = "unknown"
    model_name: str = "unknown"
    clarification_question: Optional[str] = None


class RAGGenerationService:
    """
    End-to-end RAG Generation Orchestrator.
    Executes CRAG retrieval, formats legal context and graph relationships,
    queries resilient LLM, and enforces reflection-based verification.
    """

    SYSTEM_PROMPT = """You are NyayaSaathi AI (न्यायसाथी AI), a specialized legal technology assistant for Indian Consumer Protection Law.
Your role is to assist Indian consumers by explaining their statutory rights, applicable regulations, grievance redressal options, and filing procedures.

CRITICAL INSTRUCTIONS:
1. Base all legal conclusions strictly on the PROVIDED RETRIEVED CONTEXT and LEGAL KNOWLEDGE GRAPH below.
2. DO NOT invent section numbers, rule names, or legal precedents that are not in the context.
3. Every legal claim MUST be cited with its exact Act, Section, or Rule (e.g. 'Section 28 of Consumer Protection Act, 2019' or 'Rule 5 of E-Commerce Rules, 2020').
4. Distinguish between verified official Gazette provisions and partially verified summaries.
5. Provide actionable, empathetic, step-by-step guidance for the consumer.
6. Always state clearly that this is informational and not formal legal representation.
7. Return your response as a valid JSON object matching the requested schema exactly."""

    def __init__(
        self,
        crag_pipeline: Optional[CRAGPipeline] = None,
        llm_manager: Optional[ResilientLLMManager] = None,
        verifier: Optional[ReflectionVerifier] = None
    ):
        self.crag_pipeline = crag_pipeline or get_crag_pipeline()
        self.llm_manager = llm_manager or get_llm_manager()
        self.verifier = verifier or get_reflection_verifier()

    def _build_context_prompt(
        self,
        query: str,
        candidates: List[RetrievedCandidate]
    ) -> str:
        context_parts = []
        for idx, c in enumerate(candidates, start=1):
            sec_header = f"[{idx}] {c.document_title} — {c.section_or_rule or 'General Provision'}"
            meta_line = (
                f"Category: {c.category} | Authority: {c.issuing_authority} | "
                f"Verification: {c.verification_status} | Authoritative: {c.is_authoritative}"
            )
            text_body = c.text

            # Enriched Graph Context
            graph_lines = []
            if c.graph_context:
                graph_lines.append("Legal Knowledge Graph Connections:")
                for gc in c.graph_context:
                    graph_lines.append(f"  - ({gc.relation_type}) -> {gc.target_name}")

            graph_block = "\n" + "\n".join(graph_lines) if graph_lines else ""
            context_parts.append(f"{sec_header}\n{meta_line}\n{text_body}{graph_block}\n")

        joined_context = "\n----------------------------------------\n".join(context_parts)

        json_schema_prompt = """
Respond with a JSON object containing these keys:
{
  "summary": "Clear, concise overview of consumer's rights and situation",
  "applicable_laws": [
    {
      "act_or_regulation": "Name of Act or Rules",
      "section_or_rule": "Section or Rule number",
      "provision_title": "Title/heading of provision",
      "summary_of_relevance": "How this provision applies to the consumer's grievance"
    }
  ],
  "consumer_rights": ["Specific consumer rights under the law"],
  "recommended_steps": ["Step 1: Contact customer support / Grievance Officer...", "Step 2: Register grievance on NCH..."],
  "appropriate_forums": [
    {
      "forum_name": "District Commission / NCH / CCPA",
      "pecuniary_jurisdiction": "Up to Rs 50 Lakh, etc.",
      "filing_procedure": "Online via e-Daakhil or physical filing",
      "official_portal_or_contact": "https://consumerhelpline.gov.in or 1915"
    }
  ],
  "required_documents": ["Invoice / receipt", "Proof of payment", "Email communications"],
  "statutory_timelines": ["48 hours for acknowledgment", "30 days for redressal", "2 years limitation"],
  "disclaimer": "Standard statutory disclaimer"
}
"""

        prompt = f"""=== USER CONSUMER GRIEVANCE ===
{query}

=== RETRIEVED STATUTORY CONTEXT & LEGAL KNOWLEDGE GRAPH ===
{joined_context}

=== RESPONSE FORMAT SPECIFICATION ===
{json_schema_prompt}
"""
        return prompt

    def generate_response(
        self,
        query: str,
        top_k: int = 6,
        mode: str = "hybrid_graph",
        filter_category: Optional[str] = None
    ) -> StructuredLegalResponse:
        # 1. Execute Corrective RAG (CRAG) Pipeline
        crag_result = self.crag_pipeline.run(
            query=query,
            top_k=top_k,
            mode=mode,
            filter_category=filter_category
        )

        candidates = crag_result.candidates

        # Handle INSUFFICIENT evidence early
        if crag_result.decision == CRAGDecision.INSUFFICIENT or not candidates:
            return StructuredLegalResponse(
                summary="We could not find sufficient matching statutory provisions or procedure documents in the official knowledge base.",
                disclaimer=MANDATORY_DISCLAIMER,
                clarification_question=crag_result.clarification_message,
                crag_metadata={
                    "decision": crag_result.decision.value,
                    "confidence_score": crag_result.evaluation.confidence_score,
                    "reasoning": crag_result.evaluation.reasoning
                },
                verification_metadata={"is_verified": False, "notes": "Insufficient retrieved context."}
            )

        # 2. Build Grounded Context Prompt
        prompt = self._build_context_prompt(query, candidates)

        # 3. Query Resilient LLM (Gemini with OpenRouter fallback)
        llm_response = self.llm_manager.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            json_mode=True,
            temperature=0.2,
            max_tokens=2048
        )

        raw_data = llm_response.parsed_json or {}
        summary_text = raw_data.get("summary") or llm_response.content

        # 4. Reflection-Based Answer Verification
        verification = self.verifier.verify(query, summary_text, candidates)

        # 5. Build structured citations from candidates
        citations: List[LegalCitation] = []
        for c in candidates:
            citations.append(
                LegalCitation(
                    citation=c.section_or_rule or c.document_title,
                    document_title=c.document_title,
                    category=c.category,
                    source_url=c.source_url,
                    issuing_authority=c.issuing_authority,
                    is_authoritative=c.is_authoritative,
                    verification_status=c.verification_status
                )
            )

        # 6. Parse structured sub-objects
        applicable_laws = []
        for item in raw_data.get("applicable_laws", []):
            applicable_laws.append(
                ApplicableLaw(
                    act_or_regulation=item.get("act_or_regulation", "Consumer Protection Act, 2019"),
                    section_or_rule=item.get("section_or_rule", ""),
                    provision_title=item.get("provision_title", ""),
                    summary_of_relevance=item.get("summary_of_relevance", "")
                )
            )

        appropriate_forums = []
        for item in raw_data.get("appropriate_forums", []):
            appropriate_forums.append(
                AppropriateForum(
                    forum_name=item.get("forum_name", "Consumer Commission"),
                    pecuniary_jurisdiction=item.get("pecuniary_jurisdiction", "Varies by claim value"),
                    filing_procedure=item.get("filing_procedure", "Online via e-Daakhil"),
                    official_portal_or_contact=item.get("official_portal_or_contact", "https://edaakhil.nic.in")
                )
            )

        return StructuredLegalResponse(
            summary=verification.sanitized_text or summary_text,
            applicable_laws=applicable_laws,
            consumer_rights=raw_data.get("consumer_rights", ["Right to be informed", "Right to seek redressal"]),
            recommended_steps=raw_data.get("recommended_steps", [
                "Lodge formal complaint with the merchant or Grievance Redressal Officer.",
                "Call National Consumer Helpline at 1915 or register grievance on consumerhelpline.gov.in."
            ]),
            appropriate_forums=appropriate_forums,
            required_documents=raw_data.get("required_documents", [
                "Tax invoice or bill of purchase",
                "Transaction ID / payment confirmation",
                "Copy of written communication with seller"
            ]),
            statutory_timelines=raw_data.get("statutory_timelines", [
                "Acknowledgment within 48 hours",
                "Grievance resolution within 1 month",
                "Limitation period of 2 years"
            ]),
            disclaimer=MANDATORY_DISCLAIMER,
            citations=citations,
            crag_metadata={
                "decision": crag_result.decision.value,
                "confidence_score": crag_result.evaluation.confidence_score,
                "secondary_retrieval_performed": crag_result.secondary_retrieval_performed,
                "final_query": crag_result.final_query,
                "missing_aspects": crag_result.evaluation.missing_aspects
            },
            verification_metadata={
                "is_verified": verification.is_verified,
                "citation_precision": verification.citation_precision,
                "validated_citations": verification.validated_citations,
                "invalid_citations": verification.invalid_citations,
                "hallucination_detected": verification.hallucination_detected,
                "verification_notes": verification.verification_notes
            },
            provider_used=llm_response.provider,
            model_name=llm_response.model_name
        )


def get_generation_service() -> RAGGenerationService:
    return RAGGenerationService()
