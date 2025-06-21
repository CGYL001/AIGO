"""
Tests for the OpenAI model adapter.

Note: These tests mock the OpenAI API calls to avoid actual API requests.
"""
import sys
import os
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

# Add the project root to sys.path for direct imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from aigo.models.base import ModelConfig
from aigo.models.providers.openai_runner import OpenAIModelRunner


@pytest.fixture
def mock_responses():
    """Create mock responses for API calls."""
    models_response = MagicMock()
    models_response.status_code = 200
    models_response.json.return_value = {
        "object": "list",
        "data": [
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai"
            },
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882411,
                "owned_by": "openai"
            }
        ]
    }
    
    completion_response = MagicMock()
    completion_response.status_code = 200
    completion_response.json.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the mock API."
                },
                "finish_reason": "stop",
                "index": 0
            }
        ]
    }
    
    embedding_response = MagicMock()
    embedding_response.status_code = 200
    embedding_response.json.return_value = {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "index": 0
            }
        ],
        "model": "text-embedding-3-small"
    }
    
    return {
        "models": models_response,
        "completion": completion_response,
        "embedding": embedding_response
    }


@pytest.fixture
def openai_config():
    """Create a test config for OpenAI."""
    return ModelConfig(
        provider="openai",
        model_name="gpt-3.5-turbo",
        api_key="test-api-key"
    )


@patch("requests.get")
def test_openai_load(mock_get, openai_config, mock_responses):
    """Test OpenAI adapter initialization and loading."""
    mock_get.return_value = mock_responses["models"]
    
    runner = OpenAIModelRunner(openai_config)
    assert runner.api_key == "test-api-key"
    assert runner.model == "gpt-3.5-turbo"
    assert runner.is_loaded == False
    
    # Test loading
    runner.load()
    mock_get.assert_called_once()
    assert "Bearer test-api-key" in mock_get.call_args[1]["headers"]["Authorization"]
    assert runner.is_loaded


@patch("requests.post")
def test_openai_generate(mock_post, openai_config, mock_responses):
    """Test text generation with OpenAI adapter."""
    mock_post.return_value = mock_responses["completion"]
    
    runner = OpenAIModelRunner(openai_config)
    # Skip loading by setting _is_loaded directly
    runner._is_loaded = True
    
    response = runner.generate("Hello, world!")
    
    # Check that the API was called correctly
    mock_post.assert_called_once()
    assert mock_post.call_args[0][0].endswith("/chat/completions")
    
    # Check request payload
    payload = mock_post.call_args[1]["json"]
    assert payload["model"] == "gpt-3.5-turbo"
    assert payload["messages"][0]["content"] == "Hello, world!"
    
    # Check response parsing
    assert response == "This is a test response from the mock API."


@patch("requests.post")
def test_openai_embed(mock_post, openai_config, mock_responses):
    """Test embedding generation with OpenAI adapter."""
    mock_post.return_value = mock_responses["embedding"]
    
    runner = OpenAIModelRunner(openai_config)
    # Skip loading
    runner._is_loaded = True
    
    # Test single string embedding
    embedding = runner.embed("Test text")
    
    # Check API call
    mock_post.assert_called_once()
    assert mock_post.call_args[0][0].endswith("/embeddings")
    
    # Check payload
    payload = mock_post.call_args[1]["json"]
    assert payload["input"] == ["Test text"]
    assert payload["model"] == "text-embedding-3-small"
    
    # Check result
    assert embedding == [0.1, 0.2, 0.3, 0.4, 0.5]


def test_openai_missing_api_key():
    """Test error handling for missing API key."""
    with pytest.raises(ValueError) as excinfo:
        config = ModelConfig(
            provider="openai",
            model_name="gpt-3.5-turbo"
        )
        
        # Clear env var if it exists to ensure consistent test
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            runner = OpenAIModelRunner(config)
    
    assert "API key" in str(excinfo.value) 