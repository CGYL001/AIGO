"""
Tests for the base model abstractions.
"""
import sys
import os
from pathlib import Path

# Add the project root to sys.path for direct imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now do the imports
import pytest
try:
    from aigo.models.base import BaseModelRunner, ModelConfig, register_model
except ImportError:
    # Fallback approach using absolute paths
    import importlib.util
    
    # Load base module using file path
    spec = importlib.util.spec_from_file_location(
        "aigo.models.base", 
        project_root / "aigo" / "models" / "base.py"
    )
    base_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base_module)
    
    # Extract the classes from the module
    BaseModelRunner = base_module.BaseModelRunner
    ModelConfig = base_module.ModelConfig
    register_model = base_module.register_model


def test_model_config():
    """Test ModelConfig initialization and masking."""
    config = ModelConfig(
        provider="test",
        model_name="test-model",
        api_key="secret-key",
        device="cpu"
    )
    
    assert config.provider == "test"
    assert config.model_name == "test-model"
    assert config.device == "cpu"
    assert config.api_key == "secret-key"
    
    # Test string representation masks API key
    str_repr = str(config)
    assert "test-model" in str_repr
    assert "secret-key" not in str_repr
    assert "***" in str_repr


def test_model_registry():
    """Test model registration and retrieval."""
    
    # Create a test model class
    @register_model("test-runner")
    class TestRunner(BaseModelRunner):
        name = "test-runner"
        
        @classmethod
        def supports(cls, config):
            return config.provider == "test"
            
        def load(self):
            self._is_loaded = True
            
        def generate(self, prompt, **kwargs):
            return f"Test response for: {prompt}"
    
    # Create a config that should match our runner
    config = ModelConfig(provider="test", model_name="any-model")
    
    # Import the function that looks up runners
    try:
        from aigo.models.base import get_model_runner
    except ImportError:
        get_model_runner = base_module.get_model_runner
    
    # Get a runner instance
    runner = get_model_runner(config)
    
    # Verify it's the right type
    assert isinstance(runner, TestRunner)
    assert runner.config.provider == "test"
    assert runner.config.model_name == "any-model"
    
    # Test the functionality
    runner.load()
    assert runner.is_loaded
    response = runner.generate("hello")
    assert response == "Test response for: hello"


def test_unsupported_model():
    """Test error handling for unsupported models."""
    try:
        from aigo.models.base import get_model_runner
    except ImportError:
        get_model_runner = base_module.get_model_runner
    
    config = ModelConfig(provider="nonexistent", model_name="unknown")
    
    with pytest.raises(ValueError) as excinfo:
        get_model_runner(config)
        
    # Check error message
    error_msg = str(excinfo.value)
    assert "No model runner found" in error_msg
    assert "nonexistent" in error_msg 