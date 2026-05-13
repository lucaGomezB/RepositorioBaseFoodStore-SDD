// CartItemRow — Single cart item with quantity controls, exclusion display, and delete
import { useState } from 'react';
import type { ProductoIngredienteRead } from '@/entities/product';
import type { CartItem } from '@/shared/stores/cartStore';
import { useCartStore } from '@/shared/stores/cartStore';

interface CartItemRowProps {
  item: CartItem;
  ingredientes: ProductoIngredienteRead[];
}

export function CartItemRow({ item, ingredientes }: CartItemRowProps) {
  const { updateQuantity, removeItem } = useCartStore();
  const [showConfirm, setShowConfirm] = useState(false);

  // Map ingredient IDs to display names
  const excludedNames = item.exclusiones
    .map((id) => ingredientes.find((ing) => ing.id === id)?.nombre)
    .filter((n): n is string => !!n);

  const lineTotal = (Number(item.precio_base) || 0) * item.cantidad;

  return (
    <div className="flex items-center gap-4 p-4 bg-white rounded-lg shadow">
      {/* Image */}
      <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden shrink-0">
        {item.imagen_url ? (
          <img
            src={item.imagen_url}
            alt={item.nombre}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-gray-400 text-2xl">🍽️</span>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-gray-900">{item.nombre}</h3>
        <p className="text-sm text-gray-500">${item.precio_base} c/u</p>
        {excludedNames.length > 0 && (
          <p className="text-xs text-gray-400 mt-1">
            Sin: {excludedNames.join(', ')}
          </p>
        )}
      </div>

      {/* Quantity controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => updateQuantity(item.productoId, item.cantidad - 1)}
          className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition-colors cursor-pointer"
          aria-label="Disminuir cantidad"
        >
          −
        </button>
        <span className="w-8 text-center font-medium tabular-nums">
          {item.cantidad}
        </span>
        <button
          onClick={() => updateQuantity(item.productoId, item.cantidad + 1)}
          className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition-colors cursor-pointer"
          aria-label="Aumentar cantidad"
        >
          +
        </button>
      </div>

      {/* Line total */}
      <div className="text-right min-w-[80px]">
        <p className="font-bold text-gray-900">${lineTotal.toFixed(2)}</p>
      </div>

      {/* Delete with confirmation */}
      {showConfirm ? (
        <div className="flex gap-1">
          <button
            onClick={() => {
              removeItem(item.productoId);
              setShowConfirm(false);
            }}
            className="text-xs bg-red-600 text-white px-2 py-1 rounded cursor-pointer hover:bg-red-700 transition-colors"
          >
            Eliminar
          </button>
          <button
            onClick={() => setShowConfirm(false)}
            className="text-xs bg-gray-400 text-white px-2 py-1 rounded cursor-pointer hover:bg-gray-500 transition-colors"
          >
            Cancelar
          </button>
        </div>
      ) : (
        <button
          onClick={() => setShowConfirm(true)}
          className="text-gray-400 hover:text-red-600 transition-colors cursor-pointer shrink-0"
          aria-label={`Eliminar ${item.nombre}`}
        >
          ✕
        </button>
      )}
    </div>
  );
}
