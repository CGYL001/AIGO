# AIgo Documentation

This directory contains the source files for AIgo documentation.

## Building the docs

To build the documentation, use the following commands:

```bash
cd docs

# Install dependencies
pip install sphinx sphinx-rtd-theme sphinxcontrib-httpdomain sphinx-autoapi

# Build HTML docs
make html
# or on Windows
make.bat html
```

The built documentation will be available in `_build/html/`.

## Live Preview

For development, you can use sphinx-autobuild for live preview:

```bash
pip install sphinx-autobuild
make livehtml
```

This will start a local server and automatically rebuild the documentation when files are changed.

## Documentation Structure

- `index.rst`: Main documentation entry point
- `api/`: API reference documentation
- `modules/`: Module documentation
- `_static/`: Static files like CSS
- `conf.py`: Sphinx configuration
