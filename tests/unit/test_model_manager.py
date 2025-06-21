"""
Tests for the model manager module.
"""
import sys
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to sys.path for direct imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from aigo.models.manager import ModelManager
from aigo.models.base import ModelConfig


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / "aigo_config"
    config_dir.mkdir()
    return config_dir


def test_model_manager_init(temp_config_dir):
    """Test ModelManager initialization with empty config."""
    manager = ModelManager(config_dir=temp_config_dir)
    
    # Config directory should be created
    assert temp_config_dir.exists()
    
    # Default configs should be created
    config_file = temp_config_dir / "models.json"
    assert config_file.exists()
    
    # Should contain default models
    with open(config_file, "r") as f:
        configs = json.load(f)
    
    assert "ollama:deepseek-r1" in configs
    assert "openai:gpt-3.5-turbo" in configs


def test_list_models(temp_config_dir):
    """Test listing available models."""
    manager = ModelManager(config_dir=temp_config_dir)
    models = manager.list_models()
    
    # Should have at least the default models
    assert len(models) >= 2
    
    # Check model format
    for model in models:
        assert "id" in model
        assert "name" in model
        assert "provider" in model


def test_add_and_remove_model(temp_config_dir):
    """Test adding and removing models."""
    manager = ModelManager(config_dir=temp_config_dir)
    
    # Add a new model
    test_model = "test:model"
    manager.add_model(
        model_id=test_model,
        provider="test",
        model_name="model",
        description="Test model"
    )
    
    # Verify it was added
    models = manager.list_models()
    assert any(m["id"] == test_model for m in models)
    
    # Get the config
    config = manager.get_model_config(test_model)
    assert config.provider == "test"
    assert config.model_name == "model"
    
    # Remove the model
    result = manager.remove_model(test_model)
    assert result == True
    
    # Verify it was removed
    models = manager.list_models()
    assert not any(m["id"] == test_model for m in models)
    
    # Try to remove a non-existent model
    result = manager.remove_model("nonexistent")
    assert result == False


@patch("aigo.models.base.get_model_runner")
def test_get_model_runner(mock_get_runner, temp_config_dir):
    """Test getting a model runner."""
    # Create a mock runner
    mock_runner = MagicMock()
    mock_get_runner.return_value = mock_runner
    
    manager = ModelManager(config_dir=temp_config_dir)
    
    # Get the runner for a default model
    runner = manager.get_model_runner("ollama:deepseek-r1")
    
    # Verify the runner is the mock
    assert runner == mock_runner
    
    # Verify the runner is cached
    assert "ollama:deepseek-r1" in manager._runners_cache
    
    # Call again, should return the cached runner
    mock_get_runner.reset_mock()
    runner2 = manager.get_model_runner("ollama:deepseek-r1")
    assert runner2 == mock_runner
    mock_get_runner.assert_not_called()  # Should not be called again


def test_get_model_config_not_found(temp_config_dir):
    """Test error handling for models not found."""
    manager = ModelManager(config_dir=temp_config_dir)
    
    # Try to get a non-existent model
    with pytest.raises(ValueError) as excinfo:
        manager.get_model_config("nonexistent")
    
    # Check error message
    error_msg = str(excinfo.value)
    assert "not found" in error_msg
    assert "nonexistent" in error_msg


def test_update_model(temp_config_dir):
    """Test updating a model configuration."""
    manager = ModelManager(config_dir=temp_config_dir)
    
    # Get initial config
    config = manager.get_model_config("ollama:deepseek-r1")
    original_api_base = config.api_base
    
    # Update the model
    config = manager.update_model(
        "ollama:deepseek-r1",
        api_base="http://new-url:11434"
    )
    
    # Verify it was updated
    assert config.api_base == "http://new-url:11434"
    
    # Reload manager to verify persistence
    manager = ModelManager(config_dir=temp_config_dir)
    config = manager.get_model_config("ollama:deepseek-r1")
    assert config.api_base == "http://new-url:11434" 