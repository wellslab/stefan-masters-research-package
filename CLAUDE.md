# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Australian Stem Cell Curate - A Python package providing curation, scoring and reporting functions for the Australian Stem Cell Registry.

## Development Commands

```bash
# Install dependencies (including dev dependencies)
poetry install

# Install package in editable mode
poetry install -e .

# Add a new dependency
poetry add <package-name>

# Add a development dependency
poetry add --group dev <package-name>

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=aus_stem_cell_curate

# Build the package
poetry build

# Publish to PyPI (when ready)
poetry publish

# Run linting (when configured)
poetry run ruff check aus_stem_cell_curate/

# Format code (when configured) 
poetry run ruff format aus_stem_cell_curate/

# Enter virtual environment shell
poetry shell
```

## Package Architecture

```
aus_stem_cell_curate/
├── curation/          # Data validation and cleaning functions
├── scoring/           # Scoring algorithms and metrics
├── reporting/         # Report generation and export functions
└── utils/            # Shared utilities and common functions
```

## Public API Design

The package follows a clean API pattern:
- Main functions are exposed through `aus_stem_cell_curate/__init__.py`
- Users import directly: `from aus_stem_cell_curate import validate_data`
- Implementation details are kept in submodules
- Each submodule has its own `__init__.py` for organization

## Dependencies

The project uses OpenAI's API for curation tasks:
- **openai**: Main dependency for AI-powered curation functionality
- Configuration stored in `aus_stem_cell_curate/curation/config.json`
- API key can be set via `OPENAI_API_KEY` environment variable

## Development Workflow

1. Implement functions in appropriate submodules (e.g., `curation/validators.py`)
2. Export functions through submodule `__init__.py` files
3. Expose main user-facing functions in root `__init__.py`
4. Add tests in corresponding `tests/` directories
5. Update `__all__` lists to control public API

## Testing

Run curation tests with:
```bash
# Test SCR article curation
cd tests/test_curation/vision
python test_curate_vision.py
```

Test results are saved in UUID-named folders under `tests/test_curation/vision/results/`