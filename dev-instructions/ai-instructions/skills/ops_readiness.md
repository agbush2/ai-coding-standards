---
**Skill Name**: Ops Readiness  
**Version**: 1.0 (2026-02-08)  
**Persona(s)**: Developer, Product Manager, Quality Engineer  
**Description**:  
Assess operational readiness for a change or feature: deployability, monitoring/alerting, runbooks, rollback, and reliability risks. Produces an actionable readiness checklist with verification steps.

**Usage Example**:
```prompt
Perform an ops readiness review for this change.
Return:
- Readiness checklist (deploy, monitor, alert, runbook, rollback)
- Failure modes + mitigations
- What to measure (SLIs/SLOs) and where to instrument
- Go/no-go criteria
Keep it pragmatic and testable.
```

**Implementation Notes**:
- [ ] Focus on concrete verification: dashboards, alerts, synthetic checks, and rollback drills.
- [ ] Cover deploy strategy (canary/feature flag), migration safety, and data backfill considerations if applicable.
- [ ] Include dependency risks (third-party APIs, rate limits, retries, timeouts, circuit breakers).
- [ ] Change control: if applying this skill would require creating/editing files (runbooks, dashboards-as-code, pipelines) or running write/execute actions, first propose the exact file changes and ask for explicit approval before proceeding.
- [ ] Related to: risk_assessment, security_review, test_case_generation
---
