# Security Standards (The "What")
Applies to: All Codebases

## Purpose
Enforce a secure baseline aligned with OWASP Top 10 and NIST CSF.

## 1. Authentication & Authorization
- **Identity**: Use established IdPs (OAuth2/OIDC).
- **Tokens**: Short-lived access tokens; secure refresh token storage.
- **Enforcement**: Validate tokens at the service boundary.

## 2. Secrets Management
- **Prohibition**: NO secrets in code or VCS.
- **Injection**: Use environment variables or secret managers (Vault, AWS Secrets Manager, Azure Key Vault).
- **Rotation**: Support automated rotation.

## 3. Input Validation
- **Sanitization**: Validate all inputs against strict schemas.
- **Encoding**: Encode output to prevent XSS/Injection.

## 4. Cryptography
- **Transit**: TLS 1.2+ for all communications.
- **Rest**: Encryption at rest for all persistent data.
- **Algorithms**: Use only standard, vetted algorithms (AES-256, SHA-256+). No custom crypto.

## 5. Supply Chain
- **Vetting**: Use only approved/popular packages.
- **SCA**: Software Composition Analysis is mandatory in CI.
- **SBOM**: Generate Software Bill of Materials for every release.

## 6. Logging & Privacy
- **No PII**: Do not log Personally Identifiable Information.
- **Sanitization**: Mask sensitive fields (tokens, passwords) in logs.
