// AddToCartButton — Button to add a product to cart with visual feedback
import { useState, useCallback } from 'react';
import type { ProductoCatalogoRead } from '@/entities/product';
import { useCartStore } from '@/shared/stores/cartStore';
import { useUIStore } from '@/shared/stores/uiStore';

interface AddToCartButtonProps {
  product: ProductoCatalogoRead;
}

export function AddToCartButton({ product }: AddToCartButtonProps) {
  const addItem = useCartStore((s) => s.addItem);
  const addToast = useUIStore((s) => s.addToast);
  const [justAdded, setJustAdded] = useState(false);

  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      // Stop propagation so card onClick doesn't fire
      e.stopPropagation();

      if (!product.hay_stock) return;

      addItem(product, 1, []);
      addToast({
        type: 'success',
        message: `${product.nombre} agregado al carrito`,
        duration: 2000,
      });

      // Show "Agregado ✓" feedback for 1.5s
      setJustAdded(true);
      setTimeout(() => setJustAdded(false), 1500);
    },
    [product, addItem, addToast],
  );

  if (!product.hay_stock) {
    return (
      <button
        disabled
        className="w-full bg-gray-200 text-gray-400 py-2 rounded-lg text-sm font-medium cursor-not-allowed"
      >
        Sin stock
      </button>
    );
  }

  return (
    <button
      onClick={handleClick}
      className={`w-full py-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer ${
        justAdded
          ? 'bg-green-600 text-white'
          : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
      }`}
    >
      {justAdded ? 'Agregado ✓' : 'Agregar'}
    </button>
  );
}
