"""
Test relative imports to debug import issues.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"Python executable: {sys.executable}")
print(f"sys.path: {sys.path}")
print(f"Current directory: {os.getcwd()}")

# Try to import now
try:
    import aigo
    print(f"Successfully imported aigo from {aigo.__file__}")
except ImportError as e:
    print(f"Failed to import aigo: {e}")

# Check directory structure
print(f"Project root: {project_root}")
print(f"aigo directory exists: {(project_root / 'aigo').exists()}")
print("Listing aigo directory contents:")
for item in (project_root / "aigo").iterdir():
    print(f"  {item.name}")
    
# Try direct import using file path
print("\nTrying absolute file path import:")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("aigo", project_root / "aigo" / "__init__.py")
    aigo_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aigo_module)
    print(f"Successfully loaded aigo from file: {aigo_module}")
except Exception as e:
    print(f"Failed to load aigo from file: {e}")

def test_dummy():
    """Dummy test to ensure pytest runs this file."""
    assert True 