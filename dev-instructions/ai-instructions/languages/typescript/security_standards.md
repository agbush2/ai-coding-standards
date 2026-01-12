# TypeScript Security Standards
Implementation of: /security_standards.md

## Relationship to Standards
This file provides the TypeScript-specific implementation ("How") for the security controls and requirements defined in `/security_standards.md` ("What").

## Tools
- **SAST**: `eslint-plugin-security`.
- **SCA**: `npm audit` or `snyk`.

## Cryptography
- **Hashing**: `node:crypto` (`scrypt` or `pbkdf2`) or `bcryptjs` / `argon2`.
- **Random**: `crypto.randomBytes` or `crypto.randomUUID`.

## Web Security (Express/Fastify/NestJS)
- **Headers**: `helmet`.
- **CORS**: Configure strict CORS options (allowlist origins).
- **Rate Limiting**: `express-rate-limit` or `@nestjs/throttler`.
- **Input**: **Zod** schemas for all request bodies and query params.

## Secrets
- **Loading**: `dotenv` or framework specific (e.g., `@nestjs/config`).
- **Validation**: Validate env vars on startup using Zod.

```typescript
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
});

export const env = envSchema.parse(process.env);
```
