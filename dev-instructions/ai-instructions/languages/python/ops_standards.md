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

## Dependency Pinning
- **Lock Files**: Always commit `poetry.lock` or `requirements.txt` with hashes to ensure reproducible builds.
- **Review**: Regularly update and review dependencies for security and compatibility.

## CI Example: GitHub Actions Workflow
```yaml
name: Python CI
on: [push, pull_request]
jobs:
	build:
		runs-on: ubuntu-latest
		steps:
			- uses: actions/checkout@v3
			- uses: actions/setup-python@v4
				with:
					python-version: '3.12'
			- run: pip install poetry
			- run: poetry install
			- run: poetry run ruff check .
			- run: poetry run mypy src
			- run: poetry run pytest --cov=src
			- run: poetry run bandit -r src
```
