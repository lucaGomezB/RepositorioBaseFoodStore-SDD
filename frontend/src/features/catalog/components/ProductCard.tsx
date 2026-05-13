// ProductCard — Card component for catalog product grid
import type { ProductoCatalogoRead } from '@/entities/product';
import { AddToCartButton } from '@/features/cart/components/AddToCartButton';

interface ProductCardProps {
  product: ProductoCatalogoRead;
  onClick: (product: ProductoCatalogoRead) => void;
}

export function ProductCard({ product, onClick }: ProductCardProps) {
  return (
    <div
      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer flex flex-col overflow-hidden"
      onClick={() => onClick(product)}
    >
      {/* Image */}
      <div className="h-48 bg-gray-100 flex items-center justify-center overflow-hidden">
        {product.imagenes_url ? (
          <img
            src={product.imagenes_url}
            alt={product.nombre}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-gray-400 text-4xl">🍽️</span>
        )}
      </div>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col gap-2">
        <h3 className="font-semibold text-gray-900 text-lg line-clamp-2">
          {product.nombre}
        </h3>
        <p className="text-sm text-gray-500 line-clamp-2">{product.descripcion}</p>

        {/* Price + Stock + AddToCart */}
        <div className="mt-auto space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xl font-bold text-green-700">
              ${product.precio_base}
            </span>
            {product.hay_stock ? (
              <span className="inline-flex items-center bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                En stock
              </span>
            ) : (
              <span className="inline-flex items-center bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                Sin stock
              </span>
            )}
          </div>
          <AddToCartButton product={product} />
        </div>

        {/* Categories */}
        {product.categorias.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {product.categorias.map((cat) => (
              <span
                key={cat.id}
                className="inline-block bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full"
              >
                {cat.nombre}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
