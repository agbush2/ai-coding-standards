# Python Forbidden Patterns
Implementation of: /forbidden_patterns.md

## Relationship to Standards
This file provides the Python-specific implementation ("How") for the universally forbidden patterns defined in `/forbidden_patterns.md` ("What").


## Strictly Forbidden
- **Pickle**: `pickle.load`, `pickle.dump`. Use JSON.
- **Shell Execution**: `subprocess.run(..., shell=True)`, `os.system`.
- **Mutable Defaults**: `def foo(x=[])`. Use `x: list | None = None`.
- **Bare Except**: `except:`. Use `except Exception:` at minimum, prefer specific.
- **Print Logging**: `print()`. Use `logging` or `structlog`.
- **Sync Requests**: `requests` library in async code. Use `httpx`.
- **Eval**: `eval()`, `exec()`.
- **os.environ for Secrets**: Do not access secrets directly via `os.environ`. Use `pydantic-settings` or a secure configuration manager.
- **assert for Runtime Checks**: Do not use `assert` for runtime validation in production code. Use explicit error handling (e.g., `raise ValueError`).

## Library Constraints
- **Date/Time**: No `datetime.now()` without timezone. Use `datetime.now(timezone.utc)`.
- **Random**: No `random` for security tokens. Use `secrets`.
