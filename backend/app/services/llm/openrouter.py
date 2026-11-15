import time
import json
from typing import Optional, Dict, Any
from openai import OpenAI, AsyncOpenAI

from backend.app.core.config import settings
from backend.app.services.llm.base import BaseLLMClient, LLMResponse, LLMUsage, ProviderType

class OpenRouterClient(BaseLLMClient):
    """
    OpenRouter adapter using OpenAI-compatible client specifications.
    Provides flexible fallback to open-source and commercial models (Llama 3, Mistral, etc.)
    with OpenRouter ranking headers and JSON schema enforcement.
    """

    @staticmethod
    def _is_configured(key: Optional[str]) -> bool:
        if not key:
            return False
        clean = key.strip().lower()
        return not (clean.startswith("your_") or clean.startswith("change_me") or clean == "")

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key if api_key is not None else settings.OPENROUTER_API_KEY
        self.model_name = model_name or settings.OPENROUTER_MODEL
        self.base_url = base_url or settings.OPENROUTER_BASE_URL

        self.default_headers = {
            "HTTP-Referer": "https://nyayasaathi.ai",
            "X-Title": "NyayaSaathi AI Consumer Legal Assistant"
        }

        if self._is_configured(self.api_key):
            self.sync_client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                default_headers=self.default_headers,
                timeout=30.0
            )
            self.async_client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                default_headers=self.default_headers,
                timeout=30.0
            )
        else:
            self.sync_client = None
            self.async_client = None

    def _clean_json_text(self, text: str) -> str:
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
        if not self._is_configured(self.api_key) or not self.sync_client:
            raise ValueError("OPENROUTER_API_KEY is not configured or is a placeholder.")

        t0 = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self.sync_client.chat.completions.create(**kwargs)
            latency_ms = (time.time() - t0) * 1000.0

            content = response.choices[0].message.content or ""
            parsed_json = None
            if json_mode and content:
                cleaned = self._clean_json_text(content)
                try:
                    parsed_json = json.loads(cleaned)
                except Exception as ex:
                    print(f"[OpenRouterClient] JSON parse warning: {ex}. Raw content: {content[:200]}")

            usage = LLMUsage()
            if response.usage:
                usage.prompt_tokens = response.usage.prompt_tokens or 0
                usage.completion_tokens = response.usage.completion_tokens or 0
                usage.total_tokens = response.usage.total_tokens or 0

            return LLMResponse(
                content=content,
                parsed_json=parsed_json,
                provider=ProviderType.OPENROUTER.value,
                model_name=self.model_name,
                usage=usage,
                latency_ms=latency_ms
            )
        except Exception as e:
            raise RuntimeError(f"OpenRouter API invocation error: {str(e)}") from e

    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> LLMResponse:
        if not self._is_configured(self.api_key) or not self.async_client:
            raise ValueError("OPENROUTER_API_KEY is not configured or is a placeholder.")

        t0 = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self.async_client.chat.completions.create(**kwargs)
            latency_ms = (time.time() - t0) * 1000.0

            content = response.choices[0].message.content or ""
            parsed_json = None
            if json_mode and content:
                cleaned = self._clean_json_text(content)
                try:
                    parsed_json = json.loads(cleaned)
                except Exception as ex:
                    print(f"[OpenRouterClient] JSON parse warning: {ex}. Raw content: {content[:200]}")

            usage = LLMUsage()
            if response.usage:
                usage.prompt_tokens = response.usage.prompt_tokens or 0
                usage.completion_tokens = response.usage.completion_tokens or 0
                usage.total_tokens = response.usage.total_tokens or 0

            return LLMResponse(
                content=content,
                parsed_json=parsed_json,
                provider=ProviderType.OPENROUTER.value,
                model_name=self.model_name,
                usage=usage,
                latency_ms=latency_ms
            )
        except Exception as e:
            raise RuntimeError(f"OpenRouter async API invocation error: {str(e)}") from e
