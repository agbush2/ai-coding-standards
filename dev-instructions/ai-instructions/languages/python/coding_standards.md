# Python Coding Standards
Implementation of: /master_standards.md

## Relationship to Standards
This file provides the Python-specific implementation ("How") for the general coding and style guidelines defined in `/master_standards.md` ("What").

## Interpreter
- **Version**: Python 3.12+
- **Async**: Prefer `asyncio` for I/O bound tasks.

## Style & Formatting
- **Formatter**: `black` (via `ruff` or standalone).
- **Linter**: `ruff`.
- **Imports**: Sorted by `isort` (or `ruff`). Absolute imports preferred.

## Type Annotations
- **Mandatory**: All public functions/methods.
- **Tool**: `mypy` (strict mode).
- **Syntax**: Use `|` for unions (PEP 604).
- **Generics**: Use `list[str]`, `dict[str, int]` (PEP 585).
- **Pydantic**: Use Pydantic V2 (`model_validator`, `field_validator`).

## Exception Handling
- **Base Class**: Inherit from `BaseServiceException`.
- **Forbidden**: Do not raise bare `Exception` or `ValueError`.
- **Catching**: Catch specific exceptions. Avoid `except Exception:` unless logging/re-raising.

## Project Layout
```text
src/
  <package>/
    __init__.py
    api/
    core/
    services/
    db/
    tests/
pyproject.toml
README.md
```
