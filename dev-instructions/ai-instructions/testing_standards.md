# Testing Standards (The "What")
Applies to: All Codebases

## Purpose
Define expectations for test strategy and quality gates.

## 1. Test Philosophy
- **TDD**: Test-Driven Development is preferred.
- **Determinism**: Tests must be deterministic and isolated.
- **Pyramid**: Heavy on Unit tests, moderate on Integration, light on E2E.

## 2. Coverage & Metrics
- **Target**: Minimum 90% branch coverage for new code.
- **Gating**: PRs must fail if coverage drops or tests fail.

## 3. Test Types
- **Unit**: Mock all external dependencies. Focus on logic.
- **Integration**: Test interactions with DB/Cache/Queue (using containers/emulators).
- **Contract**: Verify API/Event schemas.
- **Security**: Fuzzing and auth boundary tests.

## 4. Mocking Strategy
- **Boundaries**: Mock at the architectural boundary (IO).
- **No Network**: Unit tests must NOT make real network calls.

## 5. Test Data
- **Factories**: Use factories/builders, not hardcoded JSON blobs.
- **No Real Data**: Never use production data in tests.
