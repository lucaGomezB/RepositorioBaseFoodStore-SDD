// CartDrawer — Slide-out panel from the right showing cart contents
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useCartStore, selectCartItems, selectCartTotal, selectIsCartEmpty } from '@/shared/stores/cartStore';
import { useUIStore, selectCartDrawerOpen } from '@/shared/stores/uiStore';

export function CartDrawer() {
  const open = useUIStore(selectCartDrawerOpen);
  const setOpen = useUIStore((s) => s.setCartDrawerOpen);
  const items = useCartStore(selectCartItems);
  const total = useCartStore(selectCartTotal);
  const isCartEmpty = useCartStore(selectIsCartEmpty);

  const [visible, setVisible] = useState(false);

  // Animate slide on open/close
  useEffect(() => {
    if (open) {
      // Trigger enter animation on next frame
      const frame = requestAnimationFrame(() => setVisible(true));
      return () => cancelAnimationFrame(frame);
    } else {
      setVisible(false);
    }
  }, [open]);

  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [open, setOpen]);

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 bg-black/40 z-40 transition-opacity duration-300 ${
          visible ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setOpen(false)}
      />

      {/* Drawer panel */}
      <div
        className={`fixed top-0 right-0 h-full w-80 bg-white shadow-xl z-50 flex flex-col transition-transform duration-300 ease-in-out ${
          visible ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900">Tu Carrito</h2>
          <button
            onClick={() => setOpen(false)}
            className="text-gray-400 hover:text-gray-600 transition-colors cursor-pointer p-1"
            aria-label="Cerrar carrito"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Items list */}
        <div className="flex-1 overflow-y-auto px-4 py-4">
          {isCartEmpty ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
              <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z" />
              </svg>
              <p className="text-sm font-medium">Tu carrito está vacío</p>
              <p className="text-xs mt-1">Agregá productos desde el catálogo</p>
            </div>
          ) : (
            <ul className="space-y-3">
              {items.map((item) => (
                <li key={item.productoId} className="flex gap-3 items-start">
                  {/* Image */}
                  <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden shrink-0">
                    {item.imagen_url ? (
                      <img
                        src={item.imagen_url}
                        alt={item.nombre}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="text-gray-400 text-xl">🍽️</span>
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {item.nombre}
                    </p>
                    <p className="text-xs text-gray-500">${item.precio_base} c/u</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm text-gray-600">Cant: {item.cantidad}</span>
                      <span className="text-sm font-semibold text-gray-900 ml-auto">
                        ${((Number(item.precio_base) || 0) * item.cantidad).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-4 py-4 space-y-3">
          {!isCartEmpty && (
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600">Total</span>
              <span className="text-lg font-bold text-gray-900">${total.toFixed(2)}</span>
            </div>
          )}
          <Link
            to="/carrito"
            onClick={() => setOpen(false)}
            className={`block w-full text-center py-2.5 rounded-lg font-medium transition-colors ${
              isCartEmpty
                ? 'bg-blue-600 text-white'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            Ver carrito completo
          </Link>
        </div>
      </div>
    </>
  );
}
