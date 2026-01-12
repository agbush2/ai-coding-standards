# Compliance Checklist (The "What")
Applies to: All PRs

## Machine-Readable Checklist (JSON)
Copilot must use this structure when programmatically validating PRs:

```json
{
  "metadata": {
    "ticket_linked": false,
    "adr_linked": false
  },
  "security": {
    "no_secrets_detected": false,
    "sast_scan_passed": false,
    "sbom_generated": false
  },
  "quality": {
    "coverage_threshold_met": false,
    "tests_passed": false,
    "linting_passed": false
  },
  "documentation": {
    "public_api_documented": false,
    "readme_updated": false
  }
}
```
