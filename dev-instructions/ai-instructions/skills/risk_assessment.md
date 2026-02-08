---
**Skill Name**: Risk Assessment  
**Version**: 1.0 (2026-02-02)  
**Persona(s)**: Developer, Product Manager, Quality Engineer  
**Description**:  
Identify and communicate delivery, security, compliance, and operational risks with mitigations and verification steps.

**Usage Example**:
```prompt
For this change, produce a risk assessment:
- Top 5 risks (with likelihood x impact)
- Mitigations
- Monitoring/alerting needs
- Rollback plan / safe deployment strategy
```

**Implementation Notes**:
- [ ] Include data handling and privacy considerations.
- [ ] Consider external dependencies and failure modes.
- [ ] Tie each mitigation to a concrete verification step (test, check, metric).
- [ ] Change control: if applying this skill would require creating/editing files (e.g., risk register, rollout plan) or running write/execute actions, first propose the exact file changes and ask for explicit approval before proceeding.
- [ ] Related to: security_review, ops_readiness
---
