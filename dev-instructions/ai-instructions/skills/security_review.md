---
**Skill Name**: Security Review  
**Version**: 1.0 (2026-02-02)  
**Persona(s)**: Developer, Quality Engineer, Product Manager  
**Description**:  
Perform a practical security pass focusing on trust boundaries, authz/authn, input validation, secret handling, and common injection vectors.

**Usage Example**:
```prompt
Perform a security review with a Zero Trust mindset.
Checklist:
- Entry points and trust boundaries
- Authentication & authorization rules
- Input validation and encoding
- Secrets handling and logging redaction
- SSRF/SQLi/XSS/path traversal risks (as applicable)
Provide fixes and verification steps.
```

**Implementation Notes**:
- [ ] Prefer allowlists and explicit validation.
- [ ] Ensure logs do not leak tokens/PII.
- [ ] Add negative tests for security boundaries.
- [ ] Related to: code_review, test_case_generation
---
