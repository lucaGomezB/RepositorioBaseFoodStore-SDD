// TanStack Query hooks for Admin Usuarios CRUD
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface UsuarioAdmin {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  roles: number[];
  activo: boolean;
  fecha_creacion: string;
}

export interface UsuariosFilters {
  skip?: number;
  limit?: number;
  search?: string;
  rol_id?: number;
}

export interface UsuariosResponse {
  items: UsuarioAdmin[];
  total: number;
  skip: number;
  limit: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildFilters(filters?: UsuariosFilters): string {
  if (!filters) return '';
  const params = new URLSearchParams();
  if (filters.skip !== undefined) params.set('skip', String(filters.skip));
  if (filters.limit !== undefined) params.set('limit', String(filters.limit));
  if (filters.search) params.set('search', filters.search);
  if (filters.rol_id !== undefined) params.set('rol_id', String(filters.rol_id));
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

const USUARIOS_KEY = 'admin-usuarios';

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/** Fetch paginated/filtered list of all users (admin only) */
export function useUsuarios(filters?: UsuariosFilters) {
  return useQuery({
    queryKey: [USUARIOS_KEY, filters],
    queryFn: async () => {
      const { data } = await httpClient.get<UsuariosResponse>(
        `/admin/usuarios${buildFilters(filters)}`,
      );
      return data;
    },
  });
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/** Soft-delete a user (admin only) */
export function useDeleteUsuario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (usuarioId: number) => {
      const { data } = await httpClient.delete(`/admin/usuarios/${usuarioId}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USUARIOS_KEY] });
    },
  });
}

/** Update user's nombre, apellido, and/or activo (admin only) */
export function useUpdateUsuario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: number;
      payload: { nombre?: string; apellido?: string; activo?: boolean };
    }) => {
      const { data } = await httpClient.put(`/admin/usuarios/${id}`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USUARIOS_KEY] });
    },
  });
}

/** Assign a role to a user (admin only) */
export function useAsignarRol() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      rol_id,
      action,
    }: {
      id: number;
      rol_id: number;
      action?: string;
    }) => {
      const { data } = await httpClient.put(
        `/admin/usuarios/${id}/role`,
        { rol_id, action: action ?? 'add' },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [USUARIOS_KEY] });
    },
  });
}
