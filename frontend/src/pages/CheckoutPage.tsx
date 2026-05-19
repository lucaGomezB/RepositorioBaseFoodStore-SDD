// CheckoutPage — Payment confirmation with simple mock payment (no MercadoPago)
import { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';
import { useCartStore } from '@/shared/stores/cartStore';

// Minimal pedido type for checkout summary
interface PedidoCheckout {
  id: number;
  total: number;
  costo_envio: number;
  estado_codigo: string;
  created_at: string;
  detalles: Array<{
    id: number;
    nombre_snapshot: string;
    cantidad: number;
    precio_snapshot: number;
    subtotal: number;
    exclusiones: number[];
  }>;
  direccion_calle: string;
  direccion_numero: string;
  direccion_piso: string | null;
  direccion_ciudad: string;
  direccion_cp: string;
}

export default function CheckoutPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const pedidoId = Number(searchParams.get('pedido_id')) || 0;

  const [paymentError, setPaymentError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const clearCart = useCartStore((s) => s.clearCart);

  // Fetch order details for summary
  const { data: pedido, isLoading, isError } = useQuery({
    queryKey: ['pedido-checkout', pedidoId],
    queryFn: async () => {
      const { data } = await httpClient.get<PedidoCheckout>(`/pedidos/${pedidoId}`);
      return data;
    },
    enabled: pedidoId > 0,
  });

  const handleConfirmPayment = async () => {
    if (!pedidoId) return;

    setIsProcessing(true);
    setPaymentError(null);

    try {
      // Mock payment — no MercadoPago
      await httpClient.post('/pagos/mock', { pedido_id: pedidoId });

      clearCart();
      navigate(`/mis-pedidos/${pedidoId}`);
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : 'Error al procesar el pago. Intentá de nuevo.';
      setPaymentError(message);
      setIsProcessing(false);
    }
  };

  // ── Loading state ──
  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-500">Cargando información del pedido...</p>
        </div>
      </div>
    );
  }

  // ── Error state ──
  if (isError || !pedido) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[60vh]">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Pedido no encontrado</h1>
        <p className="text-gray-500 mb-6">
          No pudimos encontrar el pedido. Verificá que sea correcto.
        </p>
        <button
          onClick={() => navigate('/carrito')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Volver al carrito
        </button>
      </div>
    );
  }

  // ── Checkout confirmation ──
  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Confirmar y pagar</h1>

      {/* Order summary */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <h2 className="font-semibold text-gray-900 mb-3">Resumen del pedido #{pedido.id}</h2>

        <div className="space-y-2 mb-4">
          {pedido.detalles.map((item) => (
            <div key={item.id} className="flex justify-between text-sm">
              <span className="text-gray-700">
                {item.cantidad}x {item.nombre_snapshot}
              </span>
              <span className="text-gray-900 font-medium">
                ${item.subtotal.toFixed(2)}
              </span>
            </div>
          ))}
        </div>

        <div className="border-t border-gray-100 pt-2 space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Subtotal</span>
            <span>${(pedido.total - pedido.costo_envio).toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Costo de envío</span>
            <span>${pedido.costo_envio.toFixed(2)}</span>
          </div>
          <div className="flex justify-between font-bold text-base border-t border-gray-200 pt-2">
            <span>Total</span>
            <span>${pedido.total.toFixed(2)}</span>
          </div>
        </div>

        <div className="mt-3 text-xs text-gray-500">
          <p>
            📍 {pedido.direccion_calle} {pedido.direccion_numero}
            {pedido.direccion_piso && `, ${pedido.direccion_piso}`}
            , {pedido.direccion_ciudad} ({pedido.direccion_cp})
          </p>
        </div>
      </div>

      {/* Payment confirmation */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h2 className="font-semibold text-gray-900 mb-3">Confirmar pago</h2>

        {paymentError && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {paymentError}
          </div>
        )}

        <button
          onClick={handleConfirmPayment}
          disabled={isProcessing}
          className="w-full bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-lg"
        >
          {isProcessing ? (
            <span className="flex items-center justify-center gap-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              Procesando...
            </span>
          ) : (
            `Pagar $${pedido.total.toFixed(2)}`
          )}
        </button>
      </div>
    </div>
  );
}
