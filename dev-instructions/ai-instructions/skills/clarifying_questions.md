---
**Skill Name**: Clarifying Questions  
**Version**: 1.0 (2026-02-02)  
**Persona(s)**: Developer, Product Manager, Quality Engineer  
**Description**:  
Ask a small number of high-signal questions when requirements, constraints, inputs, or success criteria are ambiguous. Default to action when enough information is present; otherwise ask only what is needed to proceed safely.

**Usage Example**:
```prompt
Before implementing, identify any missing information that would change the design or acceptance criteria.
Ask up to 5 clarifying questions.
If you can proceed safely with reasonable assumptions, list the assumptions explicitly and continue.
```

**Implementation Notes**:
- [ ] Prefer questions that unblock design (scope, constraints, data shape, performance, security).
- [ ] Avoid “20 questions”; batch questions and prioritize.
- [ ] If the user is busy, propose safe defaults + how to override them.
- [ ] Related to: requirements_gathering, risk_assessment
---
