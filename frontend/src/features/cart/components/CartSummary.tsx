// CartSummary — Subtotal, total, and checkout button
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';
import { useCartStore, selectCartTotal, selectCartItems } from '@/shared/stores/cartStore';

/** Minimal create order payload */
interface CrearPedidoPayload {
  items: Array<{
    producto_id: number;
    cantidad: number;
    exclusiones: number[];
  }>;
  direccion_id: number;
  forma_pago_codigo: string;
}

interface PedidoCreated {
  id: number;
}

export function CartSummary() {
  const navigate = useNavigate();
  const total = useCartStore(selectCartTotal);
  const items = useCartStore(selectCartItems);
  const clearCart = useCartStore((s) => s.clearCart);
  const [error, setError] = useState<string | null>(null);

  const subtotal = items.reduce((sum, item) => {
    return sum + (Number(item.precio_base) || 0) * item.cantidad;
  }, 0);

  const createOrder = useMutation({
    mutationFn: async (payload: CrearPedidoPayload) => {
      const { data } = await httpClient.post<PedidoCreated>('/pedidos/', payload);
      return data;
    },
    onSuccess: (data) => {
      clearCart();
      navigate(`/checkout?pedido_id=${data.id}`);
    },
    onError: (err: unknown) => {
      const message = err instanceof Error ? err.message : 'Error al crear el pedido. Verificá tus datos.';
      setError(message);
    },
  });

  const handleCheckout = () => {
    setError(null);

    // Build payload from cart items
    const cartItems = useCartStore.getState().items;
    const payload: CrearPedidoPayload = {
      items: cartItems.map((item) => ({
        producto_id: item.productoId,
        cantidad: item.cantidad,
        exclusiones: item.exclusiones || [],
      })),
      direccion_id: 0, // Will be selected by user
      forma_pago_codigo: 'MERCADOPAGO',
    };

    createOrder.mutateAsync(payload).catch((err: unknown) => {
      const message = err instanceof Error ? err.message : 'Error al crear el pedido. Verificá tus datos.';
      setError(message);
    });
  };

  const isProcessing = createOrder.isPending;

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

      {error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          {error}
        </div>
      )}

      <button
        onClick={handleCheckout}
        disabled={isProcessing || items.length === 0}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isProcessing ? (
          <span className="flex items-center justify-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            Creando pedido...
          </span>
        ) : (
          'Proceder al pago'
        )}
      </button>
    </div>
  );
}
