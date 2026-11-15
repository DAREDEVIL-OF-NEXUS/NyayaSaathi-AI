import pytest
from unittest.mock import MagicMock, patch
from backend.app.services.llm.base import LLMResponse, LLMUsage, ProviderType
from backend.app.services.llm.gemini import GeminiClient
from backend.app.services.llm.openrouter import OpenRouterClient
from backend.app.services.llm.fallback import MockLLMClient

def test_mock_llm_client():
    client = MockLLMClient(canned_response="Hello Consumer", canned_json={"key": "val"})
    res = client.generate("test prompt", json_mode=True)
    assert isinstance(res, LLMResponse)
    assert res.content == "Hello Consumer"
    assert res.parsed_json == {"key": "val"}
    assert res.provider == ProviderType.MOCK.value

def test_gemini_missing_api_key():
    client = GeminiClient(api_key="")
    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        client.generate("test prompt")

@patch("backend.app.services.llm.gemini.genai.GenerativeModel")
def test_gemini_successful_generation(mock_model_cls):
    mock_instance = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = '{"summary": "Defective goods legal remedy"}'
    mock_resp.usage_metadata.prompt_token_count = 15
    mock_resp.usage_metadata.candidates_token_count = 25
    mock_resp.usage_metadata.total_token_count = 40
    mock_instance.generate_content.return_value = mock_resp
    mock_model_cls.return_value = mock_instance

    client = GeminiClient(api_key="fake-gemini-key", model_name="gemini-1.5-flash")
    resp = client.generate("Query about defective phone", json_mode=True)

    assert resp.provider == ProviderType.GEMINI.value
    assert resp.model_name == "gemini-1.5-flash"
    assert resp.parsed_json == {"summary": "Defective goods legal remedy"}
    assert resp.usage.total_tokens == 40
    assert resp.latency_ms >= 0

def test_openrouter_missing_api_key():
    client = OpenRouterClient(api_key="")
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY is not configured"):
        client.generate("test prompt")

def test_openrouter_successful_generation():
    client = OpenRouterClient(api_key="fake-openrouter-key")
    mock_sync_client = MagicMock()
    mock_resp = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"summary": "48 hour timeline"}'
    mock_resp.choices = [mock_choice]
    mock_resp.usage.prompt_tokens = 20
    mock_resp.usage.completion_tokens = 30
    mock_resp.usage.total_tokens = 50

    mock_sync_client.chat.completions.create.return_value = mock_resp
    client.sync_client = mock_sync_client

    resp = client.generate("E-commerce complaint timeline", json_mode=True)
    assert resp.provider == ProviderType.OPENROUTER.value
    assert resp.parsed_json == {"summary": "48 hour timeline"}
    assert resp.usage.total_tokens == 50
