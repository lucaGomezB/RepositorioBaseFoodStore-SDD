// CartPage — Shopping cart page with items, summary, and empty state
import { Link } from 'react-router-dom';
import { useCartStore, selectCartItems, selectIsCartEmpty } from '@/shared/stores/cartStore';
import { CartItemRow } from '@/features/cart';
import { CartSummary } from '@/features/cart';
import { ClearCartButton } from '@/features/cart';
import type { ProductoIngredienteRead } from '@/entities/product';
import { useCatalogoProductos } from '@/entities/product';

export default function CartPage() {
  const items = useCartStore(selectCartItems);
  const isEmpty = useCartStore(selectIsCartEmpty);

  // Fetch the catalog to get ingredient data for exclusion display
  const { data: catalogo } = useCatalogoProductos({ limit: 100 });

  // Build lookup: productoId → ingredient list
  const ingredientesMap = new Map<number, ProductoIngredienteRead[]>();
  if (catalogo?.items) {
    for (const prod of catalogo.items) {
      ingredientesMap.set(prod.id, prod.ingredientes);
    }
  }

  // ── Empty state ──
  if (isEmpty) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[60vh]">
        <span className="text-6xl mb-4">🛒</span>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Tu carrito está vacío
        </h1>
        <p className="text-gray-500 mb-6">
          Explorá nuestro catálogo y agregá productos
        </p>
        <Link
          to="/"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Ir al catálogo
        </Link>
      </div>
    );
  }

  // ── Cart with items ──
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Mi Carrito</h1>
        <ClearCartButton />
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Items list */}
        <div className="flex-1 space-y-4">
          {items.map((item) => (
            <CartItemRow
              key={item.productoId}
              item={item}
              ingredientes={ingredientesMap.get(item.productoId) ?? []}
            />
          ))}
        </div>

        {/* Summary sidebar */}
        <div className="w-full lg:w-80 shrink-0">
          <CartSummary />
        </div>
      </div>
    </div>
  );
}
