from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel, Field

class ProviderType(str, Enum):
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    MOCK = "mock"

class LLMUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class LLMResponse(BaseModel):
    content: str
    parsed_json: Optional[Dict[str, Any]] = None
    provider: str
    model_name: str
    usage: LLMUsage = Field(default_factory=LLMUsage)
    latency_ms: float = 0.0

class BaseLLMClient(ABC):
    """
    Abstract interface for LLM provider adapters.
    Ensures uniform prompt execution, JSON parsing, error isolation, and usage tracking.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> LLMResponse:
        """Execute a synchronous LLM completion request."""
        pass

    @abstractmethod
    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> LLMResponse:
        """Execute an asynchronous LLM completion request."""
        pass
