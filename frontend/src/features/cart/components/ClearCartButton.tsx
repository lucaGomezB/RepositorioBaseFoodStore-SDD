// ClearCartButton — Red button with confirmation modal for emptying the cart
import { useState } from 'react';
import { useCartStore } from '@/shared/stores/cartStore';

export function ClearCartButton() {
  const [showModal, setShowModal] = useState(false);
  const clearCart = useCartStore((s) => s.clearCart);

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="bg-red-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition-colors cursor-pointer"
      >
        Vaciar carrito
      </button>

      {showModal && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
          onClick={() => setShowModal(false)}
        >
          <div
            className="bg-white rounded-lg p-6 w-full max-w-sm shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-lg font-bold mb-2">Vaciar carrito</h2>
            <p className="text-sm text-gray-600 mb-6">
              ¿Estás seguro de que querés vaciar el carrito? Esta acción no se
              puede deshacer.
            </p>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="bg-gray-400 text-white px-4 py-2 rounded cursor-pointer hover:bg-gray-500 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  clearCart();
                  setShowModal(false);
                }}
                className="bg-red-600 text-white px-4 py-2 rounded cursor-pointer hover:bg-red-700 transition-colors"
              >
                Vaciar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
