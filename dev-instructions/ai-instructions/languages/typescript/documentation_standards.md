# TypeScript Documentation Standards
Implementation of: /documentation_standards.md

## Relationship to Standards
This file provides the TypeScript-specific implementation ("How") for the documentation requirements defined in `/documentation_standards.md` ("What").

## TSDoc
- **Style**: Use TSDoc standard (`/** ... */`).
- **Tags**: `@param`, `@returns`, `@throws`, `@example`.

## Example
```typescript
/**
 * Fetches user data from the remote API.
 *
 * @param userId - The unique identifier of the user.
 * @returns A promise resolving to the user details.
 * @throws {UserNotFoundError} If the user does not exist.
 *
 * @example
 * const user = await fetchData(123);
 */
export async function fetchData(userId: number): Promise<User> {
  // ...
}
```

## Tools
- **Generation**: `typedoc`.
- **API Docs**: Swagger/OpenAPI (via `swagger-jsdoc` or NestJS `@nestjs/swagger`).
