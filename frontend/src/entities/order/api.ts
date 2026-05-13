// TanStack Query hooks for Pedido CRUD
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';
import type {
  PedidoRead,
  PedidoDetail,
  AdminPedidoDetail,
  HistorialEstadoRead,
  PedidoFilters,
  PedidoListResponse,
} from './model';

const PEDIDOS_KEY = 'pedidos';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildFilters(filters?: PedidoFilters): string {
  if (!filters) return '';
  const params = new URLSearchParams();
  if (filters.estado) params.set('estado', filters.estado);
  if (filters.desde) params.set('desde', filters.desde);
  if (filters.hasta) params.set('hasta', filters.hasta);
  if (filters.busqueda) params.set('busqueda', filters.busqueda);
  if (filters.skip !== undefined) params.set('skip', String(filters.skip));
  if (filters.limit !== undefined) params.set('limit', String(filters.limit));
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/** Fetch paginated/filtered order list */
export function usePedidos(filters?: PedidoFilters) {
  return useQuery({
    queryKey: [PEDIDOS_KEY, filters],
    queryFn: async () => {
      const { data } = await httpClient.get<PedidoListResponse>(`/pedidos/${buildFilters(filters)}`);
      return data;
    },
  });
}

/** Fetch paginated/filtered admin order list with user email */
export function useAdminPedidos(filters?: PedidoFilters) {
  return useQuery({
    queryKey: [PEDIDOS_KEY, 'admin-list', filters],
    queryFn: async () => {
      const { data } = await httpClient.get<PedidoListResponse>(`/admin/pedidos/${buildFilters(filters)}`);
      return data;
    },
  });
}

/** Fetch a single order by ID with details and history */
export function usePedido(id: number | undefined) {
  return useQuery({
    queryKey: [PEDIDOS_KEY, id],
    queryFn: async () => {
      const { data } = await httpClient.get<PedidoDetail>(`/pedidos/${id}`);
      return data;
    },
    enabled: id !== undefined && id > 0,
  });
}

/** Fetch a single order with full user contact info (ADMIN/PEDIDOS) */
export function useAdminPedido(id: number | undefined) {
  return useQuery({
    queryKey: [PEDIDOS_KEY, 'admin-detail', id],
    queryFn: async () => {
      const { data } = await httpClient.get<AdminPedidoDetail>(`/admin/pedidos/${id}`);
      return data;
    },
    enabled: id !== undefined && id > 0,
  });
}

/** Fetch order state history by ID */
export function usePedidoHistorial(id: number | undefined) {
  return useQuery({
    queryKey: [PEDIDOS_KEY, 'historial', id],
    queryFn: async () => {
      const { data } = await httpClient.get<HistorialEstadoRead[]>(`/pedidos/${id}/historial`);
      return data;
    },
    enabled: id !== undefined && id > 0,
  });
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/** Transition an order's state (ADMIN/PEDIDOS only) */
export function useTransicionarEstado() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      pedidoId,
      nuevoEstado,
      motivo,
    }: {
      pedidoId: number;
      nuevoEstado: string;
      motivo?: string;
    }) => {
      const { data } = await httpClient.patch<PedidoRead>(`/pedidos/${pedidoId}/estado`, {
        nuevo_estado: nuevoEstado,
        motivo: motivo || null,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PEDIDOS_KEY] });
    },
  });
}
