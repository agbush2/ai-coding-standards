# Documentation Standards (The "What")
Applies to: All Codebases

## 1. Code Documentation
- **Why, not What**: Comments should explain rationale, not syntax.
- **Public API**: All public interfaces must be documented.

## 2. Architecture Decision Records (ADRs)
- **Mandatory**: Significant decisions must be recorded in `docs/adr/`.
- **Format**: Context, Decision, Consequences, Alternatives.

## 3. README Requirements
- **Top Level**: Purpose, Quick Start, Test Instructions, CI Status.
- **Module Level**: Intent and Public API surface.

## 4. API Documentation
- **Generated**: Docs should be auto-generated from code/contracts (OpenAPI).
- **Up-to-date**: CI must verify docs are in sync with code.
