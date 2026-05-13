// ProductGrid — Responsive grid of product cards
import type { ProductoCatalogoRead } from '@/entities/product';
import { ProductCard } from './ProductCard';
import { SkeletonCard } from './SkeletonCard';

interface ProductGridProps {
  products: ProductoCatalogoRead[] | undefined;
  isLoading: boolean;
  onProductClick: (product: ProductoCatalogoRead) => void;
}

export function ProductGrid({
  products,
  isLoading,
  onProductClick,
}: ProductGridProps) {
  // Loading state — show skeleton cards
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  // Empty state
  if (!products || products.length === 0) {
    return (
      <div className="text-center py-16">
        <span className="text-6xl">🔍</span>
        <p className="text-gray-500 text-lg mt-4">No se encontraron productos</p>
        <p className="text-gray-400 text-sm mt-1">
          Intentá cambiar los filtros de búsqueda.
        </p>
      </div>
    );
  }

  // Grid of product cards
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onClick={onProductClick}
        />
      ))}
    </div>
  );
}
