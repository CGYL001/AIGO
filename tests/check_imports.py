"""
Check that the core project imports work properly.
This helps diagnose packaging and path issues.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
print(f"Adding {project_root} to sys.path")
sys.path.insert(0, str(project_root))

print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Checking import paths...")
print(f"sys.path[0]: {sys.path[0]}")
print(f"Working directory: {os.getcwd()}")

# Try to import core modules
try:
    import aigo
    print(f"✓ Successfully imported aigo from {aigo.__file__}")
    print(f"  Version: {aigo.__version__}")
except ImportError as e:
    print(f"✗ Failed to import aigo: {e}")
    print("  Trying to locate aigo package...")
    for path in sys.path:
        aigo_path = os.path.join(path, "aigo")
        if os.path.exists(aigo_path):
            print(f"  Found aigo at: {aigo_path}")
            if os.path.isfile(os.path.join(aigo_path, "__init__.py")):
                print("  ✓ Has __init__.py")
            else:
                print("  ✗ Missing __init__.py")
    
try:
    from aigo.models.base import ModelConfig, BaseModelRunner
    print("✓ Successfully imported aigo.models.base")
except ImportError as e:
    print(f"✗ Failed to import aigo.models.base: {e}")
    
try:
    from aigo.models.providers import ollama_runner
    print("✓ Successfully imported aigo.models.providers.ollama_runner")
except ImportError as e:
    print(f"✗ Failed to import aigo.models.providers.ollama_runner: {e}")
    
try:
    from aigo.models.providers import openai_runner
    print("✓ Successfully imported aigo.models.providers.openai_runner")
except ImportError as e:
    print(f"✗ Failed to import aigo.models.providers.openai_runner: {e}")
    
try:
    from aigo.models.manager import ModelManager
    print("✓ Successfully imported aigo.models.manager")
except ImportError as e:
    print(f"✗ Failed to import aigo.models.manager: {e}")

try:
    from aigo.cli.__main__ import app
    print("✓ Successfully imported aigo.cli.__main__")
except ImportError as e:
    print(f"✗ Failed to import aigo.cli.__main__: {e}")

# Check if we can run tests
try:
    import pytest
    print("✓ Successfully imported pytest")
except ImportError as e:
    print(f"✗ Failed to import pytest: {e}")

# Check for missing __init__.py files
print("\nChecking for missing __init__.py files...")
for root, dirs, files in os.walk(os.path.join(project_root, "aigo")):
    if "__pycache__" in root:
        continue
    
    rel_path = os.path.relpath(root, project_root)
    init_path = os.path.join(root, "__init__.py")
    
    if os.path.exists(init_path):
        print(f"✓ {rel_path} has __init__.py")
    else:
        print(f"✗ {rel_path} missing __init__.py")

print("\nImport check complete!") 