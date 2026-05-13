// Type augmentation for @tanstack/react-query
// Fixes re-export chain issue with _tsup-dts-rollup.d.ts
import { QueryClient } from '@tanstack/react-query';

declare module '@tanstack/react-query' {
  export function useQuery<TData = unknown>(options: {
    queryKey: readonly unknown[];
    queryFn: () => Promise<TData> | TData;
    enabled?: boolean;
  }): {
    data: TData | undefined;
    isLoading: boolean;
    isError: boolean;
    error: unknown;
  };

  export function useMutation<TData = unknown, TVariables = unknown>(options?: {
    mutationFn?: (vars: TVariables) => Promise<TData> | TData;
    onSuccess?: (data: TData, variables: TVariables, context: unknown) => void | Promise<void>;
    onError?: (error: unknown, variables: TVariables, context: unknown) => void | Promise<void>;
    onSettled?: (data: TData | undefined, error: unknown, variables: TVariables, context: unknown) => void | Promise<void>;
  }): {
    mutateAsync: (vars: TVariables) => Promise<TData>;
    isPending: boolean;
    isError: boolean;
    error: unknown;
  };

  export function useQueryClient(queryClient?: QueryClient): QueryClient;
}
