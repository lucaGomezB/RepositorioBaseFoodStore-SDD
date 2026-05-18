// Test utilities for TanStack Query hooks
import type { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

/**
 * Creates a QueryClient configured for testing:
 * - No retries (tests fail fast)
 * - No gc time (clean up immediately)
 * - No refetch on window focus
 */
export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

/**
 * Wrapper component that provides a QueryClient for testing hooks.
 * Recreates the client for each call to ensure test isolation.
 */
export function createQueryWrapper() {
  const testQueryClient = createTestQueryClient();
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={testQueryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}
