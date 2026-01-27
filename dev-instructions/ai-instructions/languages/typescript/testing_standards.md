
## Coverage Reporting
- **Threshold**: Minimum 80% code coverage required for PR approval.
- **Reporting Tools**: Use `vitest` or `jest` with coverage enabled and integrate with Coveralls or Codecov for CI reporting.
# TypeScript Testing Standards
Implementation of: /testing_standards.md

## Relationship to Standards
This file provides the TypeScript-specific implementation ("How") for the testing strategies and quality gates defined in `/testing_standards.md` ("What").

## Frameworks
- **Runner**: `vitest` (preferred) or `jest`.
- **Mocking**: `vi` (Vitest) or `jest.mock`.
- **Assertions**: Built-in expect.

## Patterns
- **Isolation**: Reset mocks between tests (`mockReset` / `clearMocks`).
- **Factories**: Use helper functions to generate test data, do not hardcode large objects.
- **Network**: Use `msw` (Mock Service Worker) for HTTP mocking or mock the service layer directly.

## Example: Unit Test (Vitest)
```typescript
import { describe, it, expect, vi } from 'vitest';
import { calculateTotal } from '@/core/service';

describe('calculateTotal', () => {
  it('should sum items correctly', () => {
    // Arrange
    const items = [10, 20];
    // Act
    const result = calculateTotal(items);
    // Assert
    expect(result).toBe(30);
  });
});
```

## Example: Mocking
```typescript
import { UserService } from '@/services/user';

vi.mock('@/services/user');

it('should call external service', async () => {
  const mockGetUser = vi.mocked(UserService.getUser);
  mockGetUser.mockResolvedValue({ id: 1, name: 'Test' });
  
  // ... test logic
});
```
