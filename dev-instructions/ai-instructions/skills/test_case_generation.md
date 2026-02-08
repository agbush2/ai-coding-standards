---
**Skill Name**: Test Case Generation  
**Version**: 1.0 (2026-02-02)  
**Persona(s)**: Quality Engineer, Developer  
**Description**:  
Generate deterministic, independent test cases (unit/integration/e2e as appropriate) covering happy path, negative cases, boundary values, and concurrency where relevant.

**Usage Example**:
```prompt
Generate a test plan and test cases for this feature.
Include:
- Happy path
- Validation/boundary tests
- Authorization/permission tests
- Failure-mode tests (timeouts, retries, partial failures)
Recommend which tests should be unit vs integration.
```

**Implementation Notes**:
- [ ] Avoid flaky tests; control time, randomness, and external services.
- [ ] Prefer a small number of high-value integration tests over excessive mocking.
- [ ] Include adversarial inputs (empty strings, max sizes, special chars).
- [ ] Change control: before creating/editing test files or running any write/execute actions, first propose the exact file changes and ask for explicit approval.
- [ ] Related to: acceptance_criteria_gherkin, security_review
---
