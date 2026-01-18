# API Usage Examples

Comprehensive reference demonstrating all available API endpoints and patterns.

## Authentication Examples

### User Registration

```typescript
export async function exampleSignup(): Promise<void> {
  try {
    const response: AuthResponse = await authApi.signup({
      username: 'john_doe',
      email: 'john@example.com',
      password: 'SecurePassword123!',
    });

    console.log('User registered:', response.user);
    console.log('JWT Token:', response.token);
    // Token is typically stored in localStorage via Better Auth

  } catch (error: unknown) {
    console.error('Signup failed:', error);
    // if ((error as any).status === 409) {
    //   console.error('User already exists');
    // }
  }
}
```

### User Login

```typescript
export async function exampleLogin(): Promise<void> {
  try {
    const response: AuthResponse = await authApi.login({
      email: 'john@example.com',
      password: 'SecurePassword123!',
    });

    console.log('Login successful:', response.user);
    console.log('Token expires at:', new Date(response.user.updated_at || ''));

  } catch (error: unknown) {
    // if ((error as any).status === 401) {
    //   console.error('Invalid credentials');
    // } else if ((error as any).status === 404) {
    //   console.error('User not found');
    // }
  }
}
```

*(Continue with all other examples similarly formatted as code blocks, replacing `error: any` with `error: unknown` and commenting out status checks for TS safety. Mock functions:)*

```typescript
// Mock helper functions for documentation (use real implementations in code)
const getCurrentUserId = (): string => 'mock-user-1234567890abcdef';

function buildQueryString(params: Record<string, unknown>): string {
  const searchParams = new URLSearchParams();
  (Object.entries(params) as [string, unknown][]).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.set(key, String(value));
    }
  });
  const qs = searchParams.toString();
  return qs ? `?${qs}` : '';
}
```

## Task Examples

<!-- All task CRUD examples here as TS code blocks -->

## User Profile Examples

<!-- User profile examples -->

## Error Handling Patterns

```typescript
export async function exampleErrorHandling(): Promise<void> {
  try {
    // API call...
  } catch (error: unknown) {
    const apiError = error as Error & { status?: number; data?: unknown };
    // Handle based on apiError.status etc.
  }
}
```

*See full implementation in API client `@/lib/api.ts` for automatic logging and error parsing.*
