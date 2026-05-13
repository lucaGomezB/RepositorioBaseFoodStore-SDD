// Order entity types — matches backend API response

export interface PedidoRead {
  id: number;
  usuario_id: number;
  estado_codigo: string;
  total: number;
  costo_envio: number;
  forma_pago_codigo: string | null;
  created_at: string;
  items_count: number;
  usuario_nombre: string | null;
  usuario_email?: string | null;
}

export interface DetallePedidoRead {
  id: number;
  producto_id: number;
  nombre_snapshot: string;
  precio_snapshot: number;
  cantidad: number;
  exclusiones: number[];
  subtotal: number;
}

export interface HistorialEstadoRead {
  id: number;
  estado_desde: string | null;
  estado_hacia: string;
  motivo: string | null;
  created_at: string;
}

export interface PedidoDetail extends PedidoRead {
  direccion_calle: string;
  direccion_numero: string;
  direccion_piso: string | null;
  direccion_ciudad: string;
  direccion_cp: string;
  detalles: DetallePedidoRead[];
  historial_estados: HistorialEstadoRead[];
}

export interface PedidoFilters {
  estado?: string;
  desde?: string;
  hasta?: string;
  busqueda?: string;
  skip?: number;
  limit?: number;
}

export interface PedidoListResponse {
  items: PedidoRead[];
  total_count: number;
}

export interface AdminPedidoDetail extends PedidoDetail {
  usuario_email: string;
  usuario_telefono?: string | null;
}
