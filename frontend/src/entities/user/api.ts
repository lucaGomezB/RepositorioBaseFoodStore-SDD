// TanStack Query hooks for User profile
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';
import { useAuthStore } from '@/shared/stores/authStore';
import type { User } from '@/shared/types/api';

const PERFIL_KEY = 'perfil';

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/** Fetch the authenticated user's profile */
export function usePerfil() {
  return useQuery({
    queryKey: [PERFIL_KEY],
    queryFn: async () => {
      const { data } = await httpClient.get<User>('/perfil/');
      return data;
    },
  });
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/** Update profile fields (nombre, telefono) */
export function useUpdatePerfil() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { nombre?: string; telefono?: string }) => {
      const { data } = await httpClient.put<User>('/perfil/', payload);
      return data;
    },
    onSuccess: (data) => {
      // Sync the auth store so sidebar/user displays reflect changes immediately
      useAuthStore.getState().updateUser(data);
      queryClient.invalidateQueries({ queryKey: [PERFIL_KEY] });
    },
  });
}

/** Change the user's password */
export function useChangePassword() {
  return useMutation({
    mutationFn: async (payload: { password_actual: string; password_nueva: string }) => {
      const { data } = await httpClient.put('/perfil/password', payload);
      return data;
    },
  });
}
