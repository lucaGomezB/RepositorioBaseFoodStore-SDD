// Payments API layer
import { httpClient } from '@/shared/api/httpClient';
import type { PagoRead, CrearPagoRequest } from './payment.types';

/** Create a payment for an order via MercadoPago */
export async function crearPago(payload: CrearPagoRequest): Promise<PagoRead> {
  const { data } = await httpClient.post<PagoRead>('/pagos/crear', payload);
  return data;
}

/** Get payment status for an order */
export async function obtenerPago(pedidoId: number): Promise<PagoRead> {
  const { data } = await httpClient.get<PagoRead>(`/pagos/${pedidoId}`);
  return data;
}
