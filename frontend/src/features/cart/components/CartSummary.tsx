// CartSummary — Subtotal, total, and checkout button
import { useNavigate } from 'react-router-dom';
import { useCartStore, selectCartTotal, selectCartItems } from '@/shared/stores/cartStore';

export function CartSummary() {
  const navigate = useNavigate();
  const total = useCartStore(selectCartTotal);
  const items = useCartStore(selectCartItems);

  const subtotal = items.reduce((sum, item) => {
    return sum + (Number(item.precio_base) || 0) * item.cantidad;
  }, 0);

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-4">
      <h2 className="text-lg font-bold text-gray-900">Resumen del pedido</h2>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between text-gray-600">
          <span>Subtotal</span>
          <span className="tabular-nums">${subtotal.toFixed(2)}</span>
        </div>
        <div className="border-t pt-2 flex justify-between font-bold text-gray-900 text-base">
          <span>Total</span>
          <span className="tabular-nums">${total.toFixed(2)}</span>
        </div>
      </div>

      <button
        onClick={() => navigate('/pago')}
        disabled={items.length === 0}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Proceder al pago
      </button>
    </div>
  );
}
