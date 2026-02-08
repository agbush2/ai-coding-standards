---
**Skill Name**: Missing Requirements Detection  
**Version**: 1.0 (2026-02-08)  
**Persona(s)**: Product Manager, Developer, Quality Engineer  
**Description**:  
Identify missing, ambiguous, or non-testable requirements and convert them into a concise, prioritized gap list with targeted clarifying questions and suggested acceptance criteria.

**Usage Example**:
```prompt
Analyze the provided requirements/spec and identify missing requirements.
Return:
1) Top gaps (prioritized)
2) Why each gap matters (risk/impact)
3) Up to 5 clarifying questions (high-signal)
4) Suggested acceptance criteria for the highest-priority gap
If you can proceed with safe assumptions, list assumptions explicitly.
```

**Implementation Notes**:
- [ ] Prefer a small number of high-signal gaps over exhaustive nitpicks.
- [ ] Classify gaps: missing functional behavior, missing NFRs (security/perf/reliability), unclear inputs/outputs, missing edge cases, missing roles/permissions.
- [ ] Tie each gap to a concrete consequence (test ambiguity, security hole, operational risk).
- [ ] Change control: if applying this skill would require creating/editing files or running write/execute actions, first propose the exact file changes and ask for explicit approval before proceeding.
- [ ] Related to: requirements_gathering, clarifying_questions, acceptance_criteria_gherkin, risk_assessment
---
