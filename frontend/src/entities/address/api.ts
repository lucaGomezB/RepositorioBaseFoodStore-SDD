// TanStack Query hooks for address management
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';
import type { Direccion, DireccionCreate, DireccionUpdate } from './index';

const DIRECCIONES_KEY = 'direcciones';

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/** Fetch all addresses for the authenticated user */
export function useDirecciones() {
  return useQuery({
    queryKey: [DIRECCIONES_KEY],
    queryFn: async () => {
      const { data } = await httpClient.get<Direccion[]>('/direcciones/');
      return data;
    },
  });
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/** Create a new address */
export function useCreateDireccion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: DireccionCreate) => {
      const { data } = await httpClient.post<Direccion>('/direcciones/', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DIRECCIONES_KEY] });
    },
  });
}

/** Update an existing address */
export function useUpdateDireccion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: DireccionUpdate }) => {
      const { data } = await httpClient.put<Direccion>(`/direcciones/${id}`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DIRECCIONES_KEY] });
    },
  });
}

/** Delete an address */
export function useDeleteDireccion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await httpClient.delete(`/direcciones/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DIRECCIONES_KEY] });
    },
  });
}

/** Set an address as the default */
export function useSetDefaultDireccion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await httpClient.patch<Direccion>(`/direcciones/${id}/predeterminada`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [DIRECCIONES_KEY] });
    },
  });
}
