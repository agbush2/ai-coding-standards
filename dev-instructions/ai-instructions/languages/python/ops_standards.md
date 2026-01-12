# Python Operations Standards
Implementation of: /ops_standards.md

## Relationship to Standards
This file provides the Python-specific implementation ("How") for the operations and CI/CD requirements defined in `/ops_standards.md` ("What").

## Build System
- **Manager**: `poetry` or `uv` (preferred) or `pip` + `requirements.txt`.
- **Artifact**: Python Wheel (`.whl`) and Docker Image.

## CI Jobs (GitHub Actions Example)
- **Lint**: `ruff check .`
- **Format**: `ruff format --check .`
- **Type Check**: `mypy src`
- **Test**: `pytest --cov=src`
- **Security**: `bandit -r src`

## Docker Optimization
- Use multi-stage builds.
- Use `python:3.12-slim` or `distroless`.
- Don't run as root.
