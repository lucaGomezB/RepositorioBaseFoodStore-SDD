declare module '@tanstack/react-query' {
  import { QueryClient, QueryClientProvider } from './build/modern/index';
  export { QueryClient, QueryClientProvider };
  export * from './build/modern/index';
}