# TypeScript Coding Standards
Implementation of: /master_standards.md

## Relationship to Standards
This file provides the TypeScript-specific implementation ("How") for the general coding and style guidelines defined in `/master_standards.md` ("What").

## Compiler & Runtime
- **Runtime**: Node.js LTS.
- **Compiler Options**: `strict: true`, `noImplicitAny: true`, `strictNullChecks: true`.

## Style & Formatting
- **Linter**: `eslint` with `@typescript-eslint/recommended`.
- **Formatter**: `prettier`.
- **Imports**: Absolute imports preferred (using path aliases `@/src/...`).

## Type Annotations
- **Mandatory**: Explicit return types for public functions.
- **Avoid**: `any` (use `unknown` if necessary), `Function` (use specific signature), `Object` (use `Record`).
- **Generics**: Use descriptive names (`TItem`, `TResponse`) or standard `T`, `U` for simple utilities.
- **Validation**: Use **Zod** for boundary validation (API inputs, env vars).

## Exception Handling
- **Custom Errors**: Extend `Error` class.
- **Async**: Use `try/catch` blocks or middleware for async errors.
- **Forbidden**: Do not `throw` strings or raw objects. Always throw `Error` instances.

## Project Layout
```text
src/
  api/          # Controllers/Routers
  core/         # Business Logic/Domain
  services/     # External Integrations
  db/           # Data Access
  utils/        # Shared Utilities
  types/        # Shared Types/Interfaces
package.json
tsconfig.json
README.md
```
