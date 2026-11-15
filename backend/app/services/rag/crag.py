import re
import logging
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.services.rag.retrieval import RetrievedCandidate, HybridRetriever, get_hybrid_retriever
from backend.app.services.llm.base import BaseLLMClient
from backend.app.services.llm.fallback import get_llm_manager

logger = logging.getLogger(__name__)

class CRAGDecision(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    PARTIALLY_SUFFICIENT = "PARTIALLY_SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"

class CRAGEvaluationResult(BaseModel):
    decision: CRAGDecision
    confidence_score: float
    reasoning: str
    missing_aspects: List[str] = Field(default_factory=list)
    rewritten_query: Optional[str] = None
    clarification_question: Optional[str] = None
    is_missing_user_info: bool = False

class CRAGPipelineResult(BaseModel):
    original_query: str
    final_query: str
    decision: CRAGDecision
    candidates: List[RetrievedCandidate]
    evaluation: CRAGEvaluationResult
    secondary_retrieval_performed: bool = False
    clarification_needed: bool = False
    clarification_message: Optional[str] = None

class QueryRewriter:
    """
    Legal-aware search query rewriter and expander.
    Maps colloquial consumer complaints into formal statutory terminology
    and extracted legal concepts.
    """

    LEGAL_SYNONYMS = {
        "fake product": "counterfeit goods misleading advertisement unfair trade practice",
        "damaged product": "defective product product liability deficiency in service",
        "no refund": "refund timeline return of defective goods Rule 7 e-commerce",
        "wrong item": "defective goods delivery non-conforming goods",
        "delay": "statutory timeline delay in delivery compensation",
        "scam": "unfair trade practice misleading advertisement CCPA",
        "amazon": "marketplace e-commerce entity duties Rule 5",
        "flipkart": "marketplace e-commerce entity duties Rule 5",
        "customer care not answering": "grievance officer 48 hours acknowledgement timeline Rule 5",
        "cheated": "unfair contract unfair trade practice Section 2(47)",
        "court": "District Consumer Commission filing jurisdiction Section 34 Section 35",
        "helpline": "National Consumer Helpline 1915 NCH grievance registration",
        "appeal": "appeal to State Commission forty-five days Section 41",
        "limit": "pecuniary jurisdiction limit fifty lakh two crore Rule 2"
    }

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client

    def rewrite_heuristic(self, query: str, missing_aspects: List[str]) -> str:
        expanded_parts = [query.strip()]
        lower_q = query.lower()

        for colloquial, statutory in self.LEGAL_SYNONYMS.items():
            if colloquial in lower_q:
                expanded_parts.append(statutory)

        for aspect in missing_aspects:
            if aspect.lower() not in lower_q:
                expanded_parts.append(aspect)

        return " ".join(expanded_parts)

    def rewrite_with_llm(self, query: str, missing_aspects: List[str]) -> str:
        client = self.llm_client or get_llm_manager()
        prompt = f"""You are a legal search optimizer for Indian Consumer Protection Law.
The user submitted the following consumer grievance query:
"{query}"

The current retrieval was only partially sufficient due to missing legal aspects:
{', '.join(missing_aspects) if missing_aspects else 'Needs specific statutory provisions, sections, rules, or procedural authorities.'}

Rewrite and expand this query into a precise statutory search query targeting the Consumer Protection Act 2019, E-Commerce Rules 2020, CCPA Guidelines, or National Consumer Helpline.
Output ONLY the rewritten search query text without quotation marks or explanations."""

        try:
            resp = client.generate(prompt=prompt, temperature=0.1, max_tokens=100)
            rewritten = resp.content.strip().strip('"').strip("'")
            if rewritten and len(rewritten) > 5:
                return rewritten
        except Exception as e:
            logger.warning(f"[QueryRewriter] LLM query rewrite fallback to heuristic: {e}")

        return self.rewrite_heuristic(query, missing_aspects)


class CRAGEvaluator:
    """
    Evaluator for Retrieval-Augmented Evidence.
    Classifies retrieval outcome into SUFFICIENT, PARTIALLY_SUFFICIENT, or INSUFFICIENT.
    Distinguishes missing user facts from missing knowledge base provisions.
    """

    def __init__(
        self,
        sufficient_threshold: float = settings.CRAG_SUFFICIENT_THRESHOLD,
        insufficient_threshold: float = settings.CRAG_INSUFFICIENT_THRESHOLD,
        llm_client: Optional[BaseLLMClient] = None
    ):
        self.sufficient_threshold = sufficient_threshold
        self.insufficient_threshold = insufficient_threshold
        self.llm_client = llm_client

    def evaluate_heuristics(self, query: str, candidates: List[RetrievedCandidate]) -> CRAGEvaluationResult:
        if not candidates:
            return CRAGEvaluationResult(
                decision=CRAGDecision.INSUFFICIENT,
                confidence_score=0.0,
                reasoning="No relevant legal provisions or procedure documents found in knowledge base.",
                missing_aspects=["statutory_provisions", "official_guidance"],
                clarification_question="Could you specify the details of the consumer grievance, such as the platform or the defect involved?"
            )

        top_cand = candidates[0]
        max_score = top_cand.score

        # Check keyword presence in top candidates
        query_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", query.lower()))
        combined_text = " ".join([c.text.lower() for c in candidates[:3]])
        matched_words = {w for w in query_words if w in combined_text}
        coverage = len(matched_words) / max(1, len(query_words))

        # Check if legal provisions or rules were found
        has_specific_section = any(bool(c.section_or_rule) for c in candidates[:3])
        has_authoritative = any(c.is_authoritative for c in candidates[:3])

        # Guard: If query has substantive words but zero/near-zero matched in context,
        # vector retrieval returned distant vectors that are irrelevant. Force INSUFFICIENT.
        if query_words and coverage < 0.15:
            return CRAGEvaluationResult(
                decision=CRAGDecision.INSUFFICIENT,
                confidence_score=0.10,
                reasoning=f"Retrieved candidates do not match key factual terms of the query (keyword coverage: {coverage:.0%}).",
                missing_aspects=["relevant_statutory_topic", "consumer_protection_context"],
                clarification_question="We could not find matching consumer protection provisions for this query. Please clarify whether this relates to an e-commerce purchase, defective product, service deficiency, or unfair trade practice."
            )

        # Combined confidence metric
        confidence = (0.5 * min(1.0, max_score * 20.0)) + (0.3 * coverage) + (0.2 if has_specific_section else 0.0)
        confidence = round(min(1.0, max(0.0, confidence)), 3)

        missing = []
        if not has_specific_section:
            missing.append("specific_statutory_section_or_rule")
        if coverage < 0.5:
            missing.append("key_grievance_terms")

        # Missing user info check: user query is very short or missing essential facts
        is_missing_user_info = len(query.split()) < 4 and coverage > 0.3

        if confidence >= self.sufficient_threshold and has_specific_section:
            return CRAGEvaluationResult(
                decision=CRAGDecision.SUFFICIENT,
                confidence_score=confidence,
                reasoning=f"Retrieved candidate '{top_cand.section_or_rule}' provides strong statutory grounding.",
                missing_aspects=[]
            )
        elif confidence >= self.insufficient_threshold:
            clarif = None
            if is_missing_user_info:
                clarif = "To pinpoint the exact legal remedy, please specify the transaction value, dates, or company response."

            return CRAGEvaluationResult(
                decision=CRAGDecision.PARTIALLY_SUFFICIENT,
                confidence_score=confidence,
                reasoning="Retrieved evidence partially addresses query but lacks complete statutory provisions or specific timelines.",
                missing_aspects=missing,
                clarification_question=clarif,
                is_missing_user_info=is_missing_user_info
            )
        else:
            return CRAGEvaluationResult(
                decision=CRAGDecision.INSUFFICIENT,
                confidence_score=confidence,
                reasoning="Retrieved evidence does not adequately ground the user's grievance.",
                missing_aspects=missing or ["statutory_jurisdiction", "grievance_remedy"],
                clarification_question="We could not find matching consumer protection provisions for this specific query. Please clarify whether this relates to an e-commerce purchase, defective product, service deficiency, or unfair trade practice."
            )

    def evaluate(self, query: str, candidates: List[RetrievedCandidate]) -> CRAGEvaluationResult:
        # Fast, deterministic heuristic evaluation
        return self.evaluate_heuristics(query, candidates)


class CRAGPipeline:
    """
    Corrective RAG Orchestration Pipeline.
    Evaluates evidence sufficiency, triggers query expansion for partially sufficient results,
    and executes secondary hybrid retrieval with deduplication and loop bounds.
    """

    def __init__(
        self,
        retriever: Optional[HybridRetriever] = None,
        evaluator: Optional[CRAGEvaluator] = None,
        rewriter: Optional[QueryRewriter] = None
    ):
        self.retriever = retriever or get_hybrid_retriever()
        self.evaluator = evaluator or CRAGEvaluator()
        self.rewriter = rewriter or QueryRewriter()

    def run(
        self,
        query: str,
        top_k: int = 10,
        mode: str = "hybrid_graph",
        filter_category: Optional[str] = None
    ) -> CRAGPipelineResult:
        # Step 1: Initial Hybrid Retrieval
        initial_candidates = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            mode=mode,
            filter_category=filter_category
        )

        # Step 2: Retrieval Evaluation
        evaluation = self.evaluator.evaluate(query, initial_candidates)

        # Step 3: Handle SUFFICIENT
        if evaluation.decision == CRAGDecision.SUFFICIENT:
            return CRAGPipelineResult(
                original_query=query,
                final_query=query,
                decision=CRAGDecision.SUFFICIENT,
                candidates=initial_candidates,
                evaluation=evaluation,
                secondary_retrieval_performed=False
            )

        # Step 4: Handle PARTIALLY_SUFFICIENT -> Query Rewriting & Secondary Retrieval
        if evaluation.decision == CRAGDecision.PARTIALLY_SUFFICIENT:
            rewritten_query = self.rewriter.rewrite_with_llm(query, evaluation.missing_aspects)
            evaluation.rewritten_query = rewritten_query

            # Secondary retrieval
            secondary_candidates = self.retriever.retrieve(
                query=rewritten_query,
                top_k=top_k,
                mode=mode,
                filter_category=filter_category
            )

            # Deduplicate and merge candidates
            merged_map: Dict[str, RetrievedCandidate] = {c.chunk_id: c for c in initial_candidates}
            for sc in secondary_candidates:
                if sc.chunk_id in merged_map:
                    # Boost score if candidate surfaced in both retrieval rounds
                    merged_map[sc.chunk_id].score = max(merged_map[sc.chunk_id].score, sc.score) * 1.15
                    if sc.graph_context and not merged_map[sc.chunk_id].graph_context:
                        merged_map[sc.chunk_id].graph_context = sc.graph_context
                else:
                    merged_map[sc.chunk_id] = sc

            # Sort descending by updated score
            sorted_candidates = sorted(merged_map.values(), key=lambda c: c.score, reverse=True)[:top_k]

            # Re-evaluate merged candidates
            re_eval = self.evaluator.evaluate(rewritten_query, sorted_candidates)
            re_eval.rewritten_query = rewritten_query

            return CRAGPipelineResult(
                original_query=query,
                final_query=rewritten_query,
                decision=re_eval.decision if re_eval.decision == CRAGDecision.SUFFICIENT else CRAGDecision.PARTIALLY_SUFFICIENT,
                candidates=sorted_candidates,
                evaluation=re_eval,
                secondary_retrieval_performed=True,
                clarification_needed=bool(evaluation.clarification_question),
                clarification_message=evaluation.clarification_question
            )

        # Step 5: Handle INSUFFICIENT
        return CRAGPipelineResult(
            original_query=query,
            final_query=query,
            decision=CRAGDecision.INSUFFICIENT,
            candidates=initial_candidates,
            evaluation=evaluation,
            secondary_retrieval_performed=False,
            clarification_needed=True,
            clarification_message=evaluation.clarification_question or "Insufficient legal evidence in knowledge base."
        )


def get_crag_pipeline() -> CRAGPipeline:
    return CRAGPipeline()
