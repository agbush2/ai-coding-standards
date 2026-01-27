# Python Security Standards
Implementation of: /security_standards.md

## Relationship to Standards
This file provides the Python-specific implementation ("How") for the security controls and requirements defined in `/security_standards.md` ("What").

## Tools
- **SAST**: `bandit` (configured in `ruff` as `S` rules or standalone).
- **SCA**: `pip-audit` or `safety`.

## Cryptography
- **Hashing**: `hashlib.sha256`.
- **Passwords**: `passlib` with `bcrypt` or `argon2`.

## Web Security (FastAPI/Starlette)
- **Middleware**: `TrustedHostMiddleware`, `CORSMiddleware` (restrict origins).
- **Input**: Pydantic models for all request bodies.

## Secrets
- **Loading**: `pydantic-settings`.
- **Pattern**:
  ```python
  from pydantic_settings import BaseSettings
  class Settings(BaseSettings):
      db_password: str  # Will load from DB_PASSWORD env var
  ```

## Dependency Vulnerability Scanning
- **CI Requirement**: All CI pipelines must include a step to scan for known vulnerabilities in dependencies using `pip-audit` or `safety`.
- **Example**:
  ```yaml
  - run: poetry run pip-audit
  ```
