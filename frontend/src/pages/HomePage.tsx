// HomePage — Main landing page with full public product catalog
import { useState } from 'react';
import { useCatalogoProductos } from '@/entities/product';
import type { ProductoCatalogoRead } from '@/entities/product';
import { useCatalogFilters, useDebounce } from '@/features/catalog';
import { ProductGrid } from '@/features/catalog/components/ProductGrid';
import { CatalogFilters } from '@/features/catalog/components/CatalogFilters';
import { CatalogPagination } from '@/features/catalog/components/CatalogPagination';
import { ProductDetailModal } from '@/features/catalog/components/ProductDetailModal';

export const HomePage = () => {
  const {
    filters,
    setBusqueda,
    setCategoria,
    setPage,
    resetFilters,
  } = useCatalogFilters();

  // Debounce search input to avoid excessive API calls
  const debouncedBusqueda = useDebounce(filters.busqueda, 300);

  // Selected product for detail modal
  const [selectedProduct, setSelectedProduct] =
    useState<ProductoCatalogoRead | null>(null);

  // Merge debounced search into filters for the API query
  const queryFilters = {
    ...filters,
    busqueda: debouncedBusqueda,
  };

  const { data, isLoading, isError, error } =
    useCatalogoProductos(queryFilters);

  return (
    <div className="p-6">
      {/* Header */}
      <h1 className="text-2xl font-bold text-gray-900 mb-2">
        Catálogo de Productos
      </h1>
      <p className="text-gray-600 mb-6">
        Explorá nuestros productos disponibles
      </p>

      {/* Filters — search, category, reset */}
      <CatalogFilters
        busqueda={filters.busqueda ?? ''}
        categoria_id={filters.categoria_id}
        onBusquedaChange={setBusqueda}
        onCategoriaChange={setCategoria}
        onReset={resetFilters}
      />

      {/* Error state */}
      {isError && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-6">
          {(error as Error)?.message || 'Error al cargar el catálogo'}
        </div>
      )}

      {/* Product grid — handles loading, empty, and data states */}
      <ProductGrid
        products={data?.items}
        isLoading={isLoading}
        onProductClick={setSelectedProduct}
      />

      {/* Pagination — only shown when there are results */}
      {data && data.total_count > 0 && (
        <CatalogPagination
          page={filters.page ?? 1}
          totalCount={data.total_count}
          limit={filters.limit ?? 12}
          onPageChange={setPage}
        />
      )}

      {/* Product detail modal */}
      <ProductDetailModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />
    </div>
  );
};
