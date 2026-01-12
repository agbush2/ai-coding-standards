# Operations & CI/CD Standards (The "What")
Applies to: All Codebases

## 1. Branching Strategy
- **Main**: Protected, deployable state.
- **Feature Branches**: Short-lived, PR-based workflow.
- **Versioning**: Semantic Versioning (Major.Minor.Patch).

## 2. CI Pipeline Requirements
- **Linting**: Style and static analysis.
- **Testing**: Unit tests with coverage.
- **Security**: SAST and SCA scans.
- **Build**: Immutable artifact generation with SBOM.

## 3. Deployment
- **Strategy**: Blue/Green or Canary preferred.
- **Gates**: Automated health checks and smoke tests post-deploy.
- **Rollback**: Automated or one-click rollback capability.

## 4. Observability
- **Logs**: Structured (JSON), correlated with Trace IDs.
- **Metrics**: RED Method (Rate, Errors, Duration).
- **Tracing**: Distributed tracing for all cross-service calls.
