# TypeScript Operations Standards
Implementation of: /ops_standards.md

## Relationship to Standards
This file provides the TypeScript-specific implementation ("How") for the operations and CI/CD requirements defined in `/ops_standards.md` ("What").

## Build System
- **Manager**: `npm`, `pnpm` (preferred), or `yarn`.
- **Artifact**: Transpiled JS (`dist/` or `build/`) or Docker Image.

## CI Jobs (GitHub Actions Example)
- **Lint**: `npm run lint` (eslint).
- **Format**: `npm run format:check` (prettier).
- **Type Check**: `npm run typecheck` (tsc --noEmit).
- **Test**: `npm run test:coverage`.
- **Audit**: `npm audit`.

## Docker Optimization
- Use multi-stage builds.
- Use `node:20-alpine` or `distroless/nodejs`.
- Install only production dependencies in the final stage (`npm ci --only=production`).
- Run as non-root user (`USER node`).
