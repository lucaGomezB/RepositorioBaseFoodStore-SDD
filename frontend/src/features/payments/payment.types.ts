// Payment types for MercadoPago integration
export interface PagoRead {
  id: number;
  pedido_id: number;
  mp_payment_id: string | null;
  mp_status: PaymentStatus;
  external_reference: string;
  status_detail: string | null;
  created_at: string;
}

export type PaymentStatus = 'pending' | 'processing' | 'approved' | 'rejected' | 'cancelled';

export interface CrearPagoRequest {
  pedido_id: number;
  card_token?: string;
  payment_method_id?: string;
}

/** Result from payment creation — includes the pago record and preference URL if available */
export interface CrearPagoResponse extends PagoRead {
  init_point?: string;
}
