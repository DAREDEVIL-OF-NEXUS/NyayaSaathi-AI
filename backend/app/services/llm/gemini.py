import time
import json
import re
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from backend.app.core.config import settings
from backend.app.services.llm.base import BaseLLMClient, LLMResponse, LLMUsage, ProviderType

class GeminiClient(BaseLLMClient):
    """
    Google Gemini provider adapter using the official Google Generative AI SDK.
    Supports structured JSON generation, temperature tuning, and system instructions.
    """

    @staticmethod
    def _is_configured(key: Optional[str]) -> bool:
        if not key:
            return False
        clean = key.strip().lower()
        return not (clean.startswith("your_") or clean.startswith("change_me") or clean == "")

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL

        if self._is_configured(self.api_key):
            genai.configure(api_key=self.api_key)

    def _clean_json_text(self, text: str) -> str:
        """Strip markdown code fence if LLM returns ```json ... ```"""
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> LLMResponse:
        if not self._is_configured(self.api_key):
            raise ValueError("GEMINI_API_KEY is not configured or is a placeholder.")

        t0 = time.time()

        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json" if json_mode else "text/plain"
        )

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None
        )

        try:
            response = model.generate_content(prompt)
            latency_ms = (time.time() - t0) * 1000.0

            content = response.text if hasattr(response, "text") and response.text else ""
            parsed_json = None
            if json_mode and content:
                cleaned = self._clean_json_text(content)
                try:
                    parsed_json = json.loads(cleaned)
                except Exception as ex:
                    print(f"[GeminiClient] JSON parse warning: {ex}. Raw content: {content[:200]}")

            usage = LLMUsage()
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage.prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                usage.completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                usage.total_tokens = getattr(response.usage_metadata, "total_token_count", 0) or 0

            return LLMResponse(
                content=content,
                parsed_json=parsed_json,
                provider=ProviderType.GEMINI.value,
                model_name=self.model_name,
                usage=usage,
                latency_ms=latency_ms
            )
        except Exception as e:
            raise RuntimeError(f"Gemini API invocation error: {str(e)}") from e

    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> LLMResponse:
        if not self._is_configured(self.api_key):
            raise ValueError("GEMINI_API_KEY is not configured or is a placeholder.")

        t0 = time.time()

        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json" if json_mode else "text/plain"
        )

        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=system_prompt if system_prompt else None
        )

        try:
            response = await model.generate_content_async(prompt)
            latency_ms = (time.time() - t0) * 1000.0

            content = response.text if hasattr(response, "text") and response.text else ""
            parsed_json = None
            if json_mode and content:
                cleaned = self._clean_json_text(content)
                try:
                    parsed_json = json.loads(cleaned)
                except Exception as ex:
                    print(f"[GeminiClient] JSON parse warning: {ex}. Raw content: {content[:200]}")

            usage = LLMUsage()
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage.prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                usage.completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                usage.total_tokens = getattr(response.usage_metadata, "total_token_count", 0) or 0

            return LLMResponse(
                content=content,
                parsed_json=parsed_json,
                provider=ProviderType.GEMINI.value,
                model_name=self.model_name,
                usage=usage,
                latency_ms=latency_ms
            )
        except Exception as e:
            raise RuntimeError(f"Gemini async API invocation error: {str(e)}") from e
