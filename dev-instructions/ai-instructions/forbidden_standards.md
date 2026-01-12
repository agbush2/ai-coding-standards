# Universal Forbidden Patterns (The "What")
Applies to: All Languages

## Security
- **Hardcoded Secrets**: NEVER commit keys, passwords, or tokens.
- **Dynamic Execution**: No `eval` or equivalent dynamic code execution with user input.
- **Weak Hashing**: No MD5 or SHA1.
- **Insecure Random**: Use cryptographically secure random number generators for security contexts.

## Reliability
- **Swallowing Errors**: Do not catch generic exceptions without handling or logging.
- **Global State**: Avoid mutable global state.
- **Tautological Tests**: Tests that always pass (e.g., `assert True`).

## Operations
- **Console Logging**: Do not use `print` or `console.log` for production logging. Use a structured logger.
