import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useEffect, useState } from 'react';
import { apiMe, apiRefresh } from '../shared/api/httpClient';
import { useAuthStore } from '../shared/stores/authStore';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    },
  },
});

interface ProvidersProps {
  children: ReactNode;
}

function AuthInitializer({ children }: { children: ReactNode }) {
  const [initialized, setInitialized] = useState(false);
  const setUser = useAuthStore((s) => s.setUser);
  const logout = useAuthStore((s) => s.logout);

  useEffect(() => {
    let cancelled = false;

    async function checkSession() {
      // Paso 1: intentar GET /auth/me con las cookies existentes
      let user = await apiMe();

      // Paso 2: si fallo, intentar refresh (el access_token pudo expirar)
      if (!user) {
        try {
          await apiRefresh();
          user = await apiMe();
        } catch {
          // Refresh fallo — no hay sesion activa
        }
      }

      if (!cancelled) {
        if (user) {
          setUser(user);
        } else {
          logout();
        }
        setInitialized(true);
      }
    }

    checkSession();

    return () => {
      cancelled = true;
    };
  }, [setUser, logout]);

  if (!initialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-gray-500 text-lg">Cargando...</div>
      </div>
    );
  }

  return <>{children}</>;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthInitializer>
        {children}
      </AuthInitializer>
    </QueryClientProvider>
  );
}
