// Product entity types — matches backend API response

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio_base: string; // decimal as string from API
  stock_cantidad: number;
  disponible: boolean;
  imagenes_url: string | null;
  tiempo_prep_min: number | null;
  fecha_creacion: string;
  fecha_actualizacion: string;
  eliminado_en: string | null;
}

export interface ProductoCreate {
  nombre: string;
  descripcion?: string | null;
  precio_base?: string;
  stock_cantidad?: number;
  disponible?: boolean;
  imagenes_url?: string | null;
  tiempo_prep_min?: number | null;
}

export interface ProductoUpdate {
  nombre?: string;
  descripcion?: string | null;
  precio_base?: string;
  stock_cantidad?: number;
  disponible?: boolean;
  imagenes_url?: string | null;
  tiempo_prep_min?: number | null;
}

export interface StockUpdate {
  cantidad: number; // can be positive (increment) or negative (decrement)
}

export interface ProductoFilters {
  busqueda?: string;
  categoria_id?: number;
  disponible?: boolean;
  incluir_eliminados?: boolean;
  skip?: number;
  limit?: number;
}

// ---------------------------------------------------------------------------
// Catalog (public) types
// ---------------------------------------------------------------------------

export interface ProductoIngredienteRead {
  id: number;
  nombre: string;
  es_alergeno: boolean;
}

export interface ProductoCategoriaRead {
  id: number;
  nombre: string;
}

export interface ProductoCatalogoRead {
  id: number;
  nombre: string;
  descripcion: string;
  precio_base: string;
  imagenes_url: string | null;
  tiempo_prep_min: number | null;
  disponible: boolean;
  hay_stock: boolean;
  fecha_creacion: string;
  fecha_actualizacion: string;
  ingredientes: ProductoIngredienteRead[];
  categorias: ProductoCategoriaRead[];
}

export interface CatalogoResponse {
  items: ProductoCatalogoRead[];
  total_count: number;
}

export interface CatalogoFilters {
  page?: number;
  limit?: number;
  busqueda?: string;
  categoria_id?: number;
  excluir_alergenos?: string;
}
