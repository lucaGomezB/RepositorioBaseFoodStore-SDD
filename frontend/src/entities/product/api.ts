// TanStack Query hooks for Producto CRUD
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';
import type {
  Producto,
  ProductoCreate,
  ProductoUpdate,
  StockUpdate,
  ProductoFilters,
  ProductoCatalogoRead,
  CatalogoResponse,
  CatalogoFilters,
} from './model';

const PRODUCTOS_KEY = 'productos';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildFilters(filters?: ProductoFilters): string {
  if (!filters) return '';
  const params = new URLSearchParams();
  if (filters.busqueda) params.set('busqueda', filters.busqueda);
  if (filters.categoria_id !== undefined) params.set('categoria_id', String(filters.categoria_id));
  if (filters.disponible !== undefined) params.set('disponible', String(filters.disponible));
  if (filters.incluir_eliminados) params.set('incluir_eliminados', 'true');
  if (filters.skip !== undefined) params.set('skip', String(filters.skip));
  if (filters.limit !== undefined) params.set('limit', String(filters.limit));
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/** Fetch paginated/filtered product list */
export function useProductos(filters?: ProductoFilters) {
  return useQuery({
    queryKey: [PRODUCTOS_KEY, filters],
    queryFn: async () => {
      const { data } = await httpClient.get<Producto[]>(`/productos/${buildFilters(filters)}`);
      return data;
    },
  });
}

/** Fetch a single product by ID */
export function useProducto(id: number | undefined) {
  return useQuery({
    queryKey: [PRODUCTOS_KEY, id],
    queryFn: async () => {
      const { data } = await httpClient.get<Producto>(`/productos/${id}`);
      return data;
    },
    enabled: id !== undefined && id > 0,
  });
}

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/** Create a new product */
export function useCreateProducto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: ProductoCreate) => {
      const { data } = await httpClient.post<Producto>('/productos/', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PRODUCTOS_KEY] });
    },
  });
}

/** Update an existing product */
export function useUpdateProducto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: ProductoUpdate }) => {
      const { data } = await httpClient.patch<Producto>(`/productos/${id}`, payload);
      return data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [PRODUCTOS_KEY] });
      queryClient.invalidateQueries({ queryKey: [PRODUCTOS_KEY, id] });
    },
  });
}

/** Soft-delete a product */
export function useDeleteProducto() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await httpClient.delete(`/productos/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PRODUCTOS_KEY] });
    },
  });
}

// ---------------------------------------------------------------------------
// Catalog (public) queries
// ---------------------------------------------------------------------------

const CATALOGO_KEY = 'catalogo-productos';

/** Fetch paginated/filtered catalog products (public endpoint) */
export function useCatalogoProductos(filters?: CatalogoFilters) {
  return useQuery({
    queryKey: [CATALOGO_KEY, filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.page !== undefined) params.set('page', String(filters.page));
      if (filters?.limit) params.set('limit', String(filters.limit));
      if (filters?.busqueda) params.set('busqueda', filters.busqueda);
      if (filters?.categoria_id !== undefined) params.set('categoria_id', String(filters.categoria_id));
      if (filters?.excluir_alergenos) params.set('excluir_alergenos', filters.excluir_alergenos);
      const qs = params.toString();
      const { data } = await httpClient.get<CatalogoResponse>(`/catalogo/productos/${qs ? `?${qs}` : ''}`);
      return data;
    },
  });
}

/** Fetch a single catalog product by ID (public endpoint) */
export function useCatalogoProducto(id: number | undefined) {
  return useQuery({
    queryKey: [CATALOGO_KEY, id],
    queryFn: async () => {
      const { data } = await httpClient.get<ProductoCatalogoRead>(`/catalogo/productos/${id}`);
      return data;
    },
    enabled: id !== undefined && id > 0,
  });
}

// ---------------------------------------------------------------------------
// Mutations (admin)
// ---------------------------------------------------------------------------

/** Atomic stock update (increment/decrement) */
export function useUpdateStock() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: StockUpdate }) => {
      const { data } = await httpClient.patch<{ stock_cantidad: number }>(
        `/productos/${id}/stock`,
        payload,
      );
      return data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [PRODUCTOS_KEY] });
      queryClient.invalidateQueries({ queryKey: [PRODUCTOS_KEY, id] });
    },
  });
}
