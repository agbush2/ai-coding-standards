# TypeScript Forbidden Patterns
Implementation of: /forbidden_patterns.md

## Relationship to Standards
This file provides the TypeScript-specific implementation ("How") for the universally forbidden patterns defined in `/forbidden_patterns.md` ("What").

## Strictly Forbidden
- **Any Type**: `any`. Use `unknown` or specific types. Absolutely forbidden in public APIs.
- **Eval**: `eval()`, `new Function()`.
- **Console Log**: `console.log` in production code. Use a logger (Pino, Winston).
- **Secrets**: Hardcoded secrets.
- **Loose Equality**: `==` or `!=`. Always use `===` and `!==`.
- **Var**: `var`. Always use `const` or `let`.
- **Throwing Strings**: `throw "error"`. Always `throw new Error("message")`.
- **require() in ES Modules**: Do not use `require()` in files using ES module syntax. Use `import` statements only.

## Library Constraints
- **Request**: Do not use the deprecated `request` library. Use `fetch` (Node 18+) or `axios`.
- **Moment**: Do not use `moment.js`. Use `date-fns` or `luxon`.
