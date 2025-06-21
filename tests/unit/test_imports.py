"""
Test basic imports to verify the package structure is correct.
"""
import pytest

def test_aigo_imports():
    """Test that basic imports from aigo package work."""
    import aigo
    assert hasattr(aigo, "__version__")

def test_core_modules_exist():
    """Test that core modules are accessible."""
    from importlib import import_module
    
    # Test core subpackage imports
    modules = [
        "aigo.modules",
        "aigo.adapters",
        "aigo.runtime",
        "aigo.cli"
    ]
    
    for module_name in modules:
        module = import_module(module_name)
        assert module is not None 