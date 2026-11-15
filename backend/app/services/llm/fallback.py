import logging
from typing import Optional, Dict, Any, List
from backend.app.core.config import settings
from backend.app.services.llm.base import BaseLLMClient, LLMResponse, LLMUsage, ProviderType
from backend.app.services.llm.gemini import GeminiClient
from backend.app.services.llm.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)

DEFAULT_MOCK_LEGAL_JSON = {
    "summary": "According to the Consumer Protection Act, 2019 and E-Commerce Rules, 2020, consumers have statutory remedies against defective products and deficient services.",
    "applicable_laws": [
        {
            "act_or_regulation": "Consumer Protection (E-Commerce) Rules, 2020",
            "section_or_rule": "Rule 4 & 5",
            "provision_title": "Duties of e-commerce entities",
            "summary_of_relevance": "Mandates transparent return and refund policies for e-commerce entities."
        }
    ],
    "consumer_rights": ["Right to be protected against unfair trade practices", "Right to seek redressal"],
    "recommended_steps": [
        "Lodge an official grievance on National Consumer Helpline (NCH) portal or call 1915.",
        "Issue a formal legal notice to the opposite party demanding resolution within 15 days.",
        "File a consumer complaint on e-Daakhil / e-Jagriti portal if unresolved."
    ],
    "appropriate_forums": [
        {
            "forum_name": "District Consumer Disputes Redressal Commission",
            "pecuniary_jurisdiction": "Up to Rs 50,00,000",
            "filing_procedure": "File via e-Daakhil portal or submit physical complaint under Section 35.",
            "official_portal_or_contact": "https://edaakhil.nic.in"
        }
    ],
    "required_documents": [
        "Invoice / receipt of transaction",
        "Order confirmation and payment proof",
        "Correspondence with seller / merchant"
    ],
    "statutory_timelines": [
        "Limitation period of 2 years from date of cause of action (Section 69, CPA 2019)"
    ],
    "disclaimer": "This information is generated for educational purposes and does not constitute formal legal representation."
}

class MockLLMClient(BaseLLMClient):
    """
    Hermetic Mock LLM for offline testing and deterministic verification.
    """

    def __init__(self, canned_response: Optional[str] = None, canned_json: Optional[Dict[str, Any]] = None):
        self.canned_response = canned_response or "This is a deterministic mock response from NyayaSaathi AI."
        self.canned_json = canned_json or DEFAULT_MOCK_LEGAL_JSON

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> LLMResponse:
        return LLMResponse(
            content=self.canned_response,
            parsed_json=self.canned_json if json_mode else None,
            provider=ProviderType.MOCK.value,
            model_name="mock-model-v1",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            latency_ms=1.5
        )

    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> LLMResponse:
        return self.generate(prompt, system_prompt, json_mode, temperature, max_tokens)


class ResilientLLMManager:
    """
    Resilient LLM Manager implementing circuit failover between primary (Gemini)
    and fallback (OpenRouter) providers.
    """

    def __init__(
        self,
        primary_provider: Optional[str] = None,
        fallback_provider: Optional[str] = None,
        primary_client: Optional[BaseLLMClient] = None,
        fallback_client: Optional[BaseLLMClient] = None
    ):
        self.primary_name = primary_provider or settings.LLM_PRIMARY_PROVIDER
        self.fallback_name = fallback_provider or settings.LLM_FALLBACK_PROVIDER

        self.primary_client = primary_client or self._build_client(self.primary_name)
        self.fallback_client = fallback_client or self._build_client(self.fallback_name)

    def _build_client(self, provider_name: str) -> BaseLLMClient:
        provider_name = provider_name.lower().strip()
        if provider_name == ProviderType.GEMINI.value:
            return GeminiClient()
        elif provider_name == ProviderType.OPENROUTER.value:
            return OpenRouterClient()
        elif provider_name == ProviderType.MOCK.value:
            return MockLLMClient()
        else:
            raise ValueError(f"Unsupported LLM provider: '{provider_name}'")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> LLMResponse:
        """
        Execute request on primary provider. Upon failure, seamlessly fail over to fallback.
        """
        primary_err = None
        try:
            return self.primary_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=json_mode,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            primary_err = e
            logger.warning(
                f"[ResilientLLMManager] Primary provider '{self.primary_name}' failed: {e}. "
                f"Triggering fallback provider '{self.fallback_name}'..."
            )

        if not self.fallback_client:
            raise RuntimeError(f"Primary provider '{self.primary_name}' failed and no fallback configured: {primary_err}")

        try:
            return self.fallback_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=json_mode,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as fallback_err:
            if settings.APP_ENV in ["test", "development"] and (
                "not configured" in str(primary_err).lower() or "placeholder" in str(primary_err).lower()
            ) and (
                "not configured" in str(fallback_err).lower() or "placeholder" in str(fallback_err).lower()
            ):
                logger.warning(
                    "[ResilientLLMManager] Both primary and fallback keys unconfigured in dev/test environment. "
                    "Serving safe fallback mock response."
                )
                return MockLLMClient().generate(prompt, system_prompt, json_mode, temperature, max_tokens)

            raise RuntimeError(
                f"All LLM providers failed. Primary ('{self.primary_name}') error: {primary_err}; "
                f"Fallback ('{self.fallback_name}') error: {fallback_err}"
            ) from fallback_err

    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> LLMResponse:
        primary_err = None
        try:
            return await self.primary_client.generate_async(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=json_mode,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            primary_err = e
            logger.warning(
                f"[ResilientLLMManager] Primary provider '{self.primary_name}' failed async: {e}. "
                f"Triggering fallback provider '{self.fallback_name}'..."
            )

        if not self.fallback_client:
            raise RuntimeError(f"Primary provider '{self.primary_name}' failed and no fallback configured: {primary_err}")

        try:
            return await self.fallback_client.generate_async(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=json_mode,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as fallback_err:
            if settings.APP_ENV in ["test", "development"] and (
                "not configured" in str(primary_err).lower() or "placeholder" in str(primary_err).lower()
            ) and (
                "not configured" in str(fallback_err).lower() or "placeholder" in str(fallback_err).lower()
            ):
                logger.warning(
                    "[ResilientLLMManager] Both primary and fallback keys unconfigured in dev/test environment. "
                    "Serving safe async fallback mock response."
                )
                return await MockLLMClient().generate_async(prompt, system_prompt, json_mode, temperature, max_tokens)

            raise RuntimeError(
                f"All LLM providers failed. Primary ('{self.primary_name}') async error: {primary_err}; "
                f"Fallback ('{self.fallback_name}') async error: {fallback_err}"
            ) from fallback_err


_global_llm_manager = None

def get_llm_manager() -> ResilientLLMManager:
    global _global_llm_manager
    if _global_llm_manager is None:
        _global_llm_manager = ResilientLLMManager()
    return _global_llm_manager
