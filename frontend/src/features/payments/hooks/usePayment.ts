// usePayment hook — TanStack Query + Zustand store sync
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { crearPago, obtenerPago } from '../api';
import { usePaymentStore } from '@/shared/stores/paymentStore';
import type { CrearPagoRequest, PagoRead, PaymentStatus } from '../payment.types';

const PAYMENT_KEY = 'pagos';

// ---------------------------------------------------------------------------
// Create payment mutation
// ---------------------------------------------------------------------------
export function useCreatePayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: CrearPagoRequest) => {
      const result = await crearPago(payload);
      usePaymentStore.getState().setOrder(payload.pedido_id, 0);
      usePaymentStore.getState().setPaymentStatus(result.mp_status as PaymentStatus);
      return result;
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: [PAYMENT_KEY, variables.pedido_id] });
    },
  });
}

// ---------------------------------------------------------------------------
// Payment status query
// ---------------------------------------------------------------------------
export function usePaymentStatus(pedidoId: number | undefined) {
  return useQuery({
    queryKey: [PAYMENT_KEY, pedidoId],
    queryFn: async () => {
      if (!pedidoId) return null;
      const pago = await obtenerPago(pedidoId);
      usePaymentStore.getState().setPaymentStatus(pago.mp_status as PaymentStatus);
      return pago;
    },
    enabled: !!pedidoId,
  });
}

/** Safely extract PagoRead data from usePaymentStatus result */
export function extractPagoData(
  query: ReturnType<typeof usePaymentStatus>,
): PagoRead | null {
  const d = query.data;
  if (d && typeof d === 'object' && 'mp_status' in d) {
    return d as unknown as PagoRead;
  }
  return null;
}

/** Extract payment status from data */
export function extractPagoStatus(data: PagoRead | null | undefined): PaymentStatus {
  if (!data) return 'pending';
  return data.mp_status as PaymentStatus;
}
