// Cocina API — Kitchen Display System REST calls
import { httpClient } from '@/shared/api/httpClient';
import type { PedidoCocinaListResponse } from './cocina.types';

/** Fetch all orders visible in the KDS (CONFIRMADO + EN_PREPARACION) */
export async function fetchCocinaPedidos(): Promise<PedidoCocinaListResponse> {
  const { data } = await httpClient.get<PedidoCocinaListResponse>('/cocina/pedidos');
  return data;
}

/** Transition an order's state from the KDS */
export async function transicionarEstadoPedido(
  pedidoId: number,
  nuevoEstado: string,
): Promise<void> {
  await httpClient.patch(`/pedidos/${pedidoId}/estado`, { nuevo_estado: nuevoEstado });
}
