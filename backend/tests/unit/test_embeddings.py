import pytest
import numpy as np
from unittest.mock import MagicMock
from backend.app.services.rag.embeddings import EmbeddingService

def test_prefix_enforcement_logic():
    """
    Test that passages get 'passage: ' and queries get 'query: ' prefix
    without depending on model download during unit test.
    """
    service = EmbeddingService.__new__(EmbeddingService)
    mock_model = MagicMock()
    # Mock encode returning dummy 384-dim normalized array
    dummy_vec = np.ones((2, 384), dtype=np.float32)
    dummy_vec = dummy_vec / np.linalg.norm(dummy_vec, axis=1, keepdims=True)
    mock_model.encode.return_value = dummy_vec
    service._model = mock_model

    # Test embed_passages
    passages = ["Section 28 details.", "Section 35 complaints."]
    results = service.embed_passages(passages)

    mock_model.encode.assert_called_once()
    called_args, called_kwargs = mock_model.encode.call_args
    passed_texts = called_args[0]
    assert passed_texts == ["passage: Section 28 details.", "passage: Section 35 complaints."]
    assert called_kwargs.get("normalize_embeddings") is True
    assert len(results) == 2

    # Test embed_query
    mock_model.reset_mock()
    query_dummy = np.ones((1, 384), dtype=np.float32)
    query_dummy = query_dummy / np.linalg.norm(query_dummy, axis=1, keepdims=True)
    mock_model.encode.return_value = query_dummy

    q_result = service.embed_query("What is the pecuniary jurisdiction of District Commission?")
    mock_model.encode.assert_called_once()
    called_args, called_kwargs = mock_model.encode.call_args
    passed_query = called_args[0]
    assert passed_query == ["query: What is the pecuniary jurisdiction of District Commission?"]
    assert called_kwargs.get("normalize_embeddings") is True
    assert len(q_result) == 384

def test_empty_passages():
    service = EmbeddingService.__new__(EmbeddingService)
    service._model = MagicMock()
    assert service.embed_passages([]) == []
