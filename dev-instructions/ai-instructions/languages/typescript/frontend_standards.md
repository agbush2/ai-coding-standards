# TypeScript Frontend Standards (The "How")
Implementation of: /frontend_standards.md

## Relationship to Standards
This file provides the TypeScript-specific implementation ("How") for the frontend standards defined in `/frontend_standards.md` ("What").

## 1. Framework & Libraries

- **Primary Framework**: Next.js (React-based, SSR/SSG support).
- **Alternatives**: React with Vite for SPAs, Svelte for lightweight apps.
- **State Management**: Zustand for simple apps, Redux Toolkit for complex.
- **Styling**: Tailwind CSS with custom design tokens.
- **Testing**: Vitest for unit tests, Playwright for E2E.

## 2. Project Structure

```text
myapp/
├── app/                 # Next.js app router
├── components/          # Reusable UI components
├── hooks/               # Custom React hooks
├── lib/                 # Utilities, API clients
├── styles/              # Global styles, Tailwind config
├── types/               # TypeScript type definitions
└── tests/               # Test files
```

## 3. Example: Basic Component

```tsx
import { useState } from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
}

export function Button({ children, onClick, disabled }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
    >
      {children}
    </button>
  );
}
```

## 4. Accessibility Implementation

- **ARIA Attributes**: Use `aria-label`, `role` for custom components.
- **Keyboard Navigation**: Ensure focus management with `useRef` and `tabIndex`.
- **Screen Readers**: Test with NVDA/JAWS; use semantic HTML.

## 5. Performance Tips

- **Code Splitting**: Use dynamic imports for routes.
- **Image Optimization**: Next.js `Image` component with lazy loading.
- **Bundle Analysis**: Use `@next/bundle-analyzer`.
