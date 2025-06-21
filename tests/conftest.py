"""
Global pytest fixtures and configuration.
Ensures that 'aigo' package is available for all tests.
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Print debugging information
print(f"Python executable: {sys.executable}")
print(f"sys.path: {sys.path}")
print(f"Current directory: {os.getcwd()}")
print(f"ROOT directory: {ROOT}")

# Explicitly try to import aigo
try:
    import aigo
    print(f"Successfully imported aigo from {aigo.__file__}")
except ImportError as e:
    print(f"Failed to import aigo: {e}")

# Set environment variables for testing
os.environ["AIGO_ENV"] = "test"

# Common fixtures can be defined here
import pytest

@pytest.fixture
def sample_config():
    """Return a sample configuration for testing."""
    return {
        "name": "test-model",
        "provider": "test",
        "model_path": "test/path"
    }

@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path 