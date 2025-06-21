#!/usr/bin/env python
"""
AIgo package setup script.
"""

import os
from setuptools import setup, find_packages

# Read version from package __init__.py
with open(os.path.join("AIGO", "__init__.py"), "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
    else:
        version = "0.1.0"  # Default if not found

# Read long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="aigo",
    version=version,
    description="AI assistant platform with modular design and multi-model support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AIgo Team",
    author_email="example@example.com",
    url="https://github.com/yourusername/AIgo",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    include_package_data=True,
    install_requires=[
        "typer>=0.9.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "api": ["fastapi>=0.100.0", "uvicorn>=0.22.0", "pydantic>=2.0.0"],
        "dev": [
            "pytest>=7.3.1",
            "black>=23.3.0",
            "ruff>=0.0.262",
            "isort>=5.12.0",
        ],
        "all": [
            "fastapi>=0.100.0", 
            "uvicorn>=0.22.0", 
            "pydantic>=2.0.0",
            "pytest>=7.3.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "aigo=AIGO.cli.__main__:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
) 