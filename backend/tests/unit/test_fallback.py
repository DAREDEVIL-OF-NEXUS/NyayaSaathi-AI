import pytest
from unittest.mock import MagicMock
from backend.app.services.llm.base import LLMResponse, LLMUsage, ProviderType
from backend.app.services.llm.fallback import ResilientLLMManager

def test_primary_provider_success():
    mock_primary = MagicMock()
    mock_primary.generate.return_value = LLMResponse(
        content="Primary Success",
        parsed_json={"ans": "gemini"},
        provider=ProviderType.GEMINI.value,
        model_name="gemini-1.5-flash"
    )

    mock_fallback = MagicMock()

    manager = ResilientLLMManager(
        primary_provider="gemini",
        fallback_provider="openrouter",
        primary_client=mock_primary,
        fallback_client=mock_fallback
    )

    res = manager.generate("Hello")
    assert res.content == "Primary Success"
    assert res.provider == ProviderType.GEMINI.value
    mock_primary.generate.assert_called_once()
    mock_fallback.generate.assert_not_called()

def test_fallback_trigger_on_primary_failure():
    mock_primary = MagicMock()
    mock_primary.generate.side_effect = RuntimeError("Gemini Quota Exceeded 429")

    mock_fallback = MagicMock()
    mock_fallback.generate.return_value = LLMResponse(
        content="Fallback Success",
        parsed_json={"ans": "openrouter"},
        provider=ProviderType.OPENROUTER.value,
        model_name="meta-llama/llama-3.1-8b-instruct"
    )

    manager = ResilientLLMManager(
        primary_provider="gemini",
        fallback_provider="openrouter",
        primary_client=mock_primary,
        fallback_client=mock_fallback
    )

    res = manager.generate("Hello after failure")
    assert res.content == "Fallback Success"
    assert res.provider == ProviderType.OPENROUTER.value
    mock_primary.generate.assert_called_once()
    mock_fallback.generate.assert_called_once()

def test_all_providers_failure():
    mock_primary = MagicMock()
    mock_primary.generate.side_effect = RuntimeError("Gemini 500 Server Error")

    mock_fallback = MagicMock()
    mock_fallback.generate.side_effect = RuntimeError("OpenRouter 401 Unauthorized")

    manager = ResilientLLMManager(
        primary_provider="gemini",
        fallback_provider="openrouter",
        primary_client=mock_primary,
        fallback_client=mock_fallback
    )

    with pytest.raises(RuntimeError, match="All LLM providers failed"):
        manager.generate("Hello when all fail")
