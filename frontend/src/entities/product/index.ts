// Product entity — types, schemas, and TanStack Query hooks
export type {
  Producto,
  ProductoCreate,
  ProductoUpdate,
  StockUpdate,
  ProductoFilters,
  ProductoCatalogoRead,
  ProductoIngredienteRead,
  ProductoCategoriaRead,
  CatalogoResponse,
  CatalogoFilters,
} from './model';
export {
  ProductoFormSchema,
  StockUpdateSchema,
} from './schemas';
export type {
  ProductoFormValues,
  StockUpdateValues,
} from './schemas';
export {
  useProductos,
  useProducto,
  useCreateProducto,
  useUpdateProducto,
  useDeleteProducto,
  useUpdateStock,
  useCatalogoProductos,
  useCatalogoProducto,
} from './api';
