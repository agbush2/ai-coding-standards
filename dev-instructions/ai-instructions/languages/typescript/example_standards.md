# TypeScript Examples & Templates
Implementation of: /master_standards.md

## Relationship to Standards
This file provides the TypeScript-specific implementation ("How") for the code templates and patterns requested in `/master_standards.md` ("What").

## Template 1: Zod Environment Config
```typescript
import { z } from 'zod';

const configSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.coerce.number().default(3000),
  DB_URL: z.string().url(),
});

export const config = configSchema.parse(process.env);
```

## Template 2: Async Route Handler (Express/Zod)
```typescript
import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';

const createItemSchema = z.object({
  name: z.string().min(1),
  quantity: z.number().int().positive(),
});

export const createItem = async (req: Request, res: Response, next: NextFunction) => {
  try {
    // Validate Input
    const data = createItemSchema.parse(req.body);

    // Business Logic
    // BAD: console.log(`Creating ${data.name}`);
    // GOOD: logger.info({ msg: 'creating_item', name: data.name });

    const newItem = await itemService.create(data);
    
    res.status(201).json(newItem);
  } catch (error) {
    next(error);
  }
};
```

## Template 3: package.json Scripts
```json
{
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "lint": "eslint . --ext .ts",
    "format": "prettier --write .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run"
  }
}
```
