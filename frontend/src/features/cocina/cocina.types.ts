// Kitchen Display System — TypeScript types
// Matches backend schemas from backend/app/domain/cocina/schemas.py

export interface PedidoCocinaItem {
  nombre_producto: string;
  cantidad: number;
  exclusiones: number[]; // ingredient IDs excluded
  exclusiones_nombres: string[]; // human-readable names of excluded ingredients
}

export interface PedidoCocinaRead {
  id: number;
  numero_pedido: number;
  estado_codigo: 'CONFIRMADO' | 'EN_PREPARACION';
  items: PedidoCocinaItem[];
  notas: string | null;
  tiempo_en_cocina_segundos: number;
  created_at: string | null;
}

export interface PedidoCocinaListResponse {
  items: PedidoCocinaRead[];
  total_count: number;
}

export type CocinaEventType =
  | 'PEDIDO_CONFIRMADO'
  | 'PEDIDO_EN_PREPARACION'
  | 'PEDIDO_EN_CAMINO'
  | 'PEDIDO_CANCELADO';
