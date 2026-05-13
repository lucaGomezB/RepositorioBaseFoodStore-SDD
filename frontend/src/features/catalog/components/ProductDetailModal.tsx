// ProductDetailModal — Expanded product detail with ingredients, allergens, categories
import { useEffect, useCallback } from 'react';
import type { ProductoCatalogoRead } from '@/entities/product';

interface ProductDetailModalProps {
  product: ProductoCatalogoRead | null;
  onClose: () => void;
}

export function ProductDetailModal({
  product,
  onClose,
}: ProductDetailModalProps) {
  // Close on Escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    },
    [onClose],
  );

  useEffect(() => {
    if (product) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [product, handleKeyDown]);

  if (!product) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <div className="flex justify-end p-2">
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none cursor-pointer p-1"
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>

        {/* Large image */}
        <div className="px-6">
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
            {product.imagenes_url ? (
              <img
                src={product.imagenes_url}
                alt={product.nombre}
                className="w-full h-full object-cover"
              />
            ) : (
              <span className="text-gray-400 text-6xl">🍽️</span>
            )}
          </div>
        </div>

        {/* Detail content */}
        <div className="p-6 space-y-4">
          {/* Title + Price */}
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {product.nombre}
              </h2>
              <p className="text-gray-600 mt-1">{product.descripcion}</p>
            </div>
            <span className="text-2xl font-bold text-green-700 whitespace-nowrap">
              ${product.precio_base}
            </span>
          </div>

          {/* Stock badge + prep time */}
          <div className="flex items-center gap-3">
            {product.hay_stock ? (
              <span className="inline-flex items-center bg-green-100 text-green-800 text-sm font-medium px-3 py-1 rounded-full">
                En stock
              </span>
            ) : (
              <span className="inline-flex items-center bg-red-100 text-red-800 text-sm font-medium px-3 py-1 rounded-full">
                Sin stock
              </span>
            )}
            {product.tiempo_prep_min && (
              <span className="text-sm text-gray-500">
                ⏱️ ~{product.tiempo_prep_min} min
              </span>
            )}
          </div>

          {/* Ingredients list with allergen flag */}
          {product.ingredientes.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                Ingredientes
              </h3>
              <div className="flex flex-wrap gap-2">
                {product.ingredientes.map((ing) => (
                  <span
                    key={ing.id}
                    className={`inline-flex items-center gap-1 text-sm px-3 py-1 rounded-full ${
                      ing.es_alergeno
                        ? 'bg-yellow-50 text-yellow-800 border border-yellow-300'
                        : 'bg-gray-50 text-gray-700 border border-gray-200'
                    }`}
                  >
                    {ing.nombre}
                    {ing.es_alergeno && (
                      <span title="Alérgeno" role="img" aria-label="Alérgeno">
                        ⚠️
                      </span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Categories */}
          {product.categorias.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                Categorías
              </h3>
              <div className="flex flex-wrap gap-2">
                {product.categorias.map((cat) => (
                  <span
                    key={cat.id}
                    className="inline-flex items-center bg-blue-50 text-blue-700 text-sm px-3 py-1 rounded-full"
                  >
                    {cat.nombre}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
