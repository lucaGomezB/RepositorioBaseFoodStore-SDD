// TanStack Query hooks for Admin Dashboard Metrics
import { useQuery } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface EstadoCount {
  codigo: string;
  nombre: string;
  cantidad: number;
}

export interface ProductoCount {
  nombre: string;
  cantidad: number;
}

export interface ResumenMetricas {
  total_ventas: number;
  pedidos_por_estado: EstadoCount[];
  total_usuarios: number;
  top_productos: ProductoCount[];
}

export interface VentaPorPeriodo {
  periodo: string;
  total: number;
}

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

const METRICAS_KEY = 'metricas';

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

/** Fetch admin dashboard summary KPIs */
export function useResumenMetricas() {
  return useQuery({
    queryKey: [METRICAS_KEY, 'resumen'],
    queryFn: async () => {
      const { data } = await httpClient.get<ResumenMetricas>('/admin/metricas/resumen');
      return data;
    },
  });
}

/** Fetch aggregated sales over time with optional date range and granularity */
export function useVentasPorPeriodo(
  desde?: string,
  hasta?: string,
  granularidad: string = 'dia',
) {
  return useQuery({
    queryKey: [METRICAS_KEY, 'ventas', { desde, hasta, granularidad }],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (desde) params.set('desde', desde);
      if (hasta) params.set('hasta', hasta);
      params.set('granularidad', granularidad);
      const qs = params.toString();
      const { data } = await httpClient.get<VentaPorPeriodo[]>(
        `/admin/metricas/ventas${qs ? `?${qs}` : ''}`,
      );
      return data;
    },
  });
}

/** Fetch top N best-selling products */
export function useTopProductos(top: number = 10) {
  return useQuery({
    queryKey: [METRICAS_KEY, 'productos-top', top],
    queryFn: async () => {
      const { data } = await httpClient.get<ProductoCount[]>(
        `/admin/metricas/productos-top?top=${top}`,
      );
      return data;
    },
  });
}

/** Fetch order count distribution by state */
export function usePedidosPorEstado() {
  return useQuery({
    queryKey: [METRICAS_KEY, 'pedidos-por-estado'],
    queryFn: async () => {
      const { data } = await httpClient.get<EstadoCount[]>(
        '/admin/metricas/pedidos-por-estado',
      );
      return data;
    },
  });
}
