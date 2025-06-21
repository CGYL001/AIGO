"""
Test direct imports of core modules without packaging.
"""
import sys
import os
from pathlib import Path
import importlib

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
print(f"Adding {project_root} to sys.path")
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("sys.path:", sys.path)

# Check if aigo directory exists
aigo_dir = project_root / "aigo"
print(f"\nChecking if {aigo_dir} exists: {aigo_dir.exists()}")
if aigo_dir.exists():
    init_file = aigo_dir / "__init__.py"
    print(f"Checking if {init_file} exists: {init_file.exists()}")
    if init_file.exists():
        try:
            with open(init_file, "r") as f:
                print(f"Content of {init_file}:")
                print(f.read())
        except Exception as e:
            print(f"Error reading {init_file}: {e}")

# Try direct imports
print("\nTrying direct imports...")

try:
    import aigo
    print(f"✓ Successfully imported aigo from {aigo.__file__}")
    print(f"  Version: {aigo.__version__}")
except Exception as e:
    print(f"✗ Failed to import aigo: {e}")
    print(f"  Detailed traceback: {e.__class__.__name__}: {e}")
    
try:
    # Try to import using importlib
    print("\nTrying importlib.import_module...")
    aigo_module = importlib.import_module("aigo")
    print(f"✓ Successfully imported aigo using importlib from {aigo_module.__file__}")
except Exception as e:
    print(f"✗ Failed to import aigo using importlib: {e}")

try:
    from aigo.models.base import ModelConfig, BaseModelRunner
    print("✓ Successfully imported aigo.models.base")
except Exception as e:
    print(f"✗ Failed to import aigo.models.base: {e}")
    
try: 
    from aigo.models.providers import ollama_runner
    print("✓ Successfully imported aigo.models.providers.ollama_runner")
except Exception as e:
    print(f"✗ Failed to import aigo.models.providers.ollama_runner: {e}")
    
try: 
    from aigo.models.providers import openai_runner
    print("✓ Successfully imported aigo.models.providers.openai_runner")
except Exception as e:
    print(f"✗ Failed to import aigo.models.providers.openai_runner: {e}")
    
try:
    from aigo.models.manager import ModelManager
    print("✓ Successfully imported aigo.models.manager")
except Exception as e:
    print(f"✗ Failed to import aigo.models.manager: {e}")

# Let's check if the module files exist
print("\nChecking if module files exist...")
base_path = project_root / "aigo" / "models" / "base.py"
print(f"aigo/models/base.py exists: {base_path.exists()}")

ollama_path = project_root / "aigo" / "models" / "providers" / "ollama_runner.py"
print(f"aigo/models/providers/ollama_runner.py exists: {ollama_path.exists()}")

openai_path = project_root / "aigo" / "models" / "providers" / "openai_runner.py"
print(f"aigo/models/providers/openai_runner.py exists: {openai_path.exists()}")

manager_path = project_root / "aigo" / "models" / "manager.py"
print(f"aigo/models/manager.py exists: {manager_path.exists()}")

# Check for missing __init__.py files in the main package structure
print("\nChecking for missing __init__.py files in main package structure...")
for path in [
    "aigo",
    "aigo/models",
    "aigo/models/providers",
    "aigo/cli",
    "aigo/runtime",
    "aigo/adapters"
]:
    init_path = project_root / path / "__init__.py"
    if init_path.exists():
        print(f"✓ {path}/__init__.py exists")
    else:
        print(f"✗ {path}/__init__.py missing")

print("\nImport check complete!") 